# server/main.py

import socket
import threading
from server.capture.mac_capture import capture_screen
from shared.config import HOST, PORT

def client_handler(conn, addr):
    print(f"[CONNECTED] {addr}")
    try:
        while True:
            frame = capture_screen()
            conn.sendall(frame)
    except Exception as e:
        print(f"[ERROR] Connection error: {e}")
    finally:
        conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1)
    print(f"[LISTENING] Server running on {HOST}:{PORT}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=client_handler, args=(conn, addr)).start()

if __name__ == "__main__":
    start_server()
