import re
from utils.logger import get_action_logger, get_error_logger

class CommandProcessor:
    """
    Voice command processor that maps recognized text to agent commands.
    Supports multi-language commands and provides confidence-based processing.
    """
    def __init__(self, commands=None, min_confidence=0.6):
        self.logger = get_action_logger('voice_commands')
        self.error_logger = get_error_logger('voice_commands')
        self.commands = commands or self._default_commands()
        self.min_confidence = min_confidence

    def _default_commands(self):
        """Default command patterns with multi-language support."""
        return [
            # English Commands
            {
                'pattern': r'open (.+)',
                'command': 'open_file',
                'description': 'Open a file',
                'languages': ['en']
            },
            {
                'pattern': r'run (.+)',
                'command': 'run_command',
                'description': 'Run a command',
                'languages': ['en']
            },
            {
                'pattern': r'create (.+)',
                'command': 'create_file',
                'description': 'Create a new file',
                'languages': ['en']
            },
            {
                'pattern': r'delete (.+)',
                'command': 'delete_file',
                'description': 'Delete a file',
                'languages': ['en']
            },
            {
                'pattern': r'edit (.+)',
                'command': 'edit_file',
                'description': 'Edit a file',
                'languages': ['en']
            },
            {
                'pattern': r'undo',
                'command': 'undo',
                'description': 'Undo last action',
                'languages': ['en']
            },
            {
                'pattern': r'save',
                'command': 'save',
                'description': 'Save current work',
                'languages': ['en']
            },
            {
                'pattern': r'quit|exit',
                'command': 'exit',
                'description': 'Exit the application',
                'languages': ['en']
            },
            
            # Hindi Commands - File Operations (more specific patterns)
            {
                'pattern': r'^(.+) kholo$|^file kholo$',
                'command': 'open_file',
                'description': 'Open a file',
                'languages': ['hi']
            },
            {
                'pattern': r'^(.+) banane ke liye$|^file banane ke liye$',
                'command': 'create_file',
                'description': 'Create a new file',
                'languages': ['hi']
            },
            {
                'pattern': r'^(.+) delete karo$|^file delete karo$',
                'command': 'delete_file',
                'description': 'Delete a file',
                'languages': ['hi']
            },
            {
                'pattern': r'^(.+) hatao$',
                'command': 'delete_file',
                'description': 'Delete a file',
                'languages': ['hi']
            },
            {
                'pattern': r'^(.+) edit karo$|^file edit karo$',
                'command': 'edit_file',
                'description': 'Edit a file',
                'languages': ['hi']
            },
            {
                'pattern': r'^(.+) modify karo$',
                'command': 'edit_file',
                'description': 'Edit a file',
                'languages': ['hi']
            },
            
            # Hindi Commands - Development Operations
            {
                'pattern': r'^code run karo$|^(.+) run karo$|^script chalane ke liye$',
                'command': 'run_command',
                'description': 'Run a command',
                'languages': ['hi']
            },
            {
                'pattern': r'^function banane ke liye$',
                'command': 'create_file',
                'description': 'Create a new function',
                'languages': ['hi']
            },
            {
                'pattern': r'^class banane ke liye$',
                'command': 'create_file',
                'description': 'Create a new class',
                'languages': ['hi']
            },
            {
                'pattern': r'^variable banane ke liye$',
                'command': 'edit_file',
                'description': 'Create a variable',
                'languages': ['hi']
            },
            
            # Hindi Commands - System Operations
            {
                'pattern': r'^undo karo$|^pehle wala karo$|^wapis karo$',
                'command': 'undo',
                'description': 'Undo last action',
                'languages': ['hi']
            },
            {
                'pattern': r'^save karo$|^file save karo$|^bachena$',
                'command': 'save',
                'description': 'Save current work',
                'languages': ['hi']
            },
            {
                'pattern': r'^band karo$|^exit karo$|^quit karo$',
                'command': 'exit',
                'description': 'Exit the application',
                'languages': ['hi']
            },
            
            # Hindi Commands - Navigation
            {
                'pattern': r'^folder kholo$|^directory kholo$|^(.+) folder mein jao$',
                'command': 'navigate',
                'description': 'Navigate to folder',
                'languages': ['hi']
            },
            {
                'pattern': r'^upar jao$|^parent folder mein jao$',
                'command': 'navigate_up',
                'description': 'Navigate to parent folder',
                'languages': ['hi']
            },
            
            # Hindi Commands - Search
            {
                'pattern': r'^(.+) dhundho$|^(.+) search karo$|^(.+) find karo$',
                'command': 'search',
                'description': 'Search for files or text',
                'languages': ['hi']
            },
            
            # Hindi Commands - Git Operations
            {
                'pattern': r'^git commit karo$|^commit karo$|^changes commit karo$',
                'command': 'git_commit',
                'description': 'Commit changes to git',
                'languages': ['hi']
            },
            {
                'pattern': r'^git push karo$|^push karo$|^remote mein push karo$',
                'command': 'git_push',
                'description': 'Push to remote repository',
                'languages': ['hi']
            },
            {
                'pattern': r'^git pull karo$|^pull karo$|^remote se pull karo$',
                'command': 'git_pull',
                'description': 'Pull from remote repository',
                'languages': ['hi']
            },
            
            # Hindi Commands - Testing
            {
                'pattern': r'^test run karo$|^testing karo$|^unit test chalane ke liye$',
                'command': 'run_tests',
                'description': 'Run tests',
                'languages': ['hi']
            },
            {
                'pattern': r'^debug karo$|^debugging start karo$',
                'command': 'debug',
                'description': 'Start debugging',
                'languages': ['hi']
            },
            
            # Hindi Commands - Documentation
            {
                'pattern': r'^documentation banane ke liye$|^docs banane ke liye$',
                'command': 'create_docs',
                'description': 'Create documentation',
                'languages': ['hi']
            },
            {
                'pattern': r'^readme update karo$|^readme edit karo$',
                'command': 'edit_readme',
                'description': 'Edit README file',
                'languages': ['hi']
            }
        ]

    def process(self, transcript, confidence=1.0, language='en'):
        """
        Process transcript and map to agent command if confidence is high enough.
        
        Args:
            transcript: Recognized speech text
            confidence: Recognition confidence (0-1)
            language: Detected language code
            
        Returns:
            dict: Processing result with command details
        """
        try:
            if confidence < self.min_confidence:
                self.logger.warning(
                    f"Low confidence ({confidence:.2f}) for transcript: {transcript}",
                    extra={'confidence': confidence, 'language': language}
                )
                return {
                    'success': False, 
                    'reason': 'low_confidence', 
                    'transcript': transcript, 
                    'confidence': confidence
                }
            
            # Try to match against command patterns
            for cmd in self.commands:
                pattern = cmd.get('pattern', '')
                command = cmd.get('command', '')
                description = cmd.get('description', '')
                supported_languages = cmd.get('languages', ['en'])
                
                # Check if language is supported (or auto-detect)
                if language != 'auto' and language not in supported_languages:
                    continue
                
                match = re.match(pattern, transcript, re.IGNORECASE)
                if match:
                    matched_args = match.groups()
                    
                    result = {
                        'success': True,
                        'command': command,
                        'action': description,
                        'args': matched_args,
                        'confidence': confidence,
                        'language': language,
                        'pattern_matched': pattern
                    }
                    
                    self.logger.info(
                        f"Command matched: {command}",
                        extra={
                            'command_args': matched_args,
                            'confidence': confidence,
                            'language': language,
                            'description': description
                        }
                    )
                    
                    return result
            
            # No match found
            self.logger.warning(
                f"No command matched for transcript: {transcript}",
                extra={'confidence': confidence, 'language': language}
            )
            
            return {
                'success': False, 
                'reason': 'no_match', 
                'transcript': transcript, 
                'confidence': confidence,
                'language': language
            }
            
        except Exception as e:
            self.error_logger.error(f"Error processing command: {e}")
            return {
                'success': False,
                'reason': 'error',
                'error': str(e),
                'transcript': transcript
            }

    def add_command(self, pattern, command, description, languages=None):
        """
        Add a custom command pattern.
        
        Args:
            pattern: Regex pattern to match
            command: Command name to execute
            description: Human-readable description
            languages: List of supported language codes
        """
        try:
            new_command = {
                'pattern': pattern,
                'command': command,
                'description': description,
                'languages': languages or ['en']
            }
            
            self.commands.append(new_command)
            self.logger.info(f"Added custom command: {pattern} -> {command}")
            
        except Exception as e:
            self.error_logger.error(f"Failed to add custom command: {e}")

    def get_available_commands(self, language='en'):
        """
        Get list of available commands for a specific language.
        
        Args:
            language: Language code to filter by
            
        Returns:
            list: Available commands for the language
        """
        available = []
        for cmd in self.commands:
            supported_languages = cmd.get('languages', ['en'])
            if language in supported_languages or 'auto' in supported_languages:
                available.append({
                    'command': cmd.get('command'),
                    'description': cmd.get('description'),
                    'pattern': cmd.get('pattern')
                })
        return available

    def get_status(self):
        """Get command processor status."""
        return {
            'total_commands': len(self.commands),
            'min_confidence': self.min_confidence,
            'supported_languages': ['en', 'hi', 'auto']
        } 