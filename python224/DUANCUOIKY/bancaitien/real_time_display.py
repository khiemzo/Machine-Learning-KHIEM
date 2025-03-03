import tkinter as tk
from tkinter import ttk
import datetime
import random


def create_real_time_display(root, data, cities, data_types):
    """
    Tạo cửa sổ hiển thị thông tin khí hậu trực tuyến với màu sắc
    biểu thị tình trạng (xanh lá - tốt, đỏ - xấu)
    
    Args:
        root: Tkinter root window
        data: Dictionary chứa dữ liệu khí hậu
        cities: Danh sách các thành phố
        data_types: Danh sách các loại dữ liệu khí hậu
    """
    # Tạo cửa sổ mới
    window = tk.Toplevel(root)
    window.title("Thông tin khí hậu trực tuyến")
    window.geometry("800x500")
    window.configure(bg="#2e2e2e")
    
    # Tiêu đề
    title_label = tk.Label(window, text="Thông tin khí hậu trực tuyến",
                          font=("Arial", 16, "bold"), bg="#2e2e2e", fg="white")
    title_label.pack(pady=10)
    
    # Tạo frame chứa thông tin thời gian
    time_frame = tk.Frame(window, bg="#2e2e2e")
    time_frame.pack(fill="x", padx=10, pady=5)
    
    time_label = tk.Label(time_frame, text="Thời gian hiện tại:", 
                         font=("Arial", 12), bg="#2e2e2e", fg="white")
    time_label.pack(side=tk.LEFT, padx=5)
    
    time_value = tk.Label(time_frame, text="", 
                         font=("Arial", 12), bg="#2e2e2e", fg="#00ffff")
    time_value.pack(side=tk.LEFT, padx=5)
    
    # Tạo frame chứa bảng dữ liệu
    table_frame = tk.Frame(window, bg="#2e2e2e")
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Tạo bảng dữ liệu
    columns = ["Thành phố"] + [dt.upper() for dt in data_types] + ["Đánh giá chung"]
    tree = ttk.Treeview(table_frame, columns=columns, show="headings")
    
    # Thiết lập tiêu đề cột
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="center")
    
    # Thêm thanh cuộn
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(fill="both", expand=True)
    
    # Thêm frame chú thích
    legend_frame = tk.Frame(window, bg="#2e2e2e")
    legend_frame.pack(fill="x", padx=10, pady=5)
    
    # Chú thích màu xanh
    good_frame = tk.Frame(legend_frame, bg="#2e2e2e")
    good_frame.pack(side=tk.LEFT, padx=20)
    
    good_color = tk.Label(good_frame, text="    ", bg="#00ff00")
    good_color.pack(side=tk.LEFT, padx=2)
    
    good_label = tk.Label(good_frame, text="Tốt", bg="#2e2e2e", fg="white")
    good_label.pack(side=tk.LEFT, padx=2)
    
    # Chú thích màu vàng
    medium_frame = tk.Frame(legend_frame, bg="#2e2e2e")
    medium_frame.pack(side=tk.LEFT, padx=20)
    
    medium_color = tk.Label(medium_frame, text="    ", bg="#ffff00")
    medium_color.pack(side=tk.LEFT, padx=2)
    
    medium_label = tk.Label(medium_frame, text="Trung bình", bg="#2e2e2e", fg="white")
    medium_label.pack(side=tk.LEFT, padx=2)
    
    # Chú thích màu đỏ
    bad_frame = tk.Frame(legend_frame, bg="#2e2e2e")
    bad_frame.pack(side=tk.LEFT, padx=20)
    
    bad_color = tk.Label(bad_frame, text="    ", bg="#ff0000")
    bad_color.pack(side=tk.LEFT, padx=2)
    
    bad_label = tk.Label(bad_frame, text="Kém", bg="#2e2e2e", fg="white")
    bad_label.pack(side=tk.LEFT, padx=2)
    
    # Nút cập nhật
    refresh_button = tk.Button(window, text="Cập nhật dữ liệu", 
                              command=lambda: update_data(tree, data, cities, data_types))
    refresh_button.pack(pady=10)
    
    # Hàm cập nhật thời gian
    def update_time():
        current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        time_value.config(text=current_time)
        window.after(1000, update_time)  # Cập nhật mỗi giây
    
    # Khởi động cập nhật thời gian
    update_time()
    
    # Cập nhật dữ liệu lần đầu
    update_data(tree, data, cities, data_types)
    
    return window


def update_data(tree, data, cities, data_types):
    """
    Cập nhật dữ liệu trong bảng hiển thị
    """
    # Xóa dữ liệu cũ
    for item in tree.get_children():
        tree.delete(item)
    
    # Lấy tháng hiện tại (0-11)
    current_month = datetime.datetime.now().month - 1
    
    # Thêm dữ liệu mới
    for city in cities:
        values = [city.title()]
        
        # Đánh giá từng loại dữ liệu
        ratings = []
        for dtype in data_types:
            # Lấy giá trị thực tế từ dữ liệu
            if city in data and dtype in data[city]:
                value = data[city][dtype][current_month]
                
                # Thêm nhiễu ngẫu nhiên để mô phỏng dữ liệu thời gian thực
                random_noise = random.uniform(-0.2, 0.2)
                current_value = value * (1 + random_noise)
                current_value = round(current_value, 1)
                
                # Đánh giá giá trị theo loại dữ liệu
                rating = evaluate_value(dtype, current_value)
                ratings.append(rating)
                
                # Định dạng giá trị và thêm vào danh sách
                values.append(f"{current_value}")
            else:
                values.append("N/A")
                ratings.append(0)
        
        # Tính đánh giá tổng thể
        overall = calculate_overall_rating(ratings)
        values.append(get_rating_text(overall))
        
        # Thêm hàng mới vào bảng
        item_id = tree.insert("", "end", values=values)
        
        # Đặt màu nền cho từng ô
        for i, dtype in enumerate(data_types):
            if i < len(ratings):
                color = get_color_for_rating(ratings[i])
                tree.item(item_id, tags=(f"rating_{i}",))
                tree.tag_configure(f"rating_{i}", background=color)
        
        # Đặt màu nền cho đánh giá tổng thể
        tree.item(item_id, tags=(f"overall_{item_id}",))
        tree.tag_configure(f"overall_{item_id}", background=get_color_for_rating(overall))


def evaluate_value(data_type, value):
    """
    Đánh giá giá trị dựa trên loại dữ liệu
    Trả về giá trị từ -1 (xấu) đến 1 (tốt)
    """
    if data_type == "temp":
        # Nhiệt độ: 20-25 độ là tốt nhất
        if 20 <= value <= 25:
            return 1.0
        elif 15 <= value < 20 or 25 < value <= 30:
            return 0.0
        else:
            return -1.0
    elif data_type == "rain":
        # Lượng mưa: 50-150mm là tốt
        if 50 <= value <= 150:
            return 1.0
        elif 20 <= value < 50 or 150 < value <= 200:
            return 0.0
        else:
            return -1.0
    elif data_type == "sun":
        # Ánh nắng: 150-250 giờ ánh nắng là tốt
        if 150 <= value <= 250:
            return 1.0
        elif 100 <= value < 150 or 250 < value <= 300:
            return 0.0
        else:
            return -1.0
    return 0.0


def calculate_overall_rating(ratings):
    """
    Tính đánh giá tổng thể từ các đánh giá riêng lẻ
    """
    if not ratings:
        return 0.0
        
    return sum(ratings) / len(ratings)


def get_color_for_rating(rating):
    """
    Trả về mã màu dựa trên đánh giá
    """
    if rating > 0.5:
        return "#00ff00"  # Xanh lá - tốt
    elif rating > -0.5:
        return "#ffff00"  # Vàng - trung bình
    else:
        return "#ff0000"  # Đỏ - xấu


def get_rating_text(rating):
    """
    Trả về chuỗi mô tả đánh giá
    """
    if rating > 0.5:
        return "Tốt"
    elif rating > -0.5:
        return "Trung bình"
    else:
        return "Kém"
