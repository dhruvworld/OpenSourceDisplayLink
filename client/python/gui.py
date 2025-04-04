# client/gui.py

import socket
import struct
import io
from PIL import Image, ImageTk
import tkinter as tk
from shared.config import HOST, PORT

def receive_image(sock):
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

def run_client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    root = tk.Tk()
    root.attributes("-fullscreen", True)
    canvas = tk.Canvas(root, bg="black")
    canvas.pack(fill=tk.BOTH, expand=True)

    def update():
        image = receive_image(sock)
        if image:
            w, h = root.winfo_screenwidth(), root.winfo_screenheight()
            image = image.resize((w, h), Image.ANTIALIAS)
            tk_img = ImageTk.PhotoImage(image)
            canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)
            canvas.image = tk_img
        root.after(1, update)

    root.bind("<Escape>", lambda e: root.destroy())
    update()
    root.mainloop()

if __name__ == "__main__":
    run_client()
