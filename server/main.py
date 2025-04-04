import socket
import threading
from shared.config import HOST, PORT, FPS
from server.capture.mac_capture import capture_screen

def client_handler(conn):
    try:
        while True:
            frame = capture_screen()
            frame_size = len(frame).to_bytes(4, byteorder='big')
            conn.sendall(frame_size + frame)
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
        print(f"[CONNECTED] {addr}")
        threading.Thread(target=client_handler, args=(conn,)).start()

if __name__ == "__main__":
    start_server()
