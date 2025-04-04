# server/capture/mac_capture.py

import Quartz
import objc
import numpy as np
from PIL import Image
import io
from shared.config import USE_EXTENDED_DISPLAY, OVERLAY_MOUSE, COMPRESS_FORMAT, JPEG_QUALITY, WEBP_QUALITY

# ✅ Fix CGDirectDisplayID manually (typedef unsigned int)
CGDirectDisplayID = objc._C_UINT

def get_display_id():
    max_displays = 16
    display_array = (Quartz.CGDirectDisplayID * max_displays)()
    display_count = objc.uint32()

    # ✅ Use ctypes-style binding for count
    result = Quartz.CGGetActiveDisplayList(max_displays, display_array, objc.byref(display_count))
    if result != 0 or display_count.value == 0:
        raise RuntimeError("No displays detected")

    # ✅ Toggle based on config
    if USE_EXTENDED_DISPLAY and display_count.value > 1:
        return display_array[1]
    return display_array[0]

def get_cursor_overlay():
    if not Quartz.CGCursorIsVisible():
        return None

    cursor_image = Quartz.CGDisplayCopyCursorImage(get_display_id())
    if not cursor_image:
        return None

    width = Quartz.CGImageGetWidth(cursor_image)
    height = Quartz.CGImageGetHeight(cursor_image)
    bytes_per_row = Quartz.CGImageGetBytesPerRow(cursor_image)
    data_provider = Quartz.CGImageGetDataProvider(cursor_image)
    data = Quartz.CGDataProviderCopyData(data_provider)
    image_bytes = bytes(data)

    image = Image.frombytes("RGBA", (width, height), image_bytes, "raw", "BGRA", bytes_per_row)
    return image, Quartz.CGDisplayPixelsWide(get_display_id()), Quartz.CGDisplayPixelsHigh(get_display_id())

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
        pointer_info = get_cursor_overlay()
        if pointer_info:
            cursor_img, max_width, max_height = pointer_info
            mouse_pos = Quartz.CGEventGetLocation(Quartz.CGEventCreate(None))
            x, y = int(mouse_pos.x), int(max_height - mouse_pos.y)
            image.paste(cursor_img, (x, y), cursor_img)

    # Compress to JPEG or WebP
    buf = io.BytesIO()
    if COMPRESS_FORMAT == "WEBP":
        image.save(buf, format="WEBP", quality=WEBP_QUALITY)
    else:
        image.save(buf, format="JPEG", quality=JPEG_QUALITY)

    return buf.getvalue()
