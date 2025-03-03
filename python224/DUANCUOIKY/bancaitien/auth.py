import tkinter as tk
from tkinter import messagebox, simpledialog


def login():
    # Định nghĩa thông tin đăng nhập mẫu (có thể thay đổi theo nhu cầu thực tế)
    USERNAME = "khiem"
    PASSWORD = "123"

    root = tk.Tk()
    root.withdraw()  # Ẩn cửa sổ chính

    username = simpledialog.askstring("Đăng nhập", "Nhập username:", parent=root)
    password = simpledialog.askstring("Đăng nhập", "Nhập password:", parent=root, show="*")

    if username == USERNAME and password == PASSWORD:
        root.destroy()
        return True
    else:
        messagebox.showerror("Đăng nhập thất bại", "Username hoặc password không đúng. Vui lòng thử lại.")
        root.destroy()
        return False
