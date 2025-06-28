import os
import json
from typing import Dict, Any, List, Optional
from utils.logger import get_action_logger, get_error_logger

class LanguageManager:
    """
    Manages multiple languages for voice recognition, TTS, and command parsing.
    Supports language detection, switching, and language-specific configurations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize language manager with configuration.
        
        Args:
            config: Application configuration with language settings
        """
        self.config = config
        self.logger = get_action_logger('language_manager')
        self.error_logger = get_error_logger('language_manager')
        
        # Language configuration
        self.languages = config.get('languages', {})
        self.default_language = config.get('default_language', 'en')
        self.current_language = self.default_language
        
        # Language-specific data
        self.language_data = {}
        self.command_patterns = {}
        self.tts_voices = {}
        
        # Load language configurations
        self._load_language_configs()
        
        self.logger.info(f"Language manager initialized with {len(self.languages)} languages")

    def _load_language_configs(self):
        """
        Load language-specific configurations and data.
        """
        try:
            # Load language data from files
            language_dir = 'voice/languages'
            if os.path.exists(language_dir):
                for lang_code in self.languages.keys():
                    lang_file = os.path.join(language_dir, f'{lang_code}.json')
                    if os.path.exists(lang_file):
                        with open(lang_file, 'r', encoding='utf-8') as f:
                            self.language_data[lang_code] = json.load(f)
                            self.logger.info(f"Loaded language data for {lang_code}")
            
            # Initialize default language data if not found
            self._initialize_default_languages()
            
        except Exception as e:
            self.error_logger.error(f"Failed to load language configs: {e}")

    def _initialize_default_languages(self):
        """
        Initialize default language configurations if not found in files.
        """
        default_configs = {
            'en': {
                'name': 'English',
                'code': 'en',
                'model_path': 'model/en',
                'tts_voice': 'english',
                'commands': {
                    'open_file': r'open (.+)',
                    'run_command': r'run (.+)',
                    'create_file': r'create (.+)',
                    'delete_file': r'delete (.+)',
                    'edit_file': r'edit (.+)',
                    'undo': r'undo',
                    'save': r'save',
                    'exit': r'quit|exit',
                    'status': r'status',
                    'help': r'help'
                },
                'responses': {
                    'listening': 'I am listening for commands',
                    'command_executed': 'Command executed successfully',
                    'command_failed': 'Command execution failed',
                    'not_understood': 'I did not understand that command',
                    'low_confidence': 'I did not hear that clearly, please repeat'
                }
            },
            'es': {
                'name': 'Español',
                'code': 'es',
                'model_path': 'model/es',
                'tts_voice': 'spanish',
                'commands': {
                    'open_file': r'abrir (.+)',
                    'run_command': r'ejecutar (.+)',
                    'create_file': r'crear (.+)',
                    'delete_file': r'eliminar (.+)',
                    'edit_file': r'editar (.+)',
                    'undo': r'deshacer',
                    'save': r'guardar',
                    'exit': r'salir|terminar',
                    'status': r'estado',
                    'help': r'ayuda'
                },
                'responses': {
                    'listening': 'Estoy escuchando comandos',
                    'command_executed': 'Comando ejecutado exitosamente',
                    'command_failed': 'La ejecución del comando falló',
                    'not_understood': 'No entendí ese comando',
                    'low_confidence': 'No escuché claramente, por favor repite'
                }
            },
            'fr': {
                'name': 'Français',
                'code': 'fr',
                'model_path': 'model/fr',
                'tts_voice': 'french',
                'commands': {
                    'open_file': r'ouvrir (.+)',
                    'run_command': r'exécuter (.+)',
                    'create_file': r'créer (.+)',
                    'delete_file': r'supprimer (.+)',
                    'edit_file': r'éditer (.+)',
                    'undo': r'annuler',
                    'save': r'sauvegarder',
                    'exit': r'quitter|sortir',
                    'status': r'état',
                    'help': r'aide'
                },
                'responses': {
                    'listening': 'J\'écoute les commandes',
                    'command_executed': 'Commande exécutée avec succès',
                    'command_failed': 'L\'exécution de la commande a échoué',
                    'not_understood': 'Je n\'ai pas compris cette commande',
                    'low_confidence': 'Je n\'ai pas entendu clairement, veuillez répéter'
                }
            },
            'de': {
                'name': 'Deutsch',
                'code': 'de',
                'model_path': 'model/de',
                'tts_voice': 'german',
                'commands': {
                    'open_file': r'öffnen (.+)',
                    'run_command': r'ausführen (.+)',
                    'create_file': r'erstellen (.+)',
                    'delete_file': r'löschen (.+)',
                    'edit_file': r'bearbeiten (.+)',
                    'undo': r'rückgängig',
                    'save': r'speichern',
                    'exit': r'beenden|aussteigen',
                    'status': r'status',
                    'help': r'hilfe'
                },
                'responses': {
                    'listening': 'Ich höre auf Befehle',
                    'command_executed': 'Befehl erfolgreich ausgeführt',
                    'command_failed': 'Befehlsausführung fehlgeschlagen',
                    'not_understood': 'Ich habe diesen Befehl nicht verstanden',
                    'low_confidence': 'Ich habe das nicht klar gehört, bitte wiederholen'
                }
            },
            'hi': {
                'name': 'हिंदी',
                'code': 'hi',
                'model_path': 'model/hi',
                'tts_voice': 'hindi',
                'commands': {
                    'open_file': r'खोलें (.+)',
                    'run_command': r'चलाएं (.+)',
                    'create_file': r'बनाएं (.+)',
                    'delete_file': r'हटाएं (.+)',
                    'edit_file': r'संपादित करें (.+)',
                    'undo': r'वापस लें',
                    'save': r'सहेजें',
                    'exit': r'बाहर निकलें|समाप्त करें',
                    'status': r'स्थिति',
                    'help': r'सहायता'
                },
                'responses': {
                    'listening': 'मैं आदेश सुन रहा हूं',
                    'command_executed': 'आदेश सफलतापूर्वक निष्पादित किया गया',
                    'command_failed': 'आदेश निष्पादन विफल',
                    'not_understood': 'मैं वह आदेश नहीं समझा',
                    'low_confidence': 'मैंने स्पष्ट रूप से नहीं सुना, कृपया दोहराएं'
                }
            }
        }
        
        for lang_code, config in default_configs.items():
            if lang_code not in self.language_data:
                self.language_data[lang_code] = config
                self.logger.info(f"Initialized default config for {lang_code}")

    def get_supported_languages(self) -> List[Dict[str, Any]]:
        """
        Get list of supported languages with their details.
        
        Returns:
            List of language dictionaries
        """
        languages = []
        for lang_code, config in self.language_data.items():
            languages.append({
                'code': lang_code,
                'name': config.get('name', lang_code.upper()),
                'model_available': self._check_model_availability(lang_code),
                'tts_available': self._check_tts_availability(lang_code)
            })
        return languages

    def _check_model_availability(self, lang_code: str) -> bool:
        """
        Check if speech recognition model is available for language.
        
        Args:
            lang_code: Language code
            
        Returns:
            True if model is available, False otherwise
        """
        try:
            model_path = self.language_data.get(lang_code, {}).get('model_path', '')
            return os.path.exists(model_path) if model_path else False
        except Exception:
            return False

    def _check_tts_availability(self, lang_code: str) -> bool:
        """
        Check if TTS voice is available for language.
        
        Args:
            lang_code: Language code
            
        Returns:
            True if TTS voice is available, False otherwise
        """
        try:
            # This would check against available TTS voices
            # For now, assume all languages have TTS support
            return True
        except Exception:
            return False

    def set_language(self, lang_code: str) -> bool:
        """
        Set the current language.
        
        Args:
            lang_code: Language code to set
            
        Returns:
            True if language was set successfully, False otherwise
        """
        try:
            if lang_code not in self.language_data:
                self.error_logger.error(f"Language {lang_code} not supported")
                return False
            
            self.current_language = lang_code
            self.logger.info(f"Language set to {lang_code}")
            return True
            
        except Exception as e:
            self.error_logger.error(f"Failed to set language: {e}")
            return False

    def get_current_language(self) -> str:
        """
        Get the current language code.
        
        Returns:
            Current language code
        """
        return self.current_language

    def get_language_config(self, lang_code: str = None) -> Dict[str, Any]:
        """
        Get configuration for a specific language.
        
        Args:
            lang_code: Language code (uses current if None)
            
        Returns:
            Language configuration dictionary
        """
        if lang_code is None:
            lang_code = self.current_language
        
        return self.language_data.get(lang_code, {})

    def get_command_patterns(self, lang_code: str = None) -> Dict[str, str]:
        """
        Get command patterns for a specific language.
        
        Args:
            lang_code: Language code (uses current if None)
            
        Returns:
            Dictionary of command patterns
        """
        if lang_code is None:
            lang_code = self.current_language
        
        config = self.get_language_config(lang_code)
        return config.get('commands', {})

    def get_response(self, response_key: str, lang_code: str = None) -> str:
        """
        Get a localized response message.
        
        Args:
            response_key: Key for the response message
            lang_code: Language code (uses current if None)
            
        Returns:
            Localized response message
        """
        if lang_code is None:
            lang_code = self.current_language
        
        config = self.get_language_config(lang_code)
        responses = config.get('responses', {})
        return responses.get(response_key, f"[{response_key}]")

    def get_model_path(self, lang_code: str = None) -> str:
        """
        Get the model path for a specific language.
        
        Args:
            lang_code: Language code (uses current if None)
            
        Returns:
            Model path for the language
        """
        if lang_code is None:
            lang_code = self.current_language
        
        config = self.get_language_config(lang_code)
        return config.get('model_path', '')

    def get_tts_voice(self, lang_code: str = None) -> str:
        """
        Get the TTS voice for a specific language.
        
        Args:
            lang_code: Language code (uses current if None)
            
        Returns:
            TTS voice name for the language
        """
        if lang_code is None:
            lang_code = self.current_language
        
        config = self.get_language_config(lang_code)
        return config.get('tts_voice', '')

    def detect_language(self, text: str) -> Optional[str]:
        """
        Attempt to detect the language of input text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected language code or None if unknown
        """
        try:
            # Simple language detection based on character sets
            # This is a basic implementation - could be enhanced with ML models
            
            # Check for non-Latin characters
            if any('\u0900' <= char <= '\u097F' for char in text):  # Devanagari
                return 'hi'
            elif any('\u0600' <= char <= '\u06FF' for char in text):  # Arabic
                return 'ar'
            elif any('\u4E00' <= char <= '\u9FFF' for char in text):  # Chinese
                return 'zh'
            elif any('\u3040' <= char <= '\u309F' for char in text):  # Hiragana
                return 'ja'
            elif any('\uAC00' <= char <= '\uD7AF' for char in text):  # Hangul
                return 'ko'
            
            # Check for common words/patterns
            text_lower = text.lower()
            
            # Spanish patterns
            spanish_words = ['abrir', 'crear', 'editar', 'guardar', 'ayuda']
            if any(word in text_lower for word in spanish_words):
                return 'es'
            
            # French patterns
            french_words = ['ouvrir', 'créer', 'éditer', 'sauvegarder', 'aide']
            if any(word in text_lower for word in french_words):
                return 'fr'
            
            # German patterns
            german_words = ['öffnen', 'erstellen', 'bearbeiten', 'speichern', 'hilfe']
            if any(word in text_lower for word in german_words):
                return 'de'
            
            # Default to English
            return 'en'
            
        except Exception as e:
            self.error_logger.error(f"Language detection failed: {e}")
            return None

    def add_language(self, lang_code: str, config: Dict[str, Any]) -> bool:
        """
        Add a new language configuration.
        
        Args:
            lang_code: Language code
            config: Language configuration
            
        Returns:
            True if added successfully, False otherwise
        """
        try:
            self.language_data[lang_code] = config
            self.logger.info(f"Added language configuration for {lang_code}")
            return True
            
        except Exception as e:
            self.error_logger.error(f"Failed to add language: {e}")
            return False

    def save_language_configs(self):
        """
        Save language configurations to files.
        """
        try:
            language_dir = 'voice/languages'
            os.makedirs(language_dir, exist_ok=True)
            
            for lang_code, config in self.language_data.items():
                lang_file = os.path.join(language_dir, f'{lang_code}.json')
                with open(lang_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Language configurations saved")
            
        except Exception as e:
            self.error_logger.error(f"Failed to save language configs: {e}") 