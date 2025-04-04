# client/python/gui.py

import socket
import threading
import tkinter as tk
from PIL import Image, ImageTk
import io
from shared.config import HOST, PORT

class ScreenClient:
    def __init__(self, root):
        self.root = root
        self.fullscreen = False
        self.label = tk.Label(root)
        self.label.pack(fill="both", expand=True)
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        threading.Thread(target=self.receive_frames, daemon=True).start()

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def exit_fullscreen(self, event=None):
        self.fullscreen = False
        self.root.attributes("-fullscreen", False)

    def receive_frames(self):
        while True:
            try:
                data = b''
                while True:
                    chunk = self.sock.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                    if len(chunk) < 4096:
                        break

                image = Image.open(io.BytesIO(data)).convert("RGB")
                frame = ImageTk.PhotoImage(image)
                self.label.config(image=frame)
                self.label.image = frame
            except Exception as e:
                print(f"[ERROR] Frame receive failed: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("OpenSourceDisplayLink Client")
    app = ScreenClient(root)
    root.mainloop()
