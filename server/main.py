import socket, threading, time
from shared.config import *
from server.capture.mac_capture import capture_screen

def handle_client(conn, addr):
    print(f"[CONNECTED] {addr}")
    try:
        while True:
            frame = capture_screen()
            if frame:
                conn.sendall(len(frame).to_bytes(4, 'big'))
                conn.sendall(frame)
                print(f"[SENT] {len(frame)} bytes → {addr}")
            time.sleep(1 / FRAME_RATE)
    except Exception as e:
        print(f"[DISCONNECTED] {addr} ({e})")
    finally:
        conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[LISTENING] Server running on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
