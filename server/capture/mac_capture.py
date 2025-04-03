from Quartz import (
    CGWindowListCreateImage, CGDisplayBounds,
    kCGWindowListOptionOnScreenOnly, kCGNullWindowID, kCGWindowImageDefault,
    CGImageGetWidth, CGImageGetHeight, CGDataProviderCopyData, CGImageGetDataProvider,
    CGRectInfinite, CGEventCreate, CGEventGetLocation
)
from PIL import Image
import io
from shared.config import TARGET_RESOLUTION, IMAGE_FORMAT, IMAGE_QUALITY, ENABLE_MOUSE_TRACKING

def get_mouse_position():
    event = CGEventCreate(None)
    loc = CGEventGetLocation(event)
    return int(loc.x), int(loc.y)

def capture_screen():
    image = CGWindowListCreateImage(
        CGRectInfinite,
        kCGWindowListOptionOnScreenOnly,
        kCGNullWindowID,
        kCGWindowImageDefault
    )

    if image:
        width = CGImageGetWidth(image)
        height = CGImageGetHeight(image)

        provider = CGImageGetDataProvider(image)
        bitmap_data = CGDataProviderCopyData(provider)

        pil_image = Image.frombuffer(
            "RGBA", (width, height), bytes(bitmap_data),
            "raw", "RGBA", 0, 1
        ).convert("RGB")

        pil_image = pil_image.resize(TARGET_RESOLUTION)

        # Draw mouse cursor
        if ENABLE_MOUSE_TRACKING:
            mouse_x, mouse_y = get_mouse_position()
            scale_x = TARGET_RESOLUTION[0] / width
            scale_y = TARGET_RESOLUTION[1] / height
            mouse_x = int(mouse_x * scale_x)
            mouse_y = int(mouse_y * scale_y)
            from PIL import ImageDraw
            draw = ImageDraw.Draw(pil_image)
            draw.ellipse((mouse_x-10, mouse_y-10, mouse_x+10, mouse_y+10), fill="red")

        buffer = io.BytesIO()
        pil_image.save(buffer, format=IMAGE_FORMAT, quality=IMAGE_QUALITY, optimize=True)
        return buffer.getvalue()

    return None
