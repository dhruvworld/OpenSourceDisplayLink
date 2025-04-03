# server/capture/mac_capture.py

from Quartz import CGDisplayBounds, CGWindowListCreateImage, kCGWindowListOptionOnScreenOnly, kCGNullWindowID, kCGWindowImageDefault
from Quartz import CGDisplayCopyDisplayMode, CGMainDisplayID
from PIL import Image, ImageDraw
import Quartz.CoreGraphics as CG

def capture_screen():
    display_id = CGMainDisplayID()
    image_ref = CGWindowListCreateImage(
        CGDisplayBounds(display_id),
        kCGWindowListOptionOnScreenOnly,
        kCGNullWindowID,
        kCGWindowImageDefault
    )
    width = CG.CGImageGetWidth(image_ref)
    height = CG.CGImageGetHeight(image_ref)
    bytes_per_row = CG.CGImageGetBytesPerRow(image_ref)
    data_provider = CG.CGImageGetDataProvider(image_ref)
    data = CG.CGDataProviderCopyData(data_provider)
    pil_image = Image.frombytes("RGBA", (width, height), data, "raw", "RGBA", bytes_per_row)

    # Draw mouse
    loc = CG.CGEventGetLocation(CG.CGEventCreate(None))
    draw = ImageDraw.Draw(pil_image)
    draw.ellipse((loc.x - 5, loc.y - 5, loc.x + 5, loc.y + 5), fill="orange")

    return pil_image
