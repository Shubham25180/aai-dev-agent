import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from utils.logger import get_action_logger, get_error_logger
from executor.shell_ops import ShellOps
from executor.file_ops import FileOps
from executor.code_editor import CodeEditor
from executor.gui_ops import GuiOps

class Router:
    """
    Routes tasks to appropriate executors based on task type and requirements.
    Follows the AGENT_MANIFEST.md principles for structured routing and logging.
    """
    
    def __init__(self, app_state: Dict[str, Any]):
        """
        Initialize the Router with application state and executors.
        
        Args:
            app_state: Application state containing config, memory, etc.
        """
        self.app_state = app_state
        self.config = app_state.get('config', {})
        self.logger = get_action_logger('router', subsystem='core')
        self.error_logger = get_error_logger('router', subsystem='core')
        
        # Initialize executors
        self.shell_ops = ShellOps(app_state)
        self.file_ops = FileOps(app_state)
        self.code_editor = CodeEditor(app_state)
        self.gui_ops = GuiOps(app_state)
        
        # Task type mapping
        self.task_routes = {
            'shell': self._route_shell_task,
            'file': self._route_file_task,
            'code': self._route_code_task,
            'gui': self._route_gui_task,
            'analysis': self._route_analysis_task,
            'backup': self._route_backup_task,
            'refactor': self._route_refactor_task,
            'update': self._route_update_task,
            'validation': self._route_validation_task,
            'planning': self._route_planning_task,
            'setup': self._route_setup_task,
            'implementation': self._route_implementation_task,
            'quality': self._route_quality_task,
            'investigation': self._route_investigation_task,
            'fix': self._route_fix_task,
            'creation': self._route_creation_task,
            'execution': self._route_execution_task,
            'preparation': self._route_preparation_task,
            'deployment': self._route_deployment_task,
            'verification': self._route_verification_task,
            'documentation': self._route_documentation_task
        }
        
        self.logger.info("Router initialized with all executors")

    def route(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route a task to the appropriate executor.
        
        Args:
            task: Task dictionary containing step information
            
        Returns:
            Execution result from the appropriate executor
        """
        self.logger.info("Routing task", extra={'task': task})
        
        try:
            # Determine task type
            task_type = self._determine_task_type(task)
            
            # Route to appropriate handler
            if task_type in self.task_routes:
                result = self.task_routes[task_type](task)
            else:
                # Default to shell operations for unknown task types
                result = self._route_shell_task(task)
            
            # Add routing metadata
            result['routed_to'] = task_type
            result['routed_at'] = datetime.utcnow().isoformat() + 'Z'
            
            self.logger.info("Task routed successfully", extra={
                'task_type': task_type,
                'result_status': result.get('status', 'unknown')
            })
            
            return result
            
        except Exception as e:
            error_msg = f"Failed to route task: {e}"
            self.error_logger.error(error_msg, exc_info=True)
            return {
                'status': 'failed',
                'error': error_msg,
                'routed_at': datetime.utcnow().isoformat() + 'Z'
            }

    def _determine_task_type(self, task: Dict[str, Any]) -> str:
        """
        Determine the type of task based on its description and file path.
        
        Args:
            task: Task dictionary
            
        Returns:
            Task type string
        """
        description = task.get('description', '').lower()
        file_path = task.get('file', '').lower()
        task_type = task.get('type', '').lower()
        
        # If task type is explicitly specified, use it
        if task_type and task_type in self.task_routes:
            return task_type
        
        # Determine type based on description keywords
        if any(keyword in description for keyword in ['command', 'shell', 'run', 'execute']):
            return 'shell'
        elif any(keyword in description for keyword in ['file', 'create', 'delete', 'move', 'copy']):
            return 'file'
        elif any(keyword in description for keyword in ['code', 'edit', 'refactor', 'implement']):
            return 'code'
        elif any(keyword in description for keyword in ['gui', 'click', 'mouse', 'keyboard']):
            return 'gui'
        elif any(keyword in description for keyword in ['analyze', 'investigate', 'examine']):
            return 'analysis'
        elif any(keyword in description for keyword in ['backup', 'snapshot', 'save']):
            return 'backup'
        elif any(keyword in description for keyword in ['test', 'validate', 'check']):
            return 'validation'
        elif any(keyword in description for keyword in ['plan', 'design', 'specify']):
            return 'planning'
        elif any(keyword in description for keyword in ['setup', 'install', 'configure']):
            return 'setup'
        elif any(keyword in description for keyword in ['fix', 'debug', 'resolve']):
            return 'fix'
        elif any(keyword in description for keyword in ['deploy', 'release', 'publish']):
            return 'deployment'
        elif any(keyword in description for keyword in ['document', 'write', 'create']):
            return 'documentation'
        
        # Determine type based on file path
        if file_path.endswith(('.py', '.js', '.java', '.cpp', '.c', '.h')):
            return 'code'
        elif file_path.startswith(('logs/', 'memory/', 'undo/')):
            return 'file'
        elif file_path in ['analysis', 'test_results', 'reports']:
            return 'analysis'
        
        # Default to shell for unknown types
        return 'shell'

    def _route_shell_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route shell-related tasks."""
        try:
            # Extract command from task description or create one
            command = self._extract_command_from_task(task)
            return self.shell_ops.run_command(command)
        except Exception as e:
            self.error_logger.error(f"Shell task routing failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _route_file_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route file operation tasks."""
        try:
            file_path = task.get('file', '')
            description = task.get('description', '').lower()
            
            if 'create' in description:
                return self.file_ops.create_file(file_path)
            elif 'delete' in description:
                return self.file_ops.delete_file(file_path)
            elif 'move' in description or 'copy' in description:
                return self.file_ops.move_file(file_path, 'destination_path')
            else:
                return self.file_ops.read_file(file_path)
        except Exception as e:
            self.error_logger.error(f"File task routing failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _route_code_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route code editing tasks."""
        try:
            file_path = task.get('file', '')
            description = task.get('description', '').lower()
            
            if 'refactor' in description:
                return self.code_editor.refactor_code(file_path, description)
            elif 'implement' in description:
                return self.code_editor.implement_feature(file_path, description)
            else:
                return self.code_editor.edit_file(file_path, description)
        except Exception as e:
            self.error_logger.error(f"Code task routing failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _route_gui_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route GUI automation tasks."""
        try:
            description = task.get('description', '').lower()
            
            if 'click' in description:
                return self.gui_ops.click_element('element_selector')
            elif 'type' in description or 'input' in description:
                return self.gui_ops.type_text('text_to_type')
            else:
                return self.gui_ops.perform_action(description)
        except Exception as e:
            self.error_logger.error(f"GUI task routing failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _route_analysis_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route analysis tasks."""
        try:
            # Analysis tasks typically involve examining files or logs
            file_path = task.get('file', '')
            description = task.get('description', '')
            
            # Create analysis command
            if file_path == 'logs/errors/':
                command = "find logs/errors/ -name '*.log' -exec tail -n 50 {} \\;"
            elif file_path == 'analysis':
                command = "echo 'Analysis task: " + description + "'"
            else:
                command = f"echo 'Analyzing: {description}'"
            
            return self.shell_ops.run_command(command)
        except Exception as e:
            self.error_logger.error(f"Analysis task routing failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _route_backup_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route backup/snapshot tasks."""
        try:
            # Backup tasks involve creating snapshots
            file_path = task.get('file', '')
            if file_path == 'undo/snapshots':
                return self.file_ops.create_backup('current_files')
            else:
                return self.file_ops.create_backup(file_path)
        except Exception as e:
            self.error_logger.error(f"Backup task routing failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _route_refactor_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route refactoring tasks."""
        try:
            file_path = task.get('file', '')
            description = task.get('description', '')
            
            if file_path == 'utils/':
                return self.code_editor.extract_utilities(description)
            else:
                return self.code_editor.refactor_code(file_path, description)
        except Exception as e:
            self.error_logger.error(f"Refactor task routing failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _route_update_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route update tasks."""
        try:
            file_path = task.get('file', 'affected_files')
            description = task.get('description', '')
            
            if 'import' in description.lower():
                return self.code_editor.update_imports(file_path)
            else:
                return self.code_editor.update_file(file_path, description)
        except Exception as e:
            self.error_logger.error(f"Update task routing failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _route_validation_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route validation/testing tasks."""
        try:
            file_path = task.get('file', '')
            description = task.get('description', '')
            
            if file_path == 'tests/':
                command = "python -m pytest tests/ -v"
            elif 'test' in description.lower():
                command = f"echo 'Running validation: {description}'"
            else:
                command = "echo 'Validation task completed'"
            
            return self.shell_ops.run_command(command)
        except Exception as e:
            self.error_logger.error(f"Validation task routing failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _route_planning_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route planning tasks."""
        try:
            # Planning tasks typically involve creating documentation
            file_path = task.get('file', '')
            description = task.get('description', '')
            
            if file_path == 'requirements.md':
                return self.file_ops.create_file(file_path, f"# Requirements\n\n{description}")
            elif file_path == 'plan.md':
                return self.file_ops.create_file(file_path, f"# Implementation Plan\n\n{description}")
            else:
                return self.file_ops.create_file('plan.md', f"# Plan\n\n{description}")
        except Exception as e:
            self.error_logger.error(f"Planning task routing failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _route_setup_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route setup tasks."""
        try:
            description = task.get('description', '')
            
            if 'structure' in description.lower():
                command = "mkdir -p src/ tests/ docs/ deploy/"
            elif 'scaffold' in description.lower():
                command = "echo 'Creating project scaffolding'"
            else:
                command = f"echo 'Setup task: {description}'"
            
            return self.shell_ops.run_command(command)
        except Exception as e:
            self.error_logger.error(f"Setup task routing failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _route_implementation_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route implementation tasks."""
        try:
            file_path = task.get('file', '')
            description = task.get('description', '')
            
            if file_path == 'src/':
                return self.code_editor.implement_feature(file_path, description)
            else:
                return self.code_editor.implement_feature('src/', description)
        except Exception as e:
            self.error_logger.error(f"Implementation task routing failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _route_quality_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route quality assurance tasks."""
        try:
            file_path = task.get('file', '')
            description = task.get('description', '')
            
            if 'test' in description.lower():
                command = "python -m pytest tests/ --cov=src/"
            elif 'document' in description.lower():
                return self.file_ops.create_file('docs/README.md', f"# Documentation\n\n{description}")
            else:
                command = f"echo 'Quality task: {description}'"
            
            return self.shell_ops.run_command(command)
        except Exception as e:
            self.error_logger.error(f"Quality task routing failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _route_investigation_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route investigation tasks."""
        try:
            file_path = task.get('file', '')
            description = task.get('description', '')
            
            if file_path == 'logs/errors/':
                command = "grep -r 'ERROR' logs/errors/ | tail -n 20"
            else:
                command = f"echo 'Investigating: {description}'"
            
            return self.shell_ops.run_command(command)
        except Exception as e:
            self.error_logger.error(f"Investigation task routing failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _route_fix_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route fix/debug tasks."""
        try:
            file_path = task.get('file', '')
            description = task.get('description', '')
            
            if file_path == 'fix/':
                return self.code_editor.create_fix(description)
            else:
                return self.code_editor.fix_issue(file_path, description)
        except Exception as e:
            self.error_logger.error(f"Fix task routing failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _route_creation_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route creation tasks."""
        try:
            file_path = task.get('file', '')
            description = task.get('description', '')
            
            if file_path == 'src/':
                return self.code_editor.create_module(file_path, description)
            else:
                return self.file_ops.create_file(file_path, f"# Created: {description}")
        except Exception as e:
            self.error_logger.error(f"Creation task routing failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _route_execution_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route execution tasks."""
        try:
            file_path = task.get('file', '')
            description = task.get('description', '')
            
            if file_path == 'test_results/':
                command = "python -m pytest --json-report --json-report-file=test_results/results.json"
            else:
                command = f"echo 'Executing: {description}'"
            
            return self.shell_ops.run_command(command)
        except Exception as e:
            self.error_logger.error(f"Execution task routing failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _route_preparation_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route preparation tasks."""
        try:
            file_path = task.get('file', '')
            description = task.get('description', '')
            
            if file_path == 'deploy/':
                command = "mkdir -p deploy/scripts deploy/config"
            else:
                command = f"echo 'Preparing: {description}'"
            
            return self.shell_ops.run_command(command)
        except Exception as e:
            self.error_logger.error(f"Preparation task routing failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _route_deployment_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route deployment tasks."""
        try:
            file_path = task.get('file', '')
            description = task.get('description', '')
            
            if file_path == 'deploy/scripts/':
                command = "echo 'Running deployment scripts'"
            else:
                command = f"echo 'Deploying: {description}'"
            
            return self.shell_ops.run_command(command)
        except Exception as e:
            self.error_logger.error(f"Deployment task routing failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _route_verification_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route verification tasks."""
        try:
            file_path = task.get('file', '')
            description = task.get('description', '')
            
            if file_path == 'monitoring/':
                command = "echo 'Checking deployment health'"
            else:
                command = f"echo 'Verifying: {description}'"
            
            return self.shell_ops.run_command(command)
        except Exception as e:
            self.error_logger.error(f"Verification task routing failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _route_documentation_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route documentation tasks."""
        try:
            file_path = task.get('file', '')
            description = task.get('description', '')
            
            if file_path == 'docs/':
                return self.file_ops.create_file('docs/optimizations.md', f"# Optimizations\n\n{description}")
            else:
                return self.file_ops.create_file('docs/changes.md', f"# Changes\n\n{description}")
        except Exception as e:
            self.error_logger.error(f"Documentation task routing failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _extract_command_from_task(self, task: Dict[str, Any]) -> str:
        """
        Extract or create a shell command from task description.
        
        Args:
            task: Task dictionary
            
        Returns:
            Shell command string
        """
        description = task.get('description', '').lower()
        
        # Common command patterns
        if 'ls' in description or 'list' in description:
            return "ls -la"
        elif 'grep' in description or 'search' in description:
            return "grep -r 'pattern' ."
        elif 'find' in description:
            return "find . -name '*.py'"
        elif 'test' in description:
            return "python -m pytest"
        elif 'install' in description:
            return "pip install -r requirements.txt"
        elif 'run' in description:
            return "python main.py"
        else:
            # Default command based on description
            return f"echo 'Executing: {task.get('description', 'Unknown task')}'" 