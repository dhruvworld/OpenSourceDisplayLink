# server/capture/mac_capture.py

import ctypes
import Quartz
import AppKit
import time
from PIL import Image
from io import BytesIO
from Quartz import CGDisplayBounds, CGMainDisplayID, CGGetActiveDisplayList, CGDisplayCreateImage
from shared.config import USE_EXTENDED_DISPLAY, OVERLAY_MOUSE

# Load CoreGraphics functions
CGDirectDisplayID = ctypes.c_uint32

def get_display_id():
    max_displays = 10
    active_displays = (CGDirectDisplayID * max_displays)()
    display_count = ctypes.c_uint32()
    
    Quartz.CGGetActiveDisplayList(max_displays, active_displays, ctypes.byref(display_count))
    
    if USE_EXTENDED_DISPLAY and display_count.value > 1:
        return active_displays[1]
    return CGMainDisplayID()

def get_mouse_position():
    loc = Quartz.CGEventGetLocation(Quartz.CGEventCreate(None))
    return int(loc.x), int(loc.y)

def capture_screen():
    try:
        display_id = get_display_id()
        image_ref = CGDisplayCreateImage(display_id)
        if not image_ref:
            raise RuntimeError("Failed to capture screen")

        width = Quartz.CGImageGetWidth(image_ref)
        height = Quartz.CGImageGetHeight(image_ref)
        bpp = Quartz.CGImageGetBitsPerPixel(image_ref)

        provider = Quartz.CGImageGetDataProvider(image_ref)
        data = Quartz.CGDataProviderCopyData(provider)
        buffer = ctypes.string_at(data, Quartz.CFDataGetLength(data))

        img = Image.frombuffer("RGBA", (width, height), buffer, "raw", "BGRA", 0, 1)

        if OVERLAY_MOUSE:
            mouse_x, mouse_y = get_mouse_position()
            cursor_img = AppKit.NSCursor.arrowCursor().image()
            if cursor_img:
                rep = AppKit.NSBitmapImageRep.alloc().initWithCIImage_(cursor_img.CIImage())
                pointer = Image.frombytes("RGBA", (rep.pixelsWide(), rep.pixelsHigh()), rep.bitmapData())
                img.paste(pointer, (mouse_x, mouse_y), pointer)

        return img.convert("RGB")
    except Exception as e:
        print(f"[ERROR] Screen capture failed: {e}")
        return None
