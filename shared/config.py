# shared/config.py

HOST = "10.0.0.29"         # Your Mac’s IP (from ifconfig)
PORT = 9999                # Socket port

# Streaming settings
FRAME_RATE = 30            # FPS limit
IMAGE_FORMAT = "WEBP"      # High-efficiency compression
IMAGE_QUALITY = 90         # 0–100 (higher = better quality)
ENABLE_MOUSE_TRACKING = True
TARGET_RESOLUTION = (1280, 720)  # You can increase to 1920x1080 or 3840x2160 later
