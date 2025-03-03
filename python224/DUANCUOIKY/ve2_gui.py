import csv
import os
import tkinter as tk
from tkinter import messagebox, ttk, filedialog

# Hàm tải dữ liệu từ file CSV
def load_data():
    """Đọc dữ liệu từ các file CSV và trả về dictionary."""
    data = {}
    data_types = {
        "temp": "temperature.csv",
        "rain": "rainfall.csv",
        "sun": "sunshine.csv"
    }
    for dtype, filename in data_types.items():
        filepath = os.path.join(os.path.dirname(__file__), filename)
        if not os.path.exists(filepath):
            messagebox.showerror("Lỗi", f"Không tìm thấy file {filename}!")
            exit()
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                city = row[0].strip().lower()
                if city not in data:
                    data[city] = {}
                try:
                    data[city][dtype] = [float(x) for x in row[1:13]]
                except ValueError:
                    continue
    return data

# Hàm hiển thị dữ liệu khí hậu
def display_climate_data(data, cities, data_types, months):
    """Hiển thị dữ liệu khí hậu theo yêu cầu."""
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    # Xóa dữ liệu cũ trong bảng
    for row in result_table.get_children():
        result_table.delete(row)

    # Thêm tiêu đề cột
    columns = ["City", "Data Type"] + [month_names[i][:3] for i in months] + ["Min", "Max", "Avg"]
    result_table["columns"] = columns
    result_table.heading("#0", text="", anchor=tk.W)
    for col in columns:
        result_table.heading(col, text=col, anchor=tk.CENTER)
        result_table.column(col, anchor=tk.CENTER, width=80)

    # Điền dữ liệu vào bảng
    for city in cities:
        for dtype in data_types:
            values = data.get(city, {}).get(dtype, [])
            if not values:
                continue
            selected_values = [values[i] for i in months]
            min_val = min(selected_values)
            max_val = max(selected_values)
            avg_val = sum(selected_values) / len(selected_values)
            min_month = month_names[months[selected_values.index(min_val)]]
            max_month = month_names[months[selected_values.index(max_val)]]

            row_data = [city.title(), dtype.upper()] + \
                       [f"{v:.1f}" for v in selected_values] + \
                       [f"{min_val:.1f} ({min_month})", f"{max_val:.1f} ({max_month})", f"{avg_val:.1f}"]
            result_table.insert("", tk.END, values=row_data)

# Hàm xử lý khi nhấn nút "Hiển thị"
def on_display_button_click():
    # Lấy lựa chọn từ GUI
    selected_cities = [city_listbox.get(i).lower() for i in city_listbox.curselection()]
    selected_data = [data_type_listbox.get(i).lower() for i in data_type_listbox.curselection()]
    selected_months = [month_map[month_listbox.get(i).lower()] for i in month_listbox.curselection()]

    # Kiểm tra đầu vào
    if not selected_cities or not selected_data or not selected_months:
        messagebox.showwarning("Lỗi", "Vui lòng chọn ít nhất một thành phố, loại dữ liệu và tháng!")
        return

    # Hiển thị dữ liệu
    display_climate_data(data, selected_cities, selected_data, selected_months)

# Hàm lưu dữ liệu vào file
def save_to_file():
    # Kiểm tra xem bảng có dữ liệu hay không
    if not result_table.get_children():
        messagebox.showwarning("Lỗi", "Không có dữ liệu để lưu!")
        return

    # Hỏi người dùng có muốn lưu không
    choice = messagebox.askyesno("Lưu Dữ Liệu", "Bạn có muốn lưu kết quả vào file không?")
    if not choice:
        return

    # Chọn đường dẫn và tên file
    filepath = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv")],
        title="Chọn đường dẫn và tên file để lưu"
    )
    if not filepath:
        return

    # Kiểm tra file đã tồn tại chưa
    mode = "w"
    if os.path.exists(filepath):
        overwrite_choice = messagebox.askyesno(
            "File Đã Tồn Tại",
            "File đã tồn tại. Bạn muốn ghi đè (Yes) hay thêm vào (No)?"
        )
        mode = "w" if overwrite_choice else "a"

    # Ghi dữ liệu vào file
    try:
        with open(filepath, mode) as f:
            writer = csv.writer(f)
            if mode == "w":
                # Ghi tiêu đề
                header = ["City", "Data Type"] + list(result_table["columns"][2:])  # Chuyển tuple thành list
                writer.writerow(header)
            # Ghi dữ liệu
            for row in result_table.get_children():
                writer.writerow(result_table.item(row)["values"])
        messagebox.showinfo("Thành công", f"Dữ liệu đã được lưu vào {filepath}")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể lưu dữ liệu: {e}")

# Tạo giao diện chính
root = tk.Tk()
root.title("CLIP - Climate Plotter")
root.geometry("1000x700")

# Label tiêu đề
title_label = tk.Label(root, text="Chào mừng đến với CLIP - Climate Plotter", font=("Arial", 16))
title_label.pack(pady=10)

# Frame chứa 3 cột ngang nhau
selection_frame = tk.Frame(root)
selection_frame.pack(fill="both", expand=True, padx=10, pady=5)

# Frame để chọn thành phố
city_frame = tk.LabelFrame(selection_frame, text="Chọn Thành Phố")
city_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)
city_listbox = tk.Listbox(city_frame, selectmode=tk.MULTIPLE, exportselection=False)
city_listbox.pack(fill="both", expand=True)

# Frame để chọn loại dữ liệu
data_type_frame = tk.LabelFrame(selection_frame, text="Chọn Loại Dữ Liệu")
data_type_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)
data_type_listbox = tk.Listbox(data_type_frame, selectmode=tk.MULTIPLE, exportselection=False)
data_type_listbox.pack(fill="both", expand=True)

# Frame để chọn tháng
month_frame = tk.LabelFrame(selection_frame, text="Chọn Tháng")
month_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)
month_listbox = tk.Listbox(month_frame, selectmode=tk.MULTIPLE, exportselection=False)
month_listbox.pack(fill="both", expand=True)

# Nút hiển thị dữ liệu
button_frame = tk.Frame(root)
button_frame.pack(fill="x", padx=10, pady=5)
display_button = tk.Button(button_frame, text="Hiển Thị Dữ Liệu", command=on_display_button_click)
display_button.pack(side=tk.LEFT, padx=5)
save_button = tk.Button(button_frame, text="Lưu Dữ Liệu", command=save_to_file)
save_button.pack(side=tk.RIGHT, padx=5)

# Khu vực hiển thị kết quả
result_frame = tk.LabelFrame(root, text="Kết Quả")
result_frame.pack(fill="both", expand=True, padx=10, pady=5)
result_table = ttk.Treeview(result_frame, show="headings")
result_table.pack(fill="both", expand=True)

# Khởi tạo dữ liệu
status_label = tk.Label(root, text="Đang tải dữ liệu...", font=("Arial", 10), fg="blue")
status_label.pack()
root.update_idletasks()  # Cập nhật giao diện ngay lập tức
data = load_data()
cities = list(data.keys())
data_types = ["temp", "rain", "sun"]
month_options = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
month_map = {m: i for i, m in enumerate(month_options)}

# Đổ dữ liệu vào các Listbox
for city in cities:
    city_listbox.insert(tk.END, city.title())
for dtype in data_types:
    data_type_listbox.insert(tk.END, dtype.upper())
for month in month_options:
    month_listbox.insert(tk.END, month.capitalize())

status_label.config(text="Tải dữ liệu hoàn tất!")

# Chạy ứng dụng
root.mainloop()