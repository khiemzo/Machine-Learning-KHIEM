import csv
import os
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
            print(f"Lỗi: Không tìm thấy file {filename}!")
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
    result = []
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

            # Định dạng kết quả
            result.append(f"Thành phố: {city.title()}")
            result.append(f"Loại dữ liệu: {dtype.upper()}")
            result.append("Giá trị theo tháng:")
            for i, value in enumerate(selected_values):
                result.append(f"  {month_names[months[i]][:3]}: {value:.1f}")
            result.append(f"  Nhỏ nhất: {min_val:.1f} ({min_month})")
            result.append(f"  Lớn nhất: {max_val:.1f} ({max_month})")
            result.append(f"  Trung bình: {avg_val:.1f}")
            result.append(f"  Dự báo tháng tiếp theo: {forecast:.1f}")
            result.append("-" * 50)

    return result, forecasts

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

    print("\nĐang hiển thị biểu đồ xu hướng.")
    print("Vui lòng đóng cửa sổ biểu đồ để tiếp tục.")
    plt.show()

# Hàm lưu dữ liệu vào file
def save_to_file(result, forecasts, format_choice):
    """Lưu kết quả vào file theo định dạng .csv hoặc .xlsx."""
    while True:
        choice = input("Bạn có muốn lưu kết quả vào file không? (yes/no): ").strip().lower()
        if choice == "no":
            print("Kết quả không được lưu.")
            return
        elif choice == "yes":
            break
        else:
            print("Vui lòng nhập 'yes' hoặc 'no'.")

    # Nhập đường dẫn và tên file
    filepath = input("Nhập đường dẫn và tên file để lưu (ví dụ: output): ").strip()
    if format_choice == "csv":
        filepath += ".csv"
        try:
            with open(filepath, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["City", "Data Type", "Forecast"])
                for (city, dtype), forecast in forecasts.items():
                    writer.writerow([city.title(), dtype.upper(), f"{forecast:.1f}"])
            print(f"Kết quả đã được lưu vào file: {filepath}")
        except Exception as e:
            print(f"Lỗi khi lưu file: {e}")
    elif format_choice == "xlsx":
        filepath += ".xlsx"
        try:
            df = pd.DataFrame({
                "City": [city.title() for (city, _) in forecasts.keys()],
                "Data Type": [dtype.upper() for (_, dtype) in forecasts.keys()],
                "Forecast": [f"{forecast:.1f}" for forecast in forecasts.values()]
            })
            df.to_excel(filepath, index=False)
            print(f"Kết quả đã được lưu vào file: {filepath}")
        except Exception as e:
            print(f"Lỗi khi lưu file: {e}")

# Hàm chính
def main():
    # Khởi tạo dữ liệu
    print("Chào mừng đến với CLIP - Climate Plotter")
    print("Đang tải dữ liệu...", end='')
    data = load_data()
    cities = list(data.keys())
    data_types = ["temp", "rain", "sun"]
    month_options = ["jan", "feb", "mar", "apr", "may", "jun",
                     "jul", "aug", "sep", "oct", "nov", "dec"]
    month_map = {m: i for i, m in enumerate(month_options)}
    print(" Hoàn tất!")

    while True:
        # Chọn thành phố
        print("\nCHỌN THÀNH PHỐ")
        print("Các lựa chọn hợp lệ:", ", ".join(cities))
        print("Nhập 'all' để chọn tất cả.")
        city_input = input("Lựa chọn của bạn (phân cách bằng dấu phẩy): ").lower().strip().split(',')
        selected_cities = []
        for city in city_input:
            city = city.strip()
            if city == "all":
                selected_cities = cities.copy()
                break
            elif city in cities:
                selected_cities.append(city)
            else:
                print(f"  [!] '{city}' không hợp lệ - bỏ qua")
        if not selected_cities:
            print("Vui lòng chọn ít nhất một thành phố hợp lệ!")
            continue

        # Chọn loại dữ liệu
        print("\nCHỌN LOẠI DỮ LIỆU")
        print("Các lựa chọn hợp lệ:", ", ".join(data_types))
        print("Nhập 'all' để chọn tất cả.")
        data_input = input("Lựa chọn của bạn (phân cách bằng dấu phẩy): ").lower().strip().split(',')
        selected_data = []
        for dtype in data_input:
            dtype = dtype.strip()
            if dtype == "all":
                selected_data = data_types.copy()
                break
            elif dtype in data_types:
                selected_data.append(dtype)
            else:
                print(f"  [!] '{dtype}' không hợp lệ - bỏ qua")
        if not selected_data:
            print("Vui lòng chọn ít nhất một loại dữ liệu hợp lệ!")
            continue

        # Chọn tháng
        print("\nCHỌN THÁNG")
        print("Các lựa chọn hợp lệ:", ", ".join(month_options))
        print("Nhập 'all' để chọn tất cả.")
        month_input = input("Lựa chọn của bạn (phân cách bằng dấu phẩy): ").lower().strip().split(',')
        selected_months = []
        for month in month_input:
            month = month.strip()
            if month == "all":
                selected_months = list(range(12))
                break
            elif month in month_map:
                selected_months.append(month_map[month])
            else:
                print(f"  [!] '{month}' không hợp lệ - bỏ qua")
        if not selected_months:
            print("Vui lòng chọn ít nhất một tháng hợp lệ!")
            continue

        # Hiển thị dữ liệu và dự báo
        result, forecasts = display_climate_data_with_forecast(data, selected_cities, selected_data, selected_months)
        print("\nKẾT QUẢ:")
        print("\n".join(result))

        # Vẽ biểu đồ xu hướng
        plot_trends(data, selected_cities, selected_data, selected_months)

        # Lưu dữ liệu vào file
        format_choice = input("\nChọn định dạng lưu file (csv/xlsx): ").strip().lower()
        if format_choice not in ["csv", "xlsx"]:
            print("Định dạng không hợp lệ. Chỉ hỗ trợ 'csv' hoặc 'xlsx'.")
        else:
            save_to_file(result, forecasts, format_choice)

        # Hỏi tiếp tục
        if input("\nTiếp tục? (yes/no): ").lower() != "yes":
            break

if __name__ == "__main__":
    main()