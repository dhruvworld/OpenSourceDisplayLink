# server/capture/mac_capture.py

import Quartz
import ctypes
import numpy as np
from PIL import Image
import io
from shared.config import USE_EXTENDED_DISPLAY, OVERLAY_MOUSE, COMPRESS_FORMAT, JPEG_QUALITY, WEBP_QUALITY

# ✅ Define CGDirectDisplayID manually (C unsigned int)
CGDirectDisplayID = ctypes.c_uint32

def get_display_id():
    max_displays = 16
    active_displays = (CGDirectDisplayID * max_displays)()
    display_count = ctypes.c_uint32()

    result = Quartz.CGGetActiveDisplayList(
        max_displays,
        active_displays,
        ctypes.byref(display_count)
    )

    if result != 0 or display_count.value == 0:
        raise RuntimeError("No displays detected")

    if USE_EXTENDED_DISPLAY and display_count.value > 1:
        return active_displays[1]
    return active_displays[0]

def get_cursor_overlay(display_id):
    if not Quartz.CGCursorIsVisible():
        return None

    cursor_image = Quartz.CGDisplayCopyCursorImage(display_id)
    if not cursor_image:
        return None

    width = Quartz.CGImageGetWidth(cursor_image)
    height = Quartz.CGImageGetHeight(cursor_image)
    bytes_per_row = Quartz.CGImageGetBytesPerRow(cursor_image)
    data_provider = Quartz.CGImageGetDataProvider(cursor_image)
    data = Quartz.CGDataProviderCopyData(data_provider)
    image_bytes = bytes(data)

    image = Image.frombytes("RGBA", (width, height), image_bytes, "raw", "BGRA", bytes_per_row)
    return image

def capture_screen():
    display_id = get_display_id()
    image_ref = Quartz.CGDisplayCreateImage(display_id)

    width = Quartz.CGImageGetWidth(image_ref)
    height = Quartz.CGImageGetHeight(image_ref)
    bytes_per_row = Quartz.CGImageGetBytesPerRow(image_ref)
    provider = Quartz.CGImageGetDataProvider(image_ref)
    data = Quartz.CGDataProviderCopyData(provider)
    image_bytes = bytes(data)

    image = Image.frombytes("RGBA", (width, height), image_bytes, "raw", "BGRA", bytes_per_row)
    image = image.convert("RGB")

    if OVERLAY_MOUSE:
        cursor = get_cursor_overlay(display_id)
        if cursor:
            event = Quartz.CGEventCreate(None)
            loc = Quartz.CGEventGetLocation(event)
            cursor_x, cursor_y = int(loc.x), int(height - loc.y)
            image.paste(cursor, (cursor_x, cursor_y), cursor)

    # Compress frame
    buf = io.BytesIO()
    if COMPRESS_FORMAT == "WEBP":
        image.save(buf, format="WEBP", quality=WEBP_QUALITY)
    else:
        image.save(buf, format="JPEG", quality=JPEG_QUALITY)

    return buf.getvalue()
