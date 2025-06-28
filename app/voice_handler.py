from typing import Dict, Any, List
from utils.logger import get_action_logger, get_error_logger

class VoiceCommandHandler:
    """
    Handles voice commands by mapping them to controller actions.
    Provides a bridge between voice input and the main agent controller.
    """
    
    def __init__(self, controller):
        """
        Initialize voice command handler with controller reference.
        
        Args:
            controller: Controller instance to execute commands
        """
        self.controller = controller
        self.logger = get_action_logger('voice_handler')
        self.error_logger = get_error_logger('voice_handler')
        
        # Command mapping
        self.command_handlers = {
            'open_file': self._handle_open_file,
            'run_command': self._handle_run_command,
            'create_file': self._handle_create_file,
            'delete_file': self._handle_delete_file,
            'edit_file': self._handle_edit_file,
            'undo': self._handle_undo,
            'save': self._handle_save,
            'exit': self._handle_exit,
            'status': self._handle_status,
            'help': self._handle_help
        }
        
        self.logger.info("Voice command handler initialized")

    def handle_command(self, command: str, args: List[str], original_text: str) -> Dict[str, Any]:
        """
        Handle a voice command by routing it to the appropriate handler.
        
        Args:
            command: Command name
            args: Command arguments
            original_text: Original voice input text
            
        Returns:
            Command execution result
        """
        try:
            self.logger.info(f"Handling voice command: {command}", extra={'args': args, 'original_text': original_text})
            
            # Check if command handler exists
            if command not in self.command_handlers:
                return {
                    'success': False,
                    'error': f'Unknown command: {command}',
                    'available_commands': list(self.command_handlers.keys())
                }
            
            # Execute command handler
            handler = self.command_handlers[command]
            result = handler(args, original_text)
            
            self.logger.info(f"Command {command} executed", extra={'success': result.get('success', False)})
            return result
            
        except Exception as e:
            self.error_logger.error(f"Voice command handling error: {e}")
            return {
                'success': False,
                'error': f'Command execution failed: {str(e)}'
            }

    def _handle_open_file(self, args: List[str], original_text: str) -> Dict[str, Any]:
        """Handle 'open file' command."""
        if not args:
            return {'success': False, 'error': 'No file specified'}
        
        filename = args[0]
        task = f"Open file: {filename}"
        
        return self.controller.process_task(task, {
            'command_type': 'voice',
            'original_text': original_text,
            'safety_level': 'high'
        })

    def _handle_run_command(self, args: List[str], original_text: str) -> Dict[str, Any]:
        """Handle 'run command' command."""
        if not args:
            return {'success': False, 'error': 'No command specified'}
        
        command = args[0]
        task = f"Run command: {command}"
        
        return self.controller.process_task(task, {
            'command_type': 'voice',
            'original_text': original_text,
            'safety_level': 'high'
        })

    def _handle_create_file(self, args: List[str], original_text: str) -> Dict[str, Any]:
        """Handle 'create file' command."""
        if not args:
            return {'success': False, 'error': 'No filename specified'}
        
        filename = args[0]
        task = f"Create file: {filename}"
        
        return self.controller.process_task(task, {
            'command_type': 'voice',
            'original_text': original_text,
            'safety_level': 'normal'
        })

    def _handle_delete_file(self, args: List[str], original_text: str) -> Dict[str, Any]:
        """Handle 'delete file' command."""
        if not args:
            return {'success': False, 'error': 'No filename specified'}
        
        filename = args[0]
        task = f"Delete file: {filename}"
        
        return self.controller.process_task(task, {
            'command_type': 'voice',
            'original_text': original_text,
            'safety_level': 'high'
        })

    def _handle_edit_file(self, args: List[str], original_text: str) -> Dict[str, Any]:
        """Handle 'edit file' command."""
        if not args:
            return {'success': False, 'error': 'No filename specified'}
        
        filename = args[0]
        task = f"Edit file: {filename}"
        
        return self.controller.process_task(task, {
            'command_type': 'voice',
            'original_text': original_text,
            'safety_level': 'normal'
        })

    def _handle_undo(self, args: List[str], original_text: str) -> Dict[str, Any]:
        """Handle 'undo' command."""
        task = "Undo last action"
        
        return self.controller.process_task(task, {
            'command_type': 'voice',
            'original_text': original_text,
            'safety_level': 'normal'
        })

    def _handle_save(self, args: List[str], original_text: str) -> Dict[str, Any]:
        """Handle 'save' command."""
        task = "Save current work"
        
        return self.controller.process_task(task, {
            'command_type': 'voice',
            'original_text': original_text,
            'safety_level': 'normal'
        })

    def _handle_exit(self, args: List[str], original_text: str) -> Dict[str, Any]:
        """Handle 'exit' command."""
        task = "Exit application"
        
        return self.controller.process_task(task, {
            'command_type': 'voice',
            'original_text': original_text,
            'safety_level': 'normal'
        })

    def _handle_status(self, args: List[str], original_text: str) -> Dict[str, Any]:
        """Handle 'status' command."""
        try:
            status = self.controller.get_session_stats()
            return {
                'success': True,
                'message': 'System status retrieved',
                'status': status
            }
        except Exception as e:
            return {'success': False, 'error': f'Failed to get status: {str(e)}'}

    def _handle_help(self, args: List[str], original_text: str) -> Dict[str, Any]:
        """Handle 'help' command."""
        help_text = """
        Available voice commands:
        - "open [filename]" - Open a file
        - "run [command]" - Run a command
        - "create [filename]" - Create a new file
        - "edit [filename]" - Edit a file
        - "delete [filename]" - Delete a file
        - "undo" - Undo last action
        - "save" - Save current work
        - "status" - Get system status
        - "help" - Show this help
        - "exit" - Exit application
        """
        
        return {
            'success': True,
            'message': 'Help information',
            'help_text': help_text
        }

    def get_available_commands(self) -> List[str]:
        """Get list of available voice commands."""
        return list(self.command_handlers.keys())

    def add_custom_handler(self, command: str, handler_func):
        """
        Add a custom command handler.
        
        Args:
            command: Command name
            handler_func: Handler function
        """
        try:
            self.command_handlers[command] = handler_func
            self.logger.info(f"Added custom command handler: {command}")
        except Exception as e:
            self.error_logger.error(f"Failed to add custom handler: {e}") 