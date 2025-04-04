# server/capture/mac_capture.py

import Quartz
import ctypes
from PIL import Image, ImageDraw
import numpy as np
import io
import sys
from shared.config import USE_EXTENDED_DISPLAY, OVERLAY_MOUSE


def get_display_id():
    max_displays = 16
    display_count = ctypes.c_uint32()
    active_displays = (Quartz.CGDirectDisplayID * max_displays)()
    Quartz.CGGetActiveDisplayList(max_displays, active_displays, objc.byref(display_count))

    display_ids = active_displays[:display_count.value]

    if USE_EXTENDED_DISPLAY and len(display_ids) > 1:
        print(f"[DISPLAY] Using EXTENDED display: {display_ids[1]}")
        return display_ids[1]
    print(f"[DISPLAY] Using MAIN display: {display_ids[0]}")
    return display_ids[0]

def capture_screen():
    display_id = get_display_id()
    image_ref = Quartz.CGDisplayCreateImage(display_id)
    if not image_ref:
        raise RuntimeError("Failed to capture screen")

    provider = Quartz.CGImageGetDataProvider(image_ref)
    data = Quartz.CGDataProviderCopyData(provider)
    width = Quartz.CGImageGetWidth(image_ref)
    height = Quartz.CGImageGetHeight(image_ref)
    bpp = Quartz.CGImageGetBitsPerPixel(image_ref) // 8

    np_image = np.frombuffer(data, dtype=np.uint8).reshape((height, width, bpp))[:, :, :3]
    image = Image.fromarray(np_image, 'RGB')

    if OVERLAY_MOUSE:
        mouse_pos = Quartz.NSEvent.mouseLocation()
        mouse_x = int(mouse_pos.x)
        mouse_y = int(Quartz.CGDisplayPixelsHigh(display_id) - mouse_pos.y)
        draw = ImageDraw.Draw(image)
        draw.ellipse((mouse_x - 5, mouse_y - 5, mouse_x + 5, mouse_y + 5), fill="red")

    buffer = io.BytesIO()
    image.save(buffer, format="WebP", quality=80)
    return buffer.getvalue()
