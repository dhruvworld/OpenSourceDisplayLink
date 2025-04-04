# server/capture/mac_capture.py

import ctypes
from io import BytesIO
from PIL import Image
import numpy as np
import objc
from Quartz import (
    CGDisplayBounds,
    CGDisplayCreateImage,
    CGGetActiveDisplayList,
    CGMainDisplayID,
    CGDisplayPixelsWide,
    CGDisplayPixelsHigh,
)
from shared.config import USE_EXTENDED_DISPLAY, OVERLAY_MOUSE


def get_display_id():
    max_displays = 16
    display_count = ctypes.c_uint32(0)
    display_array = (ctypes.c_uint32 * max_displays)()

    result = CGGetActiveDisplayList(
        max_displays,
        display_array,
        ctypes.byref(display_count)
    )

    if result != 0:
        raise RuntimeError("Unable to get active display list")

    displays = list(display_array[:display_count.value])
    if USE_EXTENDED_DISPLAY and len(displays) > 1:
        display_id = displays[1]
        print(f"[DISPLAY] Using EXTENDED display: {display_id}")
    else:
        display_id = displays[0]
        print(f"[DISPLAY] Using MAIN display: {display_id}")

    return display_id


def capture_screen():
    display_id = get_display_id()
    image_ref = CGDisplayCreateImage(display_id)
    if not image_ref:
        raise RuntimeError("Unable to capture screen")

    width = CGDisplayPixelsWide(display_id)
    height = CGDisplayPixelsHigh(display_id)

    provider = image_ref.dataProvider()
    if provider is None:
        raise RuntimeError("No data provider from image_ref")

    data = provider.data()
    ptr = ctypes.c_void_p(objc.dataPointer(data))
    buf_len = objc.dataLength(data)

    raw_bytes = ctypes.string_at(ptr, buf_len)
    img = Image.frombytes("RGBA", (width, height), raw_bytes, "raw", "BGRA")

    # OPTIONAL: Draw red circle at mouse pointer location (if OVERLAY_MOUSE = True)
    if OVERLAY_MOUSE:
        from Quartz import CGEventCreate, CGEventGetLocation
        event = CGEventCreate(None)
        loc = CGEventGetLocation(event)
        mouse_x = int(loc.x)
        mouse_y = int(height - loc.y)  # Flip Y for Quartz → PIL

        import cv2
        img_np = np.array(img)
        img_np = cv2.circle(img_np, (mouse_x, mouse_y), radius=8, color=(255, 0, 0), thickness=-1)
        img = Image.fromarray(img_np)

    output = BytesIO()
    img.convert("RGB").save(output, format="WebP", quality=85)
    return output.getvalue()
