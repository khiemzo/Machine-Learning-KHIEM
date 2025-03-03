import csv
import os


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


def get_valid_input(prompt, valid_options, allow_multiple=True):
    """Lấy và kiểm tra đầu vào từ người dùng."""
    while True:
        print(f"\n{prompt}")
        print("Các lựa chọn hợp lệ:", ", ".join(valid_options))
        print("Nhập 'all' để chọn tất cả.")
        choices = input("Lựa chọn của bạn (phân cách bằng dấu phẩy): ").lower().strip().split(',')

        # Xử lý trường hợp chọn tất cả
        if "all" in choices:
            return valid_options.copy()

        # Lọc các lựa chọn hợp lệ
        valid_choices = []
        for choice in choices:
            choice = choice.strip()
            if choice in valid_options:
                valid_choices.append(choice)
            else:
                print(f"  [!] '{choice}' không hợp lệ - bỏ qua")

        # Kiểm tra ít nhất 1 lựa chọn
        if valid_choices:
            return valid_choices
        print("Vui lòng chọn ít nhất một giá trị hợp lệ!")


def display_climate_data(data, cities, data_types, months):
    """Hiển thị dữ liệu khí hậu theo yêu cầu."""
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    for city in cities:
        print(f"\n{'=' * 50}\nDữ liệu cho {city.title()}:")

        for dtype in data_types:
            values = data.get(city, {}).get(dtype, [])
            if not values:
                print(f"  Không có dữ liệu {dtype} cho {city}")
                continue

            # Lọc dữ liệu theo tháng
            selected_values = [values[i] for i in months]

            # Tính toán thống kê
            min_val = min(selected_values)
            max_val = max(selected_values)
            avg_val = sum(selected_values) / len(selected_values)
            min_month = month_names[months[selected_values.index(min_val)]]
            max_month = month_names[months[selected_values.index(max_val)]]

            # Hiển thị
            print(f"\n{dtype.upper()}:")
            print("Tháng:    " + "\t".join(f"{month_names[i][:3]:>5}" for i in months))
            print("Giá trị:  " + "\t".join(f"{v:5.1f}" for v in selected_values))
            print(f"  Nhỏ nhất: {min_val:.1f} ({min_month})")
            print(f"  Lớn nhất: {max_val:.1f} ({max_month})")
            print(f"  Trung bình: {avg_val:.1f}")


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
        selected_cities = get_valid_input(
            "\nCHỌN THÀNH PHỐ",
            [c.lower() for c in cities],
            allow_multiple=True
        )

        # Chọn loại dữ liệu
        selected_data = get_valid_input(
            "\nCHỌN LOẠI DỮ LIỆU",
            data_types,
            allow_multiple=True
        )

        # Chọn tháng
        selected_months_input = get_valid_input(
            "\nCHỌN THÁNG",
            month_options,
            allow_multiple=True
        )
        selected_months = [month_map[m] for m in selected_months_input]

        # Hiển thị dữ liệu
        display_climate_data(data, selected_cities, selected_data, selected_months)

        # Hỏi tiếp tục
        if input("\nTiếp tục? (yes/no): ").lower() != "yes":
            break


if __name__ == "__main__":
    main()