import cv2
import numpy as np
import face_recognition
from collections import defaultdict

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
image_path = ("pic/nguoivsdongvat/tranning/1g.jpg") # nhận diện nhiều người dùng 1q;

# Đọc ảnh từ file
frame = cv2.imread(image_path)
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

# Tạo một từ điển để lưu trữ các đối tượng theo class
detected_objects_by_class = defaultdict(list)

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
    print(f"Detected object: {class_name}, Confidence: {confidence}")

    cv2.putText(frame, class_name, (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

# ...

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
#keep = non_max_suppression(bboxes, scores, threshold=0.6)

# Hiển thị kết quả
detected_objects = len(keep)
print(f"Total detected objects: {detected_objects}")
'''

'''
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

# Hiển thị kết quả
cv2.imshow("Frame", frame)
cv2.waitKey(0)
cv2.destroyAllWindows()


