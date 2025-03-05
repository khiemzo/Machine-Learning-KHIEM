"""
File cấu hình cho hệ thống an ninh thông minh trên Raspberry Pi 4B
"""

# Cấu hình camera
CAMERA_INDEX = 0
CAMERA_RESOLUTION = (640, 480)
CAMERA_FPS = 20

# Cấu hình GPIO
GPIO_FALL_DETECTION_PIN = 17  # Chân GPIO thông báo phát hiện té ngã
GPIO_INTRUDER_DETECTION_PIN = 18  # Chân GPIO thông báo phát hiện ăn trộm
GPIO_OUTPUT_DURATION = 5  # Thời gian (giây) giữ tín hiệu ở mức cao

# Cấu hình nhận dạng té ngã
FALL_DETECTION_MODEL_PATH = "fall_detection/models/fall_detection_model.h5"
FALL_DETECTION_CONFIDENCE_THRESHOLD = 0.75
FALL_DETECTION_CONSECUTIVE_FRAMES = 3  # Số khung hình liên tiếp để xác nhận té ngã

# Cấu hình nhận dạng ăn trộm
FACE_DATABASE_PATH = "faces/family"
FACE_RECOGNITION_TOLERANCE = 0.6  # Ngưỡng so sánh khuôn mặt (thấp hơn = chính xác hơn)
SUSPICIOUS_BEHAVIOR_THRESHOLD = 0.7  # Ngưỡng xác định hành vi đáng ngờ

# Cấu hình thời gian
NORMAL_HOME_HOURS = [  # Thời gian thông thường có người ở nhà
    (7, 9),   # 7-9 giờ sáng
    (17, 23),  # 17-23 giờ chiều tối
]
WEEKEND_HOME_HOURS = [  # Thời gian thông thường có người ở nhà vào cuối tuần (thứ 7, CN)
    (7, 23),  # 7-23 giờ
]

# Cấu hình xử lý
PROCESSING_INTERVAL = 0.1  # Thời gian giữa các lần xử lý (giây)
LOG_FILE_PATH = "logs/system.log"
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Cấu hình hiệu suất
ENABLE_GPU = True  # Bật/tắt sử dụng GPU (nếu có)
MODEL_OPTIMIZATION = True  # Bật/tắt tối ưu hóa mô hình
DETECTION_FREQUENCY = 5  # Tần suất thực hiện phát hiện (mỗi bao nhiêu khung hình) 