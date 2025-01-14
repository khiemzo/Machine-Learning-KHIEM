# ------- Khai báo thư viện -------
import cv2 
import numpy as np 


# ------- Khai tạo các biến và hàm ----------
# Đường viền tối thiểu
min_contour_width = 40
min_contour_height = 40

# Số pixel sai số nhận biết cho phép
offset = 15

# Điểm nhận diện
line_height = 600

delay = 30

# Danh sach rỗng
detect = []

counter = 0
def tam_chu_nhat(x, y, w, h):
    # Bán kính hcn
    x1 = int(w / 2)
    y1 = int(h / 2)

    # Tọa độ của tâm
    cx = x + x1
    cy = y + y1

    return cx, cy


# ----------- Nguồn vào Video ------------
cap = cv2.VideoCapture('video.mp4')
if cap.isOpened():
    ret, frame1 = cap.read()
else:
    ret = False
ret, frame1 = cap.read()
ret, frame2 = cap.read()


# ------ Vòng lặp thực hiên các thao tác trên khung -----------

while ret:

    # Tính chênh lệch tuyệt đối giữa các khung hình liên tiếp
    d = cv2.absdiff(frame1, frame2)

    # Chuyển đổi sự khác biệt sang thang độ xám
    grey = cv2.cvtColor(d, cv2.COLOR_BGR2GRAY)

    # Áp dụng hiệu ứng làm mờ Gaussian cho ảnh thang độ xám
    blur = cv2.GaussianBlur(grey, (5, 5), 3)


    # Áp dụng ngưỡng để tạo ảnh nhị phân
    ret, mask = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)

    # Làm giãn hình ảnh nhị phân để lấp đầy khoảng trống giữa các đường viền đối tượng *dilated: giãn ra
    dilated = cv2.dilate(mask, np.ones((3, 3)))

    # Tạo kernel cho các hoạt động hình thái elip
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))

    # Ve duong thang de xac dinh so xe di qua
    cv2.line(frame1, (180, line_height), (1100, line_height), (0, 255, 0), 3)

    # Đóng hình thái ảnh nhị phân giãn ra
    closing = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel)

    # Tim duong vien
    contorno, ret = cv2.findContours(closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)


# Lặp các đường viền va kiểm tra đường viền cho đối tượng dựa trên kích thước hình chữ nhật giới hạn của chúng.

    for (i, c) in enumerate(contorno):
        # Gần tọa độ hình bao quanh chuyển động
        (x, y, w, h) = cv2.boundingRect(c)
        # Điều kiện để được nhận diện là ô tô
        contour_valid = (w >= min_contour_width) and (h >= min_contour_height)
        # Kiểm tra điều kiện đường viền
        if not contour_valid:
            continue

        # Vẽ hình chữ nhật với tọa độ đã biết
        cv2.rectangle(frame1, (x, y), (x + w, y + h), (255, 0, 0), 2)
        # Xác định tâm
        tam = tam_chu_nhat(x, y, w, h)

        # Thêm một phân tử vào danh sách hiên tại
        detect.append(tam)
        # Vẽ 1 chấm ở tâm hình chữ nhât
        cv2.circle(frame1, tam, 4, (0, 255, 0), -1)
        # cx, cy = tam_chu_nhat(x, y, w, h)

# Lặp lại danh sách các trung tâm được phát hiện (detect) và kiểm tra xem các đối tượng các vượt qua vạch định sẵn
        for (x, y) in detect:
            # Khi ô tô di chuyển qua đường định sẵn cộng 1 vào biến đếm
            if y < (line_height + offset) and y > (line_height - offset):
                # Bộ đếm
                counter += 1

                detect.remove((x, y))
                # hien thi so dem tren Terminal
                print("So phuong tien: " + str(counter))


# Gọi hàm để thêm văn bản thông tin vào hình ảnh & video.
    cv2.putText(frame1, "Dem phuong tien: " + str(counter), (730, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.putText(frame1, "~Nhom 13~ ", (210, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 127, 0), 2)

    #cv2.drawContours(frame1,contorno,-1,(0,0,255),2)  # vẽ các đường viền (contorno) trên ảnh (frame1) bằng màu đỏ.

# ---------- Hiển thị văn bản trên khung cửa sổ -----------
    cv2.imshow("Lap trinh ung dung", frame1)

    #cv2.imshow("Demo", mask)


# ------------------------ Thoát chương trình -------------------

    if cv2.waitKey(delay) & 0xFF == ord('q'):
        break

    frame1 = frame2

    ret, frame2 = cap.read()

#cv2.waitKey(0)
#cv2.imshow("frame1", frame1)


cap.release()
cv2.destroyAllWindows()