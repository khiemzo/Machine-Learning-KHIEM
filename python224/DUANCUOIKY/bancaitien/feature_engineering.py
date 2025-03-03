import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer


class FeatureEngineering:
    def __init__(self, df):
        self.data = df

    @classmethod
    def from_dict(cls, data_dict):
        """
        Chuyển đổi dữ liệu từ dictionary (như từ data_loader)
        thành DataFrame với mỗi hàng ứng với một thành phố.
        Các cột được đặt theo định dạng: "<data_type>_<tháng>" (tháng từ 1 đến 12)
        """
        rows = []
        for city, types in data_dict.items():
            row = {"city": city}
            for dtype, values in types.items():
                # Giả định rằng mỗi loại dữ liệu có 12 giá trị (tháng 1-12)
                for i, value in enumerate(values):
                    col_name = f"{dtype}_{i + 1}"
                    row[col_name] = value
            rows.append(row)
        df = pd.DataFrame(rows)
        return cls(df)

    def add_feature_manual(self, feature_name, feature_data):
        """
        Thêm đặc trưng mới được nhập thủ công.
        Số lượng phần tử trong feature_data phải bằng số hàng của DataFrame.
        """
        if len(feature_data) != len(self.data):
            raise ValueError("Số lượng phần tử của feature_data phải bằng số hàng dữ liệu.")
        self.data[feature_name] = feature_data

    def add_feature_auto(self, source=None):
        """
        Thêm đặc trưng tự động từ nguồn ngoài.
        Ở đây mô phỏng bằng cách sinh ngẫu nhiên giá trị 'humidity'.
        """
        self.data["humidity"] = np.random.randint(30, 70, size=len(self.data))

    def preprocess_data(self):
        """
        Tiền xử lý dữ liệu:
         - Xử lý giá trị khuyết thiếu (mean imputation)
         - Chuẩn hóa các cột số
        """
        numeric_cols = self.data.select_dtypes(include=["number"]).columns
        imputer = SimpleImputer(strategy="mean")
        self.data[numeric_cols] = imputer.fit_transform(self.data[numeric_cols])
        scaler = StandardScaler()
        self.data[numeric_cols] = scaler.fit_transform(self.data[numeric_cols])
        return self.data

    def add_forecast_feature(self, data_type, forecast_horizon=1, method="linear", poly_degree=2):
        """
        Tính dự báo cho mỗi thành phố dựa trên chuỗi giá trị của data_type.
        Sử dụng hàm forecast_advanced từ module forecast.
        Các kết quả dự báo (forecast, MAE, CI) sẽ được lưu dưới dạng các cột mới:
           - "<data_type>_forecast"
           - "<data_type>_mae"
           - "<data_type>_ci"
        """
        from forecast import forecast_advanced
        forecasts = []
        maes = []
        cis = []
        for idx, row in self.data.iterrows():
            # Lấy 12 giá trị từ cột data_type_1 đến data_type_12
            values = [row.get(f"{data_type}_{i + 1}") for i in range(12)]
            try:
                forecast, mae, conf_int = forecast_advanced(values, forecast_horizon, method, poly_degree)
                forecast_val = forecast[0] if forecast is not None and len(forecast) > 0 else None
            except Exception as e:
                forecast_val = None
                mae = None
                conf_int = None
            forecasts.append(forecast_val)
            maes.append(mae)
            cis.append(conf_int)
        self.data[f"{data_type}_forecast"] = forecasts
        self.data[f"{data_type}_mae"] = maes
        self.data[f"{data_type}_ci"] = cis
        return self.data

    def to_dict(self):
        """
        Chuyển đổi DataFrame đã xử lý trở lại dictionary theo định dạng ban đầu:
        Mỗi thành phố có các key data_type với danh sách 12 giá trị.
        (Các cột đặc trưng bổ sung như dự báo sẽ không được đưa vào.)
        """
        result = {}
        for _, row in self.data.iterrows():
            city = row["city"]
            result[city] = {}
            for col in self.data.columns:
                if col == "city" or any(col.endswith(suffix) for suffix in ["_forecast", "_mae", "_ci"]):
                    continue
                if "_" in col:
                    dtype, month = col.split("_")
                    if dtype not in result[city]:
                        result[city][dtype] = []
                    result[city][dtype].append(row[col])
            # Sắp xếp lại danh sách theo thứ tự tháng (giả định tên cột theo dạng dataType_1 ... dataType_12)
            for dtype in result[city]:
                result[city][dtype] = result[city][dtype][:12]
        return result


# Ví dụ sử dụng module feature_engineering
if __name__ == "__main__":
    sample_data = {
        "hanoi": {
            "temp": [20, 21, 19, 22, 23, 24, 25, 26, 27, 28, 29, 30],
            "rain": [100, 110, 90, 95, 105, 115, 120, 130, 125, 100, 85, 90],
            "sun": [200, 210, 190, 205, 215, 225, 230, 240, 235, 220, 205, 210]
        },
        "hcmc": {
            "temp": [30, 31, 29, 32, 33, 34, 35, 36, 37, 38, 39, 40],
            "rain": [80, 85, 75, 70, 90, 95, 100, 105, 110, 115, 120, 125],
            "sun": [250, 255, 245, 260, 265, 270, 275, 280, 285, 290, 295, 300]
        }
    }
    fe = FeatureEngineering.from_dict(sample_data)
    fe.add_feature_auto()
    for dtype in ["temp", "rain", "sun"]:
        fe.add_forecast_feature(dtype, forecast_horizon=1, method="linear", poly_degree=2)
    fe.preprocess_data()
    print(fe.data)
