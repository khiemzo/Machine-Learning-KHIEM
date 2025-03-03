import sys
import time
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QComboBox,
                             QLabel, QTextEdit, QVBoxLayout, QHBoxLayout, QWidget,
                             QSlider, QFileDialog, QListWidget, QSplitter, QStatusBar,
                             QAction, QFontComboBox, QSpinBox, QTabWidget, QShortcut,
                             QProgressBar, QFrame)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QKeySequence, QIcon, QColor, QPalette, QFont, QLinearGradient, QBrush, QPainter
import speech_recognition as sr
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from wordcloud import WordCloud
from textblob import TextBlob
import queue
import numpy as np

# Constants - Simplified language options
LANGUAGES = {
    "English": "en-US",
    "Vietnamese": "vi-VN",
    "Korean": "ko-KR"
}

# Custom button style
BUTTON_STYLE = """
QPushButton {
    background-color: #2C3E50;
    color: white;
    border-radius: 15px;
    padding: 10px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #3498DB;
}

QPushButton:pressed {
    background-color: #1ABC9C;
}
"""

# Custom frame style
FRAME_STYLE = """
QFrame {
    border-radius: 10px;
    background-color: #ECF0F1;
}
"""

# Custom combobox style
COMBOBOX_STYLE = """
QComboBox {
    border: 2px solid #3498DB;
    border-radius: 5px;
    padding: 5px;
    background-color: white;
}

QComboBox::drop-down {
    border: 0px;
    width: 20px;
}

QComboBox QAbstractItemView {
    border: 2px solid #3498DB;
    border-radius: 5px;
    selection-background-color: #3498DB;
}
"""

# Custom text edit style
TEXTEDIT_STYLE = """
QTextEdit {
    border: 2px solid #3498DB;
    border-radius: 10px;
    padding: 10px;
    background-color: white;
    font-size: 12pt;
}
"""


# Audio Recording Thread with enhanced sensitivity
class AudioRecorder(QThread):
    finished_signal = pyqtSignal(str)
    update_signal = pyqtSignal(str, float)
    audio_level_signal = pyqtSignal(float)

    def __init__(self, language_code):
        super().__init__()
        self.language_code = language_code
        self.is_recording = False
        self.timestamps = []
        self.texts = []
        self.current_speaker = 0
        self.last_timestamp = 0
        self.recognizer = sr.Recognizer()
        self.audio_queue = queue.Queue()

        # Enhanced sensitivity settings
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 300  # Lower threshold for increased sensitivity
        self.recognizer.pause_threshold = 0.8  # Shorter pause detection for more fluid recording

    def run(self):
        self.is_recording = True
        self.last_timestamp = time.time()

        # Setup microphone
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

            while self.is_recording:
                try:
                    # Increased phrase_time_limit from 5 to 30 seconds (6x longer)
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=30)

                    # Emit audio level for visualization
                    energy = self.get_audio_energy(audio)
                    self.audio_level_signal.emit(energy)

                    self.audio_queue.put((audio, time.time()))
                    self.process_audio_queue()
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    print(f"Error while recording: {e}")

    def get_audio_energy(self, audio):
        # Calculate audio energy level for visualization
        try:
            # Convert audio data to numpy array
            data = np.frombuffer(audio.frame_data, dtype=np.int16)
            # Calculate RMS energy
            if len(data) > 0:
                energy = np.sqrt(np.mean(np.square(data))) / 32768.0  # Normalize to 0-1
                return min(energy * 5, 1.0)  # Scale and cap at 1.0
        except:
            pass
        return 0.1

    def process_audio_queue(self):
        while not self.audio_queue.empty():
            audio, timestamp = self.audio_queue.get()
            try:
                # Use a more comprehensive speech recognition approach
                text = self.recognizer.recognize_google(audio, language=self.language_code)

                # More sophisticated speaker differentiation based on energy and silence
                if len(self.texts) > 0 and time.time() - self.last_timestamp > 2.5:
                    self.current_speaker = 1 - self.current_speaker

                # Format the text with timestamp and speaker info
                time_str = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
                speaker_label = f"Speaker {self.current_speaker + 1}"
                full_text = f"[{time_str}] {speaker_label}: {text}"

                self.timestamps.append(timestamp)
                self.texts.append(text)
                self.last_timestamp = timestamp

                # Update UI
                self.update_signal.emit(full_text, timestamp - self.timestamps[0])

            except sr.UnknownValueError:
                pass
            except Exception as e:
                print(f"Error processing audio: {e}")

    def stop(self):
        self.is_recording = False
        self.wait()

        # Combine texts into final transcript with better formatting
        final_transcript = "\n\n".join(
            [f"[{datetime.fromtimestamp(ts).strftime('%H:%M:%S')}] Speaker {1 if i % 2 else 0 + 1}: {txt}"
             for i, (ts, txt) in enumerate(zip(self.timestamps, self.texts))])

        self.finished_signal.emit(final_transcript)


# Custom styled progress bar for audio visualization
class AudioLevelBar(QProgressBar):
    def __init__(self, parent=None):
        super(AudioLevelBar, self).__init__(parent)
        self.setMinimum(0)
        self.setMaximum(100)
        self.setValue(0)
        self.setTextVisible(False)
        self.setFixedHeight(20)
        self.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3498DB;
                border-radius: 5px;
                background-color: #ECF0F1;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                                  stop:0 #1ABC9C, stop:1 #3498DB);
                border-radius: 3px;
            }
        """)


# Enhanced Sentiment Analysis Chart
class SentimentChart(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super(SentimentChart, self).__init__(fig)
        self.setParent(parent)
        fig.set_facecolor('#ECF0F1')
        self.ax.set_facecolor('#F7F9F9')

        self.timestamps = []
        self.sentiments = []

        self.ax.set_title('Sentiment Analysis', fontsize=14, fontweight='bold', color='#2C3E50')
        self.ax.set_xlabel('Time (s)', fontsize=10, color='#2C3E50')
        self.ax.set_ylabel('Sentiment (-1 to 1)', fontsize=10, color='#2C3E50')
        self.ax.set_ylim(-1, 1)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.axhline(y=0, color='#7F8C8D', alpha=0.5)

        # Create color bands for sentiment zones
        self.ax.axhspan(0.3, 1, color='#2ECC71', alpha=0.2)  # Positive zone
        self.ax.axhspan(-0.3, 0.3, color='#F1C40F', alpha=0.2)  # Neutral zone
        self.ax.axhspan(-1, -0.3, color='#E74C3C', alpha=0.2)  # Negative zone

        self.line, = self.ax.plot(self.timestamps, self.sentiments, '-o', color='#3498DB', linewidth=2, markersize=8)

        # Add annotations for sentiment categories
        self.ax.text(0.02, 0.9, 'Positive', transform=self.ax.transAxes, color='#27AE60')
        self.ax.text(0.02, 0.5, 'Neutral', transform=self.ax.transAxes, color='#D35400')
        self.ax.text(0.02, 0.1, 'Negative', transform=self.ax.transAxes, color='#C0392B')

        for spine in self.ax.spines.values():
            spine.set_color('#BDC3C7')

        self.fig.tight_layout()

    def update_sentiment(self, text, timestamp):
        analysis = TextBlob(text)
        sentiment = analysis.sentiment.polarity
        subjectivity = analysis.sentiment.subjectivity

        self.timestamps.append(timestamp)
        self.sentiments.append(sentiment)

        self.ax.set_xlim(0, max(self.timestamps) + 5 if self.timestamps else 10)
        self.line.set_data(self.timestamps, self.sentiments)

        # Color-code points based on sentiment
        colors = ['#E74C3C' if s < -0.3 else '#F1C40F' if s < 0.3 else '#2ECC71' for s in self.sentiments]
        self.scatter = self.ax.scatter(self.timestamps, self.sentiments, c=colors, s=100, zorder=5)

        self.draw()

        return sentiment, subjectivity


# Enhanced Word Cloud Widget
class WordCloudWidget(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super(WordCloudWidget, self).__init__(fig)
        self.setParent(parent)
        self.texts = []

        fig.set_facecolor('#ECF0F1')
        self.ax.set_title('Word Cloud', fontsize=14, fontweight='bold', color='#2C3E50')
        self.ax.axis('off')

        # Create default empty wordcloud
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            colormap='viridis',
            contour_width=1,
            contour_color='#3498DB',
            max_font_size=100,
            min_font_size=10,
            random_state=42
        ).generate("VoiceCraft")

        self.ax.imshow(wordcloud, interpolation='bilinear')
        self.fig.tight_layout()

    def update_wordcloud(self, text):
        self.texts.append(text)
        all_text = " ".join(self.texts)

        if all_text.strip():
            wordcloud = WordCloud(
                width=800,
                height=400,
                background_color='white',
                colormap='viridis',
                contour_width=1,
                contour_color='#3498DB',
                max_font_size=100,
                min_font_size=10,
                random_state=42
            ).generate(all_text)

            self.ax.clear()
            self.ax.imshow(wordcloud, interpolation='bilinear')
            self.ax.axis('off')
            self.draw()


# Main Application Window with Enhanced UI
class VoiceCraftApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VoiceCraft Pro - Advanced Speech-to-Text Analysis")
        self.setGeometry(100, 100, 1200, 800)

        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2C3E50;
            }
            QLabel {
                color: #2C3E50;
                font-weight: bold;
                font-size: 12pt;
            }
            QListWidget {
                border: 2px solid #3498DB;
                border-radius: 10px;
                padding: 5px;
                background-color: white;
            }
            QStatusBar {
                background-color: #34495E;
                color: white;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: 2px solid #3498DB;
                border-radius: 10px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #BDC3C7;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                padding: 8px 15px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #3498DB;
                color: white;
                font-weight: bold;
            }
        """)

        self.recorder = None
        self.current_language = "en-US"
        self.session_data = {}
        self.current_session_id = None
        self.is_recording = False
        self.audio_level = 0

        # Apply theme colors
        self.theme_colors = {
            "primary": "#3498DB",
            "secondary": "#2C3E50",
            "accent": "#1ABC9C",
            "background": "#ECF0F1",
            "text": "#2C3E50"
        }

        self.init_ui()
        self.setup_shortcuts()

    def init_ui(self):
        # Main layout
        main_layout = QHBoxLayout()

        # Create a container widget with background
        container = QWidget()
        container.setStyleSheet(f"background-color: {self.theme_colors['background']};")

        # Left sidebar - Sessions list with styled frame
        left_sidebar = QFrame()
        left_sidebar.setFrameShape(QFrame.StyledPanel)
        left_sidebar.setStyleSheet(FRAME_STYLE)
        left_layout = QVBoxLayout(left_sidebar)

        sessions_label = QLabel("📁 Saved Sessions")
        sessions_label.setAlignment(Qt.AlignCenter)

        self.sessions_list = QListWidget()
        self.sessions_list.setAlternatingRowColors(True)
        self.sessions_list.itemClicked.connect(self.load_session)

        # Add new session button
        new_session_btn = QPushButton("🔍 New Session")
        new_session_btn.setStyleSheet(BUTTON_STYLE)
        new_session_btn.clicked.connect(self.new_session)

        left_layout.addWidget(sessions_label)
        left_layout.addWidget(self.sessions_list)
        left_layout.addWidget(new_session_btn)

        # Center panel - Main content with styled frame
        center_panel = QFrame()
        center_panel.setFrameShape(QFrame.StyledPanel)
        center_panel.setStyleSheet(FRAME_STYLE)
        center_layout = QVBoxLayout(center_panel)

        # Title with logo effect
        app_title = QLabel("VoiceCraft Pro")
        app_title.setStyleSheet("font-size: 24pt; color: #3498DB; font-weight: bold;")
        app_title.setAlignment(Qt.AlignCenter)

        # Record controls with visual enhancements
        control_frame = QFrame()
        control_frame.setStyleSheet("background-color: #34495E; border-radius: 15px; padding: 10px;")
        control_layout = QHBoxLayout(control_frame)

        self.record_button = QPushButton("🎤 Record")
        self.record_button.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border-radius: 20px;
                padding: 15px;
                font-weight: bold;
                font-size: 14pt;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        """)
        self.record_button.setMinimumSize(150, 50)
        self.record_button.clicked.connect(self.toggle_recording)

        lang_label = QLabel("🌐 Language:")
        lang_label.setStyleSheet("color: white; font-size: 12pt;")

        self.language_combo = QComboBox()
        self.language_combo.setStyleSheet(COMBOBOX_STYLE)
        for lang in LANGUAGES.keys():
            self.language_combo.addItem(lang)

        # Audio level indicator
        self.audio_level_bar = AudioLevelBar()

        control_layout.addWidget(self.record_button)
        control_layout.addWidget(lang_label)
        control_layout.addWidget(self.language_combo)
        control_layout.addWidget(QLabel("Audio Level:"))
        control_layout.addWidget(self.audio_level_bar)

        # Text display area with enhanced styling
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet(TEXTEDIT_STYLE)

        # Custom font for transcript
        transcript_font = QFont("Arial", 12)
        self.text_edit.setFont(transcript_font)

        # Timeline with enhanced styling
        timeline_frame = QFrame()
        timeline_frame.setStyleSheet("background-color: #34495E; border-radius: 10px; padding: 5px;")
        timeline_layout = QHBoxLayout(timeline_frame)

        self.timeline_label = QLabel("⏱️ Recording Time: 0:00 / 0:00")
        self.timeline_label.setStyleSheet("color: white; font-size: 14pt;")
        self.timeline_label.setAlignment(Qt.AlignCenter)

        timeline_layout.addWidget(self.timeline_label)

        center_layout.addWidget(app_title)
        center_layout.addWidget(control_frame)
        center_layout.addWidget(self.text_edit)
        center_layout.addWidget(timeline_frame)

        # Right sidebar - Analysis tools with styled frame
        right_sidebar = QFrame()
        right_sidebar.setFrameShape(QFrame.StyledPanel)
        right_sidebar.setStyleSheet(FRAME_STYLE)
        right_layout = QVBoxLayout(right_sidebar)

        analysis_label = QLabel("📊 Analysis Dashboard")
        analysis_label.setAlignment(Qt.AlignCenter)

        # Create tabs for analysis tools with enhanced styling
        analysis_tabs = QTabWidget()

        # Sentiment tab with enhanced visualization
        sentiment_tab = QWidget()
        sentiment_layout = QVBoxLayout(sentiment_tab)

        # Add sentiment stats
        self.sentiment_stats = QLabel("Current Sentiment: Neutral (0.0)")
        self.sentiment_stats.setAlignment(Qt.AlignCenter)
        self.sentiment_stats.setStyleSheet("font-size: 14pt; color: #3498DB;")

        self.sentiment_chart = SentimentChart(width=4, height=3)

        sentiment_layout.addWidget(self.sentiment_stats)
        sentiment_layout.addWidget(self.sentiment_chart)

        # Word cloud tab with enhanced visualization
        wordcloud_tab = QWidget()
        wordcloud_layout = QVBoxLayout(wordcloud_tab)

        wordcloud_info = QLabel("Most Common Words")
        wordcloud_info.setAlignment(Qt.AlignCenter)

        self.wordcloud_widget = WordCloudWidget(width=4, height=3)

        wordcloud_layout.addWidget(wordcloud_info)
        wordcloud_layout.addWidget(self.wordcloud_widget)

        # Add a summary tab
        summary_tab = QWidget()
        summary_layout = QVBoxLayout(summary_tab)

        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setStyleSheet(TEXTEDIT_STYLE)
        self.summary_text.setText("Session summary will appear here after recording.")

        summary_layout.addWidget(self.summary_text)

        analysis_tabs.addTab(sentiment_tab, "Sentiment")
        analysis_tabs.addTab(wordcloud_tab, "Word Cloud")
        analysis_tabs.addTab(summary_tab, "Summary")

        right_layout.addWidget(analysis_label)
        right_layout.addWidget(analysis_tabs)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_sidebar)
        splitter.addWidget(center_panel)
        splitter.addWidget(right_sidebar)

        # Set default sizes
        splitter.setSizes([200, 600, 400])

        main_layout.addWidget(splitter)

        # Create central widget and set main layout
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Status bar with enhanced styling
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready to record. Press Space or click Record to start.")

        # Set up menu bar
        self.setup_menu()

    def setup_menu(self):
        # Create menu bar with modern styling
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #34495E;
                color: white;
            }
            QMenuBar::item {
                background-color: #34495E;
                color: white;
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #3498DB;
            }
            QMenu {
                background-color: #34495E;
                color: white;
                border: 1px solid #2C3E50;
            }
            QMenu::item:selected {
                background-color: #3498DB;
            }
        """)

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
        export_action.triggered.connect(self.export_txt)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")

        clear_action = QAction("Clear Transcript", self)
        clear_action.triggered.connect(self.clear_transcript)
        tools_menu.addAction(clear_action)

        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)

    def setup_shortcuts(self):
        # Record/stop shortcut (Space)
        record_shortcut = QShortcut(Qt.Key_Space, self)
        record_shortcut.activated.connect(self.toggle_recording)

        # Save shortcut (Ctrl+S)
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_session)

        # New session shortcut (Ctrl+N)
        new_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_shortcut.activated.connect(self.new_session)

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

        # Update UI with animation
        self.record_button.setText("⏹️ Stop")
        self.record_button.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border-radius: 20px;
                padding: 15px;
                font-weight: bold;
                font-size: 14pt;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        """)

        # Start pulsating animation for record button
        self.pulse_animation = QPropertyAnimation(self.record_button, b"minimumSize")
        self.pulse_animation.setDuration(1000)
        self.pulse_animation.setLoopCount(-1)
        self.pulse_animation.setStartValue(QSize(150, 50))
        self.pulse_animation.setEndValue(QSize(160, 55))
        self.pulse_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.pulse_animation.start()

        self.is_recording = True

        # Get current language code
        lang_text = self.language_combo.currentText()
        lang_code = LANGUAGES[lang_text]

        # Start recording thread
        self.recorder = AudioRecorder(lang_code)
        self.recorder.update_signal.connect(self.update_transcript)
        self.recorder.finished_signal.connect(self.on_recording_finished)
        self.recorder.audio_level_signal.connect(self.update_audio_level)
        self.recorder.start()

        # Update status bar
        self.status_bar.showMessage("Recording... (Press Space or click Stop to end)")

        # Start timer for updating timeline
        self.start_time = time.time()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timeline)
        self.timer.start(100)  # Update every 100ms

    def update_audio_level(self, level):
        # Update the audio level visualization
        self.audio_level_bar.setValue(int(level * 100))

    def stop_recording(self):
        if not self.is_recording:
            return

        # Update UI
        self.record_button.setText("🎤 Record")
        self.record_button.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                color: white;
                border-radius: 20px;
                padding: 15px;
                font-weight: bold;
                font-size: 14pt;
            }
            QPushButton:hover {
                background-color: #27AE60;
            }
        """)

        # Stop pulsating animation
        if hasattr(self, 'pulse_animation'):
            self.pulse_animation.stop()
            self.record_button.setMinimumSize(150, 50)

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
        # Append new text to the text edit with enhanced formatting
        cursor = self.text_edit.textCursor()
        cursor.movePosition(cursor.End)

        # Format based on speaker (different colors for different speakers)
        if "Speaker 1" in text:
            self.text_edit.setTextColor(QColor("#2980B9"))  # Blue for Speaker 1
        else:
            self.text_edit.setTextColor(QColor("#16A085"))  # Green for Speaker 2

        # Bold the timestamp and speaker info
        time_parts = text.split(":", 1)
        if len(time_parts) > 1:
            header = time_parts[0] + ":"
            content = time_parts[1]

            # Insert the header in bold
            self.text_edit.setFontWeight(QFont.Bold)
            cursor.insertText(header)

            # Insert the content in normal weight
            self.text_edit.setFontWeight(QFont.Normal)
            cursor.insertText(content + "\n\n")  # Double newline for better readability
        else:
            cursor.insertText(text + "\n\n")

        self.text_edit.setTextCursor(cursor)
        self.text_edit.ensureCursorVisible()

        # Reset text color to default
        self.text_edit.setTextColor(QColor("#2C3E50"))

        # Update analysis tools
        sentiment, subjectivity = self.sentiment_chart.update_sentiment(text, timestamp)
        self.wordcloud_widget.update_wordcloud(text)

        # Update sentiment status
        sentiment_text = "Positive" if sentiment > 0.3 else "Negative" if sentiment < -0.3 else "Neutral"
        sentiment_color = "#2ECC71" if sentiment > 0.3 else "#E74C3C" if sentiment < -0.3 else "#F1C40F"
        self.sentiment_stats.setText(f"Current Sentiment: {sentiment_text} ({sentiment:.2f})")
        self.sentiment_stats.setStyleSheet(f"font-size: 14pt; color: {sentiment_color};")

        # Update summary in real-time
        self.update_summary()

    def update_timeline(self):
        if not self.is_recording:
            return

        elapsed = time.time() - self.start_time
        minutes, seconds = div