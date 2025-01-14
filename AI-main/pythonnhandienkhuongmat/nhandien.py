import cv2
import dlib
from age_gender_classifier import AgeGenderClassifier  # Bạn cần cung cấp một mô hình phân loại tuổi và giới tính


def detect_faces(image_path):
    # Load ảnh
    image = cv2.imread(image_path)

    # Khởi tạo face detector từ Dlib
    detector = dlib.get_frontal_face_detector()
    faces = detector(image)

    if len(faces) == 0:
        print("Không có dữ liệu.")
        return

    # Load mô hình phân loại tuổi và giới tính
    age_gender_classifier = AgeGenderClassifier()  # Hãy thay đổi hàm này thành mô hình của bạn

    for face in faces:
        x, y, w, h = (face.left(), face.top(), face.width(), face.height())
        face_roi = image[y:y + h, x:x + w]

        # Nhận diện tuổi và giới tính
        age, gender = age_gender_classifier.predict(face_roi)

        # Hiển thị kết quả
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(image, f'Tuổi: {age}, Giới tính: {gender}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0),
                    2)

    # Hiển thị ảnh với kết quả
    cv2.imshow("Kết quả", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    detect_faces("path_to_your_image.jpg")
