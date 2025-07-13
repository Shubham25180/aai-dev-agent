import sys
import requests
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QStatusBar,
    QLineEdit, QPushButton, QTextEdit, QHBoxLayout
)
from PyQt6.QtCore import QTimer, Qt
import threading
from voice.always_on_audio import AlwaysOnAudioPipeline
import time

class LLMStatusWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LLM/Ollama Status + Chat + Voice Demo")
        self.setMinimumSize(500, 500)
        self.status_label = QLabel("Checking LLM status...", self)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.status_label.font()
        font.setPointSize(16)
        self.status_label.setFont(font)
        # Chat area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message and press Enter or Send...")
        self.send_button = QPushButton("Send")
        self.send_button.setDefault(True)
        self.send_button.clicked.connect(self.send_message)
        self.input_field.returnPressed.connect(self.send_message)
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.chat_display)
        layout.addLayout(input_layout)
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Initializing...")
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_ollama_status)
        self.timer.start(5000)
        self.check_ollama_status()
        # Start always-on audio pipeline
        self.audio_pipeline = AlwaysOnAudioPipeline(
            on_transcript=self.on_voice_transcript
        )
        self.audio_pipeline.start()
        self.status_bar.showMessage("Voice pipeline started. Waiting for wake word...")

    def check_ollama_status(self):
        print("[LLM DEMO] Checking Ollama status...")
        try:
            r = requests.get("http://localhost:11434/api/tags", timeout=2)
            if r.status_code == 200:
                self.status_label.setText("LLM: <span style='color:#6fff6f;'>Connected</span>")
                self.status_bar.showMessage("LLM/Ollama is connected.")
                print("[LLM DEMO] Ollama is connected.")
            else:
                self.status_label.setText("LLM: <span style='color:#ff6f6f;'>Disconnected</span>")
                self.status_bar.showMessage(f"LLM/Ollama returned status {r.status_code}.")
                print(f"[LLM DEMO] Ollama returned status {r.status_code}.")
        except Exception as e:
            self.status_label.setText("LLM: <span style='color:#ff6f6f;'>Disconnected</span>")
            self.status_bar.showMessage("LLM/Ollama not connected.")
            print(f"[LLM DEMO] Ollama not connected: {e}")

    def on_voice_transcript(self, transcript, whisper_time, total_time):
        # Display transcript and timings in chat
        self.chat_display.append(f"<b>Voice:</b> {transcript} <span style='font-size:11px;color:#aaa;'>(Whisper: {whisper_time:.2f}s)</span>")
        self.status_bar.showMessage(f"Voice transcript received. Whisper: {whisper_time:.2f}s")
        # Send to LLM and display response
        threading.Thread(target=self.llm_request_with_timing, args=(transcript, whisper_time), daemon=True).start()

    def send_message(self):
        text = self.input_field.text().strip()
        if not text:
            return
        self.chat_display.append(f"<b>You:</b> {text}")
        self.input_field.clear()
        threading.Thread(target=self.llm_request, args=(text,), daemon=True).start()

    def llm_request(self, text):
        self.llm_request_with_timing(text, None)

    def llm_request_with_timing(self, text, whisper_time):
        self.status_bar.showMessage("Sending to LLM...")
        print(f"[LLM DEMO] Sending to LLM: {text}")
        start = time.time()
        try:
            payload = {
                "model": "llama3.2:3b",
                "prompt": text,
                "stream": False
            }
            r = requests.post("http://localhost:11434/api/generate", json=payload, timeout=30)
            llm_time = time.time() - start
            if r.status_code == 200:
                response = r.json().get("response", "(no response)")
                if whisper_time is not None:
                    self.append_llm_response(response, llm_time, whisper_time)
                else:
                    self.append_llm_response(response, llm_time)
                print(f"[LLM DEMO] LLM response: {response}")
                self.status_bar.showMessage(f"LLM response received. LLM: {llm_time:.2f}s")
            else:
                self.append_llm_response(f"[Error: LLM returned status {r.status_code}]", llm_time, whisper_time)
                print(f"[LLM DEMO] LLM returned status {r.status_code}.")
                self.status_bar.showMessage(f"LLM error: {r.status_code}")
        except Exception as e:
            self.append_llm_response(f"[Error: {e}]", 0, whisper_time)
            print(f"[LLM DEMO] LLM request error: {e}")
            self.status_bar.showMessage("LLM request failed.")

    def append_llm_response(self, response, llm_time, whisper_time=None):
        if whisper_time is not None:
            self.chat_display.append(f"<b>LLM:</b> {response} <span style='font-size:11px;color:#aaa;'>(LLM: {llm_time:.2f}s, Whisper: {whisper_time:.2f}s)</span>")
        else:
            self.chat_display.append(f"<b>LLM:</b> {response} <span style='font-size:11px;color:#aaa;'>(LLM: {llm_time:.2f}s)</span>")


def main():
    app = QApplication(sys.argv)
    window = LLMStatusWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 