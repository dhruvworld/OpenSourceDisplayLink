from Quartz import CGDisplayBounds, CGWindowListCreateImage, kCGWindowListOptionOnScreenOnly, kCGNullWindowID, kCGWindowImageDefault
from Quartz import CGDisplayCopyDisplayMode, CGMainDisplayID
from PIL import Image, ImageDraw
import Quartz.CoreGraphics as CG

def capture_screen():
    display_id = CGMainDisplayID()
    bounds = CGDisplayBounds(display_id)
    image_ref = CGWindowListCreateImage(
        bounds,
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

    # Fix cursor alignment
    loc = CG.CGEventGetLocation(CG.CGEventCreate(None))
    x = int(loc.x - bounds.origin.x)
    y = int(height - (loc.y - bounds.origin.y))  # Flip Y-axis

    draw = ImageDraw.Draw(pil_image)
    draw.ellipse((x - 10, y - 10, x + 10, y + 10), fill="white")


    return pil_image
