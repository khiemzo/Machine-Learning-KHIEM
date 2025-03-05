#!/usr/bin/env python3.10
import sys
sys.stdout.reconfigure(encoding='utf-8')
import cv2
import numpy as np
import mediapipe as mp
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
import threading
import time
import pickle
import os
import queue
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler


class HandSignRecognitionApp:
    def __init__(self, root):
        # Thiết lập giao diện chính
        self.root = root
        self.root.title("Nhận Diện Số Bằng Tay")
        self.root.geometry("1200x800")  # Tăng kích thước cửa sổ
        self.root.resizable(False, False)  # Ngăn không cho phép thay đổi kích thước
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Các biến trạng thái
        self.is_running = True
        self.is_detecting = True
        self.current_label = "Không nhận diện được"
        self.current_label2 = ""
        self.current_sign = None
        self.confidence = 0.0
        self.confidence2 = 0.0
        self.hand_present = False
        self.collect_data_mode = False
        self.current_sample_class = None
        self.collected_samples = 0
        self.training_data = []
        self.training_labels = []
        self.model = None
        self.scaler = None
        self.labels = {
            0: "0", 1: "1", 2: "2", 3: "3", 4: "4",
            5: "5", 6: "6", 7: "7", 8: "8", 9: "9"
        }
        self.data_collection_target = 100
        self.current_frame = None
        self.last_frame_time = cv2.getTickCount()
        # Biến để lưu trữ kết quả phát hiện bàn tay mới nhất
        self.current_hands_landmarks = []
        self.current_handedness = []
        # Biến để lưu trữ hình ảnh hiển thị ký hiệu
        self.sign_image = None
        # Thêm các biến buffer để giảm nhấp nháy
        self.frame_buffer = None
        self.sign_image_buffer = None
        self.gui_update_interval = 50  # milliseconds
        self.last_gui_update_time = 0
        # Biến để theo dõi khi thu thập mẫu
        self.last_sample_time = 0
        self.sample_feedback_active = False
        self.sample_feedback_end_time = 0
        self.sample_interval = 200  # milliseconds giữa các mẫu
        self.data_augmentation = True  # Bật tính năng tăng cường dữ liệu
        
        # Thiết lập MediaPipe
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Tùy chỉnh style vẽ
        self.custom_hand_landmark_style = self.mp_drawing_styles.get_default_hand_landmarks_style()
        self.custom_hand_connection_style = self.mp_drawing_styles.get_default_hand_connections_style()
        
        # Cấu hình MediaPipe Hands để phát hiện nhiều bàn tay
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5)

        # Khởi tạo dữ liệu huấn luyện
        self.training_data = []
        self.training_labels = []

        # Tạo cấu trúc thư mục
        os.makedirs("models", exist_ok=True)
        os.makedirs("data", exist_ok=True)

        # Thiết lập thiết bị video
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)  # Thiết lập FPS cố định
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))  # Sử dụng codec MJPG
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)  # Tăng kích thước buffer

        # Biến lưu thời gian frame cuối cho tính FPS
        self.last_frame_time = cv2.getTickCount()
        
        # Biến buffer lưu frame và sign_image
        self.frame_buffer = None
        self.sign_image_buffer = None
        
        # Tạo frame chính
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame bên trái cho camera và điều khiển
        self.left_frame = ttk.Frame(self.main_frame, width=850)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Frame camera
        self.camera_frame = ttk.Frame(self.left_frame, borderwidth=2, relief="groove")
        self.camera_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Label hiển thị camera với kích thước lớn hơn
        self.camera_label = tk.Label(self.camera_frame, bg="black")
        self.camera_label.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Frame điều khiển
        self.control_frame = ttk.Frame(self.left_frame)
        self.control_frame.pack(fill=tk.X, padx=5, pady=5)

        # Nút điều khiển
        self.toggle_btn = ttk.Button(self.control_frame, text="Tạm dừng nhận diện", command=self.toggle_detection)
        self.toggle_btn.pack(side=tk.LEFT, padx=5)

        self.train_btn = ttk.Button(self.control_frame, text="Huấn luyện mô hình", command=self.train_model)
        self.train_btn.pack(side=tk.LEFT, padx=5)

        self.collect_btn = ttk.Button(self.control_frame, text="Thu thập dữ liệu", command=self.toggle_data_collection)
        self.collect_btn.pack(side=tk.LEFT, padx=5)

        # Frame bên phải
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=5, pady=5, ipadx=10, ipady=10)

        # Frame hiển thị ký hiệu
        self.sign_frame = ttk.LabelFrame(self.right_frame, text="Hình dạng ký hiệu")
        self.sign_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Label hiển thị hình dạng tay (thay thế canvas)
        self.sign_label = tk.Label(self.sign_frame, bg="black", width=300, height=300)
        self.sign_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame hiển thị kết quả
        self.result_frame = ttk.LabelFrame(self.right_frame, text="Kết quả nhận diện")
        self.result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Label hiển thị kết quả
        self.result_label = ttk.Label(self.result_frame, text="Không nhận diện được",
                                      font=("Arial", 40, "bold"), anchor="center")
        self.result_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Label hiển thị kết quả tay thứ hai
        self.result_label2 = ttk.Label(self.result_frame, text="",
                                     font=("Arial", 40, "bold"), anchor="center")
        self.result_label2.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Label hiển thị độ tin cậy
        self.confidence_label = ttk.Label(self.result_frame, text="Độ tin cậy: 0%",
                                          font=("Arial", 14), anchor="center")
        self.confidence_label.pack(fill=tk.X, padx=5, pady=5)

        # Label hiển thị độ tin cậy tay thứ hai
        self.confidence_label2 = ttk.Label(self.result_frame, text="",
                                         font=("Arial", 14), anchor="center")
        self.confidence_label2.pack(fill=tk.X, padx=5, pady=5)

        # Hiển thị trạng thái
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, padx=10, pady=5)

        self.status_label = ttk.Label(self.status_frame, text="Sẵn sàng", anchor="w")
        self.status_label.pack(side=tk.LEFT, padx=5)

        # Frame chứa các nút số
        self.number_frame = ttk.LabelFrame(self.left_frame, text="Các ký hiệu số")
        self.number_frame.pack(fill=tk.X, padx=5, pady=5)

        # Tạo các nút số
        self.number_buttons_frame = ttk.Frame(self.number_frame)
        self.number_buttons_frame.pack(fill=tk.X, padx=5, pady=5)

        self.number_buttons = []
        for i in range(10):
            btn = ttk.Button(self.number_buttons_frame, text=str(i), width=5,
                             command=lambda num=i: self.select_sample_class(num))
            btn.grid(row=0, column=i, padx=3, pady=3)
            self.number_buttons.append(btn)

        # Frame hiển thị trạng thái thu thập dữ liệu
        self.collection_frame = ttk.Frame(self.number_frame)
        self.collection_frame.pack(fill=tk.X, padx=5, pady=5)

        self.collection_label = ttk.Label(self.collection_frame,
                                          text="Thu thập dữ liệu: Tắt", anchor="center")
        self.collection_label.pack(side=tk.LEFT, padx=5)

        self.progress = ttk.Progressbar(self.collection_frame, orient=tk.HORIZONTAL,
                                        length=400, mode='determinate')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        # Tải mô hình nếu có
        self.load_model()

        # Tạo hàng đợi để lưu trữ khung hình
        self.frame_queue = queue.Queue(maxsize=10)

        # Bắt đầu thread xử lý video
        self.video_thread = threading.Thread(target=self.process_video)
        self.video_thread.daemon = True
        self.video_thread.start()

        # Bắt đầu thread hiển thị video
        self.display_thread = threading.Thread(target=self.update_gui)
        self.display_thread.daemon = True
        self.display_thread.start()

    def load_model(self):
        """Tải mô hình đã huấn luyện nếu có"""
        try:
            model_path = "models/hand_sign_model.pkl"
            scaler_path = "models/hand_sign_scaler.pkl"

            # Nếu file mô hình đã tồn tại, thử tải lên
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                try:
                    with open(model_path, 'rb') as f:
                        self.model = pickle.load(f)

                    with open(scaler_path, 'rb') as f:
                        self.scaler = pickle.load(f)

                    print("Đã tải mô hình thành công")
                    self.set_status("Đã tải mô hình thành công")
                    return True
                except Exception as e:
                    print(f"Lỗi khi tải mô hình cũ: {e}")
                    print("Đang xóa mô hình cũ và tạo mô hình mới...")
                    
                    # Xóa các file mô hình cũ
                    try:
                        if os.path.exists(model_path):
                            os.remove(model_path)
                        if os.path.exists(scaler_path):
                            os.remove(scaler_path)
                    except Exception as err:
                        print(f"Không thể xóa file mô hình cũ: {err}")
                    
                    self.set_status("Vui lòng thu thập dữ liệu và huấn luyện lại mô hình")
                    return False
            else:
                print("Không tìm thấy mô hình, vui lòng huấn luyện mô hình trước")
                self.set_status("Không tìm thấy mô hình, vui lòng huấn luyện mô hình trước")
                return False
        except Exception as e:
            print(f"Lỗi khi tải mô hình: {e}")
            self.set_status(f"Lỗi khi tải mô hình: {e}")
            return False

    def save_model(self):
        """Lưu mô hình đã huấn luyện"""
        try:
            with open("models/hand_sign_model.pkl", 'wb') as f:
                pickle.dump(self.model, f)

            with open("models/hand_sign_scaler.pkl", 'wb') as f:
                pickle.dump(self.scaler, f)

            print("Đã lưu mô hình thành công")
            self.set_status("Đã lưu mô hình thành công")
            return True
        except Exception as e:
            print(f"Lỗi khi lưu mô hình: {e}")
            self.set_status(f"Lỗi khi lưu mô hình: {e}")
            return False

    def toggle_detection(self):
        """Bật/tắt chế độ nhận diện"""
        self.is_detecting = not self.is_detecting
        if self.is_detecting:
            self.toggle_btn.config(text="Tạm dừng nhận diện")
            self.set_status("Đã bật nhận diện")
        else:
            self.toggle_btn.config(text="Bật nhận diện")
            self.set_status("Đã tạm dừng nhận diện")

    def toggle_data_collection(self):
        """Bật/tắt chế độ thu thập dữ liệu"""
        self.collect_data_mode = not self.collect_data_mode
        self.progress['value'] = 0
        self.collected_samples = 0

        if self.collect_data_mode:
            self.collect_btn.config(text="Dừng thu thập")
            self.collection_label.config(text="Thu thập dữ liệu: Bật")
            self.set_status("Chọn một lớp dữ liệu để bắt đầu thu thập")
        else:
            self.collect_btn.config(text="Thu thập dữ liệu")
            self.collection_label.config(text="Thu thập dữ liệu: Tắt")
            self.current_sample_class = None
            self.set_status("Đã dừng thu thập dữ liệu")

    def select_sample_class(self, class_num):
        """Chọn lớp để thu thập dữ liệu"""
        if self.collect_data_mode:
            self.current_sample_class = class_num
            self.collected_samples = 0
            self.progress['value'] = 0
            self.set_status(f"Thu thập dữ liệu cho số {class_num}. Đặt tay vào khung hình.")

    def collect_sample(self, landmarks):
        """Thu thập mẫu dữ liệu từ landmark"""
        if not self.collect_data_mode or self.current_sample_class is None:
            return
            
        # Kiểm tra thời gian từ lần cuối thu thập mẫu để tránh lấy quá nhiều mẫu giống nhau
        current_time = time.time() * 1000  # Chuyển sang milliseconds
        if current_time - self.last_sample_time < self.sample_interval:
            return
            
        self.last_sample_time = current_time
        
        # Kích hoạt hiệu ứng phản hồi
        self.sample_feedback_active = True
        self.sample_feedback_end_time = current_time + 300  # Hiệu ứng kéo dài 300ms

        # Chuyển đổi landmarks thành vector
        landmarks_list = []
        for landmark in landmarks:
            landmarks_list.extend([landmark.x, landmark.y, landmark.z])

        # Thêm vào dữ liệu huấn luyện
        self.training_data.append(landmarks_list)
        self.training_labels.append(self.current_sample_class)
        
        # Nếu bật tính năng tăng cường dữ liệu, tạo thêm các biến thể
        if self.data_augmentation:
            # 1. Thêm nhiễu nhẹ vào tọa độ x, y
            noise_sample = landmarks_list.copy()
            for i in range(0, len(noise_sample), 3):  # Chỉ thêm nhiễu vào x và y, không thêm vào z
                noise_sample[i] += np.random.normal(0, 0.005)  # Nhiễu cho x
                noise_sample[i+1] += np.random.normal(0, 0.005)  # Nhiễu cho y
            self.training_data.append(noise_sample)
            self.training_labels.append(self.current_sample_class)
            
            # 2. Thêm mẫu với tỷ lệ co giãn nhẹ
            scale_sample = landmarks_list.copy()
            scale_factor = np.random.uniform(0.98, 1.02)  # Co giãn 2%
            for i in range(0, len(scale_sample), 3):
                scale_sample[i] *= scale_factor  # Co giãn x
                scale_sample[i+1] *= scale_factor  # Co giãn y
            self.training_data.append(scale_sample)
            self.training_labels.append(self.current_sample_class)

        # Cập nhật số lượng mẫu đã thu thập
        self.collected_samples += 1
        progress_value = int((self.collected_samples / self.data_collection_target) * 100)
        self.progress['value'] = progress_value

        self.set_status(
            f"Đã thu thập {self.collected_samples}/{self.data_collection_target} mẫu cho số {self.current_sample_class}")

        # Nếu đã đủ số mẫu, dừng thu thập dữ liệu cho lớp này
        if self.collected_samples >= self.data_collection_target:
            self.current_sample_class = None
            self.set_status(
                f"Đã hoàn thành thu thập dữ liệu. Chọn lớp khác hoặc huấn luyện mô hình.")

    def train_model(self):
        """Huấn luyện mô hình từ dữ liệu đã thu thập"""
        if len(self.training_data) < 10:
            self.set_status("Không đủ dữ liệu để huấn luyện. Thu thập thêm dữ liệu.")
            return

        try:
            # Thông báo bắt đầu huấn luyện
            self.set_status("Đang huấn luyện mô hình...")

            # Chuẩn hóa dữ liệu
            X = np.array(self.training_data)
            y = np.array(self.training_labels)

            # Sử dụng StandardScaler để chuẩn hóa dữ liệu
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)

            # Sử dụng RandomForestClassifier với thông số tối ưu
            from sklearn.model_selection import train_test_split
            
            # Chia dữ liệu thành tập train và test
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42, stratify=y)
            
            # Huấn luyện mô hình với thông số tối ưu
            self.model = RandomForestClassifier(
                n_estimators=150,           # Tăng số lượng cây
                max_depth=15,               # Giới hạn độ sâu để tránh overfitting
                min_samples_split=5,        # Yêu cầu ít nhất 5 mẫu để phân tách
                min_samples_leaf=2,         # Ít nhất 2 mẫu ở mỗi lá
                bootstrap=True,             # Sử dụng bootstrap sampling
                random_state=42,
                n_jobs=-1,                  # Sử dụng đa luồng
                class_weight='balanced'     # Cân bằng trọng số các lớp nếu dữ liệu không cân bằng
            )
            self.model.fit(X_train, y_train)
            
            # Đánh giá độ chính xác trên tập test
            test_accuracy = self.model.score(X_test, y_test) * 100
            
            # Lưu mô hình
            self.save_model()

            # Thông báo hoàn thành với độ chính xác
            self.set_status(f"Đã huấn luyện mô hình với {len(X)} mẫu! Độ chính xác: {test_accuracy:.2f}%")

        except Exception as e:
            self.set_status(f"Lỗi khi huấn luyện mô hình: {e}")

    def extract_hand_features(self, hand_landmarks):
        """
        Trích xuất đặc trưng từ landmark của bàn tay
        """
        # Chuyển đổi landmarks thành vector
        landmarks_list = []
        for landmark in hand_landmarks.landmark:
            landmarks_list.extend([landmark.x, landmark.y, landmark.z])
        
        return landmarks_list

    def process_video(self):
        """
        Xử lý video từ camera và thực hiện nhận diện
        """
        # Khởi tạo giá trị cho FPS
        self.last_frame_time = cv2.getTickCount()
        
        # Biến để lưu kết quả nhận diện của tay thứ hai
        self.current_label2 = ""
        self.confidence2 = 0.0
        
        # Cấu hình cho camera để giảm nhấp nháy
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.cap.set(cv2.CAP_PROP_FPS, 60)  # Tăng FPS lên cao hơn
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 5)  # Tăng buffer size
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Tạo các buffer trống cho khung hình
        camera_width = 800
        camera_height = 600
        self.frame_buffer = np.zeros((camera_height, camera_width, 3), dtype=np.uint8)
        self.sign_image_buffer = np.zeros((300, 300, 3), dtype=np.uint8)
        
        # Kiểm tra lại một lần nữa mô hình trước khi bắt đầu xử lý video
        model_valid = True
        if self.model is not None:
            try:
                # Kiểm tra mô hình bằng cách tạo dữ liệu giả và thử dự đoán
                dummy_data = np.random.rand(1, 63) # Giả sử 21 landmarks, mỗi landmark có x,y,z
                if self.scaler is not None:
                    dummy_data_scaled = self.scaler.transform(dummy_data)
                    self.model.predict(dummy_data_scaled)
                else:
                    model_valid = False
            except Exception as e:
                print(f"Lỗi với mô hình hiện tại: {e}")
                print("Đặt mô hình về None để tránh lỗi khi xử lý video")
                self.model = None
                self.scaler = None
                model_valid = False
                
                # Xóa các file mô hình cũ
                try:
                    model_path = "models/hand_sign_model.pkl"
                    scaler_path = "models/hand_sign_scaler.pkl"
                    if os.path.exists(model_path):
                        os.remove(model_path)
                    if os.path.exists(scaler_path):
                        os.remove(scaler_path)
                    print("Đã xóa các file mô hình không tương thích")
                except Exception as err:
                    print(f"Không thể xóa file mô hình cũ: {err}")
        
        if not model_valid:
            self.set_status("Mô hình không tương thích. Vui lòng thu thập dữ liệu và huấn luyện lại.")
        
        # Tạo bộ đệm hình ảnh và biến theo dõi FPS
        last_fps_update_time = time.time()
        fps_values = []
        current_fps = 0
        skip_frames = 0  # Biến để bỏ qua một số frame xử lý nặng
        
        while self.is_running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    time.sleep(0.01)  # Tạm dừng ngắn để tránh vòng lặp quá nhanh
                    continue
                
                # Tính FPS
                current_tick = cv2.getTickCount()
                fps = int(cv2.getTickFrequency() / (current_tick - self.last_frame_time))
                self.last_frame_time = current_tick
                
                # Theo dõi FPS trung bình
                fps_values.append(fps)
                if len(fps_values) > 30:  # Theo dõi 30 frame gần nhất
                    fps_values.pop(0)
                
                # Cập nhật FPS hiển thị mỗi 0.5 giây
                if time.time() - last_fps_update_time > 0.5:
                    current_fps = int(sum(fps_values) / len(fps_values))
                    last_fps_update_time = time.time()
                
                # Lật ngang khung hình để dễ nhìn hơn
                frame = cv2.flip(frame, 1)
                
                # Vẽ FPS lên khung hình
                cv2.putText(frame, f"FPS: {current_fps}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Hiệu ứng phản hồi khi thu thập mẫu
                current_time = time.time() * 1000
                if self.sample_feedback_active and current_time < self.sample_feedback_end_time:
                    # Vẽ viền xanh lá xung quanh khung hình để thông báo thu thập thành công
                    cv2.rectangle(frame, (5, 5), (frame.shape[1]-5, frame.shape[0]-5), (0, 255, 0), 5)
                    
                    # Hiển thị thông báo
                    cv2.putText(frame, "Mẫu đã thu thập!", (frame.shape[1]//2 - 120, 50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                elif current_time >= self.sample_feedback_end_time:
                    self.sample_feedback_active = False
                
                # Nếu đang ở chế độ thu thập dữ liệu, hiển thị hướng dẫn
                if self.collect_data_mode and self.current_sample_class is not None:
                    collection_text = f"Thu thập mẫu cho số {self.current_sample_class}: {self.collected_samples}/{self.data_collection_target}"
                    cv2.putText(frame, collection_text, (10, frame.shape[0]-20), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Xử lý khung hình với MediaPipe, chỉ xử lý 1 frame trong mỗi 2 frame để tăng hiệu suất
                skip_frames = (skip_frames + 1) % 2
                
                # Chỉ phát hiện tay nếu đang trong chế độ phát hiện và không bỏ qua frame hiện tại
                if self.is_detecting and skip_frames == 0:
                    # Chuyển đổi màu sắc từ BGR sang RGB
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Xử lý khung hình với MediaPipe 
                    results = self.hands.process(rgb_frame)
                    
                    # Reset kết quả khi không có tay nào được phát hiện
                    if not results.multi_hand_landmarks:
                        self.hand_present = False
                        self.current_label = "Không nhận diện được"
                        self.confidence = 0.0
                        self.current_label2 = ""
                        self.confidence2 = 0.0
                        # Xóa dữ liệu bàn tay
                        self.current_hands_landmarks = []
                        self.current_handedness = []
                        
                        # Tạo hình ảnh trống cho khung hình dạng ký hiệu
                        sign_img = np.zeros((300, 300, 3), dtype=np.uint8)
                        cv2.putText(sign_img, "Khong phat hien ban tay", (30, 150), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                        self.sign_image = sign_img.copy()
                    else:
                        self.hand_present = True
                        # Lưu trữ các landmarks và handedness cho update_gui
                        self.current_hands_landmarks = results.multi_hand_landmarks
                        self.current_handedness = results.multi_handedness if results.multi_handedness else []
                        
                        # Reset kết quả tay thứ hai nếu chỉ phát hiện một tay
                        if len(results.multi_hand_landmarks) == 1:
                            self.current_label2 = ""
                            self.confidence2 = 0.0
                        
                        # Vẽ tất cả các bàn tay phát hiện được
                        for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                            # Xác định loại tay (trái/phải) nếu có
                            hand_type = ""
                            if results.multi_handedness and len(results.multi_handedness) > hand_idx:
                                hand_type = results.multi_handedness[hand_idx].classification[0].label
                            
                            # Tìm tọa độ trung tâm bàn tay
                            hand_center_x = int(sum(landmark.x for landmark in hand_landmarks.landmark) / len(hand_landmarks.landmark) * frame.shape[1])
                            hand_center_y = int(sum(landmark.y for landmark in hand_landmarks.landmark) / len(hand_landmarks.landmark) * frame.shape[0])
                            
                            # Vẽ các điểm landmark với kích thước lớn hơn và màu sắc rõ ràng hơn
                            self.mp_drawing.draw_landmarks(
                                frame,
                                hand_landmarks,
                                self.mp_hands.HAND_CONNECTIONS,
                                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                                self.mp_drawing_styles.get_default_hand_connections_style())
                            
                            # Chỉ hiển thị nhãn "Tay 1" hoặc "Tay 2"
                            hand_label = f"Tay {hand_idx + 1}"
                            cv2.putText(frame, hand_label, (hand_center_x - 50, hand_center_y - 50), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                            
                            # Nếu đang trong chế độ nhận diện và có mô hình đã được huấn luyện
                            if self.is_detecting and self.model is not None and not self.collect_data_mode:
                                # Trích xuất và xử lý đặc trưng
                                hand_data = self.extract_hand_features(hand_landmarks)
                                
                                # Chuẩn hóa dữ liệu
                                if self.scaler is not None:
                                    try:
                                        hand_data_scaled = self.scaler.transform([hand_data])
                                        
                                        # Dự đoán
                                        prediction = self.model.predict(hand_data_scaled)
                                        proba = self.model.predict_proba(hand_data_scaled)[0]
                                        
                                        # Kiểm tra dự đoán và xác suất hợp lệ
                                        if len(proba) > prediction[0]:
                                            confidence = proba[prediction[0]]
                                            
                                            # Cập nhật kết quả dựa vào tay thứ nhất hoặc thứ hai
                                            if hand_idx == 0:
                                                self.current_label = f"{self.labels[prediction[0]]}"
                                                self.confidence = confidence
                                            elif hand_idx == 1:
                                                self.current_label2 = f"{self.labels[prediction[0]]}"
                                                self.confidence2 = confidence
                                    except Exception as e:
                                        print(f"Lỗi khi dự đoán: {e}")
                                        # Đặt giá trị mặc định nếu có lỗi
                                        if hand_idx == 0:
                                            self.current_label = "Lỗi nhận diện"
                                            self.confidence = 0.0
                                        elif hand_idx == 1:
                                            self.current_label2 = ""
                                            self.confidence2 = 0.0
                            # Nếu đang trong chế độ thu thập dữ liệu
                            elif self.collect_data_mode and self.current_sample_class is not None:
                                if self.collected_samples < self.data_collection_target:
                                    # Chỉ thu thập dữ liệu từ tay đầu tiên được phát hiện
                                    if hand_idx == 0:
                                        # Trích xuất đặc trưng và thêm vào tập dữ liệu huấn luyện
                                        self.collect_sample(hand_landmarks.landmark)
                        
                        # Tạo hình ảnh cho khung hình dạng ký hiệu
                        if self.hand_present and len(self.current_hands_landmarks) > 0:
                            # Tạo một ảnh đen làm nền với kích thước 300x300
                            sign_img = np.zeros((300, 300, 3), dtype=np.uint8)
                            
                            # Tìm vùng bao quanh tất cả các bàn tay
                            x_min_all, y_min_all = float('inf'), float('inf')
                            x_max_all, y_max_all = 0, 0
                            
                            # Tính toán vùng bao quanh chứa tất cả bàn tay
                            for hand_landmarks in self.current_hands_landmarks:
                                for landmark in hand_landmarks.landmark:
                                    x_min_all = min(x_min_all, landmark.x)
                                    y_min_all = min(y_min_all, landmark.y)
                                    x_max_all = max(x_max_all, landmark.x)
                                    y_max_all = max(y_max_all, landmark.y)
                            
                            # Thêm padding
                            padding = 0.1
                            x_min_all = max(0, x_min_all - padding)
                            y_min_all = max(0, y_min_all - padding)
                            x_max_all = min(1, x_max_all + padding)
                            y_max_all = min(1, y_max_all + padding)
                            
                            # Tính toán kích thước của vùng chứa tất cả bàn tay
                            width_all = x_max_all - x_min_all
                            height_all = y_max_all - y_min_all
                            
                            # Tính toán tỷ lệ scale để vừa khung image, thu nhỏ bàn tay lại
                            scale_x = 260 / width_all if width_all > 0 else 1.0  # Để lại margin 20px mỗi bên
                            scale_y = 260 / height_all if height_all > 0 else 1.0
                            scale = min(scale_x, scale_y) * 0.8  # Thu nhỏ thêm 20% để đảm bảo vừa khung
                            
                            # Tính offset để canh giữa
                            offset_x = (300 - width_all * scale) / 2
                            offset_y = (300 - height_all * scale) / 2
                            
                            # Vẽ tất cả các bàn tay
                            for hand_idx, hand_landmarks in enumerate(self.current_hands_landmarks):
                                # Vẽ các kết nối giữa các điểm
                                for connection in self.mp_hands.HAND_CONNECTIONS:
                                    start_idx = connection[0]
                                    end_idx = connection[1]
                                    
                                    start_point = hand_landmarks.landmark[start_idx]
                                    end_point = hand_landmarks.landmark[end_idx]
                                    
                                    # Chuyển đổi tọa độ tương đối sang tọa độ image, canh giữa
                                    start_x = int((start_point.x - x_min_all) * scale) + int(offset_x)
                                    start_y = int((start_point.y - y_min_all) * scale) + int(offset_y)
                                    end_x = int((end_point.x - x_min_all) * scale) + int(offset_x)
                                    end_y = int((end_point.y - y_min_all) * scale) + int(offset_y)
                                    
                                    # Kiểm tra tọa độ hợp lệ
                                    start_x = max(0, min(299, start_x))
                                    start_y = max(0, min(299, start_y))
                                    end_x = max(0, min(299, end_x))
                                    end_y = max(0, min(299, end_y))
                                    
                                    # Đặt màu khác nhau cho các bàn tay
                                    connection_color = (0, 255, 0) if hand_idx == 0 else (0, 200, 255)  # Xanh lá cho tay 1, vàng cho tay 2
                                    
                                    # Vẽ đường kết nối
                                    cv2.line(sign_img, (start_x, start_y), (end_x, end_y), connection_color, 2)
                                
                                # Vẽ các điểm mốc
                                for i, landmark in enumerate(hand_landmarks.landmark):
                                    # Chuyển đổi tọa độ tương đối sang tọa độ image, canh giữa
                                    x = int((landmark.x - x_min_all) * scale) + int(offset_x)
                                    y = int((landmark.y - y_min_all) * scale) + int(offset_y)
                                    
                                    # Kiểm tra tọa độ hợp lệ
                                    x = max(0, min(299, x))
                                    y = max(0, min(299, y))
                                    
                                    # Màu sắc khác nhau cho các bàn tay
                                    base_color = (255, 255, 255) if hand_idx == 0 else (200, 200, 255)  # Trắng cho tay 1, hơi tím cho tay 2
                                    tip_color = (0, 0, 255) if hand_idx == 0 else (255, 0, 0)  # Đỏ cho tay 1, xanh dương cho tay 2
                                    
                                    # Màu sắc và kích thước của điểm
                                    if i in [4, 8, 12, 16, 20]:  # Đầu ngón tay
                                        color = tip_color
                                        radius = 6
                                    else:
                                        color = base_color
                                        radius = 4
                                    
                                    # Vẽ điểm mốc
                                    cv2.circle(sign_img, (x, y), radius, color, -1)
                                
                                # Nhãn nhỏ cho tay
                                hand_center_x = int(sum(landmark.x - x_min_all for landmark in hand_landmarks.landmark) / len(hand_landmarks.landmark) * scale) + int(offset_x)
                                hand_center_y = int(sum(landmark.y - y_min_all for landmark in hand_landmarks.landmark) / len(hand_landmarks.landmark) * scale) + int(offset_y)
                                label_color = (0, 255, 0) if hand_idx == 0 else (0, 200, 255)
                                label_text = f"T{hand_idx + 1}"
                                cv2.putText(sign_img, label_text, (hand_center_x, hand_center_y), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, label_color, 1)
                            
                            # Lưu hình ảnh để hiển thị trên GUI
                            self.sign_image = sign_img.copy()
                
                # Chuyển đổi khung hình để hiển thị trên Tkinter
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Lưu vào buffer để hiển thị trong GUI
                try:
                    self.frame_buffer = frame_rgb.copy()
                    if self.sign_image is not None:
                        self.sign_image_buffer = self.sign_image.copy()
                except Exception as e:
                    print(f"Lỗi sao chép buffer: {e}")
                
            except Exception as e:
                print(f"Lỗi xử lý video: {e}")
                time.sleep(0.01)  # Tạm dừng nếu có lỗi

    def update_gui(self):
        """Cập nhật giao diện người dùng với hình ảnh từ camera"""
        try:
            # Kiểm tra nếu ứng dụng đang dừng
            if not self.is_running:
                return
                
            # Sử dụng buffer frame thay vì trực tiếp từ process_video
            if self.frame_buffer is not None:
                try:
                    # Tăng kích thước màn hình camera
                    camera_width = 800
                    camera_height = 600
                    
                    # Chuyển đổi từ numpy array sang PIL Image
                    img = Image.fromarray(self.frame_buffer)
                    
                    # Sử dụng LANCZOS để có chất lượng tốt nhất
                    img = img.resize((camera_width, camera_height), Image.LANCZOS)
                    
                    # Chuyển đổi sang ImageTk đối tượng một cách hiệu quả
                    imgtk = ImageTk.PhotoImage(image=img)
                    
                    # Cập nhật widget mà không gây ra tái vẽ lại không cần thiết
                    self.camera_label.imgtk = imgtk
                    self.camera_label.configure(image=imgtk)
                except Exception as e:
                    print(f"Lỗi hiển thị frame: {e}")
            
            # Hiển thị hình ảnh trong khung hình dạng ký hiệu
            if self.sign_image_buffer is not None:
                try:
                    sign_img = Image.fromarray(self.sign_image_buffer)
                    sign_imgtk = ImageTk.PhotoImage(image=sign_img)
                    self.sign_label.imgtk = sign_imgtk
                    self.sign_label.configure(image=sign_imgtk)
                except Exception as e:
                    print(f"Lỗi hiển thị hình ảnh ký hiệu: {e}")
            
            # Cập nhật nhãn kết quả
            self.result_label.configure(text=self.current_label)
            self.confidence_label.configure(text=f"Độ tin cậy: {self.confidence * 100:.1f}%")
            
            # Cập nhật nhãn kết quả tay thứ hai
            if self.current_label2:
                self.result_label2.configure(text=self.current_label2)
                self.confidence_label2.configure(text=f"Độ tin cậy: {self.confidence2 * 100:.1f}%")
            else:
                self.result_label2.configure(text="")
                self.confidence_label2.configure(text="")
            
            # Cập nhật trạng thái thu thập dữ liệu
            if self.collect_data_mode:
                self.collection_label.configure(
                    text=f"Thu thập dữ liệu cho số {self.current_sample_class}: {self.collected_samples}/{self.data_collection_target}")
            else:
                self.collection_label.configure(text="Thu thập dữ liệu: Tắt")
                self.progress['value'] = 0
        except Exception as e:
            print(f"Lỗi cập nhật GUI: {e}")
        finally:
            # Gọi hàm này sau một khoảng thời gian - ổn định ở 30 fps (33ms)
            self.root.after(33, self.update_gui)

    def set_status(self, message):
        """Cập nhật thông báo trạng thái"""
        self.status_label.configure(text=message)

    def on_closing(self):
        """Xử lý khi đóng ứng dụng"""
        self.is_running = False
        if self.cap.isOpened():
            self.cap.release()
        self.hands.close()
        self.root.destroy()


def main():
    # Tạo style cho Tkinter
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('clam')  

    # Thiết lập style
    style.configure("TLabel", font=("Arial", 12))
    style.configure("TButton", font=("Arial", 12))
    style.configure("TFrame", background="#f0f0f0")
    style.configure("TLabelframe", background="#f0f0f0")
    style.configure("TLabelframe.Label", font=("Arial", 12, "bold"))

    # Khởi tạo ứng dụng
    app = HandSignRecognitionApp(root)

    # Chạy vòng lặp chính
    root.mainloop()


if __name__ == "__main__":
    main()