import Quartz
import objc
from Cocoa import NSEvent
from Quartz import CGImageGetWidth, CGImageGetHeight, CGImageGetBytesPerRow, CGImageGetBitmapInfo, CGImageGetColorSpace, CGImageGetDataProvider, CGDataProviderCopyData
from PIL import Image

def capture_screen(target_resolution=(1920, 1080)):
    try:
        max_displays = 16
        active_displays = (Quartz.CGDirectDisplayID * max_displays)()
        display_count = objc.allocateBuffer(4)  # Allocate raw buffer

        # ✅ Correct usage of display list fetch with NULL pointer
        result = Quartz.CGGetActiveDisplayList(max_displays, active_displays, display_count)
        if result != 0:
            raise RuntimeError(f"[FATAL] Could not get displays: CGGetActiveDisplayList error {result}")

        count = int.from_bytes(display_count[:4], byteorder="little")

        if count == 0:
            raise RuntimeError("[FATAL] No displays found")

        # ✅ Select extended display if available
        display_id = active_displays[1] if count > 1 else active_displays[0]
        image_ref = Quartz.CGDisplayCreateImage(display_id)
        if not image_ref:
            raise RuntimeError("[FATAL] Could not create image from display")

        width = CGImageGetWidth(image_ref)
        height = CGImageGetHeight(image_ref)
        bytes_per_row = CGImageGetBytesPerRow(image_ref)
        bitmap_info = CGImageGetBitmapInfo(image_ref)
        color_space = CGImageGetColorSpace(image_ref)
        data_provider = CGImageGetDataProvider(image_ref)
        data = CGDataProviderCopyData(data_provider)

        # Convert to PIL image
        img = Image.frombytes("RGBA", (width, height), data, "raw", "RGBA", bytes_per_row)

        # Resize for transmission
        img = img.resize(target_resolution)

        return img

    except Exception as e:
        print(f"[ERROR] Screen capture failed: {e}")
        return None
