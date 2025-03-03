import csv
import os
from tkinter import messagebox
from functools import lru_cache

@lru_cache(maxsize=1)
def load_data():
    """Đọc dữ liệu từ các file CSV và trả về dictionary. (Dữ liệu được cache để tối ưu tốc độ)"""
    data = {}
    data_types = {
        "temp": "temperature.csv",
        "rain": "rainfall.csv",
        "sun": "sunshine.csv"
    }
    for dtype, filename in data_types.items():
        filepath = os.path.join(os.path.dirname(__file__), filename)
        if not os.path.exists(filepath):
            messagebox.showerror("Lỗi", f"Không tìm thấy file {filename}! Vui lòng kiểm tra đường dẫn hoặc tên file.")
            raise FileNotFoundError(f"File {filename} không tồn tại tại {filepath}.")
        try:
            with open(filepath, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    city = row[0].strip().lower()
                    if city not in data:
                        data[city] = {}
                    try:
                        # Sửa slicing để lấy đủ 12 giá trị (tháng 1-12)
                        data[city][dtype] = [float(x) for x in row[1:13]]
                    except ValueError:
                        print(f"Dữ liệu không hợp lệ cho thành phố {city} trong file {filename}.")
                        continue
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đọc file {filename}: {e}")
            raise e
    return data
