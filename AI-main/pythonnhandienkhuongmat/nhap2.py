import cv2
import face_recognition
import os
# Hàm tải và chuyển đổi ảnh sang RGB
def load_and_convert_image(file_path):
    img = face_recognition.load_image_file(file_path)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#hức năng này tải và chuyển đổi hình ảnh từ đường dẫn file_path thành định dạng RGB.
def equalize_histogram(image):
    # Chuyển ảnh sang ảnh grayscale (nếu cần)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Cân bằng ánh sáng
    equalized = cv2.equalizeHist(gray)
    return equalized
#Chức năng này thực hiện cân bằng lược đồ màu của ảnh.
def convert_color(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray
#Chức năng này chuyển đổi ảnh sang ảnh grayscale.
def smooth_image(image):
    smoothed = cv2.GaussianBlur(image, (5, 5), 0)
    return smoothed
#Chức năng này sử dụng bộ lọc Gaussian để làm mờ ảnh.
def resize_image(image, width, height):
    resized = cv2.resize(image, (width, height))
    return resized
#Chức năng này thay đổi kích thước của ảnh.
def denoise_image(image):
    denoised = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
    return denoised
#Chức năng này sử dụng thuật toán Fast Non-Local Means Denoising để loại bỏ nhiễu từ ảnh màu.
def locate_and_encode_faces(image):
    # Tìm vị trí khuôn mặt
    faceloc = face_recognition.face_locations(image)[0]
    encode = face_recognition.face_encodings(image)[0]
    return faceloc, encode

def main():
    imgElon = load_and_convert_image("pic/hinhhoang/z4694982129982_6eaf8c6814011246437fcc99b17f57ad.jpg")


    imgCheck = load_and_convert_image("pic/nhan.jpg")


    facelocElon, encodeElon = locate_and_encode_faces(imgElon)
    facelocCheck, encodeCheck = locate_and_encode_faces(imgCheck)

    # So sánh khuôn mặt
    results = face_recognition.compare_faces([encodeElon], encodeCheck)
    faceDis = face_recognition.face_distance([encodeElon], encodeCheck)

    # Vẽ khung
    cv2.rectangle(imgElon, (facelocElon[3], facelocElon[0]), (facelocElon[1], facelocElon[2]), (255, 0, 255), 2)
    cv2.rectangle(imgCheck, (facelocCheck[3], facelocCheck[0]), (facelocCheck[1], facelocCheck[2]), (255, 0, 255), 2)

    # Hiển thị kết quả
    cv2.putText(imgCheck, f"Match: {results[0]} ({round(faceDis[0], 2)})", (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Elon", imgElon)
    cv2.imshow("ElonCheck", imgCheck)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()