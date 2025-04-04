# client/python/gui.py

import socket
import io
import tkinter as tk
from PIL import Image, ImageTk
from shared.config import HOST, PORT

class ScreenClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Mac Screen Viewer")
        self.fullscreen = False
        self.label = tk.Label(self.root)
        self.label.pack(fill=tk.BOTH, expand=True)
        self.root.bind("<f>", self.toggle_fullscreen)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        self.update_frame()

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def update_frame(self):
        try:
            size_bytes = self.sock.recv(8)
            size = int.from_bytes(size_bytes, byteorder="big")
            data = b""
            while len(data) < size:
                packet = self.sock.recv(size - len(data))
                if not packet:
                    break
                data += packet
            img = Image.open(io.BytesIO(data)).convert("RGB")
            screen_width = self.root.winfo_width()
            screen_height = self.root.winfo_height()
            img = img.resize((screen_width, screen_height), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image=img)
            self.label.config(image=photo)
            self.label.image = photo
        except Exception as e:
            print(f"[ERROR] Frame receive failed: {e}")
        self.root.after(1000 // 30, self.update_frame)

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenClient(root)
    root.mainloop()
