# vesion2 là bản nâng cấp của vesion1
import cv2
import face_recognition
import numpy as np

# Khởi tạo danh sách thông tin người
people_data = [
    {"name": "Chandler GT: Nam"},
    {"name": "joey GT: nam"},
    {"name": "monica GT: nu"},
    {"name": "phoebe GT: nu"},
    {"name": "rachel GT: nu"},
    {"name": "ross GT: nam"},
]

# Load và mã hóa khuôn mặt của các người đã lưu trữ
encoded_faces = []
for person in people_data:
    image_path1 = f"pic/chandler.jpg"  # Đường dẫn đến hình ảnh của mỗi người
    image = face_recognition.load_image_file(image_path1)
    encoding = face_recognition.face_encodings(image)[0]  # Lưu ý: chỉ lấy mã hóa đầu tiên
    encoded_faces.append({"Chandler GT: Nam": person["name"], "encoding": encoding})
    print(encoded_faces)
    image_path2 = f"pic/joey.jpg"  # Đường dẫn đến hình ảnh của mỗi người
    image = face_recognition.load_image_file(image_path2)
    encoding = face_recognition.face_encodings(image)[0]  # Lưu ý: chỉ lấy mã hóa đầu tiên
    encoded_faces.append({"joey GT: nam": person["name"], "encoding": encoding})

    image_path3 = f"pic/monica.jpg"  # Đường dẫn đến hình ảnh của mỗi người
    image = face_recognition.load_image_file(image_path3)
    encoding = face_recognition.face_encodings(image)[0]  # Lưu ý: chỉ lấy mã hóa đầu tiên
    encoded_faces.append({"monica GT: nu": person["name"], "encoding": encoding})

    image_path4 = f"pic/phoebe.jpg"  # Đường dẫn đến hình ảnh của mỗi người
    image = face_recognition.load_image_file(image_path4)
    encoding = face_recognition.face_encodings(image)[0]  # Lưu ý: chỉ lấy mã hóa đầu tiên
    encoded_faces.append({"phoebe GT: nu": person["name"], "encoding": encoding})

    image_path5 = f"pic/rachel.jpg"  # Đường dẫn đến hình ảnh của mỗi người
    image = face_recognition.load_image_file(image_path5)
    encoding = face_recognition.face_encodings(image)[0]  # Lưu ý: chỉ lấy mã hóa đầu tiên
    encoded_faces.append({"rachel GT: nu": person["name"], "encoding": encoding})


    image_path6 = f"pic/ross.jpg"  # Đường dẫn đến hình ảnh của mỗi người
    image = face_recognition.load_image_file(image_path6)
    encoding = face_recognition.face_encodings(image)[0]  # Lưu ý: chỉ lấy mã hóa đầu tiên
    encoded_faces.append({"ross GT: nam": person["name"], "encoding": encoding})
face_count =0
# Load hình ảnh chứa nhiều khuôn mặt
image_path = "pic/test.jpg"  # Đường dẫn đến hình ảnh chứa nhiều khuôn mặt
image = face_recognition.load_image_file(image_path)
face_locations = face_recognition.face_locations(image)
face_encodings = face_recognition.face_encodings(image, face_locations)

image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Xác định người trong ảnh và hiển thị thông tin (nếu có)
for face_encoding, face_location in zip(face_encodings, face_locations):
    top, right, bottom, left = face_location
    matches = face_recognition.compare_faces([person["encoding"] for person in encoded_faces], face_encoding)

    name = "name:Unknown-info:no information available"

    if np.any(matches):
        first_match_index = np.where(matches)[0][0]
        name = list(encoded_faces[first_match_index].keys())[0]  # Thay đổi tại đây
        info = encoded_faces[first_match_index][name]
        face_count += 1
        songuoi=face_count
        print("so nguoi trong hinh:", songuoi )
    # Hiển thị thông tin người và khung nhận diện khuôn mặt
    cv2.rectangle(image_rgb, (left, top), (right, bottom), (0, 0, 255), 2)
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(image_rgb, f"{name}", (left + 6, top - 6), font, 0.5, (0, 255, 0), 1)

 # Hiển thị hình ảnh
cv2.imshow('Face Recognition',image_rgb)
cv2.waitKey(0)
cv2.destroyAllWindows()
