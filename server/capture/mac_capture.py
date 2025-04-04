# server/capture/mac_capture.py

from Quartz import (
    CGDisplayCreateImage,
    CGMainDisplayID,
    CGImageGetWidth,
    CGImageGetHeight,
    CGImageGetBytesPerRow,
    CGDataProviderCopyData,
    CGImageGetDataProvider,
    CGGetActiveDisplayList
)
import Quartz.CoreGraphics as CG
from PIL import Image
import objc


def get_working_display():
    try:
        max_displays = 10
        active_displays = (CG.CGDirectDisplayID * max_displays)()
        display_count = (CG.CGDisplayCount)()

        result = CGGetActiveDisplayList(max_displays, active_displays, objc.NULL)

        if result != 0:
            print("[ERROR] CGGetActiveDisplayList failed, defaulting to main display.")
            return CGMainDisplayID()

        display_ids = []
        for i in range(max_displays):
            display_id = active_displays[i]
            if display_id == 0:
                continue
            image = CGDisplayCreateImage(display_id)
            if image:
                width = CGImageGetWidth(image)
                height = CGImageGetHeight(image)
                display_ids.append((display_id, width * height))

        if not display_ids:
            print("[WARN] No valid displays found, using main display.")
            return CGMainDisplayID()

        # Pick the largest display (by area)
        best_display = max(display_ids, key=lambda d: d[1])
        selected_id = best_display[0]

        if selected_id == CGMainDisplayID():
            print(f"[INFO] Using main display (ID: {selected_id})")
        else:
            print(f"[INFO] Using extended display (ID: {selected_id})")

        return selected_id

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
