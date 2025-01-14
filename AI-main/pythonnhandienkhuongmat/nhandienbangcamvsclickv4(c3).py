import face_recognition as fr
import cv2
import numpy as np
import os
from collections import defaultdict

def draw_name_frame(frame, top, right, bottom, left, name):
    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
    cv2.rectangle(frame, (left, bottom - 30), (right, bottom), (0, 0, 255), cv2.FILLED)
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

people_data = [
    {"name": "Khiem", "image_path": "pic/hinhkhiem/0001.jpg"},
    {"name": "Hoang", "image_path": "pic/hinhhoang/0001.jpg"},
]
known_names = []
known_name_encodings = []

for person in people_data:
    name = person["name"]
    encoding = fr.face_encodings(fr.load_image_file(person["image_path"]))[0]
    known_name_encodings.append(encoding)
    known_names.append(name)

test_image_path = "pic/nguoivsdongvat/tranning/0067a.jpg"#0099, 0056,0067,1q,0008,0067a
frame = cv2.imread(test_image_path)

face_locations = fr.face_locations(frame)
face_encodings = fr.face_encodings(frame, face_locations)

THRESHOLD = 0.4
detected_names = []
detected_faces = []
detected_objects_by_class = defaultdict(list)
for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
    matches = fr.compare_faces(known_name_encodings, face_encoding, tolerance=THRESHOLD)
    name = "nguoi khac"

    for i, match in enumerate(matches):
        if match:
            name = known_names[i]
            break
    detected_names.append(name)
    draw_name_frame(frame, top, right, bottom, left, name)
    detected_faces.append((top, right, bottom, left))  # Lưu tọa độ khuôn mặt

net = cv2.dnn.readNet("dnn_model/yolov4-tiny.weights", "dnn_model/yolov4-tiny.cfg")
model = cv2.dnn_DetectionModel(net)
model.setInputParams(size=(320, 320), scale=1/300)

classes = []
with open("dnn_model/classes.txt", "r") as file_object:
    for class_name in file_object.readlines():
        class_name = class_name.strip()
        classes.append(class_name)

print("Danh sách đối tượng")
print(classes)

brightened_frame = cv2.convertScaleAbs(frame, alpha=1.5, beta=30)
normalized_frame = brightened_frame / 300.0
blurred_frame = cv2.GaussianBlur(frame, (5, 5), 0)

gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
gray_frame = cv2.equalizeHist(gray_frame)
gray_frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR)

def non_max_suppression(boxes, scores, threshold):
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
class_ids, scores, bboxes = model.detect( combined_frame , confThreshold=0.2, nmsThreshold=0.6)
keep = non_max_suppression(bboxes, scores, threshold=0.6)

for idx in keep:
    (x, y, w, h) = bboxes[idx]
    class_name = classes[class_ids[idx]]
    confidence = scores[idx]
    detected_objects_by_class[class_name].append((x, y, w, h))
    cv2.putText(frame, class_name, (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

num_faces = len(face_locations)
num_people = len(detected_objects_by_class.get('person', []))
if num_faces > num_people:
    print(f"Số lượng người nhận diện: {num_faces}")
    print("Tọa độ các khuôn mặt:")
    for i, (top, right, bottom, left) in enumerate(set(detected_faces)):
        print(f"Khuôn mặt {i + 1}: Top: {top}, Right: {right}, Bottom: {bottom}, Left: {left}")
    for class_name, objects in detected_objects_by_class.items():
        if class_name != 'person':
            print(f"Các đối tượng được phát hiện của class '{class_name}':")
            for obj in objects:
                print(f"  Tọa độ ảnh: {obj}")
else:
    print(f"Số lượng người nhận diện là {num_people}")
    detected_objects = {}
    def detect_object(obj):
        unique_id = obj.unique_id
        if unique_id in detected_objects:
            print("Đối tượng bị trùng lặp")
        else:
            detected_objects[unique_id] = obj
            print("Đối tượng được phát hiện lần đầu tiên")
    detected_objects = len(keep)
    print(f"Tổng số đối tượng được phát hiện: {detected_objects}")
    for idx in keep:
        (x, y, w, h) = bboxes[idx]
        class_name = classes[class_ids[idx]]
        cv2.putText(frame, class_name, (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    for class_name, objects in detected_objects_by_class.items():
        print(f"Các đối tượng được phát hiện của class '{class_name}':")
        for obj in objects:
            print(f"  Tọa độ ảnh: {obj}")

total_people = len(detected_names)
total_other_people = detected_names.count("nguoi khac")
total_known_people = total_people - total_other_people

print(f"Số người đã nhận diện: {total_people}")
for name in set(detected_names):
    print(name)
print(f"Số người đã biết: {total_known_people}")
print(f"Số người không biết: {total_other_people}")

cv2.imshow("Frame", frame)
cv2.waitKey(0)
cv2.destroyAllWindows()


