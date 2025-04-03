from Quartz import CGGetActiveDisplayList, CGDisplayBounds, CGDisplayCreateImage
from PIL import Image, ImageDraw
import Quartz.CoreGraphics as CG

def get_secondary_display():
    max_displays = 10
    displays = (CG.CGDirectDisplayID * max_displays)()
    display_count = CG.uint32_t()
    CG.CGGetActiveDisplayList(max_displays, displays, display_count)
    if display_count.value > 1:
        return displays[1]  # Secondary
    return displays[0]  # Fallback to main

def capture_screen():
    display_id = get_secondary_display()
    image_ref = CGDisplayCreateImage(display_id)
    width = CG.CGImageGetWidth(image_ref)
    height = CG.CGImageGetHeight(image_ref)
    bytes_per_row = CG.CGImageGetBytesPerRow(image_ref)
    provider = CG.CGImageGetDataProvider(image_ref)
    data = CG.CGDataProviderCopyData(provider)
    img = Image.frombytes("RGBA", (width, height), data, "raw", "RGBA", bytes_per_row)

    # Optional: draw mouse
    return img
