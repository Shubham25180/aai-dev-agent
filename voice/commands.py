import re
from utils.logger import get_action_logger, get_error_logger

class VoiceCommands:
    """
    Voice command parser that maps recognized text to agent commands.
    Adds confidence checks and logs all parsed commands.
    """
    def __init__(self, command_map=None, min_confidence=0.6):
        self.logger = get_action_logger('voice_commands')
        self.error_logger = get_error_logger('voice_commands')
        self.command_map = command_map or self._default_command_map()
        self.min_confidence = min_confidence

    def _default_command_map(self):
        return {
            r'open (.+)': 'open_file',
            r'run (.+)': 'run_command',
            r'create (.+)': 'create_file',
            r'delete (.+)': 'delete_file',
            r'edit (.+)': 'edit_file',
            r'undo': 'undo',
            r'save': 'save',
            r'quit|exit': 'exit',
        }

    def interpret(self, transcript, confidence=1.0):
        """
        Interpret transcript and map to agent command if confidence is high enough.
        Returns dict with command, args, and confidence.
        """
        if confidence < self.min_confidence:
            self.logger.warning(f"Low confidence ({confidence}) for transcript: {transcript}")
            return {'success': False, 'reason': 'low_confidence', 'transcript': transcript, 'confidence': confidence}
        for pattern, command in self.command_map.items():
            match = re.match(pattern, transcript, re.IGNORECASE)
            if match:
                args = match.groups()
                self.logger.info(f"Parsed command: {command}", extra={'args': args, 'confidence': confidence})
                return {'success': True, 'command': command, 'args': args, 'confidence': confidence}
        self.logger.warning(f"No command matched for transcript: {transcript}")
        return {'success': False, 'reason': 'no_match', 'transcript': transcript, 'confidence': confidence} 