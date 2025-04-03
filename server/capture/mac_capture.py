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
import Quartz.CoreGraphics as CG
from PIL import Image
import ctypes


def get_working_display():
    try:
        max_displays = 10
        active_displays = (ctypes.c_uint32 * max_displays)()
        display_count = ctypes.c_uint32(0)

        result = CG.CGGetActiveDisplayList(
            max_displays, active_displays, ctypes.byref(display_count)
        )

        if result != 0:
            print("[ERROR] CGGetActiveDisplayList failed.")
            return CGMainDisplayID()

        print(f"[DEBUG] Found {display_count.value} displays")

        for i in range(display_count.value):
            display_id = active_displays[i]
            image_ref = CGDisplayCreateImage(display_id)
            if image_ref:
                print(f"[INFO] Using display {i} (ID {display_id})")
                return display_id

        print("[WARN] No valid displays found, fallback to main.")
        return CGMainDisplayID()

    except Exception as e:
        print(f"[FATAL] Could not get displays: {e}")
        return CGMainDisplayID()


def capture_screen():
    try:
        display_id = get_working_display()
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
