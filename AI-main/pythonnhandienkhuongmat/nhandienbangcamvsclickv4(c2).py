import face_recognition as fr
import cv2
import numpy as np
import os
from collections import defaultdict
'''
    face_recognition: Đây là một thư viện để nhận dạng khuôn mặt. 
Nó cung cấp các chức năng nhận diện khuôn mặt và mã hóa khuôn mặt.
    cv2: Đây là thư viện OpenCV, là một thư viện thị giác máy tính phổ biến.
Nó được sử dụng cho các tác vụ xử lý hình ảnh và video.
    numpy: Thư viện này cung cấp hỗ trợ cho các mảng và hàm toán học, 
thường được sử dụng trong các tác vụ xử lý hình ảnh.
    os: Thư viện này cung cấp một cách để tương tác với hệ điều hành, 
chẳng hạn như đọc các tệp từ đĩa.
    defaultdict: Đây là một lớp từ mô-đun cung cấp một đối tượng 
giống như từ điển với giá trị mặc định cho các khóa bị thiếu.collections
'''
# Hàm vẽ tên và khung khuôn mặt,Xác định một hàm để vẽ khung xung quanh khuôn mặt có tên:
def draw_name_frame(frame, top, right, bottom, left, name):
    #Hàm draw_name_frame bạn đang sử dụng trong chương trình của mình được thiết kế để vẽ khung và hiển thị tên của người được nhận diện trên ảnh.
    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
    cv2.rectangle(frame, (left, bottom - 15), (right, bottom), (0, 0, 255), cv2.FILLED)
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
'''
Chức năng này lấy hình ảnh đầu vào và tọa độ của khuôn mặt được phát hiện, 
cùng với tệp .frame(top, right, bottom, left)name
Sau đó, nó vẽ một hình chữ nhật màu đỏ xung quanh khuôn mặt, với tên hiển thị bên dưới nó.
'''
# Define thông tin của các người cần nhận diện,Xác định danh sách dữ liệu của mọi người (tên và đường dẫn hình ảnh):
people_data = [
    {"name": "Khiem", "image_path": "pic/hinhkhiem/z4700043387622_da39bf2c4f39c337a5bb0061d643a6f4.jpg"},
    {"name": "Hoang", "image_path": "pic/hinhhoang/z4694981970053_60b82639be2acda236a5afaf6397b3ff.jpg"},
]
#Danh sách này chứa từ điển,
# mỗi từ điển đại diện cho một người với tên của họ và đường dẫn đến tệp hình ảnh của họ.

#Khởi tạo danh sách để lưu trữ các tên đã biết và mã hóa khuôn mặt tương ứng của chúng:
known_names = []
known_name_encodings = []

for person in people_data:
    name = person["name"]
    encoding = fr.face_encodings(fr.load_image_file(person["image_path"]))[0]
    known_name_encodings.append(encoding)
    #Dòng này thêm mã hóa khuôn mặt của người đó vào danh sách known_name_encodings.
    known_names.append(name)
    #Dòng này thêm tên của người đó vào danh sách known_names.
'''
Vòng lặp này lặp lại trên mỗi người trong .people_data
Đối với mỗi người, nó tải hình ảnh của họ, 
tính toán mã hóa khuôn mặt và thêm tên và mã hóa vào danh sách tương ứng.
'''

# Tải ảnh test
test_image_path = "pic/nguoivsdongvat/tranning/0051.jpg"
frame = cv2.imread(test_image_path)

#Sử dụng face_recognition để tìm vị trí khuôn mặt và mã hóa trong hình ảnh thử nghiệm:
# Nhận diện khuôn mặt trong ảnh test, fr.face_locations(frame) Tìm vị trí của các khuôn mặt trong hình ảnh.
face_locations = fr.face_locations(frame)
#fr.face_locations() tìm kiếm vị trí của các khuôn mặt trong hình ảnh.
face_encodings = fr.face_encodings(frame, face_locations)
#mã hóa các khuôn mặt đã tìm thấy thành một vectơ đặc trưng. Mỗi vectơ đặc trưng tương ứng với một khuôn mặt.
#fr.face_encodings(frame, face_locations) tính toán mã hóa khuôn mặt cho các khuôn mặt được phát hiện.

THRESHOLD = 0.4  # Giá trị ngưỡng (có thể điều chỉnh),Điều này đặt ra một ngưỡng cho nhận dạng khuôn mặt.
# Ngưỡng càng thấp, tiêu chí phù hợp càng khắt khe.

# Khởi tạo danh sách để lưu trữ tên và tọa độ khuôn mặt đã phát hiện:
detected_names = []
detected_faces = []
# Danh sách tọa độ các khuôn mặt đã nhận diện
# Tạo một từ điển để lưu trữ các đối tượng theo class
detected_objects_by_class = defaultdict(list)

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
    draw_name_frame(frame, top, right, bottom, left, name)
    detected_faces.append((top, right, bottom, left))  # Lưu tọa độ khuôn mặt

# Opencv DNN
net = cv2.dnn.readNet("dnn_model/yolov4-tiny.weights", "dnn_model/yolov4-tiny.cfg")
#đọc mô hình YOLO đã được huấn luyện
model = cv2.dnn_DetectionModel(net)
#tạo ra một thể hiện của lớp, Lớp này cung cấp giao diện lập trình ứng dụng (API) để thực hiện nhận diện đối tượng sử dụng các mô hình đã được huấn luyện
model.setInputParams(size=(320, 320), scale=1/300)
#Phương thức này được sử dụng để thiết lập các tham số đầu vào cho mô hình
#size=(604, 604): Kích thước của hình ảnh đầu
#scale=1/300: Các giá trị pixel của hình ảnh được chia cho 300. Đây là một thực hành phổ biến để chuẩn hóa giá trị pixel trước khi đưa vào mô hình học sâu

# Load danh sách các loại đối tượng
classes = []
# Danh sách trống tên là CLASSES
with open("dnn_model/classes.txt", "r") as file_object:
    for class_name in file_object.readlines():
    # Vòng lặp này đi qua từng dòng trong tệp tin. Mỗi dòng trong tệp tin classes.txt tương ứng với một loại đối tượng.
        class_name = class_name.strip()
        #Mỗi dòng được loại bỏ khoảng trắng và ký tự xuống dòng ở hai bên (nếu có) bằng cách sử dụng phương thức strip()
        classes.append(class_name)

print("Danh sách đối tượng")
print(classes)

# Đường dẫn tới ảnh của bạn
#image_path = ("pic/nguoivsdongvat/tranning/1g.jpg") # nhận diện nhiều người dùng 1q;

# Đọc ảnh từ file
#frame = cv2.imread(image_path)
brightened_frame = cv2.convertScaleAbs(frame, alpha=1.5, beta=30)
#Tăng cường độ sáng (Brightness Enhancement) nhận diện rõ vật thể hơn. alpha=1.5 tăng độ sáng lên 1.5 lần, và beta=30 tăng giá trị pixel thêm 30
normalized_frame = brightened_frame / 300.0
# Chuẩn hóa về [0, 1], Chuẩn hóa và thay đổi tỷ lệ pixel
blurred_frame = cv2.GaussianBlur(frame, (5, 5), 0)
#Làm mờ hình ảnh có thể loại bỏ nhiễu,Áp dụng phép làm mờ Gaussian vào hình ảnh. (5, 5) là kích thước của kernel làm mờ (là một ma trận nhỏ) và 0 đại diện cho độ lệch chuẩn của Gaussian kernel.

# Chuyển ảnh sang ảnh xám
gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
gray_frame = cv2.equalizeHist(gray_frame)#Cân bằng histogram:cải thiện độ tương phản của hình ảnh
gray_frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR)
# Object Detection
#(class_ids, scores, bboxes) = model.detect(gray_frame, confThreshold=0.2, nmsThreshold=0.6)
# Áp dụng Non-Maximum Suppression để thực hiện quá trình loại bỏ các hộp giới hạn trùng lặp
def non_max_suppression(boxes, scores, threshold):
    #boxes: Mảng chứa các thông tin về hộp giới hạn (bounding boxes). Mỗi hàng của mảng là một hộp giới hạn,
    # với cột đầu tiên và thứ hai là tọa độ x, y của góc trái trên cùng của hộp, cột thứ ba và thứ tư là chiều rộng và chiều cao của hộp.
    #scores: Mảng chứa các điểm số tương ứng với các hộp giới hạn.
    #threshold: Ngưỡng (threshold) để quyết định liệu hai hộp giới hạn có bị loại bỏ hay không. Nếu chỉ số IoU (Intersection over Union) lớn hơn ngưỡng này, một trong hai sẽ bị loại bỏ.
    # Get coordinates of bounding boxes
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 0] + boxes[:, 2]
    y2 = boxes[:, 1] + boxes[:, 3]

    areas = (x2 - x1 + 1) * (y2 - y1 + 1)
    order = scores.argsort()[::-1]

    keep = []

    while order.size > 0:
        i = order[0]
        keep.append(i)

        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])

        w = np.maximum(0.0, xx2 - xx1 + 1)
        h = np.maximum(0.0, yy2 - yy1 + 1)

        intersection = w * h

        iou = intersection / (areas[i] + areas[order[1:]] - intersection)

        inds = np.where(iou <= threshold)[0]
        order = order[inds + 1]

    return keep
combined_frame = cv2.addWeighted(gray_frame, 0.5, blurred_frame, 0.5,   0)
#combined_frame1 = 0.5 * combined_frame + 0.5 * brightened_frame

# Sử dụng NMS trên kết quả object detection

class_ids, scores, bboxes = model.detect( combined_frame , confThreshold=0.2, nmsThreshold=0.6)

# Chọn ra các bounding box sau khi áp dụng NMS
keep = non_max_suppression(bboxes, scores, threshold=0.6)

# Hiển thị kết quả
# Hiển thị kết quả
'''
for idx in keep:
    (x, y, w, h) = bboxes[idx]
    class_name = classes[class_ids[idx]]
    confidence = scores[idx]

    cv2.putText(frame, class_name, (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
'''

# Hiển thị kết quả
for idx in keep:
    (x, y, w, h) = bboxes[idx]
    class_name = classes[class_ids[idx]]
    confidence = scores[idx]

    detected_objects_by_class[class_name].append((x, y, w, h))

    # Print the information
   # print(f"Detected object: {class_name}, Confidence: {confidence}")

    cv2.putText(frame, class_name, (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)


# Số lượng khuôn mặt được nhận diện trong ảnh
num_faces = len(face_locations)

# Số lượng trường hợp của lớp "person"
num_people = len(detected_objects_by_class.get('person', []))

# So sánh số lượng khuôn mặt và số lượng trường hợp của lớp "person"
if num_faces > num_people:
    print(f"Số lượng người nhận diện: {num_faces}")
    # In ra tọa độ các khuôn mặt
    print("Tọa độ các khuôn mặt:")
    for i, (top, right, bottom, left) in enumerate(set(detected_faces)):
        print(f"Khuôn mặt {i + 1}: Top: {top}, Right: {right}, Bottom: {bottom}, Left: {left}")
else:
    print(f"Số lượng người nhận diện: {num_people}")
    detected_objects = {}

    def detect_object(obj):
        # Assume obj has a unique_id and other attributes
        unique_id = obj.unique_id
        if unique_id in detected_objects:
            print("Object is a duplicate")
        else:
            detected_objects[unique_id] = obj
            print("Object detected for the first time")


    # Chọn ra các bounding box sau khi áp dụng NMS
    # keep = non_max_suppression(bboxes, scores, threshold=0.6)

    # Hiển thị kết quả
    detected_objects = len(keep)
    print(f"Total detected objects: {detected_objects}")

    # Hiển thị kết quả
    for idx in keep:
        (x, y, w, h) = bboxes[idx]
        class_name = classes[class_ids[idx]]

        cv2.putText(frame, class_name, (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # In ra từng nhóm Detected object riêng
    for class_name, objects in detected_objects_by_class.items():
        print(f"Detected objects of class '{class_name}':")
        for obj in objects:
            print(f"  Bounding Box: {obj}")

# In ra số lượng người đã nhận diện
#print(f"Số người đã nhận diện: {num_faces}")
#for name in set(detected_names):
#    print(name)

  # In ra từng nhóm Detected object riêng
for class_name, objects in detected_objects_by_class.items():
    if class_name != 'person':
        print(f"Detected objects of class '{class_name}':")
        for obj in objects:
            print(f"  Bounding Box: {obj}")




# Đếm số lượng người và số lượng người khác
total_people = len(detected_names)
#Đếm số lượng người được nhận diện trong ảnh. detected_names là danh sách chứa tên của các người được nhận diện.
total_other_people = detected_names.count("Người khác")
#Đếm số lượng người được ghi nhận là "Người khác". Điều này đang định nghĩa rằng họ không được nhận diện là một trong các người đã biết.
total_known_people = total_people - total_other_people
#Tính toán số người đã biết bằng cách trừ đi số người không biết từ tổng số người được nhận diện.
# Hiển thị kết quả
cv2.imshow("Result", frame)
# Hiển thị hình ảnh đã được xử lý với các khung và tên đã được vẽ lên.
#cv2.imwrite("output.jpg", frame)
# Lưu hình ảnh đã xử lý thành tệp "output.jpg".
#cv2.waitKey(0)
#Chờ đợi cho đến khi người dùng bấm một phím bất kỳ (0).
#cv2.destroyAllWindows()
#Đóng tất cả các cửa sổ hiển thị hình ảnh.
# In ra số lượng người đã nhận diện
print(f"Số người đã nhận diện: {total_people}")
for name in set(detected_names):
    print(name)
print(f"Số người đã biết: {total_other_people}")
print(f"Số người không biết: {total_known_people}")


# Hiển thị kết quả
cv2.imshow("Frame", frame)
cv2.waitKey(0)
cv2.destroyAllWindows()


