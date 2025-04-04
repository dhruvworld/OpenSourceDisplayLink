# server/capture/mac_capture.py

import Quartz
import objc
from PIL import Image
import numpy as np
from shared.config import USE_EXTENDED_DISPLAY, OVERLAY_MOUSE
from AppKit import NSWorkspace, NSImage

def get_display_id():
    max_displays = 16
    active_displays = (Quartz.CGDirectDisplayID * max_displays)()
    display_count = objc.uint32()
    Quartz.CGGetActiveDisplayList(max_displays, active_displays, display_count)
    if display_count.value == 0:
        raise RuntimeError("No active displays found.")
    return active_displays[1] if USE_EXTENDED_DISPLAY and display_count.value > 1 else active_displays[0]

def capture_mouse_overlay():
    mouse_pos = Quartz.NSEvent.mouseLocation()
    screen_height = Quartz.CGDisplayPixelsHigh(Quartz.CGMainDisplayID())
    x = int(mouse_pos.x)
    y = int(screen_height - mouse_pos.y)  # Flip y-axis
    image = NSWorkspace.sharedWorkspace().iconForFileType_("png")
    image.setSize_((24, 24))
    rep = NSImage.alloc().initWithSize_(image.size()).TIFFRepresentation()
    cursor = Image.open(rep)
    return cursor.convert("RGBA"), (x, y)

def capture_screen():
    try:
        display_id = get_display_id()
        image = Quartz.CGDisplayCreateImage(display_id)
        width = Quartz.CGImageGetWidth(image)
        height = Quartz.CGImageGetHeight(image)
        bytes_per_row = Quartz.CGImageGetBytesPerRow(image)
        data_provider = Quartz.CGImageGetDataProvider(image)
        data = Quartz.CGDataProviderCopyData(data_provider)
        buffer = np.frombuffer(data, dtype=np.uint8)
        buffer = buffer.reshape((height, bytes_per_row // 4, 4))
        rgb_frame = buffer[:, :width, :3]  # Remove alpha channel
        img = Image.fromarray(rgb_frame, "RGB")

        if OVERLAY_MOUSE:
            cursor_img, pos = capture_mouse_overlay()
            img.paste(cursor_img, pos, cursor_img)

        return img
    except Exception as e:
        print(f"[ERROR] Screen capture failed: {e}")
        return None
