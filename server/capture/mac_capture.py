import Quartz
import objc
from Cocoa import NSEvent
from PIL import Image
from shared.config import TARGET_RESOLUTION, ENABLE_MOUSE_TRACKING, USE_EXTENDED_DISPLAY

def capture_screen(target_resolution=TARGET_RESOLUTION):
    try:
        max_displays = 16
        active_displays = (Quartz.CGDirectDisplayID * max_displays)()
        display_count = objc.uint32_t()

        result = Quartz.CGGetActiveDisplayList(max_displays, active_displays, objc.byref(display_count))
        if result != 0 or display_count.value == 0:
            raise RuntimeError("[FATAL] Could not get active displays")

        # Automatically pick second display if enabled and available
        display_id = (
            active_displays[1] if USE_EXTENDED_DISPLAY and display_count.value > 1 else active_displays[0]
        )

        image_ref = Quartz.CGDisplayCreateImage(display_id)
        if image_ref is None:
            raise RuntimeError("CGDisplayCreateImage returned None")

        width = Quartz.CGImageGetWidth(image_ref)
        height = Quartz.CGImageGetHeight(image_ref)
        bytes_per_row = Quartz.CGImageGetBytesPerRow(image_ref)
        data_provider = Quartz.CGImageGetDataProvider(image_ref)
        data = Quartz.CGDataProviderCopyData(data_provider)

        img = Image.frombytes("RGBA", (width, height), data, "raw", "RGBA", bytes_per_row)
        img = img.resize(target_resolution)

        # Optional mouse cursor overlay
        if ENABLE_MOUSE_TRACKING:
            mouse = NSEvent.mouseLocation()
            cursor_ref = Quartz.CGDisplayCreateImageForRect(
                Quartz.CGMainDisplayID(), Quartz.CGRectMake(mouse.x, mouse.y, 32, 32)
            )
            if cursor_ref:
                cursor_img = Image.frombytes(
                    "RGBA",
                    (Quartz.CGImageGetWidth(cursor_ref), Quartz.CGImageGetHeight(cursor_ref)),
                    Quartz.CGDataProviderCopyData(Quartz.CGImageGetDataProvider(cursor_ref)),
                    "raw", "RGBA"
                )
                img.paste(cursor_img, (int(mouse.x), int(height - mouse.y)), cursor_img)

        return img

    except Exception as e:
        print(f"[ERROR] Screen capture failed: {e}")
        return None
