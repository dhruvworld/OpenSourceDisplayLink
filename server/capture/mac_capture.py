import Quartz
import objc
from Cocoa import NSEvent
from Quartz import CGImageGetWidth, CGImageGetHeight, CGImageGetBytesPerRow, CGImageGetBitmapInfo, CGImageGetColorSpace, CGImageGetDataProvider, CGDataProviderCopyData
from PIL import Image
import sys
from shared.config import TARGET_RESOLUTION, USE_EXTENDED_DISPLAY, DISPLAY_INDEX, FALLBACK_TO_MAIN_DISPLAY, DEBUG_MODE

def capture_screen(target_resolution=None):
    if target_resolution is None:
        target_resolution = TARGET_RESOLUTION
        
    try:
        max_displays = 16
        active_displays = (Quartz.CGDirectDisplayID * max_displays)()
        display_count = objc.allocateBuffer(4)  # Allocate raw buffer

        # Get display list
        result = Quartz.CGGetActiveDisplayList(max_displays, active_displays, display_count)
        if result != 0:
            raise RuntimeError(f"[FATAL] Could not get displays: CGGetActiveDisplayList error {result}")

        count = int.from_bytes(display_count[:4], byteorder="little")

        if count == 0:
            raise RuntimeError("[FATAL] No displays found")

        if DEBUG_MODE:
            print(f"[DEBUG] Found {count} displays")
            
        # Select appropriate display based on config
        selected_display_index = 0  # Default to main display
        
        if USE_EXTENDED_DISPLAY and count > 1:
            # Use extended display (usually index 1)
            selected_display_index = 1
        elif DISPLAY_INDEX < count:
            # Use specifically configured display index
            selected_display_index = DISPLAY_INDEX
        elif DISPLAY_INDEX >= count and FALLBACK_TO_MAIN_DISPLAY:
            # Fallback to main display
            selected_display_index = 0
        else:
            # Specified display index is out of range and no fallback
            raise RuntimeError(f"[FATAL] Requested display index {DISPLAY_INDEX} not available (only {count} displays found)")
            
        if DEBUG_MODE:
            print(f"[DEBUG] Using display at index {selected_display_index}")
            
        # Get the display ID
        display_id = active_displays[selected_display_index]
        
        # Create image from display
        image_ref = Quartz.CGDisplayCreateImage(display_id)
        if not image_ref:
            raise RuntimeError("[FATAL] Could not create image from display")

        # Process image data
        width = CGImageGetWidth(image_ref)
        height = CGImageGetHeight(image_ref)
        bytes_per_row = CGImageGetBytesPerRow(image_ref)
        bitmap_info = CGImageGetBitmapInfo(image_ref)
        color_space = CGImageGetColorSpace(image_ref)
        data_provider = CGImageGetDataProvider(image_ref)
        data = CGDataProviderCopyData(data_provider)

        # Convert to PIL image
        img = Image.frombytes("RGBA", (width, height), data, "raw", "RGBA", bytes_per_row)

        # Resize for transmission
        img = img.resize(target_resolution)

        return img

    except Exception as e:
        print(f"[ERROR] Screen capture failed: {e}")
        if DEBUG_MODE:
            import traceback
            traceback.print_exc()
        return None
