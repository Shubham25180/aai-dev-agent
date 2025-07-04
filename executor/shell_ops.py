import subprocess
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from utils.logger import get_action_logger, get_error_logger

class ShellOps:
    """
    Handles shell command execution with safety validation and logging.
    Follows the AGENT_MANIFEST.md principles for safe execution and logging.
    """
    
    def __init__(self, app_state: Dict[str, Any]):
        """
        Initialize ShellOps with application state and logging.
        
        Args:
            app_state: Application state containing config, memory, etc.
        """
        self.app_state = app_state
        self.config = app_state.get('config', {})
        self.logger = get_action_logger('shell_ops', subsystem='core')
        self.error_logger = get_error_logger('shell_ops', subsystem='core')
        
        # Dangerous commands that require confirmation
        self.dangerous_commands = [
            'rm -rf', 'sudo', 'chmod 777', 'dd if=', 'mkfs', 'fdisk',
            'shutdown', 'reboot', 'kill -9', 'pkill', 'killall'
        ]
        
        self.logger.info("ShellOps initialized with safety validation")

    def run_command(self, command: str, cwd: Optional[str] = None, timeout: int = 30) -> Dict[str, Any]:
        """
        Run a shell command with safety validation and logging.
        
        Args:
            command: Shell command to execute
            cwd: Working directory for command execution
            timeout: Command timeout in seconds
            
        Returns:
            Dictionary containing command result and metadata
        """
        self.logger.info("Executing shell command", extra={'command': command, 'cwd': cwd})
        
        try:
            # Safety validation
            if not self._is_command_safe(command):
                error_msg = f"Command blocked for safety: {command}"
                self.error_logger.warning(error_msg)
                return {
                    'status': 'blocked',
                    'error': error_msg,
                    'command': command,
                    'executed_at': datetime.utcnow().isoformat() + 'Z'
                }
            
            # Execute command
            result = self._execute_command(command, cwd, timeout)
            
            # Log result
            self.logger.info("Command executed successfully", extra={
                'command': command,
                'return_code': result.get('return_code'),
                'output_length': len(result.get('stdout', ''))
            })
            
            return result
            
        except Exception as e:
            error_msg = f"Command execution failed: {e}"
            self.error_logger.error(error_msg, exc_info=True)
            return {
                'status': 'failed',
                'error': error_msg,
                'command': command,
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }

    def _is_command_safe(self, command: str) -> bool:
        """
        Check if a command is safe to execute.
        
        Args:
            command: Command to validate
            
        Returns:
            True if command is safe, False otherwise
        """
        command_lower = command.lower()
        
        # Check for dangerous commands
        for dangerous in self.dangerous_commands:
            if dangerous.lower() in command_lower:
                return False
        
        # Check for suspicious patterns
        suspicious_patterns = [
            '> /dev/', '>> /dev/', '| bash', '| sh', '| python -c',
            'eval ', 'exec ', 'system(', 'os.system'
        ]
        
        for pattern in suspicious_patterns:
            if pattern in command_lower:
                return False
        
        return True

    def _execute_command(self, command: str, cwd: Optional[str], timeout: int) -> Dict[str, Any]:
        """
        Execute a shell command using subprocess.
        
        Args:
            command: Command to execute
            cwd: Working directory
            timeout: Command timeout
            
        Returns:
            Command execution result
        """
        try:
            # Use shell=True for command execution
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd
            )
            
            # Wait for completion with timeout
            stdout, stderr = process.communicate(timeout=timeout)
            return_code = process.returncode
            
            # Determine status
            if return_code == 0:
                status = 'success'
            else:
                status = 'error'
            
            return {
                'status': status,
                'command': command,
                'return_code': return_code,
                'stdout': stdout,
                'stderr': stderr,
                'executed_at': datetime.utcnow().isoformat() + 'Z',
                'cwd': cwd or os.getcwd()
            }
            
        except subprocess.TimeoutExpired:
            process.kill()
            return {
                'status': 'timeout',
                'command': command,
                'error': f'Command timed out after {timeout} seconds',
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'command': command,
                'error': str(e),
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }

    def run_python_script(self, script_path: str, args: Optional[list] = None) -> Dict[str, Any]:
        """
        Run a Python script with arguments.
        
        Args:
            script_path: Path to Python script
            args: Optional list of arguments
            
        Returns:
            Script execution result
        """
        command = f"python {script_path}"
        if args:
            command += " " + " ".join(args)
        
        return self.run_command(command)

    def install_package(self, package_name: str, package_manager: str = 'pip') -> Dict[str, Any]:
        """
        Install a Python package using the specified package manager.
        
        Args:
            package_name: Name of package to install
            package_manager: Package manager to use (pip, conda, etc.)
            
        Returns:
            Installation result
        """
        if package_manager == 'pip':
            command = f"pip install {package_name}"
        elif package_manager == 'conda':
            command = f"conda install -y {package_name}"
        else:
            return {
                'status': 'error',
                'error': f'Unsupported package manager: {package_manager}',
                'executed_at': datetime.utcnow().isoformat() + 'Z'
            }
        
        return self.run_command(command)

    def check_file_exists(self, file_path: str) -> Dict[str, Any]:
        """
        Check if a file exists using shell command.
        
        Args:
            file_path: Path to check
            
        Returns:
            File existence check result
        """
        command = f"test -f '{file_path}' && echo 'exists' || echo 'not_found'"
        result = self.run_command(command)
        
        if result.get('status') == 'success':
            exists = 'exists' in result.get('stdout', '')
            result['file_exists'] = exists
            result['file_path'] = file_path
        
        return result

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get file information using shell commands.
        
        Args:
            file_path: Path to file
            
        Returns:
            File information
        """
        commands = [
            f"ls -la '{file_path}'",
            f"file '{file_path}'",
            f"wc -l '{file_path}'"
        ]
        
        results = {}
        for cmd in commands:
            result = self.run_command(cmd)
            results[cmd] = result
        
        return {
            'status': 'success',
            'file_path': file_path,
            'results': results,
            'executed_at': datetime.utcnow().isoformat() + 'Z'
        }

    def create_directory(self, dir_path: str) -> Dict[str, Any]:
        """
        Create a directory using shell command.
        
        Args:
            dir_path: Path to directory to create
            
        Returns:
            Directory creation result
        """
        command = f"mkdir -p '{dir_path}'"
        result = self.run_command(command)
        result['directory_path'] = dir_path
        return result

    def list_directory(self, dir_path: str = '.') -> Dict[str, Any]:
        """
        List directory contents using shell command.
        
        Args:
            dir_path: Directory to list
            
        Returns:
            Directory listing result
        """
        command = f"ls -la '{dir_path}'"
        result = self.run_command(command)
        result['directory_path'] = dir_path
        return result

    def search_files(self, pattern: str, directory: str = '.') -> Dict[str, Any]:
        """
        Search for files using find command.
        
        Args:
            pattern: File pattern to search for
            directory: Directory to search in
            
        Returns:
            File search result
        """
        command = f"find '{directory}' -name '{pattern}' -type f"
        result = self.run_command(command)
        result['search_pattern'] = pattern
        result['search_directory'] = directory
        return result

    def grep_file(self, pattern: str, file_path: str) -> Dict[str, Any]:
        """
        Search for pattern in file using grep.
        
        Args:
            pattern: Pattern to search for
            file_path: File to search in
            
        Returns:
            Grep search result
        """
        command = f"grep -n '{pattern}' '{file_path}'"
        result = self.run_command(command)
        result['search_pattern'] = pattern
        result['file_path'] = file_path
        return result 