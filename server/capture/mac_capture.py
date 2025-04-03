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


def get_working_display():
    try:
        max_displays = 10
        displays = (CG.CGDirectDisplayID * max_displays)()
        display_count = CG.uint32_t()
        CG.CGGetActiveDisplayList(max_displays, displays, display_count)

        print(f"[DEBUG] Active Displays: {display_count.value}")

        for i in range(display_count.value):
            display_id = displays[i]
            print(f"  [DISPLAY {i}] Trying display ID: {display_id}")
            image_ref = CGDisplayCreateImage(display_id)

            if image_ref:
                print(f"[INFO] Using display {i} with ID {display_id}")
                return display_id

        print("[ERROR] No valid display found, defaulting to main.")
        return CGMainDisplayID()

    except Exception as e:
        print(f"[FATAL] Could not get displays: {e}")
        return CGMainDisplayID()


def capture_screen():
    try:
        display_id = get_working_display()
        image_ref = CGDisplayCreateImage(display_id)

        if not image_ref:
            print("[ERROR] Display image is null.")
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
