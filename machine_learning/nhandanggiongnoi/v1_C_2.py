import sys
import os
import time
import json
import numpy as np
from datetime import datetime

# Đặt mã hóa UTF-8 cho sys.stdout
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QComboBox,
                             QLabel, QTextEdit, QVBoxLayout, QHBoxLayout, QWidget,
                             QSlider, QStatusBar, QCheckBox, QGroupBox, QRadioButton,
                             QButtonGroup, QSpinBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QColor, QTextCursor
import speech_recognition as sr
import threading
import queue
import pyaudio
import wave
import librosa
import soundfile as sf
from sklearn.cluster import KMeans
import tempfile

# Constants
LANGUAGES = {
    "English": "en-US",
    "Vietnamese": "vi-VN",
    "Korean": "ko-KR",
    "Japanese": "ja-JP",
    "Russian": "ru-RU"
}

DOMAIN_VOCABULARIES = {
    "General": {},
    "Economics": {
        "en-US": ["inflation", "fiscal", "monetary", "macroeconomics", "microeconomics", "GDP"],
        "vi-VN": ["lạm phát", "tài chính", "tiền tệ", "kinh tế vĩ mô", "kinh tế vi mô", "GDP"],
        "ko-KR": ["인플레이션", "재정", "통화", "거시경제", "미시경제", "국내총생산"],
        "ja-JP": ["インフレ", "財政", "金融", "マクロ経済", "ミクロ経済", "国内総生産"],
        "ru-RU": ["инфляция", "фискальный", "денежный", "макроэкономика", "микроэкономика", "ВВП"]
    },
    "IT": {
        "en-US": ["algorithm", "database", "interface", "programming", "encryption", "cloud"],
        "vi-VN": ["thuật toán", "cơ sở dữ liệu", "giao diện", "lập trình", "mã hóa", "đám mây"],
        "ko-KR": ["알고리즘", "데이터베이스", "인터페이스", "프로그래밍", "암호화", "클라우드"],
        "ja-JP": ["アルゴリズム", "データベース", "インターフェース", "プログラミング", "暗号化", "クラウド"],
        "ru-RU": ["алгоритм", "база данных", "интерфейс", "программирование", "шифрование", "облако"]
    }
}

# Voice Activity Detection class to detect silence and speech
class VoiceActivityDetector:
    def __init__(self, threshold=0.005, min_silence_duration=0.5):
        self.threshold = threshold  # Adjust for sensitivity
        self.min_silence_duration = min_silence_duration  # Minimum duration for silence in seconds

    def detect_silence(self, audio_data, sample_rate):
        # Convert audio data to numpy array if it's not already
        if not isinstance(audio_data, np.ndarray):
            audio_data = np.frombuffer(audio_data, dtype=np.int16)

        # Normalize audio to range [-1, 1]
        audio_data = audio_data.astype(np.float32) / 32768.0

        # Calculate energy
        energy = np.abs(audio_data)

        # Determine frames with energy below threshold
        is_silence = energy < self.threshold

        # Convert to time intervals
        frames_per_second = sample_rate
        silence_starts = np.where(np.diff(is_silence.astype(int)) == 1)[0] / frames_per_second
        silence_ends = np.where(np.diff(is_silence.astype(int)) == -1)[0] / frames_per_second

        # Adjust for edge cases
        if len(silence_starts) == 0 and len(silence_ends) == 0:
            if is_silence[0]:
                return [(0, len(audio_data) / frames_per_second)]
            else:
                return []

        if len(silence_starts) > 0 and len(silence_ends) > 0:
            if silence_starts[0] > silence_ends[0]:
                silence_starts = np.insert(silence_starts, 0, 0)
            if silence_ends[-1] < silence_starts[-1]:
                silence_ends = np.append(silence_ends, len(audio_data) / frames_per_second)

        # Create list of silence intervals
        silence_intervals = [(start, end) for start, end in zip(silence_starts, silence_ends)
                             if end - start >= self.min_silence_duration]

        return silence_intervals


# Speaker Diarization class to identify different speakers
class SpeakerDiarization:
    def __init__(self, num_speakers=2):
        self.num_speakers = num_speakers
        self.sample_rate = 16000  # Common sample rate for audio processing

    def extract_features(self, audio_data):
        # Extract MFCC features
        mfccs = librosa.feature.mfcc(y=audio_data, sr=self.sample_rate, n_mfcc=13)
        return mfccs.T  # Transpose for clustering

    def diarize(self, audio_data):
        # Extract features
        features = self.extract_features(audio_data)

        # If not enough data for clustering, return default speaker
        if len(features) < self.num_speakers:
            return [0] * len(features)

        # Apply K-means clustering
        kmeans = KMeans(n_clusters=self.num_speakers, random_state=0).fit(features)

        # Get speaker labels
        labels = kmeans.labels_

        # Create segments by speaker
        segments = []
        current_speaker = labels[0]
        start_idx = 0

        for i, label in enumerate(labels):
            if label != current_speaker:
                segments.append((start_idx, i, current_speaker))
                current_speaker = label
                start_idx = i

        # Add the last segment
        segments.append((start_idx, len(labels), current_speaker))

        return segments


# Advanced Audio Recorder Thread
class AdvancedAudioRecorder(QThread):
    finished_signal = pyqtSignal(str)
    update_signal = pyqtSignal(str, float, int)

    def __init__(self, language_code, max_phrase_time=20, domain_vocab=None,
                 sensitivity=7, auto_punctuate=True, continuous_mode=True,
                 num_speakers=2):
        super().__init__()
        print("Khởi tạo AdvancedAudioRecorder")
        self.language_code = language_code
        self.domain_vocab = domain_vocab
        self.sensitivity = sensitivity
        self.auto_punctuate = auto_punctuate
        self.continuous_mode = continuous_mode
        self.num_speakers = num_speakers
        self.max_phrase_time = max_phrase_time

        self.is_recording = False
        self.timestamps = []
        self.texts = []
        self.speakers = []
        self.last_timestamp = 0

        self.recognizer = sr.Recognizer()
        self.audio_queue = queue.Queue()

        # Adjust recognizer sensitivity
        self.energy_threshold = 300 - (sensitivity * 20)  # Adjust for higher sensitivity

        # Initialize voice activity detector
        self.vad = VoiceActivityDetector(
            threshold=0.01 - (sensitivity * 0.001),  # Adjust threshold based on sensitivity
            min_silence_duration=0.7 - (sensitivity * 0.05)  # More sensitive = detect shorter silences
        )

        # Initialize diarization
        self.diarizer = SpeakerDiarization(num_speakers=num_speakers)

        # Audio parameters
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.chunk = 1024
        self.audio_buffer = []
        self.last_speaker_change = 0
        self.min_speaker_duration = 1.0  # Minimum time (seconds) before considering a speaker change

    def run(self):
        print("Thread ghi âm đã bắt đầu")
        r = sr.Recognizer()
        
        try:
            print("Đã khởi tạo PyAudio")
            with sr.Microphone() as source:
                print("Đã mở luồng âm thanh thành công")
                print("Đã khởi tạo Microphone thành công")
                r.adjust_for_ambient_noise(source, duration=1)
                print(f"Đã điều chỉnh cho tiếng ồn môi trường. Ngưỡng năng lượng: {r.energy_threshold}")
                
                self.transcriptions = []
                last_timestamp = time.time()
                recording_started = time.time()
                
                while not self.stopped and (not self.max_duration or time.time() - recording_started < self.max_duration):
                    try:
                        print(f"Lắng nghe âm thanh (chế độ: {'liên tục' if self.continuous_mode else 'không liên tục'})")
                        audio = r.listen(source, timeout=10, phrase_time_limit=10)
                        print("Đã ghi âm, đang nhận dạng...")
                        
                        try:
                            start_recognition = time.time()
                            text = r.recognize_google(audio, language=self.language_code)
                            end_recognition = time.time()
                            print(f"Đã nhận dạng: '{text}' (Thời gian: {end_recognition - start_recognition:.2f}s)")
                            
                            current_timestamp = time.time()
                            
                            if text:
                                if self.domain_vocab and self.language_code in self.domain_vocab:
                                    for term in self.domain_vocab[self.language_code]:
                                        if term.lower() in text.lower():
                                            # Boost confidence for domain terms (simplified)
                                            pass

                                if self.auto_punctuate and not text.endswith(('.', '?', '!')):
                                    # Simple rule-based approach - add period at the end
                                    text += '.'

                                speaker_id = 0
                                if self.num_speakers > 1:
                                    speaker_id = self.determine_speaker(audio, current_timestamp - last_timestamp)
                                    print(f"Đã xác định người nói: {speaker_id}")
                                
                                self.transcriptions.append((text, speaker_id, current_timestamp - recording_started))
                                self.update_signal.emit(text, current_timestamp - recording_started, speaker_id)
                                print(f"Đã gửi tín hiệu update_signal: '{text}', speaker_id: {speaker_id}")
                            else:
                                print("Văn bản nhận dạng trống")
                                # Vẫn phát tín hiệu nhưng với văn bản thông báo
                                self.update_signal.emit("[Không phát hiện tiếng nói]", current_timestamp - recording_started, 0)
                                
                            last_timestamp = current_timestamp
                            
                            if not self.continuous_mode:
                                print("Chế độ không liên tục - dừng ghi âm")
                                self.stopped = True
                                break
                                
                        except sr.UnknownValueError:
                            print("Không nhận dạng được giọng nói")
                            # Phát tín hiệu thông báo không nhận dạng được
                            self.update_signal.emit("[Không nhận dạng được giọng nói]", current_timestamp - recording_started, 0)
                            
                        except sr.RequestError as e:
                            print(f"Lỗi yêu cầu API: {e}")
                            # Phát tín hiệu thông báo lỗi
                            self.update_signal.emit(f"[Lỗi kết nối: {e}]", current_timestamp - recording_started, 0)
                    
                    except Exception as e:
                        print(f"Lỗi khi lắng nghe: {e}")
                        self.update_signal.emit(f"[Lỗi: {e}]", current_timestamp - recording_started, 0)
                
                print("Đã hoàn thành vòng lặp ghi âm")
        
        except Exception as e:
            print(f"Lỗi trong thread ghi âm: {e}")
            self.finished_signal.emit(str(e))
        
        finally:
            print("Đã đóng luồng âm thanh và kết thúc PyAudio")
            self.finished_signal.emit("")

    def determine_speaker(self, audio, time_diff):
        # Load audio file
        audio_data, sr = librosa.load(audio, sr=self.rate, mono=True)

        # Speaker change based on time since last change
        if len(self.speakers) == 0:
            # First speaker
            current_speaker = 0
        elif time_diff < self.min_speaker_duration:
            # Too soon after last change, keep the same speaker
            current_speaker = self.speakers[-1]
        else:
            # Use diarization to determine speaker
            try:
                # Get segments
                segments = self.diarizer.diarize(audio_data)

                if segments:
                    # Take the majority speaker in this segment
                    segment_speakers = [s[2] for s in segments]
                    speaker_counts = np.bincount(segment_speakers)
                    current_speaker = np.argmax(speaker_counts)

                    # Update last speaker change time if changed
                    if len(self.speakers) > 0 and current_speaker != self.speakers[-1]:
                        self.last_speaker_change = time.time()
                else:
                    # No segments found, use previous speaker
                    current_speaker = self.speakers[-1] if self.speakers else 0
            except Exception as e:
                print(f"Error in diarization: {e}")
                current_speaker = self.speakers[-1] if self.speakers else 0

        return current_speaker

    def stop(self):
        self.is_recording = False
        self.wait()


# Main Application Window
class VoiceCraftApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VoiceCraft - Ứng dụng Ghi âm và Nhận dạng giọng nói")
        self.setGeometry(100, 100, 800, 600)

        self.recorder = None
        self.is_recording = False
        self.speaker_colors = [QColor(0, 120, 215), QColor(0, 153, 0),
                               QColor(209, 52, 56), QColor(139, 0, 139)]

        self.init_ui()

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()

        # Settings group
        settings_group = QGroupBox("Cài đặt ghi âm")
        settings_layout = QVBoxLayout()

        # Top row - Basic settings
        basic_settings = QHBoxLayout()

        # Language selection
        lang_label = QLabel("Ngôn ngữ:")
        self.language_combo = QComboBox()
        for lang in LANGUAGES.keys():
            self.language_combo.addItem(lang)

        # Domain selection
        domain_label = QLabel("Lĩnh vực:")
        self.domain_combo = QComboBox()
        for domain in DOMAIN_VOCABULARIES.keys():
            self.domain_combo.addItem(domain)

        # Microphone sensitivity
        sensitivity_label = QLabel("Độ nhạy:")
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setRange(1, 10)
        self.sensitivity_slider.setValue(7)  # Default to higher sensitivity
        self.sensitivity_slider.setToolTip("Điều chỉnh độ nhạy microphone")

        basic_settings.addWidget(lang_label)
        basic_settings.addWidget(self.language_combo)
        basic_settings.addSpacing(10)
        basic_settings.addWidget(domain_label)
        basic_settings.addWidget(self.domain_combo)
        basic_settings.addSpacing(10)
        basic_settings.addWidget(sensitivity_label)
        basic_settings.addWidget(self.sensitivity_slider)

        # Second row - Advanced settings
        advanced_settings = QHBoxLayout()

        # Recording time limit
        duration_label = QLabel("Thời lượng tối đa mỗi đoạn (giây):")
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(5, 120)
        self.duration_spin.setValue(30)

        # Number of speakers
        speakers_label = QLabel("Số người nói:")
        self.speakers_spin = QSpinBox()
        self.speakers_spin.setRange(1, 4)
        self.speakers_spin.setValue(2)

        # Mode selection
        mode_label = QLabel("Chế độ:")
        self.continuous_mode = QCheckBox("Ghi liên tục")
        self.continuous_mode.setChecked(True)
        self.continuous_mode.setToolTip("Ghi âm liên tục, tự động phát hiện khoảng lặng")

        # Auto punctuate
        self.auto_punctuate = QCheckBox("Dấu câu tự động")
        self.auto_punctuate.setChecked(True)

        advanced_settings.addWidget(duration_label)
        advanced_settings.addWidget(self.duration_spin)
        advanced_settings.addSpacing(10)
        advanced_settings.addWidget(speakers_label)
        advanced_settings.addWidget(self.speakers_spin)
        advanced_settings.addSpacing(10)
        advanced_settings.addWidget(mode_label)
        advanced_settings.addWidget(self.continuous_mode)
        advanced_settings.addWidget(self.auto_punctuate)

        # Add settings to group
        settings_layout.addLayout(basic_settings)
        settings_layout.addLayout(advanced_settings)
        settings_group.setLayout(settings_layout)

        # Record button
        self.record_button = QPushButton("🎤 Bắt đầu ghi âm")
        self.record_button.clicked.connect(self.toggle_recording)
        self.record_button.setMinimumSize(100, 40)

        # Text area
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        font = QFont("Arial", 12)
        self.text_edit.setFont(font)

        # Audio timeline
        self.timeline_label = QLabel("Thời gian: 0:00 / 0:00")

        # Add all components to main layout
        main_layout.addWidget(settings_group)
        main_layout.addWidget(self.record_button)
        main_layout.addWidget(self.text_edit)
        main_layout.addWidget(self.timeline_label)

        # Create central widget and set main layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Sẵn sàng. Nhấn nút ghi âm hoặc phím Space để bắt đầu.")

        # Set space shortcut for record/stop
        self.space_shortcut = Qt.Key_Space
        self.keyPressEvent = self.handle_key_press

    def handle_key_press(self, event):
        if event.key() == self.space_shortcut:
            self.toggle_recording()
        else:
            super(VoiceCraftApp, self).keyPressEvent(event)

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        if self.is_recording:
            return

        # Update UI
        self.record_button.setText("⏹️ Dừng ghi âm")
        self.is_recording = True
        self.text_edit.clear()
        
        # Debug message
        print("Bắt đầu ghi âm...")

        # Get current settings
        lang_text = self.language_combo.currentText()
        lang_code = LANGUAGES[lang_text]
        print(f"Ngôn ngữ: {lang_text} ({lang_code})")

        domain_text = self.domain_combo.currentText()
        domain_vocab = DOMAIN_VOCABULARIES[domain_text]
        
        sensitivity = self.sensitivity_slider.value()
        max_phrase_time = self.duration_spin.value()
        num_speakers = self.speakers_spin.value()
        continuous_mode = self.continuous_mode.isChecked()
        auto_punctuate = self.auto_punctuate.isChecked()

        # Start recording thread
        self.recorder = AdvancedAudioRecorder(
            language_code=lang_code,
            domain_vocab=domain_vocab.get(lang_code, None),
            sensitivity=sensitivity,
            max_phrase_time=max_phrase_time,
            continuous_mode=continuous_mode,
            auto_punctuate=auto_punctuate,
            num_speakers=num_speakers
        )
        print("Đã tạo recorder thread")
        self.recorder.update_signal.connect(self.update_transcript)
        self.recorder.finished_signal.connect(self.on_recording_finished)
        print("Đã kết nối tín hiệu")
        self.recorder.start()
        print("Đã bắt đầu recorder thread")
        
        # Update status bar
        self.status_bar.showMessage("Đang ghi âm... (Nhấn Space để dừng)")

        # Start timer for updating timeline
        self.start_time = time.time()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timeline)
        self.timer.start(100)  # Update every 100ms

    def stop_recording(self):
        if not self.is_recording:
            return

        # Update UI
        self.record_button.setText("🎤 Bắt đầu ghi âm")
        self.is_recording = False

        # Stop recording thread
        if self.recorder:
            self.recorder.stop()

        # Stop timer
        if hasattr(self, 'timer'):
            self.timer.stop()

        # Update status bar
        self.status_bar.showMessage("Đang xử lý bản ghi...")

    def update_transcript(self, text, timestamp, speaker):
        print(f"Cập nhật transcript: {text}")
        # Get a color for this speaker
        color = self.speaker_colors[speaker % len(self.speaker_colors)]

        # Create formatted text with color
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)

        # Set text color for this speaker
        format = cursor.charFormat()
        format.setForeground(color)
        cursor.setCharFormat(format)

        # Insert the text
        cursor.insertText(text + "\n")

        # Move to the end
        cursor.movePosition(QTextCursor.End)
        self.text_edit.setTextCursor(cursor)
        self.text_edit.ensureCursorVisible()

    def update_timeline(self):
        if not self.is_recording:
            return

        elapsed = time.time() - self.start_time
        minutes, seconds = divmod(int(elapsed), 60)
        self.timeline_label.setText(f"Thời gian: {minutes}:{seconds:02d} / ∞")

    def on_recording_finished(self, transcript):
        # Save the transcript to a file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"transcript_{timestamp}.txt"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(transcript)
            self.status_bar.showMessage(f"Ghi âm đã dừng. Bản ghi đã lưu vào {filename}")
        except Exception as e:
            self.status_bar.showMessage(f"Lỗi khi lưu bản ghi: {e}")


# Application entry point
def main():
    print("Khởi tạo ứng dụng VoiceCraft")
    
    # Kiểm tra thiết bị âm thanh
    try:
        p = pyaudio.PyAudio()
        print(f"Số thiết bị âm thanh: {p.get_device_count()}")
        
        # Liệt kê các thiết bị âm thanh
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            print(f"Thiết bị {i}: {device_info['name']}")
            print(f"  - Kênh vào: {device_info['maxInputChannels']}")
            print(f"  - Kênh ra: {device_info['maxOutputChannels']}")
            print(f"  - Tần số mặc định: {device_info['defaultSampleRate']}")
        
        # Kiểm tra thiết bị thu âm mặc định
        print("\nThiết bị thu âm mặc định:")
        default_input = p.get_default_input_device_info()
        print(f"  - Tên: {default_input['name']}")
        print(f"  - Kênh: {default_input['maxInputChannels']}")
        
        p.terminate()
    except Exception as e:
        print(f"Lỗi khi kiểm tra thiết bị âm thanh: {e}")
    
    app = QApplication(sys.argv)
    window = VoiceCraftApp()
    window.show()
    print("Hiển thị cửa sổ ứng dụng")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()