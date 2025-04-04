# server/capture/mac_capture.py

import Quartz
import ctypes
from Cocoa import NSEvent
from PIL import Image

def get_extended_display_id():
    max_displays = 8
    display_count = ctypes.c_uint32()
    active_displays = (ctypes.c_uint32 * max_displays)()

    # Load CGGetActiveDisplayList from Quartz
    quartz = ctypes.cdll.LoadLibrary("/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices")
    result = quartz.CGGetActiveDisplayList(max_displays, active_displays, ctypes.byref(display_count))
    if result != 0 or display_count.value == 0:
        raise RuntimeError("No active displays found")

    print(f"[DEBUG] Found {display_count.value} displays")
    return active_displays[1] if display_count.value > 1 else active_displays[0]

def capture_screen(target_resolution=(1920, 1080)):
    try:
        display_id = get_extended_display_id()
        image_ref = Quartz.CGDisplayCreateImage(display_id)
        if not image_ref:
            raise RuntimeError("Could not capture image from display")

        width = Quartz.CGImageGetWidth(image_ref)
        height = Quartz.CGImageGetHeight(image_ref)
        data_provider = Quartz.CGImageGetDataProvider(image_ref)
        data = Quartz.CGDataProviderCopyData(data_provider)

        img = Image.frombytes("RGBA", (width, height), data, "raw", "RGBA")
        img = img.resize(target_resolution).convert("RGB")

        # Overlay mouse pointer
        mouse = NSEvent.mouseLocation()
        bounds = Quartz.CGDisplayBounds(display_id)
        rel_x = int(mouse.x - bounds.origin.x)
        rel_y = int(bounds.size.height - (mouse.y - bounds.origin.y))

        cursor_ref = Quartz.CGDisplayCreateImageForRect(
            display_id, Quartz.CGRectMake(mouse.x, mouse.y, 32, 32)
        )
        if cursor_ref:
            cursor_img = Image.frombytes(
                "RGBA",
                (Quartz.CGImageGetWidth(cursor_ref), Quartz.CGImageGetHeight(cursor_ref)),
                Quartz.CGDataProviderCopyData(Quartz.CGImageGetDataProvider(cursor_ref)),
                "raw", "RGBA"
            )
            img.paste(cursor_img, (rel_x, rel_y), cursor_img)

        return img

    except Exception as e:
        print(f"[ERROR] Screen capture failed: {e}")
        return None
