# client/gui.py

import socket
import struct
import io
from PIL import Image, ImageTk
import tkinter as tk

HOST = '10.0.0.29'
PORT = 9999

def receive_frame(sock):
    try:
        size_data = sock.recv(4)
        if not size_data:
            return None
        size = struct.unpack('>I', size_data)[0]
        data = b''
        while len(data) < size:
            packet = sock.recv(size - len(data))
            if not packet:
                return None
            data += packet
        return Image.open(io.BytesIO(data))
    except Exception as e:
        print(f"[ERROR] Receiving failed: {e}")
        return None

def main():
    root = tk.Tk()
    root.title("Live Feed")
    label = tk.Label(root)
    label.pack()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    def update_frame():
        img = receive_frame(sock)
        if img:
            photo = ImageTk.PhotoImage(img)
            label.config(image=photo)
            label.image = photo
        root.after(1, update_frame)

    update_frame()
    root.mainloop()

if __name__ == "__main__":
    main()
