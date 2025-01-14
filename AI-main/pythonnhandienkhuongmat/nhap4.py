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
    known_names.append(name)

# Tải ảnh test
test_image_path = "pic/khiemhoang.jpg"
image = cv2.imread(test_image_path)

# Nhận diện khuôn mặt trong ảnh test
face_locations = fr.face_locations(image)
face_encodings = fr.face_encodings(image, face_locations)

# Hàm vẽ tên và khung khuôn mặt
def draw_name_frame(image, top, right, bottom, left, name):
    cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)
    cv2.rectangle(image, (left, bottom - 15), (right, bottom), (0, 0, 255), cv2.FILLED)
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(image, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

THRESHOLD = 0.4  # Giá trị ngưỡng (có thể điều chỉnh)

# Nhận diện khuôn mặt và vẽ thông tin người
detected_names = []
for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
    matches = fr.compare_faces(known_name_encodings, face_encoding, tolerance=THRESHOLD)
    name = "nguoi khac"

    for i, match in enumerate(matches):
        if match:
            name = known_names[i]
            break


    detected_names.append(name)
    draw_name_frame(image, top, right, bottom, left, name)

# Hiển thị kết quả
cv2.imshow("Result", image)
cv2.imwrite("output.jpg", image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Hiển thị số lượng người và danh sách người đã nhận diện
num_people = len(set(detected_names))
print(f"Số người có trong ảnh: {num_people}")
print("Danh sách người đã nhận diện:")
for name in set(detected_names):
    print(name)