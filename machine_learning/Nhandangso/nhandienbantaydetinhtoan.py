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
        # Main interface setup
        self.root = root
        self.root.title("Hand Sign Language Recognition System")
        self.root.geometry("1280x720")
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Status variables
        self.is_running = True
        self.is_detecting = True
        self.current_label = "No sign detected"
        self.current_sign = None
        self.confidence = 0.0
        self.hand_present = False
        self.collect_data_mode = False
        self.current_sample_class = None
        self.collected_samples = 0
        self.data_collection_target = 100
        self.two_hands_mode = True  # Enable two hands detection by default

        # MediaPipe setup
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.hands = self.mp_hands.Hands(
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            max_num_hands=2)  # Set maximum hands to 2

        # Classification model
        self.model = None
        self.scaler = None
        self.labels = {
            0: "0", 1: "1", 2: "2", 3: "3", 4: "4",
            5: "5", 6: "6", 7: "7", 8: "8", 9: "9",
            10: "A", 11: "B", 12: "C", 13: "D", 14: "E",
            15: "+", 16: "-", 17: "×", 18: "÷", 19: "="
        }

        # Initialize training data
        self.training_data = []
        self.training_labels = []

        # Create directory structure
        os.makedirs("models", exist_ok=True)
        os.makedirs("data", exist_ok=True)

        # Set up video capture
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Create style
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 10, "bold"))
        style.configure("TLabel", font=("Arial", 12))
        style.configure("Result.TLabel", font=("Arial", 48, "bold"))
        style.configure("Status.TLabel", font=("Arial", 10))

        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left frame for buttons and controls
        self.left_frame = ttk.Frame(self.main_frame, width=200)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.left_frame.pack_propagate(False)

        # Create control section
        self.controls_label = ttk.Label(self.left_frame, text="ĐIỀU KHIỂN", font=("Arial", 14, "bold"))
        self.controls_label.pack(pady=(10, 20))

        # Control buttons
        self.toggle_btn = ttk.Button(self.left_frame, text="Tạm dừng Phát hiện", command=self.toggle_detection)
        self.toggle_btn.pack(fill=tk.X, padx=10, pady=5)

        self.toggle_hands_btn = ttk.Button(self.left_frame, text="Chế độ Hai Tay: BẬT", command=self.toggle_hands_mode)
        self.toggle_hands_btn.pack(fill=tk.X, padx=10, pady=5)

        self.train_btn = ttk.Button(self.left_frame, text="Huấn luyện mô hình", command=self.train_model)
        self.train_btn.pack(fill=tk.X, padx=10, pady=5)

        self.collect_btn = ttk.Button(self.left_frame, text="Thu thập dữ liệu", command=self.toggle_data_collection)
        self.collect_btn.pack(fill=tk.X, padx=10, pady=5)

        self.load_btn = ttk.Button(self.left_frame, text="Tải Mô Hình", command=self.load_model)
        self.load_btn.pack(fill=tk.X, padx=10, pady=5)

        # Create data collection section
        self.collection_label = ttk.Label(self.left_frame, text="THU THẬP DỮ LIỆU", font=("Arial", 14, "bold"))
        self.collection_label.pack(pady=(20, 10))

        # Create sign buttons grid
        self.signs_frame = ttk.Frame(self.left_frame)
        self.signs_frame.pack(fill=tk.X, padx=5, pady=5)

        # Number buttons (0-9)
        self.sign_buttons = []
        for i in range(10):
            btn = ttk.Button(self.signs_frame, text=str(i), width=3,
                             command=lambda num=i: self.select_sample_class(num))
            btn.grid(row=i // 5, column=i % 5, padx=2, pady=2)
            self.sign_buttons.append(btn)

        # Letter buttons (A-E)
        for i in range(5):
            btn = ttk.Button(self.signs_frame, text=chr(65 + i), width=3,
                             command=lambda num=i + 10: self.select_sample_class(num))
            btn.grid(row=2, column=i, padx=2, pady=2)
            self.sign_buttons.append(btn)

        # Symbol buttons (+, -, ×, ÷, =)
        symbols = ["+", "-", "×", "÷", "="]
        for i, symbol in enumerate(symbols):
            btn = ttk.Button(self.signs_frame, text=symbol, width=3,
                             command=lambda num=i + 15: self.select_sample_class(num))
            btn.grid(row=3, column=i, padx=2, pady=2)
            self.sign_buttons.append(btn)

        # Progress bar for data collection
        self.progress_frame = ttk.Frame(self.left_frame)
        self.progress_frame.pack(fill=tk.X, padx=10, pady=10)

        self.collection_status_label = ttk.Label(self.progress_frame, text="Collection: OFF")
        self.collection_status_label.pack(fill=tk.X, pady=(0, 5))

        self.progress = ttk.Progressbar(self.progress_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(fill=tk.X)

        # Status label
        self.status_label = ttk.Label(self.left_frame, text="Ready", style="Status.TLabel", wraplength=180)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=5)

        # Center frame for camera
        self.center_frame = ttk.Frame(self.main_frame)
        self.center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Camera view
        self.camera_label = ttk.Label(self.center_frame)
        self.camera_label.pack(fill=tk.BOTH, expand=True)

        # Right frame
        self.right_frame = ttk.Frame(self.main_frame, width=300)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        self.right_frame.pack_propagate(False)

        # Sign visualization frame (top right)
        self.sign_frame = ttk.LabelFrame(self.right_frame, text="Hand Sign Visualization")
        self.sign_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.sign_canvas = tk.Canvas(self.sign_frame, width=280, height=280, bg="black")
        self.sign_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Result frame (bottom right)
        self.result_frame = ttk.LabelFrame(self.right_frame, text="Recognition Result")
        self.result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.result_label = ttk.Label(self.result_frame, text="No sign detected",
                                      style="Result.TLabel", anchor="center")
        self.result_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.confidence_label = ttk.Label(self.result_frame, text="Confidence: 0%")
        self.confidence_label.pack(fill=tk.X, padx=5, pady=5)

        # Load model if exists
        self.load_model()

        # Start video processing thread
        self.video_thread = threading.Thread(target=self.process_video)
        self.video_thread.daemon = True
        self.video_thread.start()

        # Update GUI
        self.update_gui()

    def toggle_hands_mode(self):
        """Toggle between one and two hands detection mode"""
        self.two_hands_mode = not self.two_hands_mode
        if self.two_hands_mode:
            self.toggle_hands_btn.config(text="Chế độ Hai Tay: BẬT")
            self.hands = self.mp_hands.Hands(
                model_complexity=1,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
                max_num_hands=2)
            self.set_status("Phát hiện hai tay đã được kích hoạt")
        else:
            self.toggle_hands_btn.config(text="Chế độ Hai Tay: TẮT")
            self.hands = self.mp_hands.Hands(
                model_complexity=1,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
                max_num_hands=1)
            self.set_status("Phát hiện một tay đã được kích hoạt")

    def load_model(self):
        """Load trained model if exists"""
        try:
            model_path = "models/hand_sign_model.pkl"
            scaler_path = "models/hand_sign_scaler.pkl"

            if os.path.exists(model_path) and os.path.exists(scaler_path):
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)

                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)

                self.set_status("Mô hình đã được tải thành công")
                return True
            else:
                self.set_status("Không tìm thấy mô hình. Vui lòng huấn luyện một mô hình trước.")
                return False
        except Exception as e:
            self.set_status(f"Error loading model: {e}")
            return False

    def save_model(self):
        """Save trained model"""
        try:
            with open("models/hand_sign_model.pkl", 'wb') as f:
                pickle.dump(self.model, f)

            with open("models/hand_sign_scaler.pkl", 'wb') as f:
                pickle.dump(self.scaler, f)

            self.set_status("Mô hình đã được lưu thành công")
            return True
        except Exception as e:
            self.set_status(f"Error saving model: {e}")
            return False

    def toggle_detection(self):
        """Toggle detection mode"""
        self.is_detecting = not self.is_detecting
        if self.is_detecting:
            self.toggle_btn.config(text="Tạm dừng Phát hiện")
            self.set_status("Phát hiện đã được kích hoạt")
        else:
            self.toggle_btn.config(text="Tiếp tục Phát hiện")
            self.set_status("Phát hiện đã tạm dừng")

    def toggle_data_collection(self):
        """Toggle data collection mode"""
        self.collect_data_mode = not self.collect_data_mode
        self.progress['value'] = 0
        self.collected_samples = 0

        if self.collect_data_mode:
            self.collect_btn.config(text="Dừng Thu Thập")
            self.collection_status_label.config(text="Thu thập: BẬT")
            self.set_status("Chọn một lớp dấu hiệu để thu thập dữ liệu")
        else:
            self.collect_btn.config(text="Thu Thập Dữ Liệu")
            self.collection_status_label.config(text="Thu thập: Tắt")
            self.current_sample_class = None
            self.set_status("Việc thu thập dữ liệu đã dừng lại")

    def select_sample_class(self, class_num):
        """Select a class for data collection"""
        if self.collect_data_mode:
            self.current_sample_class = class_num
            self.collected_samples = 0
            self.progress['value'] = 0

            class_name = self.labels.get(class_num, str(class_num))
            self.set_status(f"Collecting data for '{class_name}'. Position your hand in frame.")

            # Highlight the selected button
            for i, btn in enumerate(self.sign_buttons):
                if i == class_num:
                    btn.state(['pressed'])
                else:
                    btn.state(['!pressed'])

    def collect_sample(self, landmarks_list):
        """Collect a data sample from landmarks"""
        if not self.collect_data_mode or self.current_sample_class is None:
            return

        # Add to training data
        self.training_data.append(landmarks_list)
        self.training_labels.append(self.current_sample_class)

        # Update sample count
        self.collected_samples += 1
        progress_value = int((self.collected_samples / self.data_collection_target) * 100)
        self.progress['value'] = progress_value

        class_name = self.labels.get(self.current_sample_class, str(self.current_sample_class))
        self.set_status(f"Collected {self.collected_samples}/{self.data_collection_target} samples for '{class_name}'")

        # If we've collected enough samples
        if self.collected_samples >= self.data_collection_target:
            self.set_status(f"Completed collecting data for '{class_name}'. Select another class or train model.")
            self.current_sample_class = None

            # Reset button states
            for btn in self.sign_buttons:
                btn.state(['!pressed'])

    def train_model(self):
        """Train the model using collected data"""
        if len(self.training_data) < 50:
            self.set_status("Không đủ dữ liệu để huấn luyện. Hãy thu thập ít nhất 50 mẫu.")
            return

        try:
            # Notify training start
            self.set_status("Training model...")

            # Normalize data
            X = np.array(self.training_data)
            y = np.array(self.training_labels)

            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)

            # Train model
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X_scaled, y)

            # Save model
            self.save_model()

            # Notify completion
            self.set_status(f"Model trained successfully with {len(X)} samples!")

        except Exception as e:
            self.set_status(f"Error training model: {e}")

    def extract_hand_landmarks(self, hand_landmarks):
        """Extract landmarks from a hand into a flat list"""
        landmarks_list = []
        for landmark in hand_landmarks.landmark:
            landmarks_list.extend([landmark.x, landmark.y, landmark.z])
        return landmarks_list

    def process_video(self):
        """Process video frames from camera"""
        while self.is_running:
            # Read frame
            ret, frame = self.cap.read()
            if not ret:
                continue

            # Flip frame horizontally for a mirror view
            frame = cv2.flip(frame, 1)

            # Create hand frame for visualization
            hand_frame = np.zeros((400, 400, 3), np.uint8)

            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process frame
            results = self.hands.process(rgb_frame)

            # Check if hands are detected
            self.hand_present = results.multi_hand_landmarks is not None

            # Draw landmarks
            if results.multi_hand_landmarks:
                # Extract landmarks from all hands
                combined_landmarks = []

                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw landmarks on main frame
                    self.mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style())

                    # Draw landmarks on hand frame (for ALL hands)
                    self.mp_drawing.draw_landmarks(
                        hand_frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style())

                    # Extract landmarks for this hand
                    hand_landmarks_list = self.extract_hand_landmarks(hand_landmarks)
                    combined_landmarks.extend(hand_landmarks_list)

                    # Collect sample if in collection mode
                    if self.collect_data_mode and self.current_sample_class is not None:
                        # For single hand collection, just use first hand
                        if not self.two_hands_mode or results.multi_hand_landmarks.index(hand_landmarks) == 0:
                            self.collect_sample(hand_landmarks_list)

                # For two hands mode, collect both hands together
                if self.two_hands_mode and self.collect_data_mode and self.current_sample_class is not None:
                    if len(results.multi_hand_landmarks) >= 2:
                        self.collect_sample(combined_landmarks)

                # Recognize sign if model exists and in detection mode
                if self.model is not None and self.is_detecting and not self.collect_data_mode:
                    try:
                        input_data = None

                        # Use combined data for two hands mode if we have two hands
                        if self.two_hands_mode and len(results.multi_hand_landmarks) >= 2:
                            input_data = np.array([combined_landmarks])
                        # Otherwise use single hand
                        elif not self.two_hands_mode or len(results.multi_hand_landmarks) == 1:
                            first_hand_landmarks = self.extract_hand_landmarks(results.multi_hand_landmarks[0])
                            input_data = np.array([first_hand_landmarks])

                        if input_data is not None:
                            # Normalize data
                            try:
                                input_scaled = self.scaler.transform(input_data)

                                # Predict
                                prediction = self.model.predict(input_scaled)[0]
                                proba = np.max(self.model.predict_proba(input_scaled)[0])

                                # Update result
                                self.current_label = self.labels.get(prediction, "Unknown")
                                self.confidence = proba * 100
                            except ValueError:
                                # Handle dimension mismatch (when training with one mode but using another)
                                self.current_label = "Mode mismatch error"
                                self.confidence = 0
                    except Exception as e:
                        print(f"Recognition error: {e}")
                        self.current_label = "Error"
                        self.confidence = 0
            else:
                # No hands in frame
                if not self.collect_data_mode:
                    self.current_label = "No sign detected"
                    self.confidence = 0

            # Store frames for GUI update
            self.current_frame = frame
            self.current_hand_frame = hand_frame

    def update_gui(self):
        """Update GUI elements"""
        if not self.is_running:
            return

        # Update camera view
        if hasattr(self, 'current_frame'):
            frame = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)

        # Update hand sign visualization
        if hasattr(self, 'current_hand_frame'):
            hand_frame = cv2.cvtColor(self.current_hand_frame, cv2.COLOR_BGR2RGB)
            hand_img = Image.fromarray(hand_frame)
            hand_imgtk = ImageTk.PhotoImage(image=hand_img)
            self.sign_canvas.imgtk = hand_imgtk
            self.sign_canvas.create_image(0, 0, anchor=tk.NW, image=hand_imgtk)

        # Update recognition result
        self.result_label.configure(text=self.current_label)
        self.confidence_label.configure(text=f"Confidence: {self.confidence:.1f}%")

        # Schedule next update
        self.root.after(30, self.update_gui)

    def set_status(self, message):
        """Update status message"""
        self.status_label.configure(text=message)

    def on_closing(self):
        """Handle application closing"""
        self.is_running = False
        if self.cap.isOpened():
            self.cap.release()
        self.hands.close()
        self.root.destroy()


def main():
    # Create root window
    root = tk.Tk()

    # Create and run application
    app = HandSignRecognitionApp(root)

    # Start main loop
    root.mainloop()


if __name__ == "__main__":
    main()