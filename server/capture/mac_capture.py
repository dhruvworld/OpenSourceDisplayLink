import objc
from Quartz import CGDisplayCreateImage, CGGetActiveDisplayList, CGMainDisplayID, CGImageGetWidth, CGImageGetHeight, CGDataProviderCopyData
from Cocoa import NSEvent
from PIL import Image
import numpy as np
import io

from shared.config import FPS, USE_EXTENDED_DISPLAY, OVERLAY_MOUSE

def get_display_id():
    max_displays = 16
    display_array = (objc.typedPointer('I') * max_displays)()
    display_count = objc.typedPointer('I')()

    result = CGGetActiveDisplayList(max_displays, display_array, display_count)
    if result != 0:
        raise Exception("Failed to get display list")

    displays = display_array[:display_count[0]]

    if USE_EXTENDED_DISPLAY and len(displays) > 1:
        print(f"[DISPLAY] Using EXTENDED display: {displays[1]}")
        return displays[1]
    else:
        print(f"[DISPLAY] Using MAIN display: {displays[0]}")
        return displays[0]

def capture_screen():
    display_id = get_display_id()
    image = CGDisplayCreateImage(display_id)

    if not image:
        raise RuntimeError("Failed to capture screen")

    width = CGImageGetWidth(image)
    height = CGImageGetHeight(image)
    provider = image.dataProvider()
    data = CGDataProviderCopyData(provider)
    buffer = np.frombuffer(data, dtype=np.uint8).reshape((height, width, 4))

    rgb_array = buffer[:, :, :3]  # Drop alpha
    img = Image.fromarray(rgb_array)

    if OVERLAY_MOUSE:
        try:
            x, y = NSEvent.mouseLocation()
            y = height - int(y)
            draw = ImageDraw.Draw(img)
            draw.ellipse((x-10, y-10, x+10, y+10), outline="red", width=2)
        except Exception as e:
            print(f"[WARNING] Mouse overlay failed: {e}")

    output = io.BytesIO()
    img.save(output, format="WebP", quality=90)
    return output.getvalue()
