import cv2
import face_recognition
import numpy as np

# Khởi tạo danh sách thông tin người
people_data = [
    {"name": "chandler", "info": "nam"},
    {"name": "joey", "info": "nam"},
    {"name": "monica", "info": "nu"},
    {"name": "phoebe", "info": "nu"},
    {"name": "rachel", "info": "nu"},
    {"name": "ross", "info": "cam"},
]

# Load và mã hóa khuôn mặt của các người đã lưu trữ
encoded_faces = []
for person in people_data:
    image_path1 = f"pic/chandler.jpg"  # Đường dẫn đến hình ảnh của mỗi người
    image = face_recognition.load_image_file(image_path1)
    encoding = face_recognition.face_encodings(image)[0]  # Lưu ý: chỉ lấy mã hóa đầu tiên
    encoded_faces.append({"chandler": person["name"], "encoding": encoding, "nam": person["info"]})

    image_path2 = f"pic/joey.jpg"  # Đường dẫn đến hình ảnh của mỗi người
    image = face_recognition.load_image_file(image_path2)
    encoding = face_recognition.face_encodings(image)[0]  # Lưu ý: chỉ lấy mã hóa đầu tiên
    encoded_faces.append({"joey": person["name"], "encoding": encoding, "nam": person["info"]})

    image_path3 = f"pic/monica.jpg"  # Đường dẫn đến hình ảnh của mỗi người
    image = face_recognition.load_image_file(image_path3)
    encoding = face_recognition.face_encodings(image)[0]  # Lưu ý: chỉ lấy mã hóa đầu tiên
    encoded_faces.append({"monica": person["name"], "encoding": encoding, "nu": person["info"]})

    image_path4 = f"pic/phoebe.jpg"  # Đường dẫn đến hình ảnh của mỗi người
    image = face_recognition.load_image_file(image_path4)
    encoding = face_recognition.face_encodings(image)[0]  # Lưu ý: chỉ lấy mã hóa đầu tiên
    encoded_faces.append({"phoebe": person["name"], "encoding": encoding, "nu": person["info"]})

    image_path5 = f"pic/rachel.jpg"  # Đường dẫn đến hình ảnh của mỗi người
    image = face_recognition.load_image_file(image_path5)
    encoding = face_recognition.face_encodings(image)[0]  # Lưu ý: chỉ lấy mã hóa đầu tiên
    encoded_faces.append({"rachel": person["name"], "encoding": encoding, "nu": person["info"]})


    image_path6 = f"pic/ross.jpg"  # Đường dẫn đến hình ảnh của mỗi người
    image = face_recognition.load_image_file(image_path6)
    encoding = face_recognition.face_encodings(image)[0]  # Lưu ý: chỉ lấy mã hóa đầu tiên
    encoded_faces.append({"ross": person["name"], "encoding": encoding, "nam": person["info"]})

# Load hình ảnh chứa nhiều khuôn mặt
image_path = "pic/test.jpg"  # Đường dẫn đến hình ảnh chứa nhiều khuôn mặt
image = face_recognition.load_image_file(image_path)
face_locations = face_recognition.face_locations(image)
face_encodings = face_recognition.face_encodings(image, face_locations)

# Xác định người trong ảnh và hiển thị thông tin (nếu có)
for face_encoding, face_location in zip(face_encodings, face_locations):
    top, right, bottom, left = face_location
    matches = face_recognition.compare_faces([person["encoding"] for person in encoded_faces], face_encoding)

    name = "Unknown"
    info = "No information available"

    if np.any(matches):
        first_match_index = np.where(matches)[0][0]
        name = list(encoded_faces[first_match_index].keys())[0]  # Thay đổi tại đây
        info = encoded_faces[first_match_index][name]

    # Hiển thị thông tin người và khung nhận diện khuôn mặt
    cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(image, f"{name} - {info}", (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

# Hiển thị hình ảnh
cv2.imshow('Face Recognition', image)
cv2.waitKey(0)
cv2.destroyAllWindows()