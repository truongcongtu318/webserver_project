import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import logging
import socket
from api import create_app
from werkzeug.serving import make_server

class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        logging.Handler.__init__(self)
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, msg + '\n')
            self.text_widget.configure(state='disabled')
            self.text_widget.yview(tk.END)
        self.text_widget.after(0, append)

class ServerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Quản lý Server Flask")

        self.log_area = scrolledtext.ScrolledText(master, state='disabled', height=20)
        self.log_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.start_button = tk.Button(master, text="Khởi động Server", command=self.start_server)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(master, text="Dừng Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.text_handler = TextHandler(self.log_area)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.text_handler.setFormatter(formatter)

        self.flask_thread = None
        self.server = None
        self.app = create_app()
        self.app.logger.addHandler(self.text_handler)

        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_server(self):
        if not self.flask_thread or not self.flask_thread.is_alive():
            host = '0.0.0.0'
            port = 8080
            self.server = make_server(host, port, self.app)
            self.flask_thread = threading.Thread(target=self.server.serve_forever)
            self.flask_thread.start()
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            server_ip = socket.gethostbyname(socket.gethostname())
            self.app.logger.info(f"Server started: {server_ip}:{port}")
            self.app.logger.info(f"Server đang lắng nghe kết nối tại {host}:{port}")

    def stop_server(self):
        if self.server:
            self.server.shutdown()
            self.flask_thread.join()
            self.server = None
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.app.logger.info("Server đã được dừng")

    def on_closing(self):
        if messagebox.askokcancel("Thoát", "Bạn có chắc chắn muốn thoát?"):
            if self.server:
                self.stop_server()
            self.app.logger.info("Ứng dụng đã được đóng")
            self.master.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    gui = ServerGUI(root)
    root.mainloop()