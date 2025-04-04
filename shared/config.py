# shared/config.py

# 🖥️ Streaming Configuration
HOST = "10.0.0.29"       # IP address of your Mac (change if dynamic)
PORT = 9999              # Port for socket server
FPS = 30                 # Frames per second to stream

# 🧩 Display Options
USE_EXTENDED_DISPLAY = True      # If True, will capture secondary display if available
SELECTED_DISPLAY_ID = None       # (Optional) Override display ID manually if set

# 🖱️ Mouse Pointer Overlay
OVERLAY_MOUSE = True             # Overlay system cursor on captured frames
