# server/capture/mac_capture.py

import Quartz
from Cocoa import NSEvent
from PIL import Image
import io

def get_active_display(index=0):
    max_displays = 16
    active_displays = (Quartz.CGDirectDisplayID * max_displays)()
    display_count = Quartz.uint32_t()
    result = Quartz.CGGetActiveDisplayList(max_displays, active_displays, Quartz.pointer(display_count))
    if result != 0 or display_count.value == 0:
        raise RuntimeError("[FATAL] Could not retrieve display list")
    return active_displays[index]

def capture_screen(target_resolution=(1920, 1080), display_index=0):
    try:
        display_id = get_active_display(display_index)
        image_ref = Quartz.CGDisplayCreateImage(display_id)
        if not image_ref:
            return None

        width = Quartz.CGImageGetWidth(image_ref)
        height = Quartz.CGImageGetHeight(image_ref)
        bytes_per_row = Quartz.CGImageGetBytesPerRow(image_ref)
        data_provider = Quartz.CGImageGetDataProvider(image_ref)
        data = Quartz.CGDataProviderCopyData(data_provider)

        # Convert to PIL image and correct RGB distortion
        img = Image.frombytes("RGBA", (width, height), data, "raw", "RGBA", bytes_per_row)
        img = img.convert("RGB").resize(target_resolution)

        # Mouse cursor overlay
        mouse_loc = NSEvent.mouseLocation()
        screen_height = Quartz.CGDisplayPixelsHigh(display_id)
        cursor_rect = Quartz.CGRectMake(mouse_loc.x, screen_height - mouse_loc.y, 64, 64)
        cursor_ref = Quartz.CGDisplayCreateImageForRect(display_id, cursor_rect)
        if cursor_ref:
            cw = Quartz.CGImageGetWidth(cursor_ref)
            ch = Quartz.CGImageGetHeight(cursor_ref)
            cdata = Quartz.CGDataProviderCopyData(Quartz.CGImageGetDataProvider(cursor_ref))
            cursor_img = Image.frombytes("RGBA", (cw, ch), cdata, "raw", "RGBA")
            img.paste(cursor_img, (int(mouse_loc.x), int(mouse_loc.y)), cursor_img)

        return img

    except Exception as e:
        print(f"[ERROR] Screen capture failed: {e}")
        return None
