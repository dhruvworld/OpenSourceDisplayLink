# server/main.py

import socket
import threading
import time
import io
from PIL import Image
from server.capture.mac_capture import capture_screen
from shared.config import HOST, PORT, FRAME_RATE, IMAGE_FORMAT, IMAGE_QUALITY, TARGET_RESOLUTION, DISPLAY_INDEX

def encode_frame(image):
    buffer = io.BytesIO()
    image.save(buffer, format=IMAGE_FORMAT, quality=IMAGE_QUALITY)
    return buffer.getvalue()

def handle_client(conn, addr):
    print(f"[CONNECTED] {addr}")
    try:
        while True:
            frame = capture_screen(target_resolution=TARGET_RESOLUTION, display_index=DISPLAY_INDEX)
            if frame is None:
                continue
            encoded = encode_frame(frame)
            size = len(encoded)
            conn.sendall(size.to_bytes(4, 'big'))
            conn.sendall(encoded)
            time.sleep(1 / FRAME_RATE)
    except Exception as e:
        print(f"[DISCONNECTED] {addr} - {e}")
    finally:
        conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[LISTENING] Server running on {HOST}:{PORT}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
