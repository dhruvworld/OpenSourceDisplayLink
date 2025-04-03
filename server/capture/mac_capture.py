# server/capture/mac_capture.py

from Quartz import CGGetActiveDisplayList, CGDisplayCreateImage, CGMainDisplayID
from Quartz import CGImageGetWidth, CGImageGetHeight, CGImageGetBytesPerRow
from Quartz import CGDataProviderCopyData, CGImageGetDataProvider
from PIL import Image, ImageDraw
import Quartz.CoreGraphics as CG

def get_secondary_display():
    max_displays = 10
    displays = (CG.CGDirectDisplayID * max_displays)()
    display_count = CG.uint32_t()
    CG.CGGetActiveDisplayList(max_displays, displays, display_count)
    print(f"[DEBUG] Found {display_count.value} displays")

    if display_count.value > 1:
        return displays[1]  # Virtual display
    return displays[0]      # Fallback to primary

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
        # Optional: draw mouse (comment if unwanted)
        # draw = ImageDraw.Draw(image)
        # draw.ellipse((100, 100, 110, 110), fill="orange")

        return image

    except Exception as e:
        print(f"[ERROR] Screen capture failed: {e}")
        return None
