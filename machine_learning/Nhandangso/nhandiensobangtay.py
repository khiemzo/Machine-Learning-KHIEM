import cv2
import numpy as np
import mediapipe as mp
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
import time
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler


class HandSignRecognitionApp:
    def __init__(self, root):
        # Thiết lập giao diện chính
        self.root = root
        self.root.title("Nhận diện ngôn ngữ ký hiệu bàn tay")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Các biến trạng thái
        self.is_running = True
        self.is_detecting = True
        self.current_label = "Không nhận diện được"
        self.current_sign = None
        self.confidence = 0.0
        self.hand_present = False
        self.collect_data_mode = False
        self.current_sample_class = None
        self.collected_samples = 0
        self.data_collection_target = 100

        # Thiết lập MediaPipe
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.hands = self.mp_hands.Hands(
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            max_num_hands=1)

        # Mô hình phân loại
        self.model = None
        self.scaler = None
        self.labels = {
            0: "0", 1: "1", 2: "2", 3: "3", 4: "4",
            5: "5", 6: "6", 7: "7", 8: "8", 9: "9"
        }

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

        # Tạo frame chính
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame bên trái cho camera và điều khiển
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Frame camera
        self.camera_label = ttk.Label(self.left_frame)
        self.camera_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

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

        # Canvas hiển thị hình dạng tay
        self.sign_canvas = tk.Canvas(self.sign_frame, width=300, height=300, bg="black")
        self.sign_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame hiển thị kết quả
        self.result_frame = ttk.LabelFrame(self.right_frame, text="Kết quả nhận diện")
        self.result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Label hiển thị kết quả
        self.result_label = ttk.Label(self.result_frame, text="Không nhận diện được",
                                      font=("Arial", 40, "bold"), anchor="center")
        self.result_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Label hiển thị độ tin cậy
        self.confidence_label = ttk.Label(self.result_frame, text="Độ tin cậy: 0%",
                                          font=("Arial", 14), anchor="center")
        self.confidence_label.pack(fill=tk.X, padx=5, pady=5)

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

        # Bắt đầu thread xử lý video
        self.video_thread = threading.Thread(target=self.process_video)
        self.video_thread.daemon = True
        self.video_thread.start()

        # Cập nhật giao diện
        self.update_gui()

    def load_model(self):
        """Tải mô hình đã huấn luyện nếu có"""
        try:
            model_path = "models/hand_sign_model.pkl"
            scaler_path = "models/hand_sign_scaler.pkl"

            if os.path.exists(model_path) and os.path.exists(scaler_path):
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)

                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)

                print("Đã tải mô hình thành công")
                self.set_status("Đã tải mô hình thành công")
                return True
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

        # Chuyển đổi landmarks thành vector
        landmarks_list = []
        for landmark in landmarks:
            landmarks_list.extend([landmark.x, landmark.y, landmark.z])

        # Thêm vào dữ liệu huấn luyện
        self.training_data.append(landmarks_list)
        self.training_labels.append(self.current_sample_class)

        # Cập nhật số lượng mẫu đã thu thập
        self.collected_samples += 1
        progress_value = int((self.collected_samples / self.data_collection_target) * 100)
        self.progress['value'] = progress_value

        self.set_status(
            f"Đã thu thập {self.collected_samples}/{self.data_collection_target} mẫu cho số {self.current_sample_class}")

        # Nếu đã đủ số mẫu, dừng thu thập cho lớp này
        if self.collected_samples >= self.data_collection_target:
            self.current_sample_class = None
            self.set_status(
                f"Đã hoàn thành thu thập dữ liệu cho số {self.current_sample_class}. Chọn lớp khác hoặc huấn luyện mô hình.")

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

            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)

            # Huấn luyện mô hình
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X_scaled, y)

            # Lưu mô hình
            self.save_model()

            # Thông báo hoàn thành
            self.set_status(f"Đã huấn luyện mô hình với {len(X)} mẫu!")

        except Exception as e:
            self.set_status(f"Lỗi khi huấn luyện mô hình: {e}")

    def process_video(self):
        """Xử lý video từ camera"""
        while self.is_running:
            # Đọc frame từ camera
            ret, frame = self.cap.read()
            if not ret:
                continue

            # Lật ngang frame để hiển thị đúng
            frame = cv2.flip(frame, 1)

            # Tạo frame ảnh tay cho canvas
            hand_frame = np.zeros((400, 400, 3), np.uint8)

            # Chuyển đổi màu cho MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Xử lý frame
            results = self.hands.process(rgb_frame)

            # Kiểm tra xem có phát hiện tay không
            self.hand_present = results.multi_hand_landmarks is not None

            # Vẽ landmarks lên frame
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Vẽ landmarks lên frame chính
                    self.mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style())

                    # Vẽ landmarks lên frame tay
                    self.mp_drawing.draw_landmarks(
                        hand_frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style())

                    # Thu thập mẫu nếu đang ở chế độ thu thập
                    if self.collect_data_mode and self.current_sample_class is not None:
                        self.collect_sample(hand_landmarks.landmark)

                    # Nhận diện ký hiệu tay nếu có mô hình và đang ở chế độ nhận diện
                    if self.model is not None and self.is_detecting and not self.collect_data_mode:
                        try:
                            # Chuyển đổi landmarks thành vector
                            landmarks_list = []
                            for landmark in hand_landmarks.landmark:
                                landmarks_list.extend([landmark.x, landmark.y, landmark.z])

                            # Chuẩn hóa dữ liệu
                            input_data = np.array([landmarks_list])
                            input_scaled = self.scaler.transform(input_data)

                            # Dự đoán
                            prediction = self.model.predict(input_scaled)[0]
                            proba = np.max(self.model.predict_proba(input_scaled)[0])

                            # Cập nhật kết quả
                            self.current_label = self.labels.get(prediction, "Không xác định")
                            self.confidence = proba * 100
                        except Exception as e:
                            print(f"Lỗi khi nhận diện: {e}")
                            self.current_label = "Lỗi"
                            self.confidence = 0
            else:
                # Không có tay trong frame
                if not self.collect_data_mode:
                    self.current_label = "Không nhận diện được"
                    self.confidence = 0

            # Hiển thị frame
            self.current_frame = frame
            self.current_hand_frame = hand_frame

    def update_gui(self):
        """Cập nhật giao diện người dùng"""
        if not self.is_running:
            return

        # Cập nhật khung camera
        if hasattr(self, 'current_frame'):
            frame = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)

        # Cập nhật khung hình dạng tay
        if hasattr(self, 'current_hand_frame'):
            hand_frame = cv2.cvtColor(self.current_hand_frame, cv2.COLOR_BGR2RGB)
            hand_img = Image.fromarray(hand_frame)
            hand_imgtk = ImageTk.PhotoImage(image=hand_img)
            self.sign_canvas.imgtk = hand_imgtk
            self.sign_canvas.create_image(0, 0, anchor=tk.NW, image=hand_imgtk)

        # Cập nhật kết quả nhận diện
        self.result_label.configure(text=self.current_label)
        self.confidence_label.configure(text=f"Độ tin cậy: {self.confidence:.1f}%")

        # Cập nhật trạng thái tay
        if self.hand_present:
            self.camera_label.configure(style="TLabel")
        else:
            self.camera_label.configure(style="TLabel")

        # Lập lịch cập nhật tiếp theo
        self.root.after(30, self.update_gui)

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
    style.theme_use('clam')  # hoặc 'alt', 'default', 'classic'

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