# shared/config.py

HOST = "10.0.0.29"  # Mac IP
PORT = 9999

FRAME_RATE = 30
IMAGE_FORMAT = "WEBP"
IMAGE_QUALITY = 90
TARGET_RESOLUTION = (1280, 720)

ENABLE_MOUSE_TRACKING = True
USE_EXTENDED_DISPLAY = False  # Changed to False to use primary display
FALLBACK_TO_MAIN_DISPLAY = True  # Fallback to main display if extended display is not available
DISPLAY_INDEX = 0  # Use display index 0 (main display) if you have issues
                   # Increment this value to try different displays

# Debug options
DEBUG_MODE = True  # Enable additional logging
