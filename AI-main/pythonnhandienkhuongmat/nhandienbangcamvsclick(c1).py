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
button.add_button("remote", 20, 260)
button.add_button("cat", 20, 340)
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

        # Nhận diện khuôn mặt khi nhấp chuột vào nút "person"
        if "person" in button.active_buttons_list():
            # Gọi hàm nhận diện khuôn mặt từ chương trình 2
            detected_names, detected_faces = detect_faces_in_image(frame)

            # Hiển thị kết quả lên video
            for name, (top, right, bottom, left) in zip(detected_names, detected_faces):
                draw_name_frame(frame, top, right, bottom, left, name)
