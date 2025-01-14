# vesion2 là bản nâng cấp của vesion1
import cv2
import face_recognition
import numpy as np

# Khởi tạo danh sách thông tin người
people_data = [
    {"name": "chandler1","encoding": "encoding", "info": "nam"},
    {"name": "joey","encoding": "encoding", "info": "nam"},
    {"name": "monica","encoding": "encoding", "info": "nu"},
    {"name": "phoebe","encoding": "encoding", "info": "nu"},
    {"name": "rachel","encoding": "encoding", "info": "nu"},
    {"name": "ross","encoding": "encoding", "info": "nam"},
]
#people_data: Danh sách thông tin về người bao gồm tên và thông tin giới tính.

# Load và mã hóa khuôn mặt của các người đã lưu trữ
encoded_faces = []
for person in people_data:
    image_path1 = f"pic/chandler.jpg"  # Đường dẫn đến hình ảnh của mỗi người
    image = face_recognition.load_image_file(image_path1)
    encoding = face_recognition.face_encodings(image)[0]  # Lưu ý: chỉ lấy mã hóa đầu tiên
    encoded_faces.append({"chandler": person["name"], "encoding": encoding, "nam": person["info"]})
    """
        tạo danh sách encoded_faces bằng cách lặp qua danh sách people_data, 
        tải hình ảnh của mỗi người và sau đó mã hóa khuôn mặt từ hình ảnh đó.
         Kết quả cuối cùng là danh sách các khuôn mặt đã mã hóa, 
         mỗi khuôn mặt đi kèm với tên của người tương ứng.
encoded_faces = []: Đây là một danh sách rỗng được sử dụng để lưu trữ thông tin về khuôn mặt đã mã hóa.
for person in people_data:: Đây là một vòng lặp for để duyệt qua mỗi người trong danh sách people_data.
"chandler": person["name"]: Đây là cặp key-value trong từ điển.
"chandler" là key (khóa), đây đang là một chuỗi.
person["name"] là giá trị tương ứng với key. Trong danh sách people_data, "name" đang chứa tên của người (trong trường hợp này, là "chandler").
Kết quả của phần này là một cặp key-value được thêm vào từ điển, ví dụ: {"chandler": "chandler1"}.
"encoding": encoding: Tương tự như trên, đây cũng là một cặp key-value.
"encoding" là key, đây là một chuỗi, đại diện cho thông tin mã hóa khuôn mặt.
encoding là giá trị tương ứng với key, đây là thông tin mã hóa khuôn mặt đã được tính toán từ hình ảnh.
Kết quả của phần này là một cặp key-value được thêm vào từ điển, ví dụ: {"encoding": [0.123, 0.456, ...]}.
"nam": person["info"]: Tương tự như trên, đây cũng là một cặp key-value.
"nam" là key, đây là một chuỗi.
person["info"] là giá trị tương ứng với key. Trong danh sách people_data, "info" đang chứa thông tin về giới tính của người (trong trường hợp này, là "nam").
Kết quả của phần này là một cặp key-value được thêm vào từ điển, ví dụ: {"nam": "nam"}.
Kết quả cuối cùng của toàn bộ từ điển này sẽ được thêm vào danh sách encoded_faces.
        """
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

# Load hình ảnh chứa nhiều khuôn mặt:
image_path = "pic/test.jpg"  # Đường dẫn đến hình ảnh chứa nhiều khuôn mặt
image = face_recognition.load_image_file(image_path)
face_locations = face_recognition.face_locations(image)
face_encodings = face_recognition.face_encodings(image, face_locations)

image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# chuyển hệ màu BGR sang RGB

print(encoded_faces)
'''print(encoded_faces), các thông tin về khuôn mặt, 
tên và thông tin giới tính của người sẽ được in ra màn hình.
 Điều này giúp bạn kiểm tra xem mã của bạn có thực hiện đúng chức năng hay không 
 và xem liệu danh sách encoded_faces có được cập nhật đúng cách không.
'''

# Xác định người trong ảnh và hiển thị thông tin (nếu có)
for face_encoding, face_location in zip(face_encodings, face_locations):
    top, right, bottom, left = face_location
    matches = face_recognition.compare_faces([person["encoding"] for person in encoded_faces], face_encoding)
    '''
    for face_encoding, face_location in zip(face_encodings, face_locations)::
     vd:face_encodings :1,2,3 face_locations:a,b,c ==>> zip(face_encodings, face_locations)= 1a 2b 3c
    Đây là một vòng lặp for sử dụng cùng lúc hai danh sách face_encodings và face_locations.
    face_encoding và face_location sẽ lấy giá trị tương ứng từ mỗi danh sách trong mỗi lần lặp.
    top, right, bottom, left = face_location:

    Lấy các tọa độ (top, right, bottom, left) của khuôn mặt từ face_location.
    matches = face_recognition.compare_faces([person["encoding"] for person in encoded_faces], face_encoding):

    Sử dụng face_recognition để so sánh khuôn mặt hiện tại (face_encoding) với danh sách các khuôn mặt đã được mã hóa (encoded_faces).
    face_recognition.compare_faces trả về một danh sách các kết quả so sánh (True/False), trong đó True nghĩa là có sự trùng khớp.
    '''

    name = "Unknown"
    info = "No information available"
    '''
    name = "Unknown" và info = "No information available":

    Đây là giá trị mặc định được gán cho tên và thông tin người trong trường hợp không tìm thấy trùng khớp.
    Kết quả của việc so sánh khuôn mặt sẽ được lưu trong biến matches.

    Nếu có ít nhất một trùng khớp (tức là một giá trị True trong danh sách matches), 
    bạn sẽ cập nhật lại name và info dựa trên thông tin của người tương ứng từ danh sách encoded_faces.
    '''
    if np.any(matches):
        first_match_index = np.where(matches)[0][0]
        name = list(encoded_faces[first_match_index].keys())[0]  # Thay đổi tại đây
        info = encoded_faces[first_match_index][name]
    '''
    matches có ít nhất một giá trị là True hay không. Nếu có ít nhất một trùng khớp, điều này có nghĩa là có ít nhất một khuôn mặt trong encoded_faces tương ứng với khuôn mặt hiện tại.

np.any(matches): np ở đây là viết tắt của numpy, một thư viện trong Python cho tính toán số học. np.any() trả về True nếu có ít nhất một giá trị True trong danh sách matches, ngược lại trả về False.
Nếu có ít nhất một trùng khớp, dòng tiếp theo sẽ được thực hiện:

first_match_index = np.where(matches)[0][0]: Dòng này sử dụng np.where() để tìm ra chỉ số của giá trị True đầu tiên trong danh sách matches. 
Điều này giúp bạn xác định vị trí đầu tiên trong danh sách encoded_faces mà có trùng khớp.

name = list(encoded_faces[first_match_index].keys())[0]: Dòng này lấy tên của người từ danh sách encoded_faces.
Đầu tiên, nó lấy ra từ điển tương ứng với vị trí đầu tiên đã được xác định trong danh sách encoded_faces. 
Tiếp theo, nó chuyển đổi từ điển này thành một danh sách các keys, và lấy key đầu tiên (do bạn chỉ đang lưu trữ một cặp key-value trong từ điển).
 Cuối cùng, nó lấy giá trị tương ứng với key này, tức là tên của người.

info = encoded_faces[first_match_index][name]: Dòng này lấy thông tin giới tính của người từ danh sách encoded_faces tương ứng với vị trí đã xác định trước đó. name ở đây chính là tên người đã được xác định.

Kết quả cuối cùng của các dòng này là name sẽ chứa tên của người được nhận diện và info sẽ chứa thông tin giới tính của người đó.
    '''
    # Hiển thị thông tin người và khung nhận diện khuôn mặt
    cv2.rectangle(image_rgb, (left, top), (right, bottom), (0, 0, 255), 2)
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(image_rgb, f"{name} - {info}", (left + 6, top - 6), font, 0.5, (0, 255, 0), 1)
    '''
    cv2.rectangle(image_rgb, (left, top), (right, bottom), (0, 0, 255), 2):

cv2.rectangle: Hàm này được sử dụng để vẽ một hình chữ nhật.
image_rgb: Đây là hình ảnh được chuyển đổi sang không gian màu RGB.
(left, top): Tọa độ góc trên bên trái của hình chữ nhật (x,y).
(right, bottom): Tọa độ góc dưới bên phải của hình chữ nhật (x,y).
(0, 0, 255): Đây là màu sắc của khung (trong không gian màu BGR, màu đỏ được đặt lên max, các kênh còn lại là 0).
2: Đây là độ dày của đường viền của hình chữ nhật.
font = cv2.FONT_HERSHEY_DUPLEX:

cv2.FONT_HERSHEY_DUPLEX: Đây là kiểu font được sử dụng cho việc vẽ chữ lên ảnh.
cv2.putText(image_rgb, f"{name} - {info}", (left + 6, top - 6), font, 0.5, (0, 255, 0), 1):

cv2.putText: Hàm này được sử dụng để thêm văn bản lên hình ảnh.
image_rgb: Đây là hình ảnh được chuyển đổi sang không gian màu RGB.
f"{name} - {info}": Đây là văn bản bạn muốn thêm lên ảnh. Nó bao gồm cả tên và thông tin của người đã nhận diện.
(left + 6, top - 6): Đây là tọa độ của góc trên bên trái của văn bản trên hình ảnh (x, y).
font: Kiểu font được sử dụng.
0.5: Kích thước của font.
(0, 255, 0): Màu sắc của văn bản (trong không gian màu BGR, màu xanh lục được đặt lên max, các kênh còn lại là 0).
1: Độ dày của viền chữ.
Tổng cộng, dòng code này vẽ một hình chữ nhật xung quanh khuôn mặt và thêm tên và thông tin của người đã nhận diện lên hình ảnh.
    '''
 # Hiển thị hình ảnh
cv2.imshow('Face Recognition',image_rgb)
cv2.waitKey(0)
cv2.destroyAllWindows()
'''
cv2.imshow('Face Recognition', image_rgb):

cv2.imshow: Hàm này hiển thị hình ảnh lên một cửa sổ.
'Face Recognition': Đây là tiêu đề của cửa sổ hiển thị. Trong trường hợp này, nó sẽ là "Face Recognition".
image_rgb: Đây là hình ảnh đã được xử lý, trong không gian màu RGB.
cv2.waitKey(0):

cv2.waitKey: Hàm này chờ một sự kiện xảy ra trong cửa sổ hiển thị.
0: Đây là thời gian chờ (trong mili giây). Trong trường hợp này, cửa sổ sẽ chờ đến khi bất kỳ phím nào trên bàn phím được nhấn.
cv2.destroyAllWindows():

cv2.destroyAllWindows: Hàm này đóng tất cả các cửa sổ đã mở bởi OpenCV.
'''