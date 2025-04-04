# server/capture/mac_capture.py
import Quartz
import objc
import numpy as np
from PIL import Image, ImageDraw
from io import BytesIO
from shared.config import USE_EXTENDED_DISPLAY, OVERLAY_MOUSE

def get_display_id():
    max_displays = 16
    active_displays = (Quartz.CGDirectDisplayID * max_displays)()
    display_count = objc.typedPointer(objc._C_UINT)(0)
    
    result = Quartz.CGGetActiveDisplayList(max_displays, active_displays, display_count)
    if result != 0:
        raise RuntimeError("CGGetActiveDisplayList failed")

    display_ids = [active_displays[i] for i in range(display_count.value)]
    
    if USE_EXTENDED_DISPLAY and len(display_ids) > 1:
        print(f"[DISPLAY] Using EXTENDED display: {display_ids[1]}")
        return display_ids[1]
    else:
        print(f"[DISPLAY] Using MAIN display: {display_ids[0]}")
        return display_ids[0]

def capture_screen():
    display_id = get_display_id()
    image = Quartz.CGDisplayCreateImage(display_id)
    if image is None:
        raise RuntimeError("Failed to capture screen")

    width = Quartz.CGImageGetWidth(image)
    height = Quartz.CGImageGetHeight(image)
    bytes_per_row = Quartz.CGImageGetBytesPerRow(image)
    data_provider = Quartz.CGImageGetDataProvider(image)
    data = Quartz.CGDataProviderCopyData(data_provider)
    
    buffer = np.frombuffer(data, dtype=np.uint8)
    buffer = buffer.reshape((height, bytes_per_row // 4, 4))
    rgb_frame = buffer[:, :width, :3]

    img = Image.fromarray(rgb_frame, 'RGB')

    if OVERLAY_MOUSE:
        img = draw_mouse_pointer(img)

    with BytesIO() as output:
        img.save(output, format="WebP", quality=80)
        return output.getvalue()

def draw_mouse_pointer(img):
    cursor_pos = Quartz.NSEvent.mouseLocation()
    screen_height = Quartz.CGDisplayPixelsHigh(Quartz.CGMainDisplayID())
    x, y = int(cursor_pos.x), int(screen_height - cursor_pos.y)

    draw = ImageDraw.Draw(img)
    radius = 10
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill="red")
    return img
