# client/python/gui.py

import socket, io
from tkinter import Tk, Label
from PIL import Image, ImageTk
from shared.config import HOST, PORT, TARGET_RESOLUTION

def receive_exact(sock, num_bytes):
    data = b""
    while len(data) < num_bytes:
        chunk = sock.recv(num_bytes - len(data))
        if not chunk:
            raise ConnectionError("Socket connection broken")
        data += chunk
    return data

def start_client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    print("[CONNECTED] to server")

    root = Tk()
    root.attributes("-fullscreen", True)
    label = Label(root)
    label.pack()

    try:
        while True:
            size_data = receive_exact(sock, 4)
            size = int.from_bytes(size_data, byteorder="big")

            frame_data = receive_exact(sock, size)
            image = Image.open(io.BytesIO(frame_data)).resize(TARGET_RESOLUTION)
            photo = ImageTk.PhotoImage(image)
            label.config(image=photo)
            label.image = photo
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    start_client()
