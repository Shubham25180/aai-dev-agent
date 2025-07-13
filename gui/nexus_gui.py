#!/usr/bin/env python3
"""
NEXUS AI Agent - PyQt6 GUI Interface

A modern, ChatGPT-style desktop application for the NEXUS AI development agent.
Features: chat interface, voice controls, automation toggles, memory management,
and real-time integration with the agent's conversational brain.
"""

import sys
import os
import asyncio
import threading
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import requests

# PyQt6 imports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QLineEdit, QPushButton, QLabel, QCheckBox, QSlider,
    QGroupBox, QTabWidget, QScrollArea, QFrame, QSplitter, QComboBox,
    QProgressBar, QStatusBar, QMenuBar, QMenu, QMessageBox,
    QFileDialog, QSystemTrayIcon, QToolButton, QButtonGroup
)
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve,
    QRect, QSize, QPoint
)
from PyQt6.QtGui import (
    QFont, QIcon, QPixmap, QPalette, QColor, QTextCursor, QKeySequence,
    QAction, QFontMetrics
)

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# NEXUS imports
from agents.conversational_brain import ConversationalBrain
from agents.hybrid_llm_connector import HybridLLMConnector
from voice.always_on_audio import AlwaysOnAudioPipeline
from utils.logger import get_action_logger, get_error_logger
from executor.gui_ops import GuiOps
from gui_hybrid.action_router import ActionRouter
# Remove Vision import
# from gui_hybrid.vision import Vision
from gui_hybrid.llm_planner import LLMPlanner
from gui_hybrid.executor import Executor


class ChatWidget(QWidget):
    """Chat interface widget with message history."""
    
    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window  # Store direct reference to main window
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the chat interface UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMinimumHeight(400)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #fafafa;
                border: none;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                padding: 10px;
            }
        """)
        
        # Input area
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(10, 10, 10, 10)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.setMinimumHeight(40)
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #232323;
                color: #fafafa;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #fafafa;
            }
        """)
        
        self.send_button = QPushButton("Send")
        self.send_button.setMinimumHeight(40)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #fafafa;
                color: #1a1a1a;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        
        layout.addWidget(self.chat_display)
        layout.addLayout(input_layout)
        
        # Connect signals
        self.send_button.clicked.connect(self.send_message)
        self.input_field.returnPressed.connect(self.send_message)
        
    def add_message(self, text: str, sender: str = "User", timestamp: str = None):
        """Add a message to the chat display."""
        if timestamp is None:
            timestamp = datetime.now().strftime("%H:%M")
            
        # Format message based on sender
        if sender.lower() == "user":
            message_html = f"""
                <div style="margin: 10px 0; text-align: right;">
                    <div style="display: inline-block; background-color: #fafafa; color: #1a1a1a; 
                                padding: 8px 12px; border-radius: 12px; max-width: 70%; 
                                text-align: left; font-size: 14px;">
                        {text}
                    </div>
                    <div style="font-size: 11px; color: #888; margin-top: 4px;">{timestamp}</div>
                </div>
            """
        else:
            message_html = f"""
                <div style="margin: 10px 0; text-align: left;">
                    <div style="display: inline-block; background-color: #232323; color: #fafafa; 
                                padding: 8px 12px; border-radius: 12px; max-width: 70%; 
                                font-size: 14px;">
                        {text}
                    </div>
                    <div style="font-size: 11px; color: #888; margin-top: 4px;">{timestamp}</div>
                </div>
            """
        
        # Append to chat display
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.chat_display.setTextCursor(cursor)
        self.chat_display.insertHtml(message_html)
        
        # Scroll to bottom
        scrollbar = self.chat_display.verticalScrollBar()
        if scrollbar:
            scrollbar.setValue(scrollbar.maximum())
    
    def send_message(self):
        """Send the current message."""
        text = self.input_field.text().strip()
        if text:
            self.add_message(text, "User")
            self.input_field.clear()
            # Call main window method directly
            if self.main_window:
                self.main_window.process_user_input(text)

    # Add a method to ChatWidget for streaming tokens
    def stream_message(self, tokens, sender="NEXUS"):
        """Append tokens to the chat display as they arrive (GPT-style, in-place update)."""
        import string
        buffer = ""
        # Insert a new message bubble for streaming
        timestamp = datetime.now().strftime("%H:%M")
        # Add an empty message first
        self.add_message("", sender, timestamp)
        # Find the end position of the last message
        for token in tokens:
            # Add a space before the token unless it's punctuation or buffer is empty
            if buffer and token not in string.punctuation:
                buffer += " "
            buffer += token
            # Update the last message in the chat display
            self.chat_display.moveCursor(QTextCursor.MoveOperation.End)
            # Remove the last message (assumes it's the streaming one)
            self.chat_display.undo()
            # Re-insert the updated message
            message_html = f"""
                <div style='margin: 10px 0; text-align: left;'>
                    <div style='display: inline-block; background-color: #232323; color: #fafafa; padding: 8px 12px; border-radius: 12px; max-width: 70%; font-size: 14px;'>
                        {buffer}
                    </div>
                    <div style='font-size: 11px; color: #888; margin-top: 4px;'>{timestamp}</div>
                </div>
            """
            self.chat_display.insertHtml(message_html)
            self.chat_display.ensureCursorVisible()
            QApplication.processEvents()


class ControlPanel(QWidget):
    """Control panel with toggles and settings."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the control panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Voice Controls
        voice_group = QGroupBox("Voice Controls")
        voice_layout = QVBoxLayout(voice_group)
        
        self.voice_enabled = QCheckBox("Enable Voice Recognition")
        self.voice_enabled.setChecked(True)
        
        self.wake_word_enabled = QCheckBox("Enable Wake Word ('nexus')")
        self.wake_word_enabled.setChecked(True)
        
        self.tts_enabled = QCheckBox("Enable Text-to-Speech")
        self.tts_enabled.setChecked(True)
        
        voice_layout.addWidget(self.voice_enabled)
        voice_layout.addWidget(self.wake_word_enabled)
        voice_layout.addWidget(self.tts_enabled)
        
        # Automation Controls
        auto_group = QGroupBox("Automation Controls")
        auto_layout = QVBoxLayout(auto_group)
        
        self.auto_mode = QCheckBox("Autonomous Mode (No Permission Required)")
        self.auto_mode.setChecked(True)
        
        self.reflex_mode = QCheckBox("Reflex Mode (Auto-Retry Failed Tasks)")
        self.reflex_mode.setChecked(True)
        
        self.vision_enabled = QCheckBox("Enable Vision (OCR/YOLO)")
        self.vision_enabled.setChecked(True)
        
        auto_layout.addWidget(self.auto_mode)
        auto_layout.addWidget(self.reflex_mode)
        auto_layout.addWidget(self.vision_enabled)
        
        # Memory Controls
        memory_group = QGroupBox("Memory Controls")
        memory_layout = QVBoxLayout(memory_group)
        
        self.memory_enabled = QCheckBox("Enable Memory Management")
        self.memory_enabled.setChecked(True)
        
        self.auto_logging = QCheckBox("Automatic Action Logging")
        self.auto_logging.setChecked(True)
        
        memory_layout.addWidget(self.memory_enabled)
        memory_layout.addWidget(self.auto_logging)
        
        # Voice Settings
        voice_settings_group = QGroupBox("Voice Settings")
        voice_settings_layout = QVBoxLayout(voice_settings_group)
        
        # Voice selection
        voice_layout = QHBoxLayout()
        voice_layout.addWidget(QLabel("TTS Voice:"))
        self.voice_combo = QComboBox()
        self.voice_combo.addItems(["edge-tts", "pyttsx3", "Windows TTS"])
        voice_layout.addWidget(self.voice_combo)
        voice_settings_layout.addLayout(voice_layout)
        
        # Volume control
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("Volume:"))
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        volume_layout.addWidget(self.volume_slider)
        voice_settings_layout.addLayout(volume_layout)
        
        # VAD Aggressiveness
        vad_layout = QHBoxLayout()
        vad_layout.addWidget(QLabel("VAD Aggressiveness:"))
        self.vad_slider = QSlider(Qt.Orientation.Horizontal)
        self.vad_slider.setRange(0, 3)
        self.vad_slider.setValue(0)  # Default to 0 (least aggressive)
        self.vad_slider.setTickInterval(1)
        self.vad_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        vad_layout.addWidget(self.vad_slider)
        voice_settings_layout.addLayout(vad_layout)
        self.vad_slider.valueChanged.connect(self.on_vad_aggressiveness_changed)

        # Add all groups to main layout
        layout.addWidget(voice_group)
        layout.addWidget(auto_group)
        layout.addWidget(memory_group)
        layout.addWidget(voice_settings_group)
        layout.addStretch()
        
        # Connect signals
        self.voice_enabled.toggled.connect(self.on_voice_toggled)
        self.wake_word_enabled.toggled.connect(self.on_wake_word_toggled)
        self.tts_enabled.toggled.connect(self.on_tts_toggled)
        self.auto_mode.toggled.connect(self.on_auto_mode_toggled)
        self.reflex_mode.toggled.connect(self.on_reflex_mode_toggled)
        self.vision_enabled.toggled.connect(self.on_vision_toggled)
        self.memory_enabled.toggled.connect(self.on_memory_toggled)
        self.auto_logging.toggled.connect(self.on_auto_logging_toggled)
        
    def on_voice_toggled(self, enabled: bool):
        """Handle voice toggle."""
        if hasattr(self.parent().parent().parent(), 'toggle_voice'):
            self.parent().parent().parent().toggle_voice(enabled)
    
    def on_wake_word_toggled(self, enabled: bool):
        """Handle wake word toggle."""
        if hasattr(self.parent().parent().parent(), 'toggle_wake_word'):
            self.parent().parent().parent().toggle_wake_word(enabled)
    
    def on_tts_toggled(self, enabled: bool):
        """Handle TTS toggle."""
        if hasattr(self.parent().parent().parent(), 'toggle_tts'):
            self.parent().parent().parent().toggle_tts(enabled)
    
    def on_auto_mode_toggled(self, enabled: bool):
        """Handle autonomous mode toggle."""
        if hasattr(self.parent().parent().parent(), 'toggle_auto_mode'):
            self.parent().parent().parent().toggle_auto_mode(enabled)
    
    def on_reflex_mode_toggled(self, enabled: bool):
        """Handle reflex mode toggle."""
        if hasattr(self.parent().parent().parent(), 'toggle_reflex_mode'):
            self.parent().parent().parent().toggle_reflex_mode(enabled)
    
    def on_vision_toggled(self, enabled: bool):
        """Handle vision toggle."""
        if hasattr(self.parent().parent().parent(), 'toggle_vision'):
            self.parent().parent().parent().toggle_vision(enabled)
    
    def on_memory_toggled(self, enabled: bool):
        """Handle memory toggle."""
        if hasattr(self.parent().parent().parent(), 'toggle_memory'):
            self.parent().parent().parent().toggle_memory(enabled)
    
    def on_auto_logging_toggled(self, enabled: bool):
        """Handle auto logging toggle."""
        if hasattr(self.parent().parent().parent(), 'toggle_auto_logging'):
            self.parent().parent().parent().toggle_auto_logging(enabled)

    def on_vad_aggressiveness_changed(self, value):
        # Call main window method to update VAD
        if self.parent() and hasattr(self.parent().parent(), 'set_vad_aggressiveness'):
            self.parent().parent().set_vad_aggressiveness(value)


class StatusPanel(QWidget):
    """Status panel showing system status and logs."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the status panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Status indicators
        status_group = QGroupBox("System Status")
        status_layout = QVBoxLayout(status_group)
        
        # LLM Status
        llm_layout = QHBoxLayout()
        self.llm_status = QLabel("LLM: Disconnected")
        self.llm_status.setStyleSheet("color: #ff6f6f; font-weight: bold;")
        llm_layout.addWidget(self.llm_status)
        status_layout.addLayout(llm_layout)
        
        # Voice Status
        voice_layout = QHBoxLayout()
        self.voice_status = QLabel("Voice: Disabled")
        self.voice_status.setStyleSheet("color: #ff6f6f; font-weight: bold;")
        voice_layout.addWidget(self.voice_status)
        status_layout.addLayout(voice_layout)
        
        # Memory Status
        memory_layout = QHBoxLayout()
        self.memory_status = QLabel("Memory: Disabled")
        self.memory_status.setStyleSheet("color: #ff6f6f; font-weight: bold;")
        memory_layout.addWidget(self.memory_status)
        status_layout.addLayout(memory_layout)
        
        # Recent logs
        logs_group = QGroupBox("Recent Activity")
        logs_layout = QVBoxLayout(logs_group)
        
        self.log_display = QTextEdit()
        self.log_display.setMaximumHeight(200)
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #fafafa;
                border: 1px solid #333;
                border-radius: 6px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                padding: 5px;
            }
        """)
        
        logs_layout.addWidget(self.log_display)
        
        layout.addWidget(status_group)
        layout.addWidget(logs_group)
        
    def update_status(self, component: str, status: str, color: str = "#fafafa"):
        """Update status for a component."""
        if component == "llm":
            self.llm_status.setText(f"LLM: {status}")
            self.llm_status.setStyleSheet(f"color: {color}; font-weight: bold;")
        elif component == "voice":
            self.voice_status.setText(f"Voice: {status}")
            self.voice_status.setStyleSheet(f"color: {color}; font-weight: bold;")
        elif component == "memory":
            self.memory_status.setText(f"Memory: {status}")
            self.memory_status.setStyleSheet(f"color: {color}; font-weight: bold;")
    
    def add_log(self, message: str, level: str = "INFO"):
        """Add a log message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = "#fafafa"  # Default white
        
        if level == "ERROR":
            color = "#ff6f6f"
        elif level == "WARNING":
            color = "#ffe066"
        elif level == "SUCCESS":
            color = "#6fff6f"
        
        log_html = f'<span style="color: {color};">[{timestamp}] {level}: {message}</span><br>'
        
        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_display.setTextCursor(cursor)
        self.log_display.insertHtml(log_html)
        
        # Keep only last 50 lines
        lines = self.log_display.toPlainText().split('\n')
        if len(lines) > 50:
            self.log_display.setPlainText('\n'.join(lines[-50:]))


class NexusMainWindow(QMainWindow):
    """Main window for the NEXUS AI Agent GUI."""
    
    def __init__(self):
        super().__init__()
        self.brain = None
        self.action_router = None
        self.llm_planner = None
        self.executor = None
        self.gui_ops = None
        self.audio_pipeline = None  # <-- Add reference to audio pipeline
        self.vad_aggressiveness = 0
        
        # Add thread safety for voice processing
        self._voice_processing_lock = threading.Lock()
        self._voice_processing = False
        
        # Configuration
        self.config = {
            'voice_enabled': True,
            'wake_word_enabled': True,
            'tts_enabled': True,
            'auto_mode': True,
            'reflex_mode': True,
            'vision_enabled': True,
            'memory_enabled': True,
            'auto_logging': True
        }
        
        self.setup_ui()
        self.setup_menu()
        self.initialize_agent()
        self.setup_status_timer()
        self.start_audio_pipeline()  # <-- Start audio pipeline
        
    def setup_ui(self):
        """Setup the main window UI."""
        self.setWindowTitle("NEXUS AI Development Agent")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Load stylesheet
        stylesheet_path = os.path.join(os.path.dirname(__file__), 'nexus_gui.qss')
        if os.path.exists(stylesheet_path):
            with open(stylesheet_path, 'r') as f:
                self.setStyleSheet(f.read())
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Chat and Controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        
        # Chat widget
        self.chat_widget = ChatWidget(main_window=self)
        left_layout.addWidget(self.chat_widget)
        
        # Add to splitter
        splitter.addWidget(left_panel)
        
        # Right panel - Controls and Status
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # Tab widget for right panel
        self.tab_widget = QTabWidget()
        
        # Control panel tab
        self.control_panel = ControlPanel()
        self.tab_widget.addTab(self.control_panel, "Controls")
        
        # Status panel tab
        self.status_panel = StatusPanel()
        self.tab_widget.addTab(self.status_panel, "Status")
        
        right_layout.addWidget(self.tab_widget)
        
        # Add to splitter
        splitter.addWidget(right_panel)
        
        # Set splitter proportions (70% chat, 30% controls)
        splitter.setSizes([980, 420])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("NEXUS AI Agent - Ready")
        
        # Add welcome message
        self.chat_widget.add_message(
            "Hello! I'm NEXUS, your AI development assistant. I can help you with coding, automation, and much more. What would you like to work on today?",
            "NEXUS"
        )
        
    def setup_menu(self):
        """Setup the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        # Export chat action
        export_action = QAction("Export Chat", self)
        export_action.setShortcut(QKeySequence.StandardKey.Save)
        export_action.triggered.connect(self.export_chat)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        # Memory management
        memory_action = QAction("Memory Management", self)
        memory_action.triggered.connect(self.show_memory_manager)
        tools_menu.addAction(memory_action)
        
        # Settings
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        # About action
        about_action = QAction("About NEXUS", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def initialize_agent(self):
        """Initialize the NEXUS agent components."""
        try:
            self.status_bar.showMessage("Initializing NEXUS agent...")
            self.status_panel.add_log("Initializing NEXUS agent...", "INFO")
            
            # Initialize LLM connector
            self.llm_connector = HybridLLMConnector({})
            self.status_panel.update_status("llm", "Connected", "#6fff6f")
            self.status_panel.add_log("LLM connector initialized", "SUCCESS")
            
            # Initialize conversational brain
            self.brain = ConversationalBrain(
                config=self.config,
                llm_connector=self.llm_connector,
                memory_manager=None # Memory layer removed
            )
            self.status_panel.add_log("Conversational brain initialized", "SUCCESS")
            
            # Initialize automation components
            self.action_router = ActionRouter()
            # Remove or comment out Vision initialization
            # self.vision = Vision()
            self.llm_planner = LLMPlanner()
            self.executor = Executor()
            self.gui_ops = GuiOps(app_state={})
            
            self.status_panel.add_log("Automation components initialized", "SUCCESS")
            
            # Initialize voice system
            # The always-on audio pipeline is now the primary voice input method.
            # No specific initialization or signal connections for voice are needed here
            # as the audio pipeline handles its own input and output.
            
            self.status_bar.showMessage("NEXUS agent ready")
            self.status_panel.add_log("NEXUS agent initialization complete", "SUCCESS")
            
        except Exception as e:
            self.status_panel.add_log(f"Initialization error: {str(e)}", "ERROR")
            self.status_bar.showMessage("Initialization failed")
    
    def setup_status_timer(self):
        """Setup timer for periodic status updates."""
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(5000)  # Update every 5 seconds
        self.update_status()  # Initial check

    def check_ollama_status(self):
        """Check if Ollama/LLM is connected."""
        try:
            r = requests.get("http://localhost:11434/api/tags", timeout=2)
            if r.status_code == 200:
                return True
            else:
                print(f"[LLM] Ollama returned status {r.status_code}.")
                return False
        except Exception as e:
            print(f"[LLM] Ollama not connected: {e}")
            return False

    def update_status(self):
        """Update system status."""
        # Check LLM/Ollama connection
        llm_connected = self.check_ollama_status()
        if llm_connected:
            self.status_panel.update_status("llm", "Connected", "#6fff6f")
        else:
            self.status_panel.update_status("llm", "Disconnected", "#ff6f6f")
        # Check voice status
        if hasattr(self, 'audio_pipeline') and self.audio_pipeline and self.audio_pipeline.running:
            self.status_panel.update_status("voice", "Listening", "#6fff6f")
        else:
            self.status_panel.update_status("voice", "Disabled", "#ff6f6f")
        # Check memory status
        # Memory management removed, so this status is no longer relevant.
        # self.status_panel.update_status("memory", "Active", "#6fff6f")
        # self.status_panel.update_status("memory", "Disabled", "#ff6f6f")
    
    def process_user_input(self, text: str):
        """Process user input through the brain."""
        try:
            self.status_panel.add_log(f"Processing user input: {text[:50]}...", "INFO")
            
            # Process with brain
            if self.brain:
                # Run in thread to avoid blocking UI
                threading.Thread(
                    target=self._process_input_thread,
                    args=(text,),
                    daemon=True
                ).start()
            else:
                self.chat_widget.add_message("Sorry, the brain is not initialized.", "NEXUS")
                
        except Exception as e:
            self.status_panel.add_log(f"Error processing input: {str(e)}", "ERROR")
            self.chat_widget.add_message("Sorry, there was an error processing your request.", "NEXUS")
    
    def _process_input_thread(self, text: str):
        """Process input in background thread."""
        try:
            print(f"[DEBUG] Sending to LLM: {text}")
            if hasattr(self.brain.llm_connector, 'stream_prompt'):
                print(f"[DEBUG] Streaming to LLM (typed): {text}")
                tokens = self.brain.llm_connector.stream_prompt(text)
                self.chat_widget.stream_message(tokens, sender="NEXUS")
                response = "".join(tokens)
            else:
                result = self.brain.process_input(text, input_type='text')
                print(f"[DEBUG] LLM result: {result}")
                response = result.get('response') or result.get('text') or 'No response generated.'
                self.chat_widget.add_message(response, "NEXUS")
            print(f"[DEBUG] Passing response to UI: {response}")
            self.status_panel.add_log("Response generated successfully", "SUCCESS")
            if self.config['tts_enabled'] and self.audio_pipeline:
                pass
        except Exception as e:
            self.status_panel.add_log(f"Brain processing error: {str(e)}", "ERROR")
            self.chat_widget.add_message("Sorry, there was an error processing your request.", "NEXUS")
    
    # Control toggle methods
    def toggle_voice(self, enabled: bool):
        """Toggle voice recognition."""
        self.config['voice_enabled'] = enabled
        # The always-on audio pipeline handles voice input, so we don't need to start/stop it here.
        # The audio pipeline's vad_mode can be adjusted.
        if enabled:
            self.audio_pipeline.set_vad_mode(self.vad_aggressiveness)
            self.status_panel.update_status("voice", "Listening", "#6fff6f")
        else:
            self.audio_pipeline.set_vad_mode(0) # Disable VAD
            self.status_panel.update_status("voice", "Disabled", "#ff6f6f")
    
    def toggle_wake_word(self, enabled: bool):
        """Toggle wake word detection."""
        self.config['wake_word_enabled'] = enabled
    
    def toggle_tts(self, enabled: bool):
        """Toggle text-to-speech."""
        self.config['tts_enabled'] = enabled
    
    def toggle_auto_mode(self, enabled: bool):
        """Toggle autonomous mode."""
        self.config['auto_mode'] = enabled
    
    def toggle_reflex_mode(self, enabled: bool):
        """Toggle reflex mode."""
        self.config['reflex_mode'] = enabled
    
    def toggle_vision(self, enabled: bool):
        """Toggle vision capabilities."""
        self.config['vision_enabled'] = enabled
    
    def toggle_memory(self, enabled: bool):
        """Toggle memory management."""
        self.config['memory_enabled'] = enabled
    
    def toggle_auto_logging(self, enabled: bool):
        """Toggle automatic logging."""
        self.config['auto_logging'] = enabled
    
    # Menu action methods
    def export_chat(self):
        """Export chat history to file."""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Chat", "", "Text Files (*.txt);;All Files (*)"
            )
            if filename:
                chat_text = self.chat_widget.chat_display.toPlainText()
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(chat_text)
                self.status_panel.add_log(f"Chat exported to {filename}", "SUCCESS")
        except Exception as e:
            self.status_panel.add_log(f"Export error: {str(e)}", "ERROR")
    
    def show_memory_manager(self):
        """Show memory management dialog."""
        QMessageBox.information(self, "Memory Management", "Memory management feature coming soon!")
    
    def show_settings(self):
        """Show settings dialog."""
        QMessageBox.information(self, "Settings", "Settings dialog coming soon!")
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self, "About NEXUS",
            "NEXUS AI Development Agent\n\n"
            "A sophisticated AI assistant for developers with voice recognition, "
            "automation capabilities, and intelligent task management.\n\n"
            "Version: 1.0.0\n"
            "Built with PyQt6 and Python"
        )
    
    def closeEvent(self, event):
        """Handle window close event."""
        try:
            # Stop audio pipeline
            if self.audio_pipeline:
                self.audio_pipeline.stop()
            
            # Save configuration
            config_path = os.path.join(os.path.dirname(__file__), 'nexus_config.json')
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            self.status_panel.add_log("NEXUS agent shutting down", "INFO")
            event.accept()
            
        except Exception as e:
            self.status_panel.add_log(f"Shutdown error: {str(e)}", "ERROR")
            event.accept()

    def start_audio_pipeline(self):
        """Start the always-on audio pipeline and connect it to the GUI."""
        def on_transcript(transcript, whisper_time, total_time):
            self.chat_widget.add_message(
                f"<b>[Voice]</b> {transcript}<br><span style='font-size:11px;color:#aaa;'>Whisper: {whisper_time:.2f}s, Total: {total_time:.2f}s</span>",
                sender="User (Voice)"
            )
            self.status_panel.add_log(f"Voice transcript: {transcript}", "INFO")
            self.process_voice_to_llm(transcript, whisper_time, total_time)
        # Stop previous pipeline if running
        if hasattr(self, 'audio_pipeline') and self.audio_pipeline:
            self.audio_pipeline.stop()
        self.audio_pipeline = AlwaysOnAudioPipeline(
            whisper_model_size='medium',
            device='cpu',
            vad_mode=2,  # Set VAD aggressiveness to 2 (more strict)
            on_transcript=on_transcript
        )
        self.audio_pipeline.start()
        self.status_panel.add_log(f"Always-on audio pipeline started (VAD aggressiveness: {self.vad_aggressiveness})", "SUCCESS")

    def process_voice_to_llm(self, transcript, whisper_time, total_time):
        """Send transcript to LLM, display response and timings, and (optionally) TTS."""
        def llm_thread():
            start = time.time()
            if self.brain:
                # Try streaming if available
                if hasattr(self.brain.llm_connector, 'stream_prompt'):
                    print(f"[DEBUG] Streaming to LLM: {transcript}")
                    tokens = self.brain.llm_connector.stream_prompt(transcript)
                    self.chat_widget.stream_message(tokens, sender="NEXUS")
                    response = "".join(tokens)
                else:
                    result = self.brain.process_input(transcript, input_type='text')
                    print(f"[DEBUG] LLM result: {result}")
                    response = result.get('response', 'No response generated.')
                    self.chat_widget.add_message(
                        f"<b>[NEXUS]</b> {response}<br><span style='font-size:11px;color:#aaa;'>LLM: {time.time()-start:.2f}s, Whisper: {whisper_time:.2f}s</span>",
                        sender="NEXUS"
                    )
            else:
                response = "Sorry, the brain is not initialized."
                self.chat_widget.add_message(response, "NEXUS")
            self.status_panel.add_log(f"LLM response: {response}", "SUCCESS")
            
            # Release the voice processing lock
            with self._voice_processing_lock:
                self._voice_processing = False
        
        # Check if we're already processing voice input
        with self._voice_processing_lock:
            if self._voice_processing:
                print("[GUI][DEBUG] Already processing voice input, skipping this transcript.")
                return
            self._voice_processing = True
        
        threading.Thread(target=llm_thread, daemon=True).start()

    def set_vad_aggressiveness(self, value):
        self.vad_aggressiveness = value
        self.start_audio_pipeline()
        self.status_panel.add_log(f"VAD aggressiveness set to {value} and audio pipeline restarted", "INFO")


# This file contains only UI widgets and layout classes.
# The main() entry point is in main.py which orchestrates everything. 