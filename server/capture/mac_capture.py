# server/capture/mac_capture.py

from Quartz import (
    CGGetActiveDisplayList,
    CGDisplayCreateImage,
    CGMainDisplayID,
    CGImageGetWidth,
    CGImageGetHeight,
    CGImageGetBytesPerRow,
    CGDataProviderCopyData,
    CGImageGetDataProvider
)
from PIL import Image
import Quartz.CoreGraphics as CG


def get_secondary_display():
    max_displays = 10
    displays = (CG.CGDirectDisplayID * max_displays)()
    display_count = CG.uint32_t()
    CG.CGGetActiveDisplayList(max_displays, displays, display_count)

    print(f"[DEBUG] Active Displays: {display_count.value}")
    for i in range(display_count.value):
        print(f"  [DISPLAY {i}] ID: {displays[i]}")

    if display_count.value > 1:
        print("[INFO] Using secondary display.")
        return displays[1]
    else:
        print("[WARN] Only one display detected. Falling back to main display.")
        return CGMainDisplayID()


def capture_screen():
    try:
        display_id = get_secondary_display()
        image_ref = CGDisplayCreateImage(display_id)

        if not image_ref:
            print("[ERROR] Display image is null")
            return None

        width = CGImageGetWidth(image_ref)
        height = CGImageGetHeight(image_ref)
        bytes_per_row = CGImageGetBytesPerRow(image_ref)
        provider = CGImageGetDataProvider(image_ref)
        data = CGDataProviderCopyData(provider)

        image = Image.frombytes("RGBA", (width, height), data, "raw", "RGBA", bytes_per_row)
        return image

    except Exception as e:
        print(f"[ERROR] Screen capture failed: {e}")
        return None
