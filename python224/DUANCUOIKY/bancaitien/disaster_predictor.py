# disaster_predictor.py
import numpy as np
from sklearn.ensemble import RandomForestClassifier

def train_dummy_model():
    """
    Huấn luyện mô hình dự đoán thiên tai trên dữ liệu giả định.
    Giả sử các đặc trưng gồm: trung bình nhiệt độ, lượng mưa, và ánh sáng.
    Nhãn: 0 - No Disaster, 1 - Flood, 2 - Drought, 3 - Storm.
    """
    np.random.seed(42)
    X = np.random.rand(100, 3)  # 100 mẫu, 3 đặc trưng
    y = np.random.randint(0, 4, size=100)  # Nhãn ngẫu nhiên từ 0 đến 3
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X, y)
    return model

# Huấn luyện mô hình khi module được load
disaster_model = train_dummy_model()

def predict_disaster(climate_values):
    """
    Dự đoán hiện tượng thiên tai dựa trên dữ liệu khí hậu trung bình của một thành phố.
    Tham số:
      - climate_values: dict chứa các key 'temp', 'rain', 'sun'
    Trả về:
      - Chuỗi dự đoán, ví dụ: "Flood", "Drought", "Storm", hoặc "No Disaster".
    """
    avg_temp = np.mean(climate_values.get("temp", [0]))
    avg_rain = np.mean(climate_values.get("rain", [0]))
    avg_sun = np.mean(climate_values.get("sun", [0]))
    X_new = np.array([[avg_temp, avg_rain, avg_sun]])
    pred = disaster_model.predict(X_new)[0]
    disaster_mapping = {0: "No Disaster", 1: "Flood", 2: "Drought", 3: "Storm"}
    return disaster_mapping.get(pred, "No Disaster")

def get_action_recommendations(disaster_prediction):
    """
    Đề xuất hành động dựa trên dự đoán thiên tai.
    """
    recommendations = {
        "Flood": "Dự báo lũ lụt: Hãy chuẩn bị sơ tán và bảo vệ tài sản.",
        "Drought": "Dự báo hạn hán: Tiết kiệm nước và chuẩn bị nguồn nước dự phòng.",
        "Storm": "Dự báo bão: Kiểm tra thiết bị chống bão và theo dõi cảnh báo.",
        "No Disaster": "Tình hình khí hậu ổn định. Tiếp tục theo dõi."
    }
    return recommendations.get(disaster_prediction, "Không có đề xuất cụ thể.")