# server/capture/mac_capture.py

import Quartz
from Quartz import CGDisplayBounds, CGDisplayCreateImage
from Cocoa import NSEvent
from PIL import Image
import io

def get_extended_display_id():
    max_displays = 8
    active_displays = (Quartz.CGDirectDisplayID * max_displays)()
    display_count = Quartz.UInt32()
    result = Quartz.CGGetActiveDisplayList(max_displays, active_displays, Quartz.pointer(display_count))
    if result != 0 or display_count.value == 0:
        raise RuntimeError("No active displays found")

    # Prefer external monitor (second display if available)
    return active_displays[1] if display_count.value > 1 else active_displays[0]

def capture_screen(target_resolution=(1920, 1080)):
    try:
        display_id = get_extended_display_id()
        display_bounds = CGDisplayBounds(display_id)
        image_ref = CGDisplayCreateImage(display_id)

        if not image_ref:
            raise RuntimeError("Failed to capture display image")

        width = Quartz.CGImageGetWidth(image_ref)
        height = Quartz.CGImageGetHeight(image_ref)
        data_provider = Quartz.CGImageGetDataProvider(image_ref)
        data = Quartz.CGDataProviderCopyData(data_provider)
        img = Image.frombytes("RGBA", (width, height), data, "raw", "RGBA")

        # Resize and convert to RGB (drop alpha for compression)
        img = img.resize(target_resolution).convert("RGB")

        # Optional mouse cursor overlay
        mouse = NSEvent.mouseLocation()
        cursor_x = int(mouse.x - display_bounds.origin.x)
        cursor_y = int(display_bounds.size.height - (mouse.y - display_bounds.origin.y))
        cursor_box = Quartz.CGRectMake(mouse.x, mouse.y, 32, 32)
        cursor_ref = Quartz.CGDisplayCreateImageForRect(display_id, cursor_box)

        if cursor_ref:
            cursor = Image.frombytes(
                "RGBA",
                (Quartz.CGImageGetWidth(cursor_ref), Quartz.CGImageGetHeight(cursor_ref)),
                Quartz.CGDataProviderCopyData(Quartz.CGImageGetDataProvider(cursor_ref)),
                "raw", "RGBA"
            )
            img.paste(cursor, (cursor_x, cursor_y), cursor)

        return img

    except Exception as e:
        print(f"[ERROR] Screen capture failed: {e}")
        return None
