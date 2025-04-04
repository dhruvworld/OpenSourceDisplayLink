# client/gui.py

import socket
import struct
import tkinter as tk
from PIL import Image, ImageTk
import io
from shared.config import HOST, PORT

class ScreenClient(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Screen Client")
        self.attributes("-fullscreen", True)

        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<F11>", self.toggle_fullscreen)
        self.fullscreen = True

        self.label = tk.Label(self)
        self.label.pack(expand=True)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))

        self.after(0, self.receive_frame)

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.attributes("-fullscreen", self.fullscreen)

    def receive_frame(self):
        try:
            raw_size = self.sock.recv(4)
            if not raw_size:
                return
            size = struct.unpack('>I', raw_size)[0]
            data = b''
            while len(data) < size:
                packet = self.sock.recv(size - len(data))
                if not packet:
                    return
                data += packet
            image = Image.open(io.BytesIO(data))
            photo = ImageTk.PhotoImage(image.resize((self.winfo_width(), self.winfo_height())))
            self.label.config(image=photo)
            self.label.image = photo
        except Exception as e:
            print(f"[CLIENT ERROR] {e}")
        self.after(1, self.receive_frame)

if __name__ == "__main__":
    app = ScreenClient()
    app.mainloop()
