# server/main.py

import socket
import threading
import io
from PIL import Image
from server.capture.mac_capture import capture_screen
from shared.config import HOST, PORT, FPS
import time

def client_handler(conn, addr):
    print(f"[CONNECTED] {addr}")
    while True:
        frame = capture_screen()
        if frame:
            with io.BytesIO() as buffer:
                frame.save(buffer, format="JPEG", quality=80)
                data = buffer.getvalue()
            try:
                conn.sendall(len(data).to_bytes(4, 'big') + data)
            except Exception:
                break
        time.sleep(1 / FPS)
    conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1)
    print(f"[LISTENING] Server running on {HOST}:{PORT}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=client_handler, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    start_server()
