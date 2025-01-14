import face_recognition as fr
import cv2
import numpy as np
import os

# Define thông tin của các người cần nhận diện
people_data = [
    {"name": "Khiem", "image_path": "pic/hinhkhiem/z4700043387622_da39bf2c4f39c337a5bb0061d643a6f4.jpg"},
    {"name": "Hoang", "image_path": "pic/hinhhoang/z4694981970053_60b82639be2acda236a5afaf6397b3ff.jpg"},
]

# Tải và mã hóa khuôn mặt của các người đã lưu trữ
known_names = []
known_name_encodings = []

for person in people_data:
    name = person["name"]
    encoding = fr.face_encodings(fr.load_image_file(person["image_path"]))[0]

    known_name_encodings.append(encoding)
    #Dòng này thêm mã hóa khuôn mặt của người đó vào danh sách known_name_encodings.
    known_names.append(name)
    #Dòng này thêm tên của người đó vào danh sách known_names.
# Tải ảnh test
test_image_path = "pic/hoangkhiemthoi.jpg"
image = cv2.imread(test_image_path)

# Nhận diện khuôn mặt trong ảnh test
face_locations = fr.face_locations(image)
#fr.face_locations() tìm kiếm vị trí của các khuôn mặt trong hình ảnh.
face_encodings = fr.face_encodings(image, face_locations)
#mã hóa các khuôn mặt đã tìm thấy thành một vectơ đặc trưng. Mỗi vectơ đặc trưng tương ứng với một khuôn mặt.
# Hàm vẽ tên và khung khuôn mặt
def draw_name_frame(image, top, right, bottom, left, name):
    #Hàm draw_name_frame bạn đang sử dụng trong chương trình của mình được thiết kế để vẽ khung và hiển thị tên của người được nhận diện trên ảnh.
    cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)
    cv2.rectangle(image, (left, bottom - 15), (right, bottom), (0, 0, 255), cv2.FILLED)
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(image, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

THRESHOLD = 0.4  # Giá trị ngưỡng (có thể điều chỉnh)

# Nhận diện khuôn mặt và vẽ thông tin người
detected_names = []
detected_faces = []  # Danh sách tọa độ các khuôn mặt đã nhận diện
for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
    matches = fr.compare_faces(known_name_encodings, face_encoding, tolerance=THRESHOLD)
    #Dòng này so sánh mã hóa khuôn mặt của khuôn mặt hiện tại (face_encoding) với danh sách các mã hóa khuôn mặt đã biết (known_name_encodings).
    #fr.compare_faces trả về một danh sách các giá trị True hoặc False tương ứng với việc so sánh khuôn mặt hiện tại với các khuôn mặt đã biết.
    #tolerance=THRESHOLD cho phép bạn chỉ định một ngưỡng (threshold) cho phép sai số trong việc so sánh khuôn mặt.
    name = "nguoi khac"

    for i, match in enumerate(matches):
        if match:
            name = known_names[i]
            break


    detected_names.append(name)
    draw_name_frame(image, top, right, bottom, left, name)
    detected_faces.append((top, right, bottom, left))  # Lưu tọa độ khuôn mặt
    # In ra tọa độ các khuôn mặt
print("Tọa độ các khuôn mặt:")
for i, (top, right, bottom, left) in enumerate(set(detected_faces)):
 print(f"Khuôn mặt {i + 1}: Top: {top}, Right: {right}, Bottom: {bottom}, Left: {left}")

# Đếm số lượng người và số lượng người khác
total_people = len(detected_names)
#Đếm số lượng người được nhận diện trong ảnh. detected_names là danh sách chứa tên của các người được nhận diện.
total_other_people = detected_names.count("Người khác")
#Đếm số lượng người được ghi nhận là "Người khác". Điều này đang định nghĩa rằng họ không được nhận diện là một trong các người đã biết.
total_known_people = total_people - total_other_people
#Tính toán số người đã biết bằng cách trừ đi số người không biết từ tổng số người được nhận diện.
# Hiển thị kết quả
cv2.imshow("Result", image)
# Hiển thị hình ảnh đã được xử lý với các khung và tên đã được vẽ lên.
cv2.imwrite("output.jpg", image)
# Lưu hình ảnh đã xử lý thành tệp "output.jpg".
cv2.waitKey(0)
#Chờ đợi cho đến khi người dùng bấm một phím bất kỳ (0).
cv2.destroyAllWindows()
#Đóng tất cả các cửa sổ hiển thị hình ảnh.

# In ra số lượng người đã nhận diện
print(f"Số người đã nhận diện: {total_people}")
for name in set(detected_names):
    print(name)
print(f"Số người đã biết: {total_known_people}")
print(f"Số người không biết: {total_other_people}")