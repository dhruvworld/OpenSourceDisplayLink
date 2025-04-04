# server/capture/mac_capture.py

import Quartz
import time
import io
import ctypes
from PIL import Image, ImageDraw
from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
from Quartz import CGDisplayCreateImage, CGRectInfinite

from shared.config import DISPLAY_INDEX, CAPTURE_FRAME_RATE, SHOW_MOUSE

def get_active_display(index=0):
    max_displays = 16
    active_displays = (Quartz.CGDirectDisplayID * max_displays)()
    display_count = ctypes.c_uint32()

    result = Quartz.CGGetActiveDisplayList(max_displays, active_displays, ctypes.byref(display_count))
    if result != Quartz.kCGErrorSuccess:
        raise RuntimeError("[FATAL] Could not retrieve active display list")
    if display_count.value == 0:
        raise RuntimeError("[FATAL] No active displays found")
    if index >= display_count.value:
        raise RuntimeError(f"[FATAL] Display index {index} out of range")
    
    return active_displays[index]

def get_mouse_position():
    loc = Quartz.NSEvent.mouseLocation()
    screen_height = Quartz.CGDisplayPixelsHigh(Quartz.CGMainDisplayID())
    return int(loc.x), int(screen_height - loc.y)

def capture_frame():
    display_id = get_active_display(DISPLAY_INDEX)
    image_ref = CGDisplayCreateImage(display_id)
    
    if image_ref is None:
        raise RuntimeError("[ERROR] CGDisplayCreateImage returned None")
    
    width = Quartz.CGImageGetWidth(image_ref)
    height = Quartz.CGImageGetHeight(image_ref)
    bpp = Quartz.CGImageGetBitsPerPixel(image_ref)
    bpc = Quartz.CGImageGetBitsPerComponent(image_ref)
    bytes_per_row = Quartz.CGImageGetBytesPerRow(image_ref)
    data_provider = Quartz.CGImageGetDataProvider(image_ref)
    data = Quartz.CGDataProviderCopyData(data_provider)
    buffer = ctypes.string_at(Quartz.CFDataGetBytePtr(data), Quartz.CFDataGetLength(data))

    image = Image.frombuffer("RGB", (width, height), buffer, "raw", "BGRA", bytes_per_row, 1)

    if SHOW_MOUSE:
        x, y = get_mouse_position()
        draw = ImageDraw.Draw(image)
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(255, 0, 0))

    return image

def capture_loop(callback):
    frame_delay = 1.0 / CAPTURE_FRAME_RATE
    while True:
        try:
            frame = capture_frame()
            callback(frame)
        except Exception as e:
            print(f"[ERROR] Screen capture failed: {e}")
        time.sleep(frame_delay)
