import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import time
import threading
import json
import os
import math
import random

# Tên file lưu trữ lịch sử (JSON)
HISTORY_FILE = "bmi_history.json"


# Hàm load lịch sử đo từ file (nếu tồn tại)
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# Hàm lưu lịch sử đo vào file
def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)


# Hàm cập nhật thời gian thực trên giao diện
def cap_nhat_thoi_gian():
    while True:
        now = datetime.datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
        time_label.config(text=f"🕒 {now}")
        time.sleep(1)


# Hàm mô phỏng AI đánh giá cải thiện (so sánh với lần đo trước)
def ai_recommendation(previous, current, gender):
    """
    previous, current: dictionary với các thông số 'bmi', 'weight', 'height', 'age'
    gender: "Nam" hoặc "Nữ"
    Hàm này so sánh chỉ số BMI hiện tại với lần đo trước và đưa ra lời khuyên đa dạng,
    thậm chí với sự khác biệt nhỏ.
    """
    import random
    # Xác định chỉ số BMI mục tiêu dựa trên giới tính
    target = 22.5 if gender == "Nam" else 21.5
    prev_bmi = previous["bmi"]
    curr_bmi = current["bmi"]

    # Tính độ lệch so với mục tiêu
    prev_diff = abs(prev_bmi - target)
    curr_diff = abs(curr_bmi - target)

    # Sự cải thiện tính theo mức giảm độ lệch so với chỉ số mục tiêu
    diff_change = prev_diff - curr_diff

    # Nếu sự cải thiện rõ ràng (cách biệt hơn 0.5)
    if diff_change > 0.5:
        messages = [
            "Tuyệt vời! Bạn đã tiến gần hơn nhiều đến chỉ số lý tưởng, hãy tự hào về thành tích của mình.",
            "Cải thiện vượt trội! Chỉ số của bạn đã tiến bộ rõ rệt, tiếp tục duy trì thói quen tốt nhé.",
            "Bước tiến ấn tượng! BMI của bạn đã giảm đáng kể so với mục tiêu. Hãy tiếp tục nỗ lực!"
        ]
        return random.choice(messages)
    # Nếu có cải thiện nhẹ (trên 0.1 đến 0.5)
    elif diff_change > 0.1:
        messages = [
            "Bạn có dấu hiệu cải thiện, dù chỉ nhỏ nhưng đó là bước khởi đầu tốt.",
            "Tiến bộ đang diễn ra! Hãy giữ vững phong độ và cải thiện thêm chút nữa.",
            "Một cải thiện nhỏ nhưng ý nghĩa, hãy tiếp tục duy trì lối sống lành mạnh."
        ]
        return random.choice(messages)
    # Nếu gần như không thay đổi (chênh lệch dưới 0.1)
    elif abs(diff_change) < 0.1:
        messages = [
            "Chỉ số của bạn khá ổn định, tuy nhiên hãy duy trì chế độ ăn uống và luyện tập đều đặn.",
            "Không có nhiều thay đổi, cố gắng cải thiện thêm một chút để đạt chỉ số lý tưởng.",
            "Sự ổn định là tốt, nhưng hãy theo dõi sát sao để kịp thời điều chỉnh nếu cần."
        ]
        return random.choice(messages)
    # Nếu có sự xấu đi nhẹ (giảm hiệu quả không quá 0.5)
    elif diff_change > -0.5:
        messages = [
            "Có dấu hiệu xấu nhẹ so với lần đo trước, hãy cân nhắc điều chỉnh một số thói quen hàng ngày.",
            "BMI của bạn có chút xấu đi, thử thay đổi chế độ ăn hoặc tăng cường vận động nhé.",
            "Một sự thay đổi nhỏ không mấy khả quan, hãy chú ý đến dinh dưỡng và hoạt động thể chất."
        ]
        return random.choice(messages)
    # Nếu sự thay đổi tiêu cực rõ rệt (dưới -0.5)
    else:
        messages = [
            "Chỉ số của bạn đã xấu đi đáng kể, cần có sự can thiệp ngay từ bây giờ!",
            "Cảnh báo: BMI của bạn có xu hướng xấu, hãy xem xét lại chế độ ăn và luyện tập, hoặc tham khảo ý kiến chuyên gia.",
            "Sự thay đổi nghiêm trọng, bạn cần cải thiện chế độ sống ngay để bảo vệ sức khỏe của mình!"
        ]
        return random.choice(messages)


# Hàm đề xuất thời gian biểu cơ bản dựa trên tuổi
def goi_y_thoi_gian_bieu(tuoi):
    if tuoi < 18:
        time_table = "Ngủ: 22h-6h | Học tập: 8h-12h, 14h-17h | Vận động: 17h-18h"
    elif tuoi < 40:
        time_table = "Ngủ: 23h-6h | Làm việc: 9h-12h, 13h-17h | Tập thể dục: 18h-19h"
    else:
        time_table = "Ngủ: 22h-6h | Làm việc: 8h-12h, 14h-16h | Thư giãn: 16h-18h"

    # Giả lập AI đưa thêm gợi ý (ngẫu nhiên)
    if random.random() > 0.5:
        time_table += " | Gợi ý thêm: 30 phút thiền buổi tối"
    return time_table


# Hàm hiển thị lịch sử đo của 1 người (theo tên)
def show_history(name, history):
    records = history.get(name, [])
    if not records:
        messagebox.showinfo("Lịch sử", f"Chưa có lịch sử đo cho {name}")
        return

    # Tạo cửa sổ mới để hiển thị lịch sử
    history_win = tk.Toplevel(root)
    history_win.title(f"Lịch sử đo của {name}")
    history_win.geometry("450x300")

    text_area = tk.Text(history_win, font=("Arial", 11))
    text_area.pack(expand=True, fill="both", padx=10, pady=10)

    # Sắp xếp theo thời gian (mới nhất ở dưới)
    for record in records:
        text_area.insert(tk.END, f"Ngày: {record['date']}\n")
        text_area.insert(tk.END,
                         f"Tuổi: {record['age']} | Cân nặng: {record['weight']} kg | Chiều cao: {record['height']} cm\n")
        text_area.insert(tk.END, f"BMI: {record['bmi']:.2f}\n")
        text_area.insert(tk.END, f"Phân loại: {record['classification']}\n")
        if "ai_advice" in record:
            text_area.insert(tk.END, f"Lời khuyên: {record['ai_advice']}\n")
        text_area.insert(tk.END, "-" * 40 + "\n")
    text_area.config(state="disabled")


# Hàm hiển thị bảng thông tin đầy đủ (tất cả các lịch sử đo của mọi người, sắp xếp theo tên)
def show_full_history_table():
    history = load_history()
    # Tạo cửa sổ mới để hiển thị bảng
    table_win = tk.Toplevel(root)
    table_win.title("Bảng thông tin đầy đủ")
    table_win.geometry("900x400")

    # Hiển thị ngày giờ hiện tại trên cửa sổ bảng
    now = datetime.datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
    current_time_label = tk.Label(table_win, text=f"Thời gian hiện tại: {now}", font=("Arial", 12))
    current_time_label.pack(pady=5)

    # Tạo Treeview
    columns = ("Tên", "Ngày đo", "Tuổi", "Cân nặng (kg)", "Chiều cao (cm)", "BMI", "Phân loại", "Lời khuyên")
    tree = ttk.Treeview(table_win, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=110, anchor=tk.CENTER)
    tree.pack(expand=True, fill="both", padx=10, pady=10)

    # Chèn dữ liệu từ lịch sử, sắp xếp theo tên
    for name in sorted(history.keys()):
        for record in history[name]:
            ai_advice = record.get("ai_advice", "")
            tree.insert("", "end", values=(name, record["date"], record["age"],
                                           record["weight"], record["height"],
                                           f"{record['bmi']:.2f}", record["classification"],
                                           ai_advice))
    # Thêm thanh cuộn dọc cho Treeview
    scrollbar = ttk.Scrollbar(table_win, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")


# Hàm tính BMI, lưu lịch sử và đưa ra lời khuyên tích hợp AI
def tinh_bmi():
    try:
        name = entry_name.get().strip()
        if not name:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên của bạn!")
            return

        can_nang = float(entry_can_nang.get())
        chieu_cao = float(entry_chieu_cao.get()) / 100  # chuyển từ cm sang m
        gioi_tinh = gioi_tinh_var.get()
        tuoi = int(entry_tuoi.get())

        if can_nang <= 0 or chieu_cao <= 0 or tuoi <= 0:
            messagebox.showerror("Lỗi", "Dữ liệu không hợp lệ!")
            return

        bmi = can_nang / (chieu_cao ** 2)
        bmi_text.set(f"BMI: {bmi:.2f}")

        # Xác định phân loại và màu nền dựa trên giới tính
        if gioi_tinh == "Nam":
            nguong_bmi = [20, 25, 30, 35]
        else:
            nguong_bmi = [19, 24, 29, 34]

        if bmi < nguong_bmi[0]:
            classification, basic_advice, mau_nen = "Gầy", "Bạn cần bổ sung dinh dưỡng.", "#ADD8E6"
        elif bmi < nguong_bmi[1]:
            classification, basic_advice, mau_nen = "Bình thường", "Tuyệt vời, hãy duy trì lối sống này!", "#90EE90"
        elif bmi < nguong_bmi[2]:
            classification, basic_advice, mau_nen = "Thừa cân", "Cần tăng cường hoạt động thể chất.", "#FFD700"
        elif bmi < nguong_bmi[3]:
            classification, basic_advice, mau_nen = "Béo phì", "Hãy cân nhắc chế độ ăn kiêng và tập luyện.", "#FFA07A"
        else:
            classification, basic_advice, mau_nen = "Béo phì nghiêm trọng", "Cần tư vấn y tế ngay!", "#FF4500"

        # Tạo chuỗi kết quả cơ bản
        ket_qua = f"Phân loại: {classification}\nLời khuyên: {basic_advice}"

        # Lấy lịch sử đo của người dùng
        history = load_history()
        user_history = history.get(name, [])
        ai_extra = ""
        if user_history:
            # Lấy bản ghi đo gần nhất
            last_record = user_history[-1]
            current_data = {"bmi": bmi, "weight": can_nang, "height": chieu_cao * 100, "age": tuoi}
            ai_extra = ai_recommendation(last_record, current_data, gioi_tinh)
            ket_qua += f"\n\nSo sánh lần đo trước: {ai_extra}"

        # Gợi ý thời gian biểu
        time_table = goi_y_thoi_gian_bieu(tuoi)
        ket_qua += f"\n\n📅 Thời gian biểu gợi ý:\n{time_table}"

        ket_qua_label.config(text=ket_qua, bg=mau_nen)

        # Lưu kết quả mới vào lịch sử
        record = {
            "date": datetime.datetime.now().strftime("%H:%M:%S - %d/%m/%Y"),
            "age": tuoi,
            "weight": can_nang,
            "height": chieu_cao * 100,
            "bmi": bmi,
            "classification": classification,
            "ai_advice": ai_extra
        }
        user_history.append(record)
        history[name] = user_history
        save_history(history)

    except ValueError:
        messagebox.showerror("Lỗi", "Vui lòng nhập dữ liệu hợp lệ (số)!")


# Tạo giao diện chính
root = tk.Tk()
root.title("BMI & AI Personal Coach")
root.geometry("600x700")
root.configure(bg="#f8f9fa")

# --- Frame tiêu đề ---
frame_title = tk.Frame(root, bg="#007BFF", pady=15)
frame_title.pack(fill="x")
title_label = tk.Label(frame_title, text="BMI & AI Personal Coach", font=("Arial", 20, "bold"), fg="white",
                       bg="#007BFF")
title_label.pack()

# Hiển thị thời gian thực
time_label = tk.Label(root, text="", font=("Arial", 12, "bold"), fg="#007BFF", bg="#f8f9fa")
time_label.pack(pady=5)
threading.Thread(target=cap_nhat_thoi_gian, daemon=True).start()

# --- Frame nhập dữ liệu ---
frame_input = tk.Frame(root, bg="#f8f9fa", padx=20, pady=20)
frame_input.pack(fill="both", expand=True)

# Nhập tên
tk.Label(frame_input, text="Tên của bạn:", font=("Arial", 12), bg="#f8f9fa").grid(row=0, column=0, sticky="w", pady=5)
entry_name = tk.Entry(frame_input, font=("Arial", 12), width=25)
entry_name.grid(row=0, column=1, pady=5)

# Chọn giới tính
tk.Label(frame_input, text="Giới tính:", font=("Arial", 12), bg="#f8f9fa").grid(row=1, column=0, sticky="w", pady=5)
gioi_tinh_var = tk.StringVar(value="Nam")
ttk.Combobox(frame_input, textvariable=gioi_tinh_var, values=["Nam", "Nữ"], state="readonly", width=23).grid(row=1,
                                                                                                             column=1,
                                                                                                             pady=5)

# Nhập tuổi
tk.Label(frame_input, text="Tuổi:", font=("Arial", 12), bg="#f8f9fa").grid(row=2, column=0, sticky="w", pady=5)
entry_tuoi = tk.Entry(frame_input, font=("Arial", 12), width=25)
entry_tuoi.grid(row=2, column=1, pady=5)

# Nhập cân nặng
tk.Label(frame_input, text="Cân nặng (kg):", font=("Arial", 12), bg="#f8f9fa").grid(row=3, column=0, sticky="w", pady=5)
entry_can_nang = tk.Entry(frame_input, font=("Arial", 12), width=25)
entry_can_nang.grid(row=3, column=1, pady=5)

# Nhập chiều cao
tk.Label(frame_input, text="Chiều cao (cm):", font=("Arial", 12), bg="#f8f9fa").grid(row=4, column=0, sticky="w",
                                                                                     pady=5)
entry_chieu_cao = tk.Entry(frame_input, font=("Arial", 12), width=25)
entry_chieu_cao.grid(row=4, column=1, pady=5)

# Nút tính toán BMI
calc_btn = tk.Button(root, text="📊 Tính BMI & Đánh giá", font=("Arial", 13, "bold"), command=tinh_bmi, bg="#28a745",
                     fg="white", width=25)
calc_btn.pack(pady=15)

# Hiển thị kết quả BMI và lời khuyên
bmi_text = tk.StringVar()
bmi_label = tk.Label(root, textvariable=bmi_text, font=("Arial", 16, "bold"), fg="#28a745", bg="#f8f9fa")
bmi_label.pack()

ket_qua_label = tk.Label(root, text="", font=("Arial", 12, "bold"), wraplength=500, bg="#f8f9fa", pady=15)
ket_qua_label.pack(pady=10)


# Nút xem lịch sử đo của người dùng (theo tên)
def xem_lich_su():
    name = entry_name.get().strip()
    if not name:
        messagebox.showerror("Lỗi", "Vui lòng nhập tên để xem lịch sử đo!")
        return
    history = load_history()
    show_history(name, history)


history_btn = tk.Button(root, text="📜 Xem lịch sử đo", font=("Arial", 12), command=xem_lich_su, bg="#007BFF",
                        fg="white", width=20)
history_btn.pack(pady=10)

# Nút xem bảng thông tin đầy đủ (tất cả lịch sử, sắp xếp theo tên)
full_history_btn = tk.Button(root, text="📋 Xem bảng thông tin đầy đủ", font=("Arial", 12),
                             command=show_full_history_table, bg="#17a2b8", fg="white", width=25)
full_history_btn.pack(pady=10)

# --- Frame hiển thị gợi ý thời gian biểu ---
frame_schedule = tk.Frame(root, bg="#f8f9fa", pady=10)
frame_schedule.pack(fill="x")
time_label_2 = tk.Label(frame_schedule, text="", font=("Arial", 12), wraplength=500, bg="#f8f9fa", fg="#6c757d")
time_label_2.pack()

# Chạy ứng dụng
root.mainloop()
