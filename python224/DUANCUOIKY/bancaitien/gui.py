# gui.py
import tkinter as tk
from tkinter import messagebox, ttk
from file_manager import save_to_file
from display import display_climate_data_with_forecast
from plotting import plot_trends
from real_time_display import create_real_time_display

forecasts = {}  # Biến toàn cục lưu trữ dữ liệu dự báo


def setup_gui(data, cities, data_types, month_options, month_map):
    root = tk.Tk()
    root.title("CLIP - Climate Plotter")
    root.geometry("1100x750")  # Kích thước mặc định có thể tùy chỉnh

    # Áp dụng dark mode nếu người dùng chọn (ban đầu mặc định light mode)
    style = ttk.Style(root)
    # Ví dụ: nếu sử dụng theme 'clam' và chỉnh sửa một số màu (hoặc sử dụng thư viện ttkthemes)
    style.theme_use("clam")
    root.configure(bg="#2e2e2e")

    title_label = tk.Label(root, text="Chào mừng đến với CLIP - Climate Plotter",
                           font=("Arial", 16), bg="#2e2e2e", fg="white")
    title_label.pack(pady=10)

    # Frame chứa danh sách lựa chọn
    selection_frame = tk.Frame(root, bg="#2e2e2e")
    selection_frame.pack(fill="both", expand=True, padx=10, pady=5)

    # Hàm tạo Listbox có scrollbar
    def create_listbox_with_scroll(parent, items):
        frame = tk.Frame(parent)
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
        listbox = tk.Listbox(frame, selectmode=tk.MULTIPLE, exportselection=False, yscrollcommand=scrollbar.set,
                             bg="white", fg="black")
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        for item in items:
            listbox.insert(tk.END, item)
        return frame, listbox

    # Frame chọn thành phố
    city_frame = tk.LabelFrame(selection_frame, text="Chọn Thành Phố", bg="#2e2e2e", fg="white")
    city_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)
    city_frame_inner, city_listbox = create_listbox_with_scroll(city_frame, [c.title() for c in cities])
    city_frame_inner.pack(fill="both", expand=True)

    # Frame chọn loại dữ liệu
    data_type_frame = tk.LabelFrame(selection_frame, text="Chọn Loại Dữ Liệu", bg="#2e2e2e", fg="white")
    data_type_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)
    data_type_frame_inner, data_type_listbox = create_listbox_with_scroll(data_type_frame,
                                                                           [d.upper() for d in data_types])
    data_type_frame_inner.pack(fill="both", expand=True)

    # Frame chọn tháng
    month_frame = tk.LabelFrame(selection_frame, text="Chọn Tháng", bg="#2e2e2e", fg="white")
    month_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)
    month_frame_inner, month_listbox = create_listbox_with_scroll(month_frame, [m.capitalize() for m in month_options])
    month_frame_inner.pack(fill="both", expand=True)

    # Frame cho tùy chọn dự báo nâng cao
    forecast_frame = tk.LabelFrame(root, text="Tùy chọn Dự Báo Nâng Cao", bg="#2e2e2e", fg="white")
    forecast_frame.pack(fill="x", padx=10, pady=5)

    tk.Label(forecast_frame, text="Số tháng dự báo:", bg="#2e2e2e", fg="white").pack(side=tk.LEFT, padx=5)
    forecast_horizon_var = tk.StringVar(value="1")
    forecast_horizon_entry = tk.Entry(forecast_frame, textvariable=forecast_horizon_var, width=5)
    forecast_horizon_entry.pack(side=tk.LEFT, padx=5)

    tk.Label(forecast_frame, text="Phương pháp dự báo:", bg="#2e2e2e", fg="white").pack(side=tk.LEFT, padx=5)
    forecast_method_var = tk.StringVar(value="linear")
    forecast_method_combo = ttk.Combobox(forecast_frame, textvariable=forecast_method_var,
                                         values=["linear", "polynomial", "arima", "ann"],
                                         state="readonly", width=12)
    forecast_method_combo.pack(side=tk.LEFT, padx=5)

    tk.Label(forecast_frame, text="Bậc đa thức (nếu dùng):", bg="#2e2e2e", fg="white").pack(side=tk.LEFT, padx=5)
    poly_degree_var = tk.StringVar(value="2")
    poly_degree_entry = tk.Entry(forecast_frame, textvariable=poly_degree_var, width=5)
    poly_degree_entry.pack(side=tk.LEFT, padx=5)

    # Nút chuyển đổi dark/light mode
    dark_mode_var = tk.BooleanVar(value=True)

    def toggle_dark_mode():
        if dark_mode_var.get():
            root.configure(bg="#2e2e2e")
            title_label.config(bg="#2e2e2e", fg="white")
        else:
            root.configure(bg="white")
            title_label.config(bg="white", fg="black")

    dark_mode_check = tk.Checkbutton(forecast_frame, text="Dark Mode", variable=dark_mode_var,
                                     command=toggle_dark_mode, bg="#2e2e2e", fg="white", selectcolor="#2e2e2e")
    dark_mode_check.pack(side=tk.RIGHT, padx=5)

    # Frame cho các nút chức năng
    button_frame = tk.Frame(root, bg="#2e2e2e")
    button_frame.pack(fill="x", padx=10, pady=5)

    display_button = tk.Button(button_frame, text="Hiển Thị Dữ Liệu",
                               command=lambda: on_display_button_click(data, city_listbox, data_type_listbox,
                                                                       month_listbox, month_map, result_table,
                                                                       forecast_horizon_var, forecast_method_var,
                                                                       poly_degree_var))
    display_button.pack(side=tk.LEFT, padx=5)

    plot_button = tk.Button(button_frame, text="Vẽ Biểu Đồ",
                            command=lambda: on_plot_button_click(data, city_listbox, data_type_listbox, month_listbox,
                                                                 month_map))
    plot_button.pack(side=tk.LEFT, padx=5)

    # Thêm nút "Dự đoán thiên tai"
    predict_button = tk.Button(button_frame, text="Dự đoán thiên tai",
                               command=lambda: on_predict_disaster_click(data))
    predict_button.pack(side=tk.LEFT, padx=5)

    # Thêm nút "Thông tin trực tuyến"
    realtime_button = tk.Button(button_frame, text="Thông tin trực tuyến",
                              command=lambda: on_realtime_button_click(root, data, cities, data_types))
    realtime_button.pack(side=tk.LEFT, padx=5)

    save_frame = tk.Frame(button_frame, bg="#2e2e2e")
    save_frame.pack(side=tk.RIGHT, padx=5)
    format_var = tk.StringVar(value="csv")
    csv_radio = tk.Radiobutton(save_frame, text="CSV", variable=format_var, value="csv", bg="#2e2e2e", fg="white")
    csv_radio.pack(side=tk.LEFT)
    xlsx_radio = tk.Radiobutton(save_frame, text="XLSX", variable=format_var, value="xlsx", bg="#2e2e2e", fg="white")
    xlsx_radio.pack(side=tk.LEFT)
    save_button = tk.Button(save_frame, text="Lưu Dữ Liệu",
                            command=lambda: on_save_button_click(format_var))
    save_button.pack(side=tk.RIGHT)

    # Khu vực hiển thị kết quả: cho phép kéo thả (resize) bằng cách đặt vào Frame có khả năng thay đổi kích thước
    result_frame = tk.LabelFrame(root, text="Kết Quả", bg="#2e2e2e", fg="white")
    result_frame.pack(fill="both", expand=True, padx=10, pady=5)
    result_table = ttk.Treeview(result_frame, show="headings")
    result_table.pack(fill="both", expand=True)

    status_label = tk.Label(root, text="Tải dữ liệu...", font=("Arial", 10), fg="white", bg="#2e2e2e")
    status_label.pack()
    root.update_idletasks()
    status_label.config(text="Tải dữ liệu hoàn tất!")

    gui_elements = {
        "root": root,
        "city_listbox": city_listbox,
        "data_type_listbox": data_type_listbox,
        "month_listbox": month_listbox,
        "month_map": month_map,
        "result_table": result_table,
        "status_label": status_label,
        "format_var": format_var,
        "forecast_horizon_var": forecast_horizon_var,
        "forecast_method_var": forecast_method_var,
        "poly_degree_var": poly_degree_var
    }
    return gui_elements


def on_display_button_click(data, city_listbox, data_type_listbox, month_listbox, month_map, result_table,
                            forecast_horizon_var, forecast_method_var, poly_degree_var):
    selected_cities = [city_listbox.get(i).lower() for i in city_listbox.curselection()]
    selected_data = [data_type_listbox.get(i).lower() for i in data_type_listbox.curselection()]
    selected_months = [month_map[month_listbox.get(i).lower()] for i in month_listbox.curselection()]

    if not selected_cities or not selected_data or not selected_months:
        messagebox.showwarning("Lỗi", "Vui lòng chọn ít nhất một thành phố, loại dữ liệu và tháng!")
        return

    try:
        forecast_horizon = int(forecast_horizon_var.get())
    except ValueError:
        messagebox.showwarning("Lỗi", "Số tháng dự báo không hợp lệ!")
        return

    # Lấy giá trị forecast_method, chuyển về chữ thường và loại bỏ khoảng trắng thừa.
    forecast_method = forecast_method_var.get().strip().lower()
    if not forecast_method:
        forecast_method = "linear"

    allowed_methods = ["linear", "polynomial", "arima", "ann"]
    if forecast_method not in allowed_methods:
        messagebox.showwarning("Lỗi",
                               f"Phương pháp dự báo '{forecast_method}' không hợp lệ! Vui lòng chọn một trong các giá trị: {', '.join(allowed_methods)}.")
        return

    try:
        poly_degree = int(poly_degree_var.get())
    except ValueError:
        poly_degree = 2  # Sử dụng giá trị mặc định nếu không hợp lệ

    try:
        global forecasts
        forecasts = display_climate_data_with_forecast(
            data, selected_cities, selected_data, selected_months, result_table,
            forecast_horizon, forecast_method, poly_degree
        )
    except Exception as e:
        messagebox.showerror("Lỗi dự báo", str(e))
        return


def on_plot_button_click(data, city_listbox, data_type_listbox, month_listbox, month_map):
    selected_cities = [city_listbox.get(i).lower() for i in city_listbox.curselection()]
    selected_data = [data_type_listbox.get(i).lower() for i in data_type_listbox.curselection()]
    selected_months = [month_map[month_listbox.get(i).lower()] for i in month_listbox.curselection()]

    if not selected_cities or not selected_data or not selected_months:
        messagebox.showwarning("Lỗi", "Vui lòng chọn ít nhất một thành phố, loại dữ liệu và tháng!")
        return

    plot_trends(data, selected_cities, selected_data, selected_months)


def on_save_button_click(format_var):
    from file_manager import save_to_file
    global forecasts
    if not forecasts:
        messagebox.showwarning("Lỗi", "Không có dữ liệu để lưu!")
        return
    format_choice = format_var.get()
    if format_choice not in ["csv", "xlsx"]:
        messagebox.showwarning("Lỗi", "Vui lòng chọn định dạng file hợp lệ (CSV hoặc XLSX).")
        return
    save_to_file(forecasts, format_choice)


# Thêm hàm xử lý sự kiện cho nút "Dự đoán thiên tai"
def on_predict_disaster_click(data):
    from tkinter import messagebox
    from disaster_predictor import predict_disaster, get_action_recommendations
    result_str = ""
    # Duyệt qua từng thành phố trong dữ liệu
    for city, climate_data in data.items():
        # Mỗi city có thể chứa các loại dữ liệu: temp, rain, sun
        prediction = predict_disaster(climate_data)
        action = get_action_recommendations(prediction)
        result_str += f"{city.title()}:\n  Dự đoán: {prediction}\n  Đề xuất: {action}\n\n"
    messagebox.showinfo("Dự đoán thiên tai & Đề xuất hành động", result_str)


# Thêm hàm xử lý sự kiện cho nút "Thông tin trực tuyến"
def on_realtime_button_click(root, data, cities, data_types):
    """
    Hiển thị cửa sổ thông tin khí hậu trực tuyến với màu sắc biểu thị tình trạng
    """
    try:
        create_real_time_display(root, data, cities, data_types)
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể hiển thị thông tin trực tuyến: {e}")