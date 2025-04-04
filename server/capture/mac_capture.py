import Quartz
from Cocoa import NSScreen, NSRect
from PIL import Image
import ctypes
import objc
import io
import sys
from shared.config import TARGET_RESOLUTION, USE_EXTENDED_DISPLAY, DISPLAY_INDEX, FALLBACK_TO_MAIN_DISPLAY, DEBUG_MODE

def capture_screen(target_resolution=None):
    if target_resolution is None:
        target_resolution = TARGET_RESOLUTION
        
    try:
        # Get screen information using NSScreen
        screens = NSScreen.screens()
        
        if not screens or len(screens) == 0:
            raise RuntimeError("[FATAL] No displays found")
            
        if DEBUG_MODE:
            print(f"[DEBUG] Found {len(screens)} displays")
            
        # Select appropriate display based on config
        selected_display_index = 0
        
        if USE_EXTENDED_DISPLAY and len(screens) > 1:
            selected_display_index = 1
        elif DISPLAY_INDEX < len(screens):
            selected_display_index = DISPLAY_INDEX
        elif DISPLAY_INDEX >= len(screens) and FALLBACK_TO_MAIN_DISPLAY:
            selected_display_index = 0
        else:
            raise RuntimeError(f"[FATAL] Requested display index {DISPLAY_INDEX} not available (only {len(screens)} displays found)")
            
        if DEBUG_MODE:
            print(f"[DEBUG] Using display at index {selected_display_index}")
            
        # Get the selected screen
        screen = screens[selected_display_index]
        
        # Get screen dimensions
        frame = screen.frame()
        width = int(frame.size.width)
        height = int(frame.size.height)
        x = int(frame.origin.x)
        y = int(frame.origin.y)
        
        if DEBUG_MODE:
            print(f"[DEBUG] Screen dimensions: {width}x{height} at position ({x},{y})")
        
        # Capture the screen content
        region = Quartz.CGRectMake(x, y, width, height)
        image_ref = Quartz.CGWindowListCreateImage(
            region,
            Quartz.kCGWindowListOptionOnScreenOnly,
            Quartz.kCGNullWindowID,
            Quartz.kCGWindowImageDefault
        )
        
        if not image_ref:
            raise RuntimeError("[FATAL] Could not create image from display")
        
        # Get image dimensions
        width = Quartz.CGImageGetWidth(image_ref)
        height = Quartz.CGImageGetHeight(image_ref)
        bytes_per_row = Quartz.CGImageGetBytesPerRow(image_ref)
        
        # Get image data
        data_provider = Quartz.CGImageGetDataProvider(image_ref)
        data = Quartz.CGDataProviderCopyData(data_provider)
        
        # Convert to PIL image
        img = Image.frombytes("RGBA", (width, height), data, "raw", "BGRA", bytes_per_row)
        
        # Resize for transmission
        img = img.resize(target_resolution)
        
        # Release resources
        del data
        
        return img

    except Exception as e:
        print(f"[ERROR] Screen capture failed: {e}")
        if DEBUG_MODE:
            import traceback
            traceback.print_exc()
        return None
