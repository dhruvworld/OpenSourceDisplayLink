import socket
import tkinter as tk
from PIL import Image, ImageTk
import io
from shared.config import HOST, PORT

class ScreenClient:
    def __init__(self, root):
        self.root = root
        self.root.attributes("-fullscreen", True)
        self.label = tk.Label(root)
        self.label.pack()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))

        self.update_frame()

    def update_frame(self):
        try:
            raw_size = self.sock.recv(4)
            if len(raw_size) < 4:
                raise Exception("Incomplete size")

            size = int.from_bytes(raw_size, byteorder='big')
            data = b''
            while len(data) < size:
                packet = self.sock.recv(size - len(data))
                if not packet:
                    raise Exception("Disconnected")
                data += packet

            image = Image.open(io.BytesIO(data))
            photo = ImageTk.PhotoImage(image)

            self.label.config(image=photo)
            self.label.image = photo
        except Exception as e:
            print(f"[ERROR] Frame receive failed: {e}")

        self.root.after(1000 // 30, self.update_frame)

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenClient(root)
    root.mainloop()
