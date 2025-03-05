import cv2
import numpy as np
import time
import os
import threading
import RPi.GPIO as GPIO
import tensorflow as tf
from tensorflow.keras.models import load_model
import face_recognition
import pickle
import datetime
import logging
from tensorflow.lite.python.interpreter import Interpreter

# Thiết lập logging
logging.basicConfig(filename='home_security.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Cấu hình GPIO
GPIO.setmode(GPIO.BCM)
FALL_DETECTION_PIN = 17
INTRUDER_DETECTION_PIN = 18
GPIO.setup(FALL_DETECTION_PIN, GPIO.OUT)
GPIO.setup(INTRUDER_DETECTION_PIN, GPIO.OUT)

# Đường dẫn tới các mô hình
FALL_DETECTION_MODEL = "models/fall_detection_model.tflite"
FACE_ENCODINGS_PATH = "models/known_face_encodings.pkl"

# Biến toàn cục để chia sẻ dữ liệu giữa các luồng
frame = None
frame_available = threading.Event()
program_running = True

# Tải mô hình nhận dạng té ngã (TensorFlow Lite để tối ưu hiệu suất)
def load_fall_detection_model():
    try:
        interpreter = Interpreter(model_path=FALL_DETECTION_MODEL)
        interpreter.allocate_tensors()
        logging.info("Tải mô hình phát hiện té ngã thành công")
        return interpreter
    except Exception as e:
        logging.error(f"Lỗi khi tải mô hình phát hiện té ngã: {e}")
        return None

# Tải dữ liệu khuôn mặt đã biết
def load_known_faces():
    try:
        with open(FACE_ENCODINGS_PATH, 'rb') as f:
            data = pickle.load(f)
            # data = {"encodings": [...], "names": [...], "schedule": {...}}
            logging.info("Tải dữ liệu khuôn mặt đã biết thành công")
            return data
    except Exception as e:
        logging.error(f"Lỗi khi tải dữ liệu khuôn mặt đã biết: {e}")
        return {"encodings": [], "names": [], "schedule": {}}

# Kiểm tra lịch trình của gia đình
def check_schedule(known_data):
    now = datetime.datetime.now()
    day_of_week = now.strftime("%A")
    current_time = now.strftime("%H:%M")
    
    schedule = known_data.get("schedule", {})
    day_schedule = schedule.get(day_of_week, {})
    
    for time_range, people_at_home in day_schedule.items():
        start_time, end_time = time_range.split("-")
        if start_time <= current_time <= end_time:
            return people_at_home
    
    # Mặc định, nếu không có thông tin lịch trình
    return []

# Phát hiện té ngã từ khung hình
def detect_fall(interpreter, frame):
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    # Tiền xử lý khung hình
    input_shape = input_details[0]['shape'][1:3]  # Bỏ qua batch dimension
    processed_frame = cv2.resize(frame, (input_shape[1], input_shape[0]))
    processed_frame = processed_frame.astype(np.float32) / 255.0
    processed_frame = np.expand_dims(processed_frame, axis=0)
    
    # Thực hiện dự đoán
    interpreter.set_tensor(input_details[0]['index'], processed_frame)
    interpreter.invoke()
    
    # Lấy kết quả
    output_data = interpreter.get_tensor(output_details[0]['index'])
    fall_probability = output_data[0][0]
    
    return fall_probability > 0.7  # Ngưỡng 0.7 có thể điều chỉnh

# Phát hiện hành vi đáng ngờ
def detect_suspicious_behavior(frame, person_locations):
    suspicious_score = 0
    
    for (top, right, bottom, left) in person_locations:
        person_roi = frame[top:bottom, left:right]
        
        # Phát hiện che mặt (kiểm tra vùng mặt có bị che khuất)
        face_area = person_roi[0:int((bottom-top)*0.3), :]
        face_hsv = cv2.cvtColor(face_area, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(face_hsv, (0, 0, 0), (180, 255, 100))  # Phát hiện vùng tối/che khuất
        covered_ratio = np.sum(mask > 0) / (face_area.shape[0] * face_area.shape[1])
        
        if covered_ratio > 0.7:  # Nếu > 70% khuôn mặt bị che
            suspicious_score += 3
        
        # Phát hiện di chuyển lén lút (sử dụng HOG để phân tích dáng đi)
        # Đây là phân tích đơn giản, trong thực tế cần sử dụng mô hình phức tạp hơn
        hog = cv2.HOGDescriptor()
        h_features = hog.compute(cv2.resize(person_roi, (64, 128)))
        
        # Giả lập phân tích dáng đi lén lút (cần thay thế bằng mô hình thực tế)
        if np.mean(h_features) < 0.1:  # Ngưỡng giả định
            suspicious_score += 2
    
    return suspicious_score > 3  # Ngưỡng tổng điểm đáng ngờ

# Luồng lấy hình ảnh từ camera
def camera_thread():
    global frame, program_running
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logging.error("Không thể mở camera")
        program_running = False
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    while program_running:
        ret, captured_frame = cap.read()
        if not ret:
            logging.error("Không thể đọc khung hình từ camera")
            time.sleep(1)
            continue
        
        # Cập nhật khung hình toàn cục
        frame = captured_frame.copy()
        frame_available.set()  # Báo hiệu có khung hình mới
        time.sleep(0.1)  # Giảm tải cho CPU
    
    cap.release()

# Luồng phát hiện té ngã
def fall_detection_thread():
    global frame, program_running
    
    # Tải mô hình
    fall_model = load_fall_detection_model()
    if fall_model is None:
        logging.error("Không thể tải mô hình phát hiện té ngã, dừng luồng")
        return
    
    while program_running:
        if frame_available.wait(1):  # Đợi khung hình mới, timeout 1 giây
            local_frame = frame.copy()
            frame_available.clear()
            
            # Phát hiện té ngã
            fall_detected = detect_fall(fall_model, local_frame)
            
            if fall_detected:
                logging.info("Phát hiện té ngã!")
                GPIO.output(FALL_DETECTION_PIN, GPIO.HIGH)
                time.sleep(2)  # Giữ tín hiệu trong 2 giây
                GPIO.output(FALL_DETECTION_PIN, GPIO.LOW)
            
            time.sleep(0.5)  # Giảm tải CPU

# Luồng phát hiện ăn trộm
def intruder_detection_thread():
    global frame, program_running
    
    # Tải dữ liệu khuôn mặt đã biết
    known_data = load_known_faces()
    if not known_data["encodings"]:
        logging.warning("Không có dữ liệu khuôn mặt đã biết, hệ thống sẽ coi tất cả người lạ là đáng ngờ")
    
    while program_running:
        if frame_available.wait(1):  # Đợi khung hình mới, timeout 1 giây
            local_frame = frame.copy()
            frame_available.clear()
            
            # Giảm kích thước khung hình để tăng tốc xử lý
            small_frame = cv2.resize(local_frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Tìm tất cả khuôn mặt trong khung hình
            face_locations = face_recognition.face_locations(rgb_small_frame)
            
            if face_locations:
                # Mã hóa khuôn mặt đã tìm thấy
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                
                # Kiểm tra xem có phải là người trong gia đình
                family_member_detected = False
                
                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(known_data["encodings"], face_encoding)
                    
                    if True in matches:
                        family_member_detected = True
                        match_index = matches.index(True)
                        name = known_data["names"][match_index]
                        logging.info(f"Phát hiện thành viên gia đình: {name}")
                        break
                
                # Kiểm tra lịch trình gia đình và hành vi đáng ngờ nếu không phải là thành viên gia đình
                expected_people = check_schedule(known_data)
                person_locations = [(top*4, right*4, bottom*4, left*4) for (top, right, bottom, left) in face_locations]
                
                intruder_detected = False
                
                if not family_member_detected:
                    # Không phải thành viên gia đình, kiểm tra thêm
                    logging.info("Phát hiện người lạ, đang kiểm tra hành vi")
                    
                    # Kiểm tra lịch trình - nếu không ai dự kiến có mặt
                    if not expected_people:
                        logging.info("Không ai dự kiến có mặt tại thời điểm này")
                        intruder_detected = True
                    
                    # Kiểm tra hành vi đáng ngờ
                    suspicious_behavior = detect_suspicious_behavior(local_frame, person_locations)
                    if suspicious_behavior:
                        logging.info("Phát hiện hành vi đáng ngờ")
                        intruder_detected = True
                
                if intruder_detected:
                    logging.warning("CẢNH BÁO: Phát hiện ăn trộm!")
                    GPIO.output(INTRUDER_DETECTION_PIN, GPIO.HIGH)
                    time.sleep(2)  # Giữ tín hiệu trong 2 giây
                    GPIO.output(INTRUDER_DETECTION_PIN, GPIO.LOW)
            
            time.sleep(1)  # Giảm tải CPU - phát hiện ăn trộm không cần quá nhanh

# Hàm chính
def main():
    global program_running
    
    try:
        # Tạo và khởi động các luồng
        camera_thread_obj = threading.Thread(target=camera_thread)
        fall_thread_obj = threading.Thread(target=fall_detection_thread)
        intruder_thread_obj = threading.Thread(target=intruder_detection_thread)
        
        camera_thread_obj.daemon = True
        fall_thread_obj.daemon = True
        intruder_thread_obj.daemon = True
        
        camera_thread_obj.start()
        logging.info("Luồng camera đã khởi động")
        
        time.sleep(2)  # Đợi camera khởi động
        
        fall_thread_obj.start()
        logging.info("Luồng phát hiện té ngã đã khởi động")
        
        intruder_thread_obj.start()
        logging.info("Luồng phát hiện ăn trộm đã khởi động")
        
        # Vòng lặp chính
        logging.info("Hệ thống đang chạy. Nhấn Ctrl+C để thoát.")
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        logging.info("Đã nhận lệnh thoát chương trình")
    except Exception as e:
        logging.error(f"Lỗi không mong muốn: {e}")
    finally:
        # Dọn dẹp
        program_running = False
        GPIO.output(FALL_DETECTION_PIN, GPIO.LOW)
        GPIO.output(INTRUDER_DETECTION_PIN, GPIO.LOW)
        GPIO.cleanup()
        logging.info("Đã dọn dẹp tài nguyên và thoát")

# Điểm vào chương trình
if __name__ == "__main__":
    main()