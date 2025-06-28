import os
import json
import shutil
from datetime import datetime
from typing import Dict, Any, Optional
from utils.logger import get_action_logger, get_error_logger

class FileOps:
    """
    Handles file operations with safety validation and logging.
    Follows the AGENT_MANIFEST.md principles for safe file operations and logging.
    """
    
    def __init__(self, app_state: Dict[str, Any]):
        """
        Initialize FileOps with application state and logging.
        
        Args:
            app_state: Application state containing config, memory, etc.
        """
        self.app_state = app_state
        self.config = app_state.get('config', {})
        self.logger = get_action_logger('file_ops')
        self.error_logger = get_error_logger('file_ops')
        
        # Dangerous file patterns
        self.dangerous_patterns = [
            '/etc/', '/var/', '/usr/', '/bin/', '/sbin/', '/boot/',
            '/proc/', '/sys/', '/dev/', '/root/', '/home/'
        ]
        
        self.logger.info("FileOps initialized with safety validation")

    def create_file(self, file_path: str, content: str = '') -> Dict[str, Any]:
        """
        Create a new file with optional content.
        
        Args:
            file_path: Path to the file to create
            content: Optional content to write to the file
            
        Returns:
            File creation result
        """
        self.logger.info("Creating file", extra={'file_path': file_path})
        
        try:
            # Safety validation
            if not self._is_path_safe(file_path):
                error_msg = f"File path blocked for safety: {file_path}"
                self.error_logger.warning(error_msg)
                return {
                    'status': 'blocked',
                    'error': error_msg,
                    'file_path': file_path,
                    'executed_at': datetime.utcnow().isoformat() + 'Z'
                }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write content to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Get file info
            file_info = self._get_file_info(file_path)
            
            result = {
                'status': 'success',
                'file_path': file_path,
                'file_size': len(content),
                'file_info': file_info,
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }
            
            self.logger.info("File created successfully", extra=result)
            return result
            
        except Exception as e:
            error_msg = f"Failed to create file: {e}"
            self.error_logger.error(error_msg, exc_info=True)
            return {
                'status': 'failed',
                'error': error_msg,
                'file_path': file_path,
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }

    def read_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read content from a file.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            File reading result
        """
        self.logger.info("Reading file", extra={'file_path': file_path})
        
        try:
            # Safety validation
            if not self._is_path_safe(file_path):
                error_msg = f"File path blocked for safety: {file_path}"
                self.error_logger.warning(error_msg)
                return {
                    'status': 'blocked',
                    'error': error_msg,
                    'file_path': file_path,
                    'executed_at': datetime.utcnow().isoformat() + 'Z'
                }
            
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    'status': 'not_found',
                    'error': f'File not found: {file_path}',
                    'file_path': file_path,
                    'executed_at': datetime.utcnow().isoformat() + 'Z'
                }
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get file info
            file_info = self._get_file_info(file_path)
            
            result = {
                'status': 'success',
                'file_path': file_path,
                'content': content,
                'content_length': len(content),
                'file_info': file_info,
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }
            
            self.logger.info("File read successfully", extra={
                'file_path': file_path,
                'content_length': len(content)
            })
            return result
            
        except Exception as e:
            error_msg = f"Failed to read file: {e}"
            self.error_logger.error(error_msg, exc_info=True)
            return {
                'status': 'failed',
                'error': error_msg,
                'file_path': file_path,
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }

    def edit_file(self, file_path: str, new_content: str) -> Dict[str, Any]:
        """
        Edit an existing file with new content.
        
        Args:
            file_path: Path to the file to edit
            new_content: New content to write to the file
            
        Returns:
            File editing result
        """
        self.logger.info("Editing file", extra={'file_path': file_path})
        
        try:
            # Safety validation
            if not self._is_path_safe(file_path):
                error_msg = f"File path blocked for safety: {file_path}"
                self.error_logger.warning(error_msg)
                return {
                    'status': 'blocked',
                    'error': error_msg,
                    'file_path': file_path,
                    'executed_at': datetime.utcnow().isoformat() + 'Z'
                }
            
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    'status': 'not_found',
                    'error': f'File not found: {file_path}',
                    'file_path': file_path,
                    'executed_at': datetime.utcnow().isoformat() + 'Z'
                }
            
            # Create backup before editing
            backup_path = self._create_backup(file_path)
            
            # Write new content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # Get file info
            file_info = self._get_file_info(file_path)
            
            result = {
                'status': 'success',
                'file_path': file_path,
                'backup_path': backup_path,
                'content_length': len(new_content),
                'file_info': file_info,
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }
            
            self.logger.info("File edited successfully", extra=result)
            return result
            
        except Exception as e:
            error_msg = f"Failed to edit file: {e}"
            self.error_logger.error(error_msg, exc_info=True)
            return {
                'status': 'failed',
                'error': error_msg,
                'file_path': file_path,
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }

    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """
        Delete a file with safety validation.
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            File deletion result
        """
        self.logger.info("Deleting file", extra={'file_path': file_path})
        
        try:
            # Safety validation
            if not self._is_path_safe(file_path):
                error_msg = f"File path blocked for safety: {file_path}"
                self.error_logger.warning(error_msg)
                return {
                    'status': 'blocked',
                    'error': error_msg,
                    'file_path': file_path,
                    'executed_at': datetime.utcnow().isoformat() + 'Z'
                }
            
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    'status': 'not_found',
                    'error': f'File not found: {file_path}',
                    'file_path': file_path,
                    'executed_at': datetime.utcnow().isoformat() + 'Z'
                }
            
            # Get file info before deletion
            file_info = self._get_file_info(file_path)
            
            # Delete the file
            os.remove(file_path)
            
            result = {
                'status': 'success',
                'file_path': file_path,
                'deleted_file_info': file_info,
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }
            
            self.logger.info("File deleted successfully", extra=result)
            return result
            
        except Exception as e:
            error_msg = f"Failed to delete file: {e}"
            self.error_logger.error(error_msg, exc_info=True)
            return {
                'status': 'failed',
                'error': error_msg,
                'file_path': file_path,
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }

    def move_file(self, source_path: str, destination_path: str) -> Dict[str, Any]:
        """
        Move a file from source to destination.
        
        Args:
            source_path: Source file path
            destination_path: Destination file path
            
        Returns:
            File move result
        """
        self.logger.info("Moving file", extra={
            'source_path': source_path,
            'destination_path': destination_path
        })
        
        try:
            # Safety validation
            if not self._is_path_safe(source_path) or not self._is_path_safe(destination_path):
                error_msg = f"File path blocked for safety: {source_path} -> {destination_path}"
                self.error_logger.warning(error_msg)
                return {
                    'status': 'blocked',
                    'error': error_msg,
                    'source_path': source_path,
                    'destination_path': destination_path,
                    'executed_at': datetime.utcnow().isoformat() + 'Z'
                }
            
            # Check if source file exists
            if not os.path.exists(source_path):
                return {
                    'status': 'not_found',
                    'error': f'Source file not found: {source_path}',
                    'source_path': source_path,
                    'destination_path': destination_path,
                    'executed_at': datetime.utcnow().isoformat() + 'Z'
                }
            
            # Create destination directory if it doesn't exist
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            
            # Move the file
            shutil.move(source_path, destination_path)
            
            # Get file info
            file_info = self._get_file_info(destination_path)
            
            result = {
                'status': 'success',
                'source_path': source_path,
                'destination_path': destination_path,
                'file_info': file_info,
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }
            
            self.logger.info("File moved successfully", extra=result)
            return result
            
        except Exception as e:
            error_msg = f"Failed to move file: {e}"
            self.error_logger.error(error_msg, exc_info=True)
            return {
                'status': 'failed',
                'error': error_msg,
                'source_path': source_path,
                'destination_path': destination_path,
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }

    def copy_file(self, source_path: str, destination_path: str) -> Dict[str, Any]:
        """
        Copy a file from source to destination.
        
        Args:
            source_path: Source file path
            destination_path: Destination file path
            
        Returns:
            File copy result
        """
        self.logger.info("Copying file", extra={
            'source_path': source_path,
            'destination_path': destination_path
        })
        
        try:
            # Safety validation
            if not self._is_path_safe(source_path) or not self._is_path_safe(destination_path):
                error_msg = f"File path blocked for safety: {source_path} -> {destination_path}"
                self.error_logger.warning(error_msg)
                return {
                    'status': 'blocked',
                    'error': error_msg,
                    'source_path': source_path,
                    'destination_path': destination_path,
                    'executed_at': datetime.utcnow().isoformat() + 'Z'
                }
            
            # Check if source file exists
            if not os.path.exists(source_path):
                return {
                    'status': 'not_found',
                    'error': f'Source file not found: {source_path}',
                    'source_path': source_path,
                    'destination_path': destination_path,
                    'executed_at': datetime.utcnow().isoformat() + 'Z'
                }
            
            # Create destination directory if it doesn't exist
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            
            # Copy the file
            shutil.copy2(source_path, destination_path)
            
            # Get file info
            file_info = self._get_file_info(destination_path)
            
            result = {
                'status': 'success',
                'source_path': source_path,
                'destination_path': destination_path,
                'file_info': file_info,
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }
            
            self.logger.info("File copied successfully", extra=result)
            return result
            
        except Exception as e:
            error_msg = f"Failed to copy file: {e}"
            self.error_logger.error(error_msg, exc_info=True)
            return {
                'status': 'failed',
                'error': error_msg,
                'source_path': source_path,
                'destination_path': destination_path,
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }

    def create_backup(self, file_path: str) -> Dict[str, Any]:
        """
        Create a backup of a file.
        
        Args:
            file_path: Path to the file to backup
            
        Returns:
            Backup creation result
        """
        self.logger.info("Creating backup", extra={'file_path': file_path})
        
        try:
            # Safety validation
            if not self._is_path_safe(file_path):
                error_msg = f"File path blocked for safety: {file_path}"
                self.error_logger.warning(error_msg)
                return {
                    'status': 'blocked',
                    'error': error_msg,
                    'file_path': file_path,
                    'executed_at': datetime.utcnow().isoformat() + 'Z'
                }
            
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    'status': 'not_found',
                    'error': f'File not found: {file_path}',
                    'file_path': file_path,
                    'executed_at': datetime.utcnow().isoformat() + 'Z'
                }
            
            # Create backup path
            backup_path = self._create_backup(file_path)
            
            result = {
                'status': 'success',
                'file_path': file_path,
                'backup_path': backup_path,
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }
            
            self.logger.info("Backup created successfully", extra=result)
            return result
            
        except Exception as e:
            error_msg = f"Failed to create backup: {e}"
            self.error_logger.error(error_msg, exc_info=True)
            return {
                'status': 'failed',
                'error': error_msg,
                'file_path': file_path,
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }

    def _is_path_safe(self, file_path: str) -> bool:
        """
        Check if a file path is safe to operate on.
        
        Args:
            file_path: Path to validate
            
        Returns:
            True if path is safe, False otherwise
        """
        # Normalize path
        abs_path = os.path.abspath(file_path)
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if pattern in abs_path:
                return False
        
        # Check if path is within current working directory
        cwd = os.getcwd()
        if not abs_path.startswith(cwd):
            return False
        
        return True

    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File information dictionary
        """
        try:
            stat = os.stat(file_path)
            return {
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'permissions': oct(stat.st_mode)[-3:]
            }
        except Exception as e:
            return {'error': str(e)}

    def _create_backup(self, file_path: str) -> str:
        """
        Create a backup of a file in the undo directory.
        
        Args:
            file_path: Path to the file to backup
            
        Returns:
            Path to the backup file
        """
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = os.path.basename(file_path)
        backup_filename = f"{filename}.backup_{timestamp}"
        
        # Create backup directory
        backup_dir = os.path.join(self.config.get('paths', {}).get('undo', 'undo'), 'snapshots')
        os.makedirs(backup_dir, exist_ok=True)
        
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Copy file to backup location
        shutil.copy2(file_path, backup_path)
        
        return backup_path 