import csv
import os
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

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

# Hàm dự báo giá trị trung bình cho tháng tiếp theo
def forecast_next_month(values):
    """Sử dụng hồi quy tuyến tính để dự báo giá trị tháng tiếp theo."""
    months = np.array(range(len(values))).reshape(-1, 1)
    model = LinearRegression()
    model.fit(months, values)
    next_month = len(values)
    forecast = model.predict([[next_month]])[0]
    return forecast

# Hàm hiển thị dữ liệu khí hậu và dự báo
def display_climate_data_with_forecast(data, cities, data_types, months):
    """Hiển thị dữ liệu khí hậu và dự báo giá trị tháng tiếp theo."""
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    # Xóa dữ liệu cũ trong bảng
    for row in result_table.get_children():
        result_table.delete(row)

    # Thêm tiêu đề cột
    columns = ["City", "Data Type"] + [month_names[i][:3] for i in months] + ["Min", "Max", "Avg", "Forecast"]
    result_table["columns"] = columns
    result_table.heading("#0", text="", anchor=tk.W)
    for col in columns:
        result_table.heading(col, text=col, anchor=tk.CENTER)
        result_table.column(col, anchor=tk.CENTER, width=80)

    forecasts = {}
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

            # Dự báo giá trị tháng tiếp theo
            forecast = forecast_next_month(values)
            forecasts[(city, dtype)] = forecast

            row_data = [city.title(), dtype.upper()] + \
                       [f"{v:.1f}" for v in selected_values] + \
                       [f"{min_val:.1f} ({min_month})", f"{max_val:.1f} ({max_month})", f"{avg_val:.1f}", f"{forecast:.1f}"]
            result_table.insert("", tk.END, values=row_data)

    return forecasts

# Hàm vẽ biểu đồ xu hướng
def plot_trends(data, cities, data_types, months):
    """Vẽ biểu đồ xu hướng của từng thành phố."""
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    plt.figure(figsize=(12, 6))
    for city in cities:
        for dtype in data_types:
            values = data.get(city, {}).get(dtype, [])
            if not values:
                continue
            selected_values = [values[i] for i in months]
            plt.plot([month_names[i] for i in months], selected_values, marker='o', label=f"{city.title()} - {dtype.upper()}")

    plt.title("Xu hướng dữ liệu khí hậu")
    plt.xlabel("Month")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    messagebox.showinfo("Thông báo", "Đang hiển thị biểu đồ xu hướng.")
    plt.show()

# Hàm lưu dữ liệu vào file
def save_to_file(forecasts, format_choice):
    """Lưu kết quả vào file theo định dạng .csv hoặc .xlsx."""
    filepath = filedialog.asksaveasfilename(
        defaultextension=f".{format_choice}",
        filetypes=[(f"{format_choice.upper()} Files", f"*.{format_choice}")],
        title="Chọn đường dẫn và tên file để lưu"
    )
    if not filepath:
        return

    try:
        if format_choice == "csv":
            with open(filepath, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["City", "Data Type", "Forecast"])
                for (city, dtype), forecast in forecasts.items():
                    writer.writerow([city.title(), dtype.upper(), f"{forecast:.1f}"])
        elif format_choice == "xlsx":
            df = pd.DataFrame({
                "City": [city.title() for (city, _) in forecasts.keys()],
                "Data Type": [dtype.upper() for (_, dtype) in forecasts.keys()],
                "Forecast": [f"{forecast:.1f}" for forecast in forecasts.values()]
            })
            df.to_excel(filepath, index=False)
        messagebox.showinfo("Thành công", f"Dữ liệu đã được lưu vào {filepath}")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể lưu file: {e}")

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

    # Hiển thị dữ liệu và dự báo
    global forecasts
    forecasts = display_climate_data_with_forecast(data, selected_cities, selected_data, selected_months)

# Hàm xử lý khi nhấn nút "Vẽ Biểu Đồ"
def on_plot_button_click():
    # Lấy lựa chọn từ GUI
    selected_cities = [city_listbox.get(i).lower() for i in city_listbox.curselection()]
    selected_data = [data_type_listbox.get(i).lower() for i in data_type_listbox.curselection()]
    selected_months = [month_map[month_listbox.get(i).lower()] for i in month_listbox.curselection()]

    # Kiểm tra đầu vào
    if not selected_cities or not selected_data or not selected_months:
        messagebox.showwarning("Lỗi", "Vui lòng chọn ít nhất một thành phố, loại dữ liệu và tháng!")
        return

    # Vẽ biểu đồ xu hướng
    plot_trends(data, selected_cities, selected_data, selected_months)

# Hàm xử lý khi nhấn nút "Lưu Dữ Liệu"
def on_save_button_click():
    # Kiểm tra xem có dữ liệu dự báo không
    if not forecasts:
        messagebox.showwarning("Lỗi", "Không có dữ liệu để lưu!")
        return

    # Chọn định dạng file
    format_choice = format_var.get()
    if format_choice not in ["csv", "xlsx"]:
        messagebox.showwarning("Lỗi", "Vui lòng chọn định dạng file hợp lệ (CSV hoặc XLSX).")
        return

    # Lưu dữ liệu vào file
    save_to_file(forecasts, format_choice)

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

# Nút hiển thị dữ liệu, vẽ biểu đồ và lưu dữ liệu
button_frame = tk.Frame(root)
button_frame.pack(fill="x", padx=10, pady=5)
display_button = tk.Button(button_frame, text="Hiển Thị Dữ Liệu", command=on_display_button_click)
display_button.pack(side=tk.LEFT, padx=5)
plot_button = tk.Button(button_frame, text="Vẽ Biểu Đồ", command=on_plot_button_click)
plot_button.pack(side=tk.LEFT, padx=5)

# Frame để chọn định dạng file
save_frame = tk.Frame(button_frame)
save_frame.pack(side=tk.RIGHT, padx=5)
format_var = tk.StringVar(value="csv")
csv_radio = tk.Radiobutton(save_frame, text="CSV", variable=format_var, value="csv")
csv_radio.pack(side=tk.LEFT)
xlsx_radio = tk.Radiobutton(save_frame, text="XLSX", variable=format_var, value="xlsx")
xlsx_radio.pack(side=tk.LEFT)
save_button = tk.Button(save_frame, text="Lưu Dữ Liệu", command=on_save_button_click)
save_button.pack(side=tk.RIGHT)

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

# Biến toàn cục để lưu trữ dữ liệu dự báo
forecasts = {}

# Chạy ứng dụng
root.mainloop()