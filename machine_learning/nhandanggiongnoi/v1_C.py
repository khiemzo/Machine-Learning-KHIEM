import sys
import os
import time
import json
import threading
import numpy as np
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QComboBox,
                             QLabel, QTextEdit, QVBoxLayout, QHBoxLayout, QWidget,
                             QSlider, QFileDialog, QListWidget, QSplitter, QStatusBar,
                             QAction, QMenu, QToolBar, QFontComboBox, QSpinBox, QTreeWidget,
                             QTreeWidgetItem, QTabWidget, QShortcut)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize
from PyQt5.QtGui import QIcon, QKeySequence, QFont, QColor, QPalette
import pyaudio
import wave
import speech_recognition as sr
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from wordcloud import WordCloud
from textblob import TextBlob
import threading
import queue

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


# Audio Recording Thread
class AudioRecorder(QThread):
    finished_signal = pyqtSignal(str)
    update_signal = pyqtSignal(str, float)

    def __init__(self, language_code, domain_vocab=None):
        super().__init__()
        self.language_code = language_code
        self.domain_vocab = domain_vocab
        self.is_recording = False
        self.timestamps = []
        self.texts = []
        self.speakers = []
        self.current_speaker = 0
        self.last_timestamp = 0
        self.recognizer = sr.Recognizer()
        self.audio_queue = queue.Queue()

    def run(self):
        self.is_recording = True
        self.last_timestamp = time.time()

        # Setup microphone
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.energy_threshold = 300

            while self.is_recording:
                try:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    self.audio_queue.put((audio, time.time()))
                    self.process_audio_queue()
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    print(f"Error while recording: {e}")

    def process_audio_queue(self):
        while not self.audio_queue.empty():
            audio, timestamp = self.audio_queue.get()
            try:
                # This would be replaced by a more sophisticated model in a real implementation
                # For speaker differentiation, we'd use a diarization model
                text = self.recognizer.recognize_google(audio, language=self.language_code)

                # Apply domain-specific vocabulary boosting (simplified)
                if self.domain_vocab and self.language_code in self.domain_vocab:
                    for term in self.domain_vocab[self.language_code]:
                        if term.lower() in text.lower():
                            # Boost confidence for domain terms (simplified)
                            pass

                # Add automatic punctuation (simplified implementation)
                # In a real app, we'd use a proper punctuation model
                if not text.endswith(('.', '?', '!')):
                    text += '.'

                # Speaker differentiation (simplified implementation)
                # In a real app, we'd use a proper speaker diarization model
                if len(self.texts) > 0 and time.time() - self.last_timestamp > 3:
                    self.current_speaker = 1 - self.current_speaker  # Toggle between speakers

                # Store the transcribed text with timestamp and speaker info
                time_str = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
                full_text = f"[{time_str}] Speaker {self.current_speaker + 1}: {text}"

                self.timestamps.append(timestamp)
                self.texts.append(text)
                self.speakers.append(self.current_speaker)
                self.last_timestamp = timestamp

                # Emit the transcribed text to update the UI
                self.update_signal.emit(full_text, timestamp - self.timestamps[0])

            except sr.UnknownValueError:
                pass
            except Exception as e:
                print(f"Error processing audio: {e}")

    def stop(self):
        self.is_recording = False
        self.wait()

        # Combine all texts into a final transcript
        final_transcript = "\n".join([f"[{datetime.fromtimestamp(ts).strftime('%H:%M:%S')}] Speaker {spk + 1}: {txt}"
                                      for ts, txt, spk in zip(self.timestamps, self.texts, self.speakers)])

        self.finished_signal.emit(final_transcript)


# Sentiment Analysis Chart
class SentimentChart(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super(SentimentChart, self).__init__(fig)
        self.setParent(parent)
        self.timestamps = []
        self.sentiments = []
        self.ax.set_title('Sentiment Analysis')
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Sentiment (-1 to 1)')
        self.ax.set_ylim(-1, 1)
        self.line, = self.ax.plot(self.timestamps, self.sentiments, '-o', color='blue')

    def update_sentiment(self, text, timestamp):
        sentiment = TextBlob(text).sentiment.polarity
        self.timestamps.append(timestamp)
        self.sentiments.append(sentiment)

        self.ax.set_xlim(0, max(self.timestamps) + 5 if self.timestamps else 10)
        self.line.set_data(self.timestamps, self.sentiments)
        self.draw()


# Word Cloud Widget
class WordCloudWidget(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super(WordCloudWidget, self).__init__(fig)
        self.setParent(parent)
        self.texts = []
        self.ax.set_title('Word Cloud')

    def update_wordcloud(self, text):
        self.texts.append(text)
        all_text = " ".join(self.texts)

        if all_text.strip():
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_text)
            self.ax.clear()
            self.ax.imshow(wordcloud, interpolation='bilinear')
            self.ax.axis('off')
            self.draw()


# Main Application Window
class VoiceCraftApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VoiceCraft - Speech-to-Text Application")
        self.setGeometry(100, 100, 1200, 800)

        self.recorder = None
        self.current_language = "en-US"
        self.current_domain = "General"
        self.session_data = {}
        self.current_session_id = None
        self.is_recording = False

        self.init_ui()
        self.setup_shortcuts()

    def init_ui(self):
        # Main layout
        main_layout = QHBoxLayout()

        # Left sidebar
        left_sidebar = QWidget()
        left_layout = QVBoxLayout(left_sidebar)
        left_layout.setContentsMargins(5, 5, 5, 5)

        # Sessions section
        sessions_label = QLabel("Saved Sessions")
        self.sessions_list = QListWidget()
        self.sessions_list.itemClicked.connect(self.load_session)

        # Version history
        history_label = QLabel("Version History")
        self.history_tree = QTreeWidget()
        self.history_tree.setHeaderLabels(["Time", "Duration"])

        left_layout.addWidget(sessions_label)
        left_layout.addWidget(self.sessions_list)
        left_layout.addSpacing(20)
        left_layout.addWidget(history_label)
        left_layout.addWidget(self.history_tree)

        # Center panel
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(10, 10, 10, 10)

        # Header controls
        header_layout = QHBoxLayout()

        # Record/Stop buttons
        self.record_button = QPushButton("🎤 Record")
        self.record_button.clicked.connect(self.toggle_recording)
        self.record_button.setMinimumSize(80, 40)

        # Language selection
        lang_label = QLabel("Language:")
        self.language_combo = QComboBox()
        for lang in LANGUAGES.keys():
            self.language_combo.addItem(lang)

        # Domain selection
        domain_label = QLabel("Domain:")
        self.domain_combo = QComboBox()
        for domain in DOMAIN_VOCABULARIES.keys():
            self.domain_combo.addItem(domain)

        # Display speed
        speed_label = QLabel("Display Speed:")
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 5)
        self.speed_slider.setValue(3)

        header_layout.addWidget(self.record_button)
        header_layout.addSpacing(10)
        header_layout.addWidget(lang_label)
        header_layout.addWidget(self.language_combo)
        header_layout.addSpacing(10)
        header_layout.addWidget(domain_label)
        header_layout.addWidget(self.domain_combo)
        header_layout.addSpacing(10)
        header_layout.addWidget(speed_label)
        header_layout.addWidget(self.speed_slider)

        # Text display area
        font_layout = QHBoxLayout()
        font_label = QLabel("Font:")
        self.font_combo = QFontComboBox()
        size_label = QLabel("Size:")
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(12)
        self.font_size.valueChanged.connect(self.update_font)
        self.font_combo.currentFontChanged.connect(self.update_font)

        font_layout.addWidget(font_label)
        font_layout.addWidget(self.font_combo)
        font_layout.addWidget(size_label)
        font_layout.addWidget(self.font_size)
        font_layout.addStretch()

        # Text area
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)

        # Audio timeline (simplified representation)
        self.timeline_label = QLabel("Audio Timeline: 0:00 / 0:00")

        center_layout.addLayout(header_layout)
        center_layout.addSpacing(10)
        center_layout.addLayout(font_layout)
        center_layout.addWidget(self.text_edit)
        center_layout.addWidget(self.timeline_label)

        # Right sidebar
        right_sidebar = QWidget()
        right_layout = QVBoxLayout(right_sidebar)

        # AI analysis tools
        analysis_label = QLabel("AI Analysis Tools")

        # Create tabs for different analysis tools
        analysis_tabs = QTabWidget()

        # Sentiment graph
        sentiment_tab = QWidget()
        sentiment_layout = QVBoxLayout(sentiment_tab)
        self.sentiment_chart = SentimentChart(width=4, height=3)
        sentiment_layout.addWidget(self.sentiment_chart)

        # Word cloud
        wordcloud_tab = QWidget()
        wordcloud_layout = QVBoxLayout(wordcloud_tab)
        self.wordcloud_widget = WordCloudWidget(width=4, height=3)
        wordcloud_layout.addWidget(self.wordcloud_widget)

        # Stats tab
        stats_tab = QWidget()
        stats_layout = QVBoxLayout(stats_tab)
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        stats_layout.addWidget(self.stats_text)

        analysis_tabs.addTab(sentiment_tab, "Sentiment")
        analysis_tabs.addTab(wordcloud_tab, "Word Cloud")
        analysis_tabs.addTab(stats_tab, "Statistics")

        right_layout.addWidget(analysis_label)
        right_layout.addWidget(analysis_tabs)

        # Create splitter for resizable panels
        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.addWidget(left_sidebar)
        splitter1.addWidget(center_panel)
        splitter1.addWidget(right_sidebar)

        # Set default sizes
        splitter1.setSizes([200, 600, 300])

        main_layout.addWidget(splitter1)

        # Create central widget and set main layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready. Storage available: 2.5 GB")

        # Set up menu bar
        self.setup_menu()

    def setup_menu(self):
        # Create menu bar
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        new_session = QAction("New Session", self)
        new_session.setShortcut("Ctrl+N")
        new_session.triggered.connect(self.new_session)
        file_menu.addAction(new_session)

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_session)
        file_menu.addAction(save_action)

        export_action = QAction("Export as TXT", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_txt)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo_last)
        edit_menu.addAction(undo_action)

        clear_action = QAction("Clear All", self)
        clear_action.triggered.connect(self.clear_all)
        edit_menu.addAction(clear_action)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")

        report_action = QAction("Generate AI Report", self)
        report_action.triggered.connect(self.generate_report)
        tools_menu.addAction(report_action)

    def setup_shortcuts(self):
        # Record/stop shortcut (Space)
        record_shortcut = QShortcut(Qt.Key_Space, self)
        record_shortcut.activated.connect(self.toggle_recording)

        # Save shortcut (Ctrl+S)
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_session)

        # Undo shortcut (Ctrl+Z)
        undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        undo_shortcut.activated.connect(self.undo_last)

    def update_font(self):
        font = self.font_combo.currentFont()
        font.setPointSize(self.font_size.value())
        self.text_edit.setFont(font)

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        if self.is_recording:
            return

        # Create a new session if needed
        if not self.current_session_id:
            self.new_session()

        # Update UI
        self.record_button.setText("⏹️ Stop")
        self.is_recording = True

        # Get current language code and domain vocabulary
        lang_text = self.language_combo.currentText()
        lang_code = LANGUAGES[lang_text]

        domain_text = self.domain_combo.currentText()
        domain_vocab = DOMAIN_VOCABULARIES[domain_text]

        # Start recording thread
        self.recorder = AudioRecorder(lang_code, domain_vocab.get(lang_code, None))
        self.recorder.update_signal.connect(self.update_transcript)
        self.recorder.finished_signal.connect(self.on_recording_finished)
        self.recorder.start()

        # Update status bar
        self.status_bar.showMessage("Recording... (Press Space to stop)")

        # Start timer for updating timeline
        self.start_time = time.time()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timeline)
        self.timer.start(100)  # Update every 100ms

    def stop_recording(self):
        if not self.is_recording:
            return

        # Update UI
        self.record_button.setText("🎤 Record")
        self.is_recording = False

        # Stop recording thread
        if self.recorder:
            self.recorder.stop()

        # Stop timer
        if hasattr(self, 'timer'):
            self.timer.stop()

        # Update status bar
        self.status_bar.showMessage("Processing transcript...")

    def update_transcript(self, text, timestamp):
        # Append new text to the text edit
        cursor = self.text_edit.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text + "\n")
        self.text_edit.setTextCursor(cursor)
        self.text_edit.ensureCursorVisible()

        # Update AI analysis tools
        self.sentiment_chart.update_sentiment(text, timestamp)
        self.wordcloud_widget.update_wordcloud(text)
        self.update_stats()

    def update_timeline(self):
        if not self.is_recording:
            return

        elapsed = time.time() - self.start_time
        minutes, seconds = divmod(int(elapsed), 60)
        self.timeline_label.setText(f"Audio Timeline: {minutes}:{seconds:02d} / ∞")

    def on_recording_finished(self, transcript):
        # Save the transcript to the current session
        if self.current_session_id:
            self.session_data[self.current_session_id]["transcript"] = transcript
            self.session_data[self.current_session_id]["duration"] = time.time() - self.start_time

            # Add to version history
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            duration = time.time() - self.start_time
            minutes, seconds = divmod(int(duration), 60)
            duration_str = f"{minutes}:{seconds:02d}"

            item = QTreeWidgetItem([timestamp, duration_str])
            self.history_tree.insertTopLevelItem(0, item)

        # Update status bar
        self.status_bar.showMessage("Recording stopped. Transcript ready.")

    def update_stats(self):
        # Get current text
        text = self.text_edit.toPlainText()

        if not text:
            return

        # Calculate simple statistics
        words = text.split()
        word_count = len(words)

        # Count frequent words (excluding common stop words)
        stop_words = set(["the", "and", "is", "in", "to", "of", "a", "for", "on", "with"])
        word_freq = {}

        for word in words:
            word = word.lower().strip(".,?!;:()")
            if word and word not in stop_words and len(word) > 1:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Sort by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

        # Update stats text
        stats = f"Word Count: {word_count}\n\n"
        stats += "Top Words:\n"

        for word, count in sorted_words[:10]:
            stats += f"• {word}: {count}\n"

        self.stats_text.setText(stats)

    def new_session(self):
        # Create a new session ID based on timestamp
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_session_id = session_id

        # Initialize session data
        self.session_data[session_id] = {
            "name": f"Session {len(self.session_data) + 1}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "transcript": "",
            "language": self.language_combo.currentText(),
            "duration": 0
        }

        # Add to sessions list
        self.sessions_list.addItem(self.session_data[session_id]["name"])

        # Clear text edit and history
        self.text_edit.clear()
        self.history_tree.clear()

        # Reset analysis tools
        self.sentiment_chart.timestamps = []
        self.sentiment_chart.sentiments = []
        self.sentiment_chart.line.set_data([], [])
        self.sentiment_chart.draw()

        self.wordcloud_widget.texts = []
        self.wordcloud_widget.ax.clear()
        self.wordcloud_widget.ax.set_title('Word Cloud')
        self.wordcloud_widget.draw()

        self.stats_text.clear()

        # Update status bar
        self.status_bar.showMessage(f"New session created: {self.session_data[session_id]['name']}")

    def save_session(self):
        if not self.current_session_id:
            self.status_bar.showMessage("No active session to save")
            return

        # In a real application, we would save to a file or database
        self.status_bar.showMessage(f"Session {self.session_data[self.current_session_id]['name']} saved")

    def export_txt(self):
        if not self.current_session_id or not self.text_edit.toPlainText():
            self.status_bar.showMessage("No transcript to export")
            return

        # Get file path from dialog
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Transcript",
                                                   f"{self.session_data[self.current_session_id]['name']}.txt",
                                                   "Text Files (*.txt)")

        if not file_path:
            return

        # Write transcript to file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.text_edit.toPlainText())
            self.status_bar.showMessage(f"Transcript exported to {file_path}")
        except Exception as e:
            self.status_bar.showMessage(f"Error exporting transcript: {e}")

    def load_session(self, item):
        # Find session by name
        session_name = item.text()
        session_id = None

        for sid, data in self.session_data.items():
            if data["name"] == session_name:
                session_id = sid
                break

        if not session_id:
            return

        # Set current session
        self.current_session_id = session_id

        # Load transcript
        self.text_edit.setText(self.session_data[session_id]["transcript"])

        # Set language
        index = self.language_combo.findText(self.session_data[session_id]["language"])
        if index >= 0:
            self.language_combo.setCurrentIndex(index)

        # Update status bar
        self.status_bar.showMessage(f"Loaded session: {session_name}")

    def undo_last(self):
        # In a real application, this would implement proper undo functionality
        # For this demo, we'll just remove the last line of text
        text = self.text_edit.toPlainText()
        lines = text.split("\n")

        if len(lines) > 1:
            self.text_edit.setText("\n".join(lines[:-2]))
            self.status_bar.showMessage("Last text segment removed")

    def clear_all(self):
        self.text_edit.clear()
        self.status_bar.showMessage("Transcript cleared")

    def generate_report(self):
        if not self.text_edit.toPlainText():
            self.status_bar.showMessage("No transcript data to generate report")
            return

        # In a real application, this would generate a detailed AI report
        # For this demo, we'll just display a message
        self.status_bar.showMessage("AI Report generated (would be saved in a real application)")


# Application entry point
def main():
    app = QApplication(sys.argv)
    window = VoiceCraftApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()