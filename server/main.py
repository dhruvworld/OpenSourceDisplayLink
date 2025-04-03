import socket, threading, time, io
from PIL import Image
from shared.config import HOST, PORT, FRAME_RATE, TARGET_RESOLUTION, IMAGE_FORMAT, IMAGE_QUALITY
from server.capture.mac_capture import capture_screen  # This returns a PIL.Image object

def encode_frame(image):
    buffer = io.BytesIO()
    image = image.resize(TARGET_RESOLUTION).convert("RGB")  # Ensures 3-channel RGB
    image.save(buffer, format="JPEG", quality=IMAGE_QUALITY)  # Switch to JPEG for testing
    return buffer.getvalue()


def handle_client(conn, addr):
    print(f"[CONNECTED] {addr}")
    try:
        while True:
            frame = capture_screen()             # ✅ This is a PIL image
            data = encode_frame(frame)           # ✅ Encode it as JPEG/WEBP
            size = len(data)

            conn.sendall(size.to_bytes(4, byteorder="big"))
            conn.sendall(data)

            print(f"[SENT] {size} bytes → {addr}")
            time.sleep(1 / FRAME_RATE)
    except Exception as e:
        print(f"[DISCONNECTED] {addr} {e}")
    finally:
        conn.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"[LISTENING] Server running on {HOST}:{PORT}")
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start_server()
