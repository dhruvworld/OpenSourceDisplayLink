import Quartz
import ctypes
from Cocoa import NSEvent
from PIL import Image

def get_extended_display_id():
    max_displays = 16
    active_displays = (Quartz.CGDirectDisplayID * max_displays)()
    display_count = ctypes.c_uint32(0)

    result = Quartz.CGGetActiveDisplayList(
        max_displays,
        active_displays,
        ctypes.byref(display_count)
    )

    if result != 0 or display_count.value == 0:
        raise RuntimeError("[FATAL] Could not get displays")

    if display_count.value == 1:
        print("[INFO] Only one display detected. Using main display.")
        return active_displays[0]
    else:
        print(f"[INFO] Using extended display [Index 1] out of {display_count.value}")
        return active_displays[1]  # Second display (index 1)

def capture_screen(target_resolution=(1920, 1080)):
    try:
        display_id = get_extended_display_id()
        image_ref = Quartz.CGDisplayCreateImage(display_id)

        if not image_ref:
            raise RuntimeError("[FATAL] Could not capture screen image")

        width = Quartz.CGImageGetWidth(image_ref)
        height = Quartz.CGImageGetHeight(image_ref)
        bytes_per_row = Quartz.CGImageGetBytesPerRow(image_ref)
        data_provider = Quartz.CGImageGetDataProvider(image_ref)
        data = Quartz.CGDataProviderCopyData(data_provider)

        img = Image.frombytes("RGBA", (width, height), data, "raw", "RGBA", bytes_per_row)

        # Resize to target resolution
        img = img.resize(target_resolution)

        # Optional: Draw mouse cursor
        mouse_location = NSEvent.mouseLocation()
        cursor_img = Quartz.CGDisplayCreateImageForRect(
            display_id, Quartz.CGRectMake(mouse_location.x, mouse_location.y, 32, 32)
        )
        if cursor_img:
            cursor_pil = Image.frombytes(
                "RGBA",
                (Quartz.CGImageGetWidth(cursor_img), Quartz.CGImageGetHeight(cursor_img)),
                Quartz.CGDataProviderCopyData(Quartz.CGImageGetDataProvider(cursor_img)),
                "raw",
                "RGBA"
            )
            img.paste(cursor_pil, (int(mouse_location.x), int(height - mouse_location.y)), cursor_pil)

        return img

    except Exception as e:
        print(f"[ERROR] Screen capture failed: {e}")
        return None
