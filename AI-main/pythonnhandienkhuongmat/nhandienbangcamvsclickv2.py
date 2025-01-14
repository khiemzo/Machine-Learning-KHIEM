import cv2

# Opencv DNN
net = cv2.dnn.readNet("dnn_model/yolov4-tiny.weights", "dnn_model/yolov4-tiny.cfg")
model = cv2.dnn_DetectionModel(net)
model.setInputParams(size=(320, 320), scale=1/300)

# Load danh sách các loại đối tượng
classes = []
with open("dnn_model/classes.txt", "r") as file_object:
    for class_name in file_object.readlines():
        class_name = class_name.strip()
        classes.append(class_name)

print("Danh sách đối tượng")
print(classes)

# Đường dẫn tới ảnh của bạn
image_path = ("pic/nguoivsdongvat/trencan/0001.jpg")

# Đọc ảnh từ file
frame = cv2.imread(image_path)

# Chuyển ảnh sang ảnh xám
gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
gray_frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR)

# Object Detection
(class_ids, scores, bboxes) = model.detect(gray_frame, confThreshold=0.2, nmsThreshold=0.6)

# Hiển thị tất cả các classes
for class_id, score, bbox in zip(class_ids, scores, bboxes):
    (x, y, w, h) = bbox
    class_name = classes[class_id]

    cv2.putText(frame, class_name, (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 2)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

# Hiển thị kết quả
cv2.imshow("Frame", frame)
cv2.waitKey(0)
cv2.destroyAllWindows()
