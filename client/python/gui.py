import socket, threading, io, tkinter as tk
from PIL import Image, ImageTk
from shared.config import HOST, PORT

def receive_frames(sock, canvas, img_id):
    try:
        while True:
            header = sock.recv(4)
            if not header: break
            length = int.from_bytes(header, 'big')
            data = b''
            while len(data) < length:
                packet = sock.recv(length - len(data))
                if not packet: return
                data += packet
            image = Image.open(io.BytesIO(data))
            photo = ImageTk.PhotoImage(image)
            canvas.itemconfig(img_id, image=photo)
            canvas.image = photo
    except Exception as e:
        print(f"[ERROR] {e}")
        sock.close()

def start_client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    root = tk.Tk()
    root.title("DisplayLink Client")
    root.attributes("-fullscreen", True)

    canvas = tk.Canvas(root, bg="black")
    canvas.pack(fill="both", expand=True)

    placeholder = ImageTk.PhotoImage(Image.new("RGB", (100, 100)))
    img_id = canvas.create_image(0, 0, anchor="nw", image=placeholder)

    threading.Thread(target=receive_frames, args=(sock, canvas, img_id), daemon=True).start()
    root.mainloop()

if __name__ == "__main__":
    start_client()
