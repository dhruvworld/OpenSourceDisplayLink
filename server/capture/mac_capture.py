# server/capture/mac_capture.py

import Quartz
from PIL import Image
import io

def capture_screen():
    display_id = Quartz.CGMainDisplayID()
    image_ref = Quartz.CGDisplayCreateImage(display_id)
    if not image_ref:
        raise RuntimeError("Unable to capture screen")

    width = Quartz.CGImageGetWidth(image_ref)
    height = Quartz.CGImageGetHeight(image_ref)
    bytes_per_row = Quartz.CGImageGetBytesPerRow(image_ref)
    data_provider = Quartz.CGImageGetDataProvider(image_ref)
    data = Quartz.CGDataProviderCopyData(data_provider)
    buffer = bytes(data)

    # ✅ Convert raw data to Pillow Image
    return Image.frombuffer(
        "RGBA", (width, height), buffer, "raw", "RGBA", bytes_per_row, 1
    ).convert("RGB")  # ← Add this!
