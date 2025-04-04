# server/capture/mac_capture.py

import ctypes
import objc
import Quartz
from PIL import Image
import io

def get_display_id():
    # Setup ctypes access to CoreGraphics
    CoreGraphics = ctypes.cdll.LoadLibrary("/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics")
    
    max_displays = 16
    display_count = ctypes.c_uint32(0)
    active_displays = (ctypes.c_uint32 * max_displays)()

    # Properly pass pointer to display_count
    result = CoreGraphics.CGGetActiveDisplayList(
        max_displays,
        ctypes.byref(active_displays),
        ctypes.byref(display_count)
    )

    if result != 0:
        raise Exception("CGGetActiveDisplayList failed")

    # Print all display IDs (debug)
    print(f"[DEBUG] Found {display_count.value} active displays: {list(active_displays)[:display_count.value]}")
    
    # Use primary/main display for now (first one)
    return active_displays[0]

def capture_screen_webp(quality=90):
    display_id = get_display_id()
    image = Quartz.CGDisplayCreateImage(display_id)
    if image is None:
        raise Exception("CGDisplayCreateImage failed")

    width = Quartz.CGImageGetWidth(image)
    height = Quartz.CGImageGetHeight(image)
    bytes_per_row = Quartz.CGImageGetBytesPerRow(image)
    data_provider = Quartz.CGImageGetDataProvider(image)
    pixel_data = Quartz.CGDataProviderCopyData(data_provider)
    buffer = bytes(pixel_data)

    pil_image = Image.frombuffer("RGBA", (width, height), buffer, "raw", "RGBA", bytes_per_row, 1)

    with io.BytesIO() as output:
        pil_image.save(output, format="WEBP", quality=quality)
        return output.getvalue()
