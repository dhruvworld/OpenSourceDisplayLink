# client/python/gui.py

import socket, io
from tkinter import Tk, Label
from PIL import Image, ImageTk, UnidentifiedImageError
from shared.config import HOST, PORT, TARGET_RESOLUTION

def receive_exact(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise ConnectionError("Socket connection broken")
        data += chunk
    return data

def start_client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    print("[CONNECTED] to server")

    root = Tk()
    root.title("OpenSourceDisplayLink Viewer")
    root.geometry(f"{TARGET_RESOLUTION[0]}x{TARGET_RESOLUTION[1]}")
    label = Label(root)
    label.pack()

    def update_frame():
        try:
            size_data = receive_exact(sock, 4)
            size = int.from_bytes(size_data, byteorder="big")
            frame_data = receive_exact(sock, size)

            image = Image.open(io.BytesIO(frame_data))
            image = image.resize(TARGET_RESOLUTION)
            photo = ImageTk.PhotoImage(image)

            label.config(image=photo)
            label.image = photo

        except (ConnectionError, UnidentifiedImageError) as e:
            print(f"[ERROR] {e}")
            root.destroy()
            sock.close()
            return

        root.after(1, update_frame)  # Schedule next frame

    update_frame()
    root.mainloop()

if __name__ == "__main__":
    start_client()
