#!/usr/bin/env python3
"""
Enhanced Voice System with Dual-Model LLM Integration and Web Search
Integrates voice recognition with intelligent LLM processing and web search capabilities.
"""

import yaml
import os
import threading
import time
import asyncio
import requests
from typing import Dict, Any, Optional, Callable
from utils.logger import get_action_logger, get_error_logger
from .recognizer import Recognizer
from .responder import Responder
from .commands import CommandProcessor
from agents.llm_connector import LLMConnector

class EnhancedVoiceSystem:
    """
    Enhanced voice system with:
    1. Dual-model LLM integration (phi3:mini + llama3.2:3b)
    2. Web search capabilities
    3. Intelligent task routing
    4. Real-time voice processing
    """
    
    def __init__(self, config_path='config/settings.yaml'):
        self.logger = get_action_logger('enhanced_voice_system')
        self.error_logger = get_error_logger('enhanced_voice_system')
        self.config_path = config_path
        self.config = self._load_config()
        
        # Initialize components
        self.recognizer = None
        self.responder = None
        self.command_processor = None
        self.llm_connector = None
        self.is_active = False
        
        # Voice processing state
        self.processing_queue = []
        self.processing_lock = threading.Lock()
        
        self._initialize_components()

    def _load_config(self):
        """Load voice system configuration."""
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
            self.logger.info("Enhanced voice system configuration loaded")
            return config
        except Exception as e:
            self.error_logger.error(f"Failed to load voice config: {e}")
            return {}

    def _initialize_components(self):
        """Initialize voice recognition and response components."""
        try:
            voice_config = self.config.get('voice', {})
            
            # Initialize Whisper recognizer with multi-language support
            self.recognizer = Recognizer(
                model_size=voice_config.get('model_size', 'medium'),
                device=voice_config.get('device', 'cpu'),
                compute_type=voice_config.get('compute_type', 'int8')
            )
            
            # Initialize text-to-speech responder
            self.responder = Responder(
                rate=voice_config.get('tts_rate', 180),
                volume=voice_config.get('tts_volume', 1.0)
            )
            
            # Initialize command processor
            self.command_processor = CommandProcessor(
                commands=voice_config.get('commands', [])
            )
            
            # Initialize LLM connector for dual-model strategy
            self.llm_connector = LLMConnector(self.config)
            
            self.logger.info("Enhanced voice system components initialized successfully")
            
        except Exception as e:
            self.error_logger.error(f"Failed to initialize voice components: {e}")
            raise

    def start(self):
        """Start the enhanced voice system."""
        try:
            if not self.config.get('voice', {}).get('enabled', False):
                self.logger.warning("Voice system is disabled in configuration")
                return False
            
            if self.is_active:
                self.logger.warning("Voice system is already active")
                return True
            
            # Start LLM connector
            if not asyncio.run(self.llm_connector.start()):
                self.logger.error("Failed to start LLM connector")
                return False
            
            # Start recognition
            if self.recognizer.start():
                self.is_active = True
                self.logger.info("Enhanced voice system started successfully")
                self.responder.speak("Enhanced voice system activated. I can help with tasks, answer questions, and search the web.")
                return True
            else:
                self.logger.error("Failed to start voice recognition")
                return False
                
        except Exception as e:
            self.error_logger.error(f"Failed to start enhanced voice system: {e}")
            return False

    def stop(self):
        """Stop the enhanced voice system."""
        try:
            if not self.is_active:
                return True
            
            self.recognizer.stop()
            asyncio.run(self.llm_connector.stop())
            self.is_active = False
            self.logger.info("Enhanced voice system stopped")
            return True
            
        except Exception as e:
            self.error_logger.error(f"Failed to stop enhanced voice system: {e}")
            return False

    def listen_once(self, duration=5.0):
        """
        Listen for a single voice command with enhanced processing.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            dict: Recognition result with text, confidence, and language
        """
        try:
            if not self.is_active:
                self.logger.warning("Voice system not active, starting temporarily")
                self.recognizer.start()
            
            result = self.recognizer.recognize_once(duration)
            
            if result.get('success') and result.get('text'):
                # Process with enhanced capabilities
                self._process_enhanced_command(result)
            
            return result
            
        except Exception as e:
            self.error_logger.error(f"Error during single listening: {e}")
            return {'success': False, 'error': str(e)}

    def _process_enhanced_command(self, recognition_result):
        """
        Process recognized speech with dual-model LLM and web search capabilities.
        
        Args:
            recognition_result: Result from speech recognition
        """
        try:
            text = recognition_result.get('text', '')
            confidence = recognition_result.get('confidence', 0.0)
            language = recognition_result.get('language', 'unknown')
            
            self.logger.info(
                f"Processing enhanced command: '{text}' (lang: {language}, conf: {confidence:.2f})",
                extra={
                    'confidence': confidence,
                    'language': language,
                    'command_text': text
                }
            )
            
            # Check confidence threshold
            min_confidence = self.config.get('voice', {}).get('min_confidence', 0.6)
            if confidence < min_confidence:
                self.responder.speak(f"Command not recognized clearly. Please repeat.")
                return
            
            # First, try basic command processing
            command_result = self.command_processor.process(text)
            
            if command_result.get('success'):
                # Basic command found, execute it
                self.responder.speak(f"Executing: {command_result.get('action')}")
                self.logger.info(f"Basic command executed: {command_result}")
                return
            
            # If no basic command, use LLM for intelligent processing
            llm_result = self._process_with_llm(text, language)
            
            if llm_result.get('success'):
                self.responder.speak(f"Processing your request: {llm_result.get('response', '')[:100]}...")
                self.logger.info(f"LLM processed command: {llm_result}")
            else:
                self.responder.speak("I'm sorry, I couldn't understand that command. Please try again.")
                
        except Exception as e:
            self.error_logger.error(f"Error processing enhanced command: {e}")
            self.responder.speak("Error processing command.")

    def _process_with_llm(self, text: str, language: str) -> Dict[str, Any]:
        """
        Process voice input with dual-model LLM strategy.
        
        Args:
            text: Recognized voice text
            language: Detected language
            
        Returns:
            dict: LLM processing result
        """
        try:
            # Classify task complexity
            task_type = self._classify_task_complexity(text)
            
            # Determine which model to use
            if task_type == 'complex':
                model_name = 'phi3:mini'
                temperature = 0.7
                max_tokens = 2048
            else:
                model_name = 'llama3.2:3b'
                temperature = 0.5
                max_tokens = 512
            
            # Check if web search is needed
            if self._needs_web_search(text):
                web_result = self._perform_web_search(text)
                if web_result.get('success'):
                    # Include web search results in prompt
                    enhanced_prompt = f"""
Voice Command: {text}
Language: {language}
Task Type: {task_type}
Model: {model_name}

Web Search Results:
{web_result.get('results', '')}

Please process this voice command intelligently, using the web search results if relevant.
Provide a helpful response that addresses the user's request.
"""
                else:
                    enhanced_prompt = f"""
Voice Command: {text}
Language: {language}
Task Type: {task_type}
Model: {model_name}

Please process this voice command intelligently and provide a helpful response.
"""
            else:
                enhanced_prompt = f"""
Voice Command: {text}
Language: {language}
Task Type: {task_type}
Model: {model_name}

Please process this voice command intelligently and provide a helpful response.
"""
            
            # Call LLM
            response = asyncio.run(self.llm_connector.send_prompt(
                enhanced_prompt,
                task_type=task_type,
                temperature=temperature,
                max_tokens=max_tokens
            ))
            
            return {
                'success': response.get('success', False),
                'response': response.get('content', ''),
                'model_used': model_name,
                'task_type': task_type,
                'web_search_used': self._needs_web_search(text)
            }
            
        except Exception as e:
            self.error_logger.error(f"Error processing with LLM: {e}")
            return {'success': False, 'error': str(e)}

    def _classify_task_complexity(self, text: str) -> str:
        """
        Classify task complexity to determine which model to use.
        
        Args:
            text: Voice input text
            
        Returns:
            str: 'simple' or 'complex'
        """
        # Simple task keywords
        simple_keywords = [
            'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
            'how are you', 'what time', 'what date', 'weather', 'temperature',
            'open', 'close', 'save', 'delete', 'undo', 'redo', 'stop', 'start',
            'yes', 'no', 'okay', 'sure', 'thanks', 'thank you', 'bye', 'goodbye',
            'status', 'check', 'list', 'show', 'display'
        ]
        
        # Complex task keywords
        complex_keywords = [
            'write', 'create', 'generate', 'code', 'function', 'algorithm',
            'explain', 'analyze', 'compare', 'discuss', 'describe', 'define',
            'solve', 'calculate', 'implement', 'design', 'plan', 'strategy',
            'why', 'how does', 'what is the difference', 'pros and cons',
            'story', 'narrative', 'creative', 'imagine', 'think about',
            'optimize', 'debug', 'refactor', 'architecture', 'system',
            'search', 'find', 'look up', 'research', 'information about'
        ]
        
        text_lower = text.lower()
        
        # Count matches
        simple_matches = sum(1 for keyword in simple_keywords if keyword in text_lower)
        complex_matches = sum(1 for keyword in complex_keywords if keyword in text_lower)
        
        # Determine task type
        if complex_matches > simple_matches:
            return 'complex'
        else:
            return 'simple'

    def _needs_web_search(self, text: str) -> bool:
        """
        Determine if the voice command needs web search.
        
        Args:
            text: Voice input text
            
        Returns:
            bool: True if web search is needed
        """
        web_search_keywords = [
            'search', 'find', 'look up', 'research', 'information about',
            'what is', 'who is', 'where is', 'when is', 'how to',
            'latest', 'news', 'current', 'recent', 'update',
            'weather', 'stock', 'price', 'definition', 'meaning'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in web_search_keywords)

    def _perform_web_search(self, query: str) -> Dict[str, Any]:
        """
        Perform web search using DuckDuckGo API.
        
        Args:
            query: Search query
            
        Returns:
            dict: Search results
        """
        try:
            # Use DuckDuckGo Instant Answer API
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract relevant information
                results = []
                
                if data.get('Abstract'):
                    results.append(f"Summary: {data['Abstract']}")
                
                if data.get('Answer'):
                    results.append(f"Answer: {data['Answer']}")
                
                if data.get('RelatedTopics'):
                    for topic in data['RelatedTopics'][:3]:  # Limit to 3 topics
                        if isinstance(topic, dict) and topic.get('Text'):
                            results.append(f"Related: {topic['Text']}")
                
                return {
                    'success': True,
                    'results': '\n'.join(results) if results else 'No specific information found.',
                    'query': query
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'query': query
                }
                
        except Exception as e:
            self.error_logger.error(f"Web search failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': query
            }

    def get_status(self):
        """Get current enhanced voice system status."""
        return {
            'active': self.is_active,
            'enabled': self.config.get('voice', {}).get('enabled', False),
            'model_info': self.recognizer.get_model_info() if self.recognizer else None,
            'supported_languages': self.recognizer.get_supported_languages() if self.recognizer else [],
            'llm_connector_status': self.llm_connector.get_status() if self.llm_connector else None
        }

    def __del__(self):
        """Cleanup on destruction."""
        if self.is_active:
            self.stop() 