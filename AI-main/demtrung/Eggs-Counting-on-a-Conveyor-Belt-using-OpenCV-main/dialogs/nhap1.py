import cv2
import numpy as np

# Bước 1: Đọc ảnh đầu vào
image = cv2.imread('K:\hoccode\AI-main\AI-main\demtrung\Eggs-Counting-on-a-Conveyor-Belt-using-OpenCV-main\dialogs\images1.jpeg')

# Bước 2: Chuyển đổi ảnh sang không gian màu xám
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Bước 3: Làm mờ ảnh để giảm nhiễu
blurred = cv2.GaussianBlur(gray, (11, 11), 0)

# Bước 4: Áp dụng ngưỡng nhị phân (Thresholding)
_, thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY_INV)

# Bước 5: Sử dụng phép biến đổi hình thái học để loại bỏ nhiễu (Morphological Transformations)
kernel = np.ones((5, 5), np.uint8)
closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

# Bước 6: Tìm các đường viền (Contours) của các vật thể
contours, _ = cv2.findContours(closing.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Bước 7: Khởi tạo bộ đếm trứng
egg_count = 0

# Bước 8: Duyệt qua các đường viền để nhận diện và đếm trứng
for contour in contours:
    # Xác định hình elip hoặc hình tròn bao quanh vật thể
    if len(contour) >= 5:  # Đảm bảo có đủ điểm để khớp hình elip
        ellipse = cv2.fitEllipse(contour)
        (x, y), (major_axis, minor_axis), angle = ellipse

        # Xác định kích thước và hình dạng trứng dựa trên tỉ lệ giữa các trục
        aspect_ratio = major_axis / minor_axis
        if 0.8 <= aspect_ratio <= 1.2:  # Điều kiện để xác định trứng có hình elip hoặc gần tròn
            egg_count += 1
            # Vẽ hình elip bao quanh trứng
            cv2.ellipse(image, ellipse, (0, 255, 0), 2)

# Bước 9: Hiển thị số lượng trứng lên ảnh
cv2.putText(image, f'Egg Count: {egg_count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

# Bước 10: Hiển thị kết quả
cv2.imshow('Egg Detection', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
