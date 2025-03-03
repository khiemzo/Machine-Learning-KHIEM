import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

def forecast_advanced(values, forecast_horizon=1, method='linear', poly_degree=2):
    """
    Dự báo giá trị trong tương lai từ dữ liệu lịch sử với nhiều phương pháp.

    Parameters:
      - values: danh sách giá trị lịch sử.
      - forecast_horizon: số tháng cần dự báo (mặc định 1).
      - method: phương pháp dự báo: 'linear', 'polynomial', 'arima', 'ann'
      - poly_degree: bậc của mô hình hồi quy đa thức (chỉ dùng nếu method=='polynomial')

    Returns:
      - forecast: mảng dự báo cho số tháng tiếp theo.
      - mae: sai số trung bình tuyệt đối trên tập huấn luyện.
      - conf_int: khoảng tin cậy (danh sách các cặp [lower, upper]) nếu có; nếu không thì None.
    """
    values = np.array(values)
    n = len(values)
    X = np.arange(n).reshape(-1, 1)
    y = values

    forecast, mae, conf_int = None, None, None

    try:
        if method == 'linear':
            model = LinearRegression()
            model.fit(X, y)
            y_pred_train = model.predict(X)
            mae = mean_absolute_error(y, y_pred_train)
            forecast = model.predict(np.arange(n, n + forecast_horizon).reshape(-1, 1))

        elif method == 'polynomial':
            from sklearn.preprocessing import PolynomialFeatures
            poly = PolynomialFeatures(degree=poly_degree)
            X_poly = poly.fit_transform(X)
            model = LinearRegression()
            model.fit(X_poly, y)
            y_pred_train = model.predict(X_poly)
            mae = mean_absolute_error(y, y_pred_train)
            X_future = poly.transform(np.arange(n, n + forecast_horizon).reshape(-1, 1))
            forecast = model.predict(X_future)

        elif method == 'arima':
            try:
                from statsmodels.tsa.arima.model import ARIMA
                model = ARIMA(y, order=(1, 1, 1))
                model_fit = model.fit()
                forecast_result = model_fit.get_forecast(steps=forecast_horizon)
                forecast = forecast_result.predicted_mean
                conf_int = forecast_result.conf_int().tolist()
                in_sample_forecast = model_fit.predict(start=1, end=n - 1, dynamic=False)
                mae = mean_absolute_error(y[1:], in_sample_forecast)
            except Exception as e:
                raise Exception(f"Lỗi ARIMA: {e}. Vui lòng kiểm tra cài đặt statsmodels và dữ liệu đầu vào.")

        elif method == 'ann':
            from sklearn.neural_network import MLPRegressor
            # Tăng max_iter để giảm cảnh báo hội tụ (có thể điều chỉnh thêm nếu cần)
            model = MLPRegressor(hidden_layer_sizes=(50,), max_iter=2000, random_state=42)
            model.fit(X, y)
            y_pred_train = model.predict(X)
            mae = mean_absolute_error(y, y_pred_train)
            forecast = model.predict(np.arange(n, n + forecast_horizon).reshape(-1, 1))

        else:
            raise ValueError("Phương pháp dự báo không hợp lệ! Vui lòng chọn 'linear', 'polynomial', 'arima' hoặc 'ann'.")
    except Exception as e:
        raise Exception(f"Lỗi dự báo ({method}): {e}")

    return forecast, mae, conf_int
