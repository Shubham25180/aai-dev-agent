import os
import sys
import yaml
import json
from typing import Dict, Any
from utils.logger import get_action_logger, get_error_logger
from agents.planner import Planner
from app.router import Router
from app.controller import Controller
from app.voice_handler import VoiceCommandHandler
from voice.voice_system import VoiceSystem
from memory.memory_layer import MemoryLayer
from datetime import datetime

class Bootstrap:
    """
    Application bootstrap and initialization system.
    Sets up all components with proper memory integration and voice system.
    Follows AGENT_MANIFEST.md principles for automatic initialization.
    """
    
    def __init__(self, config_path: str = 'config/settings.yaml'):
        """
        Initialize Bootstrap with configuration path.

    Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.logger = get_action_logger('bootstrap', subsystem='core')
        self.error_logger = get_error_logger('bootstrap', subsystem='core')
        
        # Core components
        self.config = {}
        self.memory = None
        self.planner = None
        self.router = None
        self.controller = None
        self.voice_handler = None
        self.voice_system = None
        
        self.logger.info("Bootstrap initialized")

    def load_configuration(self) -> bool:
        """
        Load application configuration from YAML file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(self.config_path):
                self.error_logger.error(f"Configuration file not found: {self.config_path}")
                return False
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            
            # Validate required configuration sections
            required_sections = ['paths', 'logging', 'planning']
            for section in required_sections:
                if section not in self.config:
                    self.error_logger.error(f"Missing required configuration section: {section}")
                    return False
            
            # Create required directories
            self._create_directories()
            
            self.logger.info("Configuration loaded successfully", 
                           extra={'config_sections': list(self.config.keys())})
            return True
            
        except Exception as e:
            self.error_logger.error(f"Failed to load configuration: {e}")
            return False

    def _create_directories(self):
        """
        Create required directories from configuration.
        """
        try:
            paths = self.config.get('paths', {})
            
            # Create all required directories
            for path_key, path_value in paths.items():
                if isinstance(path_value, str) and path_value:
                    os.makedirs(path_value, exist_ok=True)
                    self.logger.info(f"Created directory: {path_value}")
            
            # Create additional required directories
            additional_dirs = [
                'logs/plans',
                'logs/actions',
                'logs/errors',
                'logs/sessions',
                'memory/embeddings',
                'model'  # For Vosk models
            ]
            
            for dir_path in additional_dirs:
                os.makedirs(dir_path, exist_ok=True)
                self.logger.info(f"Created directory: {dir_path}")
                
        except Exception as e:
            self.error_logger.error(f"Failed to create directories: {e}")

    def initialize_memory(self) -> bool:
        """
        Initialize the new modular memory system.
        Returns:
            True if successful, False otherwise
        """
        try:
            self.memory = MemoryLayer(
                core_path="memory/core_behavior.json",
                session_db="memory/session/session_" + datetime.utcnow().strftime('%Y-%m-%dT%H-%M') + ".sqlite",
                long_term_dir="memory/long_term/chroma_db"
            )
            self.logger.info("MemoryLayer initialized successfully")
            return True
        except Exception as e:
            self.error_logger.error(f"Failed to initialize MemoryLayer: {e}")
            return False

    def initialize_planner(self) -> bool:
        """
        Initialize the planning system with memory integration.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.memory:
                self.error_logger.error("Memory not initialized")
                return False
            
            self.planner = Planner(self.config, memory_manager=self.memory)
            
            self.logger.info("Planner initialized with memory integration")
            return True
            
        except Exception as e:
            self.error_logger.error(f"Failed to initialize planner: {e}")
            return False

    def initialize_router(self) -> bool:
        """
        Initialize the routing system.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.router = Router(self.config)
            
            self.logger.info("Router initialized successfully")
            return True
            
        except Exception as e:
            self.error_logger.error(f"Failed to initialize router: {e}")
            return False

    def initialize_controller(self) -> bool:
        """
        Initialize the main controller with all components.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not all([self.memory, self.planner, self.router]):
                self.error_logger.error("Required components not initialized")
                return False
            
            self.controller = Controller(
                config=self.config,
                router=self.router,
                planner=self.planner,
                memory=self.memory
            )
            
            self.logger.info("Controller initialized with all components")
            return True
            
        except Exception as e:
            self.error_logger.error(f"Failed to initialize controller: {e}")
            return False

    def initialize_voice_system(self) -> bool:
        """
        Initialize the voice system with command handler.

    Returns:
            True if successful, False otherwise
        """
        try:
            # Check if voice is enabled in config
            voice_config = self.config.get('voice', {})
            if not voice_config.get('enabled', False):
                self.logger.info("Voice system disabled in configuration")
                return True
            
            if not self.controller:
                self.error_logger.error("Controller not initialized")
                return False
            
            # Initialize voice command handler
            self.voice_handler = VoiceCommandHandler(self.controller)
            
            # Initialize voice system (without command_callback parameter)
            self.voice_system = VoiceSystem()
            
            # Auto-start voice system if configured
            if voice_config.get('auto_start', False):
                if self.voice_system.start():
                    self.logger.info("Voice system auto-started")
                else:
                    self.logger.warning("Failed to auto-start voice system")
            
            self.logger.info("Voice system initialized successfully")
            return True
            
        except Exception as e:
            self.error_logger.error(f"Failed to initialize voice system: {e}")
            return False

    def bootstrap_application(self) -> Dict[str, Any]:
        """
        Complete application bootstrap process.
        
        Returns:
            Bootstrap result with status and component information
        """
        try:
            self.logger.info("Starting application bootstrap")
            
            # Step 1: Load configuration
            if not self.load_configuration():
                return {'success': False, 'error': 'Failed to load configuration'}
            
            # Step 2: Initialize memory
            if not self.initialize_memory():
                return {'success': False, 'error': 'Failed to initialize memory'}
            
            # Step 3: Initialize planner
            if not self.initialize_planner():
                return {'success': False, 'error': 'Failed to initialize planner'}
            
            # Step 4: Initialize router
            if not self.initialize_router():
                return {'success': False, 'error': 'Failed to initialize router'}
            
            # Step 5: Initialize controller
            if not self.initialize_controller():
                return {'success': False, 'error': 'Failed to initialize controller'}
            
            # Step 6: Initialize voice system
            if not self.initialize_voice_system():
                return {'success': False, 'error': 'Failed to initialize voice system'}
            
            # Step 7: Update memory with bootstrap completion
            if self.memory:
                self.memory.session.add_chunk('bootstrap_status', json.dumps({
                    'status': 'completed',
                    'components_initialized': ['memory', 'planner', 'router', 'controller', 'voice_system'],
                    'completed_at': self.memory.core.get('bootstrap_completed_at', '')
                }))
            
            bootstrap_result = {
                'success': True,
                'status': 'bootstrapped',
                'components': {
                    'memory': self.memory is not None,
                    'planner': self.planner is not None,
                    'router': self.router is not None,
                    'controller': self.controller is not None,
                    'voice_handler': self.voice_handler is not None,
                    'voice_system': self.voice_system is not None
                },
                'config_sections': list(self.config.keys()),
                'memory_stats': self.memory.get_memory_stats() if self.memory else {},
                'voice_enabled': self.config.get('voice', {}).get('enabled', False)
            }
            
            self.logger.info("Application bootstrap completed successfully", 
                           extra=bootstrap_result)
            
            return bootstrap_result
            
        except Exception as e:
            self.error_logger.error(f"Bootstrap failed: {e}")
            return {'success': False, 'error': str(e)}

    def get_component(self, component_name: str):
        """
        Get a specific component by name.

    Args:
            component_name: Name of the component to retrieve
            
        Returns:
            Component instance or None if not found
        """
        components = {
            'memory': self.memory,
            'planner': self.planner,
            'router': self.router,
            'controller': self.controller,
            'voice_handler': self.voice_handler,
            'voice_system': self.voice_system
        }
        
        return components.get(component_name)

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get current system status and health.
        
        Returns:
            System status information
        """
        try:
            status = {
                'bootstrap_completed': all([
                    self.memory is not None,
                    self.planner is not None,
                    self.router is not None,
                    self.controller is not None
                ]),
                'components': {
                    'memory': {
                        'initialized': self.memory is not None,
                        'stats': self.memory.get_memory_stats() if self.memory else {}
                    },
                    'planner': {
                        'initialized': self.planner is not None
                    },
                    'router': {
                        'initialized': self.router is not None
                    },
                    'controller': {
                        'initialized': self.controller is not None,
                        'session_stats': self.controller.get_session_stats() if self.controller else {}
                    },
                    'voice_handler': {
                        'initialized': self.voice_handler is not None
                    },
                    'voice_system': {
                        'initialized': self.voice_system is not None,
                        'status': self.voice_system.get_status() if self.voice_system else {}
                    }
                },
                'configuration': {
                    'loaded': bool(self.config),
                    'sections': list(self.config.keys()) if self.config else []
                }
            }
            
            return status
            
        except Exception as e:
            self.error_logger.error(f"Failed to get system status: {e}")
            return {'error': str(e)}

    def shutdown(self) -> bool:
        """
        Gracefully shutdown the application and save state.
    
    Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info("Starting application shutdown")
            
            # Stop voice system
            if self.voice_system:
                self.voice_system.stop()
            
            # Save memory state
            if self.memory:
                self.memory.save_all_memory()
                self.memory.session.add_chunk('shutdown_status', json.dumps({
                    'status': 'shutdown',
                    'shutdown_at': self.memory.core.get('shutdown_at', '')
                }))
            
            # Save controller session state
            if self.controller:
                self.controller.save_session_state()
            
            self.logger.info("Application shutdown completed")
            return True
            
        except Exception as e:
            self.error_logger.error(f"Shutdown failed: {e}")
            return False

if __name__ == '__main__':
    # Example of how to use the bootstrap function
    try:
        # Assuming the script is run from the root of the ai_dev_agent directory
        bootstrap = Bootstrap()
        app_state = bootstrap.bootstrap_application()
        print("\n--- Loaded Configuration ---")
        print(app_state['config'])
    except Exception as e:
        print(f"Bootstrap failed: {e}") 