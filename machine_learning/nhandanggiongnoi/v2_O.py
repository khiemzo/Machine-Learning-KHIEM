import sys
import threading
import time
import datetime
from collections import Counter

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QTextEdit, QLabel, QListWidget, QComboBox, QSlider,
    QShortcut, QFileDialog, QStatusBar
)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt, QTimer

import speech_recognition as sr

# --- Simulated AI Analysis and Processing Functions ---

def analyze_sentiment(text):
    # Very basic simulated sentiment analysis.
    positive = sum(word in text.lower() for word in ['good', 'great', 'excellent', 'happy'])
    negative = sum(word in text.lower() for word in ['bad', 'poor', 'terrible', 'sad'])
    if positive > negative:
        return "Positive"
    elif negative > positive:
        return "Negative"
    return "Neutral"

def keyword_cloud(text):
    words = text.split()
    common = Counter(words).most_common(5)
    return ', '.join([word for word, count in common]) if common else "N/A"

def accuracy_trend():
    # Simulated static accuracy trend report.
    return "Accuracy trend: 95% (steady)"

def integrate_vocabulary(text, vocab_list):
    # Simulate domain-specific vocabulary integration by ensuring proper casing.
    for term in vocab_list:
        text = text.replace(term.lower(), term)
    return text

def auto_punctuate(text):
    # Simple auto-punctuation: add a period if missing.
    if text and text[-1] not in '.!?':
        text += '.'
    return text

# --- Main Application Class ---

class VoiceCraftApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VoiceCraft")
        self.setGeometry(100, 100, 1200, 800)
        self.is_recording = False
        self.transcribed_text = ""
        self.vocab_list = ["Economics", "IT"]  # Danh sách từ chuyên ngành
        self.speaker_counter = 1

        # Khởi tạo bộ nhận dạng với điều chỉnh năng lượng động
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.recognizer.dynamic_energy_threshold = True
        # Có thể thiết lập ngưỡng năng lượng ban đầu:
        self.recognizer.energy_threshold = 300

        # Thêm thanh trượt để điều chỉnh độ nhạy (energy_threshold)
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setMinimum(50)
        self.sensitivity_slider.setMaximum(4000)
        self.sensitivity_slider.setValue(self.recognizer.energy_threshold)
        self.sensitivity_slider.valueChanged.connect(self.update_sensitivity)

        self.initUI()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)

    def initUI(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Header: Record/Stop buttons, language selection, display speed.
        header_layout = QHBoxLayout()
        self.record_button = QPushButton("🎤 Record")
        self.stop_button = QPushButton("⏹️ Stop")
        self.language_select = QComboBox()
        # Using language codes: English (en-US), Vietnamese (vi-VN), Korean (ko-KR), Japanese (ja-JP), Russian (ru-RU)
        self.language_select.addItems(["en-US", "vi-VN", "ko-KR", "ja-JP", "ru-RU"])
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(100)
        self.speed_slider.setValue(50)
        header_layout.addWidget(self.record_button)
        header_layout.addWidget(self.stop_button)
        header_layout.addWidget(QLabel("Language:"))
        header_layout.addWidget(self.language_select)
        header_layout.addWidget(QLabel("Display Speed:"))
        header_layout.addWidget(self.speed_slider)
        main_layout.addLayout(header_layout)

        # Main Content Layout: Left Sidebar, Center Panel, Right Sidebar.
        content_layout = QHBoxLayout()

        # Left Sidebar: Saved sessions and version history.
        left_sidebar = QVBoxLayout()
        self.sessions_list = QListWidget()
        self.sessions_list.addItem("Session 1")
        self.version_history = QListWidget()
        self.version_history.addItem("v1.0")
        left_sidebar.addWidget(QLabel("Saved Sessions"))
        left_sidebar.addWidget(self.sessions_list)
        left_sidebar.addWidget(QLabel("Version History"))
        left_sidebar.addWidget(self.version_history)
        content_layout.addLayout(left_sidebar, 1)

        # Center Panel: Real-time text display and audio timeline.
        center_panel = QVBoxLayout()
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.audio_timeline = QSlider(Qt.Horizontal)
        center_panel.addWidget(self.text_display)
        center_panel.addWidget(QLabel("Audio Timeline"))
        center_panel.addWidget(self.audio_timeline)
        content_layout.addLayout(center_panel, 3)

        # Right Sidebar: AI Analysis Tools.
        right_sidebar = QVBoxLayout()
        self.sentiment_label = QLabel("Sentiment: Neutral")
        self.keyword_label = QLabel("Keywords: N/A")
        self.accuracy_label = QLabel("Accuracy: N/A")
        right_sidebar.addWidget(QLabel("AI Analysis Tools"))
        right_sidebar.addWidget(self.sentiment_label)
        right_sidebar.addWidget(self.keyword_label)
        right_sidebar.addWidget(self.accuracy_label)
        content_layout.addLayout(right_sidebar, 1)

        main_layout.addLayout(content_layout)

        # Footer: Status bar showing recording time and remaining storage.
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.recording_start_time = None

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Connect button actions.
        self.record_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)

        # Keyboard Shortcuts for Record (Ctrl+S) and Undo (Ctrl+Z).
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self.start_recording)
        QShortcut(QKeySequence("Ctrl+Z"), self, activated=self.undo_last_segment)

    def update_status(self):
        if self.is_recording and self.recording_start_time:
            elapsed = int(time.time() - self.recording_start_time)
            self.status_bar.showMessage(f"Recording... {elapsed} sec elapsed")

    def start_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.recording_start_time = time.time()
            self.timer.start(1000)
            threading.Thread(target=self.record_loop, daemon=True).start()

    def stop_recording(self):
        self.is_recording = False
        self.timer.stop()
        self.export_transcript()
        self.perform_ai_analysis()

    def update_sensitivity(self, value):
        # Cập nhật ngưỡng năng lượng của bộ nhận dạng khi thanh trượt thay đổi
        self.recognizer.energy_threshold = value
        self.status_bar.showMessage(f"Độ nhạy được đặt là: {value}")

    def record_loop(self):
        # Tăng thời gian giới hạn của một đoạn nói để bắt được các đoạn hội thoại dài hơn
        phrase_time_limit = 15  # ví dụ: 15 giây cho mỗi đoạn nói
        while self.is_recording:
            with self.microphone as source:
                try:
                    # Lắng nghe đoạn nói với timeout nhỏ (0.5 giây) và giới hạn thời gian phrase_time_limit
                    audio = self.recognizer.listen(source, timeout=0.5, phrase_time_limit=phrase_time_limit)
                    lang = self.language_select.currentText()
                    text = self.recognizer.recognize_google(audio, language=lang)

                    # Xử lý văn bản: tích hợp từ vựng chuyên ngành và tự động thêm dấu câu
                    text = integrate_vocabulary(text, self.vocab_list)
                    text = auto_punctuate(text)

                    timestamp = datetime.datetime.now().strftime("%H:%M:%S")

                    # Giả lập phân biệt người nói: trong ứng dụng thật, bạn có thể tích hợp phân đoạn người nói (diarization)
                    speaker = f"Speaker {self.speaker_counter}: "
                    # Giả lập đơn giản: xen kẽ nhãn người nói
                    self.speaker_counter = 1 if self.speaker_counter >= 2 else self.speaker_counter + 1

                    segment = f"[{timestamp}] {speaker}{text}\n"
                    self.transcribed_text += segment

                    # Cập nhật hiển thị văn bản liên tục. Ở đây chỉ đơn giản là thêm đoạn mới vào hiển thị.
                    self.update_transcript(segment)
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except Exception as e:
                    print("Lỗi:", e)

    def update_transcript(self, segment):
        # Update real-time text display.
        self.text_display.append(segment)

    def undo_last_segment(self):
        # Simple undo: remove the last line from the transcript.
        lines = self.transcribed_text.strip().split('\n')
        if lines:
            lines.pop()
            self.transcribed_text = "\n".join(lines) + "\n"
            self.text_display.setPlainText(self.transcribed_text)

    def export_transcript(self):
        # Export transcribed text as a TXT file.
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self, "Export Transcript", "", "Text Files (*.txt)", options=options)
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.transcribed_text)

    def perform_ai_analysis(self):
        # Generate and display AI reports.
        sentiment = analyze_sentiment(self.transcribed_text)
        keywords = keyword_cloud(self.transcribed_text)
        accuracy = accuracy_trend()
        self.sentiment_label.setText(f"Sentiment: {sentiment}")
        self.keyword_label.setText(f"Keywords: {keywords}")
        self.accuracy_label.setText(accuracy)

def main():
    app = QApplication(sys.argv)
    window = VoiceCraftApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
