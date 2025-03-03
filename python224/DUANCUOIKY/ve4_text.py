import csv
import os
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

# Hàm hiển thị dữ liệu khí hậu
def display_climate_data(data, cities, data_types, months):
    """Hiển thị dữ liệu khí hậu theo yêu cầu."""
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    result = []
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

            # Định dạng kết quả
            result.append(f"Thành phố: {city.title()}")
            result.append(f"Loại dữ liệu: {dtype.upper()}")
            result.append("Giá trị theo tháng:")
            for i, value in enumerate(selected_values):
                result.append(f"  {month_names[months[i]][:3]}: {value:.1f}")
            result.append(f"  Nhỏ nhất: {min_val:.1f} ({min_month})")
            result.append(f"  Lớn nhất: {max_val:.1f} ({max_month})")
            result.append(f"  Trung bình: {avg_val:.1f}")
            result.append("-" * 50)

    return result

# Hàm vẽ biểu đồ cho nhiều thành phố
def plot_multiple_cities(data, cities, dtype, months):
    """Vẽ biểu đồ so sánh nhiều thành phố."""
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    plt.figure(figsize=(12, 6))
    for city in cities:
        values = data.get(city, {}).get(dtype, [])
        if not values:
            print(f"Không có dữ liệu cho thành phố '{city}' và loại dữ liệu '{dtype}'.")
            continue
        selected_values = [values[i] for i in months]
        plt.plot([month_names[i] for i in months], selected_values, marker='o', label=city.title())

    plt.title(f"So sánh {dtype.upper()} giữa các thành phố")
    plt.xlabel("Month")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    print(f"\nĐang hiển thị biểu đồ so sánh {dtype.upper()} giữa các thành phố.")
    print("Vui lòng đóng cửa sổ biểu đồ để tiếp tục.")
    plt.show()

# Hàm vẽ biểu đồ riêng cho từng loại dữ liệu
def plot_multiple_data_types(data, city, data_types, months):
    """Vẽ biểu đồ riêng cho từng loại dữ liệu."""
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    for dtype in data_types:
        values = data.get(city, {}).get(dtype, [])
        if not values:
            print(f"Không có dữ liệu cho thành phố '{city}' và loại dữ liệu '{dtype}'.")
            continue

        plt.figure(figsize=(10, 6))
        selected_values = [values[i] for i in months]
        plt.plot([month_names[i] for i in months], selected_values, marker='o', color='b')
        plt.title(f"{dtype.upper()} Data for {city.title()}")
        plt.xlabel("Month")
        plt.ylabel("Value")
        plt.grid(True)
        plt.tight_layout()

        print(f"\nĐang hiển thị biểu đồ {dtype.upper()} cho thành phố '{city}'.")
        print("Vui lòng đóng cửa sổ biểu đồ để tiếp tục.")
        plt.show()

# Hàm lưu dữ liệu vào file
def save_to_file(result):
    """Lưu kết quả vào file."""
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
    filepath = input("Nhập đường dẫn và tên file để lưu (ví dụ: output.txt): ").strip()

    # Kiểm tra file đã tồn tại chưa
    if os.path.exists(filepath):
        overwrite_choice = input("File đã tồn tại. Bạn muốn ghi đè (overwrite) hay thêm vào (append)? (overwrite/append): ").strip().lower()
        if overwrite_choice not in ["overwrite", "append"]:
            print("Vui lòng chọn 'overwrite' hoặc 'append'.")
            return

        mode = "w" if overwrite_choice == "overwrite" else "a"
    else:
        mode = "w"

    # Ghi dữ liệu vào file
    try:
        with open(filepath, mode) as f:
            f.write("\n".join(result))
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

        # Hiển thị dữ liệu
        result = display_climate_data(data, selected_cities, selected_data, selected_months)
        print("\nKẾT QUẢ:")
        print("\n".join(result))

        # Lưu dữ liệu vào file
        save_to_file(result)

        # Vẽ biểu đồ
        if len(selected_cities) > 1 and len(selected_data) == 1:
            # So sánh nhiều thành phố với một loại dữ liệu
            dtype = selected_data[0]
            plot_multiple_cities(data, selected_cities, dtype, selected_months)
        elif len(selected_cities) == 1 and len(selected_data) > 1:
            # So sánh nhiều loại dữ liệu với một thành phố
            city = selected_cities[0]
            plot_multiple_data_types(data, city, selected_data, selected_months)
        else:
            print("\n[!] Cảnh báo: Chỉ hỗ trợ vẽ biểu đồ khi chọn:")
            print("- Nhiều thành phố và một loại dữ liệu, hoặc")
            print("- Một thành phố và nhiều loại dữ liệu.")

        # Hỏi tiếp tục
        if input("\nTiếp tục? (yes/no): ").lower() != "yes":
            break

if __name__ == "__main__":
    main()