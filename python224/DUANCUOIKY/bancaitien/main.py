from data_loader import load_data
from gui import setup_gui
from auth import login
from feature_engineering import FeatureEngineering

def main():
    # Yêu cầu đăng nhập
    if not login():
        return

    try:
        raw_data = load_data()  # Dữ liệu ban đầu ở dạng dictionary
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # Sử dụng FeatureEngineering để xử lý dữ liệu
    fe = FeatureEngineering.from_dict(raw_data)
    fe.add_feature_auto()  # Thêm đặc trưng tự động, ví dụ: humidity
    # Tính dự báo cho từng loại dữ liệu cần thiết
    for dtype in ["temp", "rain", "sun"]:
        fe.add_forecast_feature(dtype, forecast_horizon=1, method="linear", poly_degree=2)
    fe.preprocess_data()
    # Chuyển đổi DataFrame đã xử lý về dạng dictionary ban đầu
    processed_data = fe.to_dict()

    # Các tham số giao diện (vẫn giữ nguyên cấu trúc ban đầu)
    cities = list(processed_data.keys())
    data_types = ["temp", "rain", "sun"]
    month_options = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    month_map = {m: i for i, m in enumerate(month_options)}

    gui_elements = setup_gui(processed_data, cities, data_types, month_options, month_map)
    root = gui_elements["root"]
    root.mainloop()

if __name__ == "__main__":
    main()
