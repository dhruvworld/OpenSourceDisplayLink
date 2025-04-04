# server/capture/mac_capture.py (fixed mouse pointer overlay)

import ctypes
import Quartz
import time
from PIL import Image, ImageDraw
from Quartz import CGDisplayCreateImage, CGMainDisplayID, CGGetActiveDisplayList
from shared.config import USE_EXTENDED_DISPLAY, OVERLAY_MOUSE

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
            draw = ImageDraw.Draw(img)
            draw.ellipse(
                (mouse_x - 5, mouse_y - 5, mouse_x + 5, mouse_y + 5),
                fill=(255, 0, 0, 255)
            )

        return img.convert("RGB")

    except Exception as e:
        print(f"[ERROR] Screen capture failed: {e}")
        return None
