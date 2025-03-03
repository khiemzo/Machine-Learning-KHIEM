import tkinter as tk
from tkinter import messagebox

# Hàm tính BMI
def tinh_bmi():
    try:
        can_nang = float(entry_can_nang.get())
        chieu_cao = float(entry_chieu_cao.get()) / 100  # Chuyển cm sang m

        if can_nang <= 0 or chieu_cao <= 0:
            messagebox.showerror("Lỗi", "Chiều cao và cân nặng phải lớn hơn 0!")
            return

        bmi = can_nang / (chieu_cao ** 2)
        bmi_text.set(f"BMI: {bmi:.2f}")

        # Phân loại và lời khuyên
        if bmi < 18.5:
            phan_loai = "Cân nặng thấp (Gầy)"
            loi_khuyen = "Bạn nên ăn uống đủ dinh dưỡng hơn!"
            mau_nen = "#ADD8E6"
        elif 18.5 <= bmi <= 24.9:
            phan_loai = "Bình thường"
            loi_khuyen = "Tuyệt vời! Hãy duy trì chế độ ăn uống và tập luyện."
            mau_nen = "#90EE90"
        elif 25 <= bmi <= 29.9:
            phan_loai = "Thừa cân"
            loi_khuyen = "Bạn nên kiểm soát chế độ ăn uống và tập thể dục."
            mau_nen = "#FFD700"
        elif 30 <= bmi <= 34.9:
            phan_loai = "Béo phì độ I"
            loi_khuyen = "Bạn nên áp dụng chế độ ăn lành mạnh và tập luyện thường xuyên!"
            mau_nen = "#FFA07A"
        elif 35 <= bmi <= 39.9:
            phan_loai = "Béo phì độ II"
            loi_khuyen = "Nên tìm kiếm sự tư vấn từ chuyên gia dinh dưỡng!"
            mau_nen = "#FF6347"
        else:
            phan_loai = "Béo phì độ III"
            loi_khuyen = "Cần có kế hoạch giảm cân nghiêm túc với bác sĩ!"
            mau_nen = "#FF4500"

        # Hiển thị kết quả
        ket_qua_label.config(text=f"Phân loại: {phan_loai}\n{loi_khuyen}", bg=mau_nen)

    except ValueError:
        messagebox.showerror("Lỗi", "Vui lòng nhập số hợp lệ!")

# Tạo giao diện
root = tk.Tk()
root.title("BMI Calculator")
root.geometry("400x350")
root.configure(bg="#f0f0f0")

# Tiêu đề
tk.Label(root, text="Tính Chỉ Số BMI", font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=10)

# Nhập cân nặng
tk.Label(root, text="Nhập cân nặng (kg):", font=("Arial", 12), bg="#f0f0f0").pack()
entry_can_nang = tk.Entry(root, font=("Arial", 12))
entry_can_nang.pack(pady=5)

# Nhập chiều cao
tk.Label(root, text="Nhập chiều cao (cm):", font=("Arial", 12), bg="#f0f0f0").pack()
entry_chieu_cao = tk.Entry(root, font=("Arial", 12))
entry_chieu_cao.pack(pady=5)

# Nút tính toán
tk.Button(root, text="Tính BMI", font=("Arial", 12, "bold"), command=tinh_bmi, bg="#007BFF", fg="white").pack(pady=10)

# Hiển thị BMI
bmi_text = tk.StringVar()
bmi_label = tk.Label(root, textvariable=bmi_text, font=("Arial", 14, "bold"), bg="#f0f0f0")
bmi_label.pack()

# Kết quả
ket_qua_label = tk.Label(root, text="", font=("Arial", 12, "bold"), wraplength=300, bg="#f0f0f0")
ket_qua_label.pack(pady=10)

# Chạy ứng dụng
root.mainloop()
