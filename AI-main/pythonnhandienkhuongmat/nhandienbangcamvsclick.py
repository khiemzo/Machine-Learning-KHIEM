import cv2
from gui_buttons import Buttons
import numpy as np
import face_recognition as fr
import os
from collections import defaultdict

#['person', 'bicycle', 'car', 'motorbike', 'aeroplane', 'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'sofa', 'pottedplant', 'bed', 'diningtable', 'toilet', 'tvmonitor', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush']


button = Buttons()
button.add_button("person", 20, 20)
button.add_button("cell phone", 20, 100)
button.add_button("keyboard", 20, 180)
button.add_button("cat", 20, 260)
button.add_button("dog", 20, 340)
#Khởi tạo một đối tượng của lớp Buttons và thêm các nút vào đối tượng đó với tên và vị trí tương ứng.

colors = button.colors
#Lấy danh sách màu sắc của các nút từ đối tượng Buttons.

net = cv2.dnn.readNet("dnn_model/yolov4-tiny.weights", "dnn_model/yolov4-tiny.cfg")
model = cv2.dnn_DetectionModel(net)
model.setInputParams(size=(320, 320), scale=1/255)
#Sử dụng OpenCV DNN để đọc mô hình YOLOv4 Tiny và cài đặt các tham số cho mô hình.

classes = []
with open("dnn_model/classes.txt", "r") as file_object:
    for class_name in file_object.readlines():
        class_name = class_name.strip()
        classes.append(class_name)
#Đọc danh sách các lớp đối tượng từ file văn bản và lưu vào danh sách classes.

print("Objects list")
print(classes)
#In ra danh sách các lớp đối tượng.


cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
# FULL HD 1920 x 1080
#Khởi tạo và cấu hình video capture từ webcam với độ phân giải 1280x720.

def click_button(event, x, y, flags, params):
    global button_person
    if event == cv2.EVENT_LBUTTONDOWN:
        button.button_click(x, y)
#Định nghĩa hàm xử lý sự kiện khi người dùng nhấp chuột
#Nếu nhấp chuột vào một nút, thực hiện hàm button_click để xử lý sự kiện.

cv2.namedWindow("Frame")
cv2.setMouseCallback("Frame", click_button)
#Tạo một cửa sổ hiển thị hình ảnh và thiết lập hàm xử lý sự kiện chuột.

while True:
    ret, frame = cap.read()
    #Đọc khung hình từ webcam.

    frame = cv2.flip(frame, 1)
    #Đảo ngược ảnh.

    active_buttons = button.active_buttons_list()
    #Lấy danh sách các nút đang được kích hoạt.

    (class_ids, scores, bboxes) = model.detect(frame, confThreshold=0.3, nmsThreshold=0.2)
    #Sử dụng mô hình để nhận diện đối tượng trong khung hình.

    for class_id, score, bbox in zip(class_ids, scores, bboxes):
        (x, y, w, h) = bbox
        class_name = classes[class_id]
        color = colors[class_id]

        if class_name in active_buttons:
            cv2.putText(frame, class_name, (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 255), 2)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
    #Mỗi đối tượng được nhận diện, vẽ hình chữ nhật và hiển thị tên đối tượng nếu nút tương ứng được kích hoạt.

    button.display_buttons(frame)
    #Hiển thị các nút lên trên khung hình.

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1)
    if key == 27:
        break
    #Hiển thị khung hình và thoát khỏi vòng lặp nếu người dùng nhấn phím ESC.

cap.release()
cv2.destroyAllWindows()
#Giải phóng tài nguyên và đóng cửa sổ khi chương trình kết thúc
