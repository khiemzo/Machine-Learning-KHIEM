import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import time
import threading
import json
import os
import math
import random
import requests
from openai import OpenAI



# Hàm cập nhật thời gian thực trên giao diện
def update_time():
    while True:
        now = datetime.datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
        time_label.config(text=f"🕒 {now}")
        time.sleep(1)


# Hàm gọi API ChatGPT trên website của bạn để lấy lịch trình tối ưu
def get_optimized_schedule(name, age, gender, occupation, weight, height, bmi):
    # Xây dựng prompt dựa trên thông tin cá nhân (chỉnh sửa payload cho phù hợp với API)
    prompt = (f"Tạo lịch trình tối ưu cho {name} với các thông tin sau:\n"
              f"Tuổi: {age}, Giới tính: {gender}, Nghề nghiệp: {occupation},\n"
              f"Cân nặng: {weight}kg, Chiều cao: {height}cm, BMI: {bmi:.2f}.\n"
              "Vui lòng đưa ra lịch trình cá nhân hóa.")

    payload = {

            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 100,
            "temperature": 0.7


    }

    # Lấy API key từ biến môi trường (hoặc gán trực tiếp)
    api_key = ""  # Thay YOUR_API_KEY bằng key của bạn

    # Thêm header với định dạng đúng
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/completions",
            headers=headers,
            json=payload,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0].get("text", "Không có lịch trình tối ưu!")
            else:
                return "Không có lịch trình tối ưu!"
        else:
            return f"Lỗi API: {response.status_code}"
    except Exception as e:
        return f"Lỗi khi gọi API: {e}"


# Hàm xử lý tạo lịch trình
def process_schedule():
    try:
        name = entry_name.get().strip()
        if not name:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên của bạn!")
            return
        age = int(entry_age.get())
        gender = gender_var.get()
        occupation = entry_occupation.get().strip()
        weight = float(entry_weight.get())
        height = float(entry_height.get())

        if age <= 0 or weight <= 0 or height <= 0:
            messagebox.showerror("Lỗi", "Giá trị tuổi, cân nặng và chiều cao phải lớn hơn 0!")
            return

        bmi = weight / ((height / 100) ** 2)
        bmi_text.set(f"BMI: {bmi:.2f}")

        # Tạo lịch trình cơ bản (có thể giữ lại các gợi ý ban đầu nếu cần)
        basic_schedule = f"Chỉ số BMI của bạn là {bmi:.2f}.\n"
        basic_schedule += "Đang tạo lịch trình tối ưu cho bạn, vui lòng chờ..."
        schedule_text.config(state="normal")
        schedule_text.delete("1.0", tk.END)
        schedule_text.insert(tk.END, basic_schedule)
        schedule_text.config(state="disabled")

        # Gọi API ChatGPT trên website (trong luồng riêng để không làm treo giao diện)
        def call_api():
            optimized_schedule = get_optimized_schedule(name, age, gender, occupation, weight, height, bmi)
            # Cập nhật giao diện với lịch trình nhận được
            schedule_text.config(state="normal")
            schedule_text.delete("1.0", tk.END)
            schedule_text.insert(tk.END, optimized_schedule)
            schedule_text.config(state="disabled")

        threading.Thread(target=call_api, daemon=True).start()

    except ValueError:
        messagebox.showerror("Lỗi", "Vui lòng nhập đúng dữ liệu số cho tuổi, cân nặng, chiều cao!")


# Giao diện Tkinter
root = tk.Tk()
root.title("AI Schedule Planner")
root.geometry("650x750")
root.configure(bg="#f8f9fa")

# Frame tiêu đề
frame_title = tk.Frame(root, bg="#007BFF", pady=15)
frame_title.pack(fill="x")
tk.Label(frame_title, text="AI Schedule Planner", font=("Arial", 22, "bold"), fg="white", bg="#007BFF").pack()

# Hiển thị thời gian thực
time_label = tk.Label(root, text="", font=("Arial", 12, "bold"), fg="#007BFF", bg="#f8f9fa")
time_label.pack(pady=5)
threading.Thread(target=update_time, daemon=True).start()

# Frame nhập dữ liệu
frame_input = tk.Frame(root, bg="#f8f9fa", padx=20, pady=20)
frame_input.pack(fill="both", expand=True)

# Nhập tên
tk.Label(frame_input, text="Tên:", font=("Arial", 12), bg="#f8f9fa").grid(row=0, column=0, sticky="w", pady=5, padx=10)
entry_name = tk.Entry(frame_input, font=("Arial", 12), width=30)
entry_name.grid(row=0, column=1, pady=5)

# Nhập tuổi
tk.Label(frame_input, text="Tuổi:", font=("Arial", 12), bg="#f8f9fa").grid(row=1, column=0, sticky="w", pady=5, padx=10)
entry_age = tk.Entry(frame_input, font=("Arial", 12), width=30)
entry_age.grid(row=1, column=1, pady=5)

# Chọn giới tính
tk.Label(frame_input, text="Giới tính:", font=("Arial", 12), bg="#f8f9fa").grid(row=2, column=0, sticky="w", pady=5,
                                                                                padx=10)
gender_var = tk.StringVar(value="Nam")
ttk.Combobox(frame_input, textvariable=gender_var, values=["Nam", "Nữ"], state="readonly", width=28).grid(row=2,
                                                                                                          column=1,
                                                                                                          pady=5)

# Nhập nghề nghiệp
tk.Label(frame_input, text="Nghề nghiệp:", font=("Arial", 12), bg="#f8f9fa").grid(row=3, column=0, sticky="w", pady=5,
                                                                                  padx=10)
entry_occupation = tk.Entry(frame_input, font=("Arial", 12), width=30)
entry_occupation.grid(row=3, column=1, pady=5)

# Nhập cân nặng
tk.Label(frame_input, text="Cân nặng (kg):", font=("Arial", 12), bg="#f8f9fa").grid(row=4, column=0, sticky="w", pady=5,
                                                                                    padx=10)
entry_weight = tk.Entry(frame_input, font=("Arial", 12), width=30)
entry_weight.grid(row=4, column=1, pady=5)

# Nhập chiều cao
tk.Label(frame_input, text="Chiều cao (cm):", font=("Arial", 12), bg="#f8f9fa").grid(row=5, column=0, sticky="w",
                                                                                     pady=5, padx=10)
entry_height = tk.Entry(frame_input, font=("Arial", 12), width=30)
entry_height.grid(row=5, column=1, pady=5)

# Nút tạo lịch trình
btn_generate = tk.Button(root, text="📝 Tạo lịch trình cá nhân", font=("Arial", 14, "bold"),
                         command=process_schedule, bg="#28a745", fg="white", width=25)
btn_generate.pack(pady=15)

# Hiển thị BMI
bmi_text = tk.StringVar()
bmi_label = tk.Label(root, textvariable=bmi_text, font=("Arial", 16, "bold"), fg="#28a745", bg="#f8f9fa")
bmi_label.pack()

# Text area hiển thị lịch trình tối ưu
schedule_text = tk.Text(root, font=("Arial", 12), wrap="word", bg="white", relief="solid", bd=1, padx=10, pady=10)
schedule_text.pack(padx=20, pady=10, fill="both", expand=True)
schedule_text.config(state="disabled")


# Nút xem lịch sử (nếu cần)
def show_history():
    name = entry_name.get().strip()
    if not name:
        messagebox.showerror("Lỗi", "Vui lòng nhập tên để xem lịch sử!")
        return
    history = load_history()
    records = history.get(name, [])
    history_win = tk.Toplevel(root)
    history_win.title(f"Lịch sử đo của {name}")
    history_win.geometry("500x400")
    txt = tk.Text(history_win, font=("Arial", 11))
    txt.pack(expand=True, fill="both", padx=10, pady=10)
    if not records:
        txt.insert(tk.END, "Chưa có dữ liệu lịch sử!")
    else:
        for rec in records:
            txt.insert(tk.END, f"Ngày: {rec['date']}\n")
            txt.insert(tk.END, f"Tuổi: {rec['age']} | Nghề nghiệp: {rec['occupation']}\n")
            txt.insert(tk.END, f"Cân nặng: {rec['weight']} kg | Chiều cao: {rec['height']} cm\n")
            txt.insert(tk.END, f"BMI: {rec['bmi']:.2f}\n")
            txt.insert(tk.END, "-" * 40 + "\n")
    txt.config(state="disabled")


btn_history = tk.Button(root, text="📜 Xem lịch sử đo", font=("Arial", 12),
                        command=show_history, bg="#007BFF", fg="white", width=20)
btn_history.pack(pady=10)

# Chạy ứng dụng
root.mainloop()
