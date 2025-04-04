# client/python/gui.py
import socket
import tkinter as tk
from PIL import Image, ImageTk
from io import BytesIO
from shared.config import HOST, PORT

class ScreenClient:
    def __init__(self, root):
        self.root = root
        self.root.title("OpenSourceDisplayLink Client")
        self.root.attributes('-fullscreen', True)
        self.canvas = tk.Canvas(root, bg="black")
        self.canvas.pack(fill="both", expand=True)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((HOST, PORT))
        except Exception as e:
            print(f"[ERROR] Could not connect to server: {e}")
            return

        self.image_on_canvas = None
        self.update_screen()

    def update_screen(self):
        try:
            size_bytes = self.sock.recv(4)
            if len(size_bytes) < 4:
                raise ValueError("Incomplete frame size")
            size = int.from_bytes(size_bytes, 'big')
            data = b""
            while len(data) < size:
                packet = self.sock.recv(size - len(data))
                if not packet:
                    raise ValueError("Incomplete frame data")
                data += packet

            image = Image.open(BytesIO(data))
            photo = ImageTk.PhotoImage(image)
            if self.image_on_canvas:
                self.canvas.itemconfig(self.image_on_canvas, image=photo)
            else:
                self.image_on_canvas = self.canvas.create_image(0, 0, anchor="nw", image=photo)
            self.canvas.image = photo
        except Exception as e:
            print(f"[ERROR] Frame receive failed: {e}")

        self.root.after(1000 // 30, self.update_screen)

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenClient(root)
    root.mainloop()
