import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from utils.logger import get_action_logger, get_error_logger
from agents.planner import Planner
from agents.llm_connector import LLMConnector
from app.router import Router

class Controller:
    """
    Main application controller for AI Dev Agent.
    Manages the flow between input → plan → execute with memory integration.
    Follows AGENT_MANIFEST.md principles for automatic control and memory management.
    """
    
    def __init__(self, config: Dict[str, Any], router=None, planner=None, memory_manager=None):
        """
        Initialize Controller with all required components.
        
        Args:
            config: Application configuration
            router: Router instance for task execution
            planner: Planner instance for task planning
            memory_manager: MemoryManager instance for memory operations
        """
        self.config = config
        self.logger = get_action_logger('controller')
        self.error_logger = get_error_logger('controller')
        
        # Core components
        self.router = router
        self.planner = planner
        self.memory_manager = memory_manager
        
        # Controller state
        self.current_task = None
        self.current_plan = None
        self.execution_history = []
        self.session_start = datetime.utcnow()
        
        # Setup memory hooks if memory manager is available
        if self.memory_manager:
            self._setup_memory_hooks()
        
        self.logger.info("Controller initialized with memory integration")

    def _setup_memory_hooks(self):
        """
        Setup memory update hooks for automatic memory management.
        """
        if self.memory_manager:
            # Hook for task completion
            self.memory_manager.add_update_hook(self._on_memory_update)
            self.logger.info("Memory hooks configured")

    def _on_memory_update(self, memory_type: str, key: str, value: Any):
        """
        Handle memory updates from other components.
        
        Args:
            memory_type: Type of memory updated
            key: Memory key
            value: Updated value
        """
        try:
            self.logger.info(f"Memory update received", 
                           extra={'memory_type': memory_type, 'key': key})
            
            # Update controller state based on memory changes
            if memory_type == 'short_term' and key == 'current_plan':
                self.current_plan = value
            elif memory_type == 'short_term' and key == 'task_status':
                self._handle_task_status_update(value)
                
        except Exception as e:
            self.error_logger.error(f"Failed to handle memory update: {e}")

    def process_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a task through the complete workflow: plan → execute → memory update.
        
        Args:
            task: Task description
            context: Additional context for task execution
            
        Returns:
            Complete execution result with status and details
        """
        try:
            self.logger.info("Starting task processing", extra={'task': task})
            
            # Update memory with new task
            if self.memory_manager:
                self.memory_manager.update_short_term('current_task', {
                    'task': task,
                    'started_at': datetime.utcnow().isoformat() + 'Z',
                    'context': context or {}
                })
            
            self.current_task = task
            
            # Step 1: Create plan
            plan_result = self._create_plan(task, context)
            if not plan_result.get('success', False):
                return self._create_error_result("Failed to create plan", str(plan_result.get('error', 'Unknown error')))
            
            # Step 2: Execute plan
            execution_result = self._execute_plan(plan_result['plan'])
            if not execution_result.get('success', False):
                return self._create_error_result("Failed to execute plan", str(execution_result.get('error', 'Unknown error')))
            
            # Step 3: Update memory with results
            self._update_memory_with_results(task, plan_result['plan'], execution_result)
            
            # Step 4: Create final result
            final_result = self._create_success_result(task, plan_result['plan'], execution_result)
            
            self.logger.info("Task processing completed successfully", 
                           extra={'task': task, 'steps_completed': len(execution_result.get('step_results', []))})
            
            return final_result
            
        except Exception as e:
            self.error_logger.error(f"Task processing failed: {e}")
            return self._create_error_result("Task processing failed", str(e))

    def _create_plan(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create execution plan for the task.
        
        Args:
            task: Task description
            context: Additional context
            
        Returns:
            Plan creation result
        """
        try:
            if not self.planner:
                return {'success': False, 'error': 'Planner not available'}
            
            # Get memory context for planning
            memory_context: Optional[Dict[str, Any]] = None
            if self.memory_manager:
                memory_context = self.memory_manager.get_memory_context()
            
            # Create plan
            plan = self.planner.create_plan(task, context or {})
            
            if plan.get('error'):
                return {'success': False, 'error': str(plan['error'])}
            
            self.current_plan = plan
            
            # Update memory with plan
            if self.memory_manager:
                self.memory_manager.update_short_term('current_plan', {
                    'plan_id': plan['plan_id'],
                    'task': task,
                    'status': 'created',
                    'step_count': len(plan.get('steps', []))
                })
            
            return {'success': True, 'plan': plan}
            
        except Exception as e:
            self.error_logger.error(f"Plan creation failed: {e}")
            return {'success': False, 'error': str(e)}

    def _execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the created plan step by step.
        
        Args:
            plan: Execution plan
            
        Returns:
            Execution result
        """
        try:
            if not self.router:
                return {'success': False, 'error': 'Router not available'}
            
            steps = plan.get('steps', [])
            step_results = []
            failed_steps = []
            
            # Update plan status
            if self.planner:
                self.planner.update_plan_status(plan['plan_id'], 'in_progress')
            
            # Execute each step
            for step in steps:
                step_result = self._execute_step(step, plan)
                step_results.append(step_result)
                
                if not step_result.get('success', False):
                    failed_steps.append(step_result)
                    # Continue with other steps unless critical
                    if step.get('priority') == 'high':
                        break
            
            # Determine overall success
            success = len(failed_steps) == 0 or all(step.get('priority') != 'high' for step in failed_steps)
            
            # Update plan status
            if self.planner:
                final_status = 'completed' if success else 'failed'
                self.planner.update_plan_status(plan['plan_id'], final_status, step_results)
            
            return {
                'success': success,
                'step_results': step_results,
                'failed_steps': failed_steps,
                'total_steps': len(steps),
                'completed_steps': len([r for r in step_results if r.get('success', False)])
            }
            
        except Exception as e:
            self.error_logger.error(f"Plan execution failed: {e}")
            return {'success': False, 'error': str(e)}

    def _execute_step(self, step: Dict[str, Any], plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single plan step.
        
        Args:
            step: Step to execute
            plan: Parent plan
            
        Returns:
            Step execution result
        """
        try:
            step_id = step.get('step_id', 'unknown')
            action = step.get('action', 'unknown_action')
            module = step.get('module', 'unknown_module')
            
            self.logger.info(f"Executing step {step_id}", 
                           extra={'action': action, 'module': module})
            
            # Update step status
            step['status'] = 'in_progress'
            step['started_at'] = datetime.utcnow().isoformat() + 'Z'
            
            # Execute via router
            if self.router:
                result = self.router.execute_action(action, step, plan)
            else:
                result = {'success': False, 'error': 'Router not available'}
            
            # Update step status
            step['status'] = 'completed' if result.get('success', False) else 'failed'
            step['completed_at'] = datetime.utcnow().isoformat() + 'Z'
            step['result'] = result
            
            # Update memory with step result
            if self.memory_manager:
                self.memory_manager.update_short_term(f'step_{step_id}_result', {
                    'step_id': step_id,
                    'action': action,
                    'module': module,
                    'success': result.get('success', False),
                    'result': result,
                    'timestamp': step['completed_at']
                })
            
            self.logger.info(f"Step {step_id} completed", 
                           extra={'success': result.get('success', False)})
            
            return {
                'step_id': step_id,
                'action': action,
                'module': module,
                'success': result.get('success', False),
                'result': result,
                'started_at': step['started_at'],
                'completed_at': step['completed_at']
            }
            
        except Exception as e:
            self.error_logger.error(f"Step execution failed: {e}")
            return {
                'step_id': step.get('step_id', 'unknown'),
                'action': step.get('action', 'unknown'),
                'module': step.get('module', 'unknown'),
                'success': False,
                'error': str(e),
                'started_at': datetime.utcnow().isoformat() + 'Z',
                'completed_at': datetime.utcnow().isoformat() + 'Z'
            }

    def _update_memory_with_results(self, task: str, plan: Dict[str, Any], 
                                  execution_result: Dict[str, Any]):
        """
        Update memory with task execution results.
        
        Args:
            task: Original task
            plan: Execution plan
            execution_result: Execution results
        """
        try:
            if not self.memory_manager:
                return
            
            # Update short-term memory with task completion
            self.memory_manager.update_short_term('task_completion', {
                'task': task,
                'plan_id': plan.get('plan_id'),
                'success': execution_result.get('success', False),
                'total_steps': execution_result.get('total_steps', 0),
                'completed_steps': execution_result.get('completed_steps', 0),
                'completed_at': datetime.utcnow().isoformat() + 'Z'
            })
            
            # Update long-term memory with task summary
            if execution_result.get('success', False):
                self.memory_manager.update_long_term('successful_tasks', {
                    'task': task,
                    'plan_id': plan.get('plan_id'),
                    'task_type': plan.get('metadata', {}).get('complexity', 'unknown'),
                    'steps_completed': execution_result.get('completed_steps', 0),
                    'completed_at': datetime.utcnow().isoformat() + 'Z'
                })
            
            # Update core behavior with patterns
            self._update_behavior_patterns(task, plan, execution_result)
            
        except Exception as e:
            self.error_logger.error(f"Failed to update memory with results: {e}")

    def _update_behavior_patterns(self, task: str, plan: Dict[str, Any], 
                                execution_result: Dict[str, Any]):
        """
        Update core behavior patterns based on task execution.
        
        Args:
            task: Original task
            plan: Execution plan
            execution_result: Execution results
        """
        try:
            if not self.memory_manager:
                return
            
            # Extract patterns from successful executions
            if execution_result.get('success', False):
                task_type = plan.get('metadata', {}).get('complexity', 'medium')
                step_count = len(plan.get('steps', []))
                
                # Update task type patterns
                current_patterns = self.memory_manager.get_core_behavior('task_patterns', {})
                if not isinstance(current_patterns, dict):
                    current_patterns = {}
                
                if task_type not in current_patterns:
                    current_patterns[task_type] = {'count': 0, 'avg_steps': 0}
                
                current_patterns[task_type]['count'] += 1
                current_patterns[task_type]['avg_steps'] = (
                    (current_patterns[task_type]['avg_steps'] * (current_patterns[task_type]['count'] - 1) + step_count) 
                    / current_patterns[task_type]['count']
                )
                
                self.memory_manager.update_core_behavior('task_patterns', current_patterns)
                
                # Update user preferences
                self._update_user_preferences(task, plan, execution_result)
                
        except Exception as e:
            self.error_logger.error(f"Failed to update behavior patterns: {e}")

    def _update_user_preferences(self, task: str, plan: Dict[str, Any], 
                               execution_result: Dict[str, Any]):
        """
        Update user preferences based on task execution.
        
        Args:
            task: Original task
            plan: Execution plan
            execution_result: Execution results
        """
        try:
            if not self.memory_manager:
                return
            
            # Extract user preferences from context
            user_context = plan.get('user_context', {})
            if user_context:
                current_preferences = self.memory_manager.get_core_behavior('user_preferences', {})
                if not isinstance(current_preferences, dict):
                    current_preferences = {}
                
                # Update preferences based on context
                for key, value in user_context.items():
                    if key in ['safety_level', 'verbose_logging', 'preferences']:
                        current_preferences[key] = value
                
                self.memory_manager.update_core_behavior('user_preferences', current_preferences)
                
        except Exception as e:
            self.error_logger.error(f"Failed to update user preferences: {e}")

    def _handle_task_status_update(self, status_update: Dict[str, Any]):
        """
        Handle task status updates from memory.
        
        Args:
            status_update: Task status update
        """
        try:
            self.logger.info("Task status update received", extra=status_update)
            
            # Update controller state
            if status_update.get('status') == 'completed':
                self.current_task = None
                self.current_plan = None
                
        except Exception as e:
            self.error_logger.error(f"Failed to handle task status update: {e}")

    def _create_success_result(self, task: str, plan: Dict[str, Any], 
                             execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create success result for task completion.
        
        Args:
            task: Original task
            plan: Execution plan
            execution_result: Execution results
            
        Returns:
            Success result dictionary
        """
        return {
            'success': True,
            'task': task,
            'plan_id': plan.get('plan_id'),
            'status': 'completed',
            'total_steps': execution_result.get('total_steps', 0),
            'completed_steps': execution_result.get('completed_steps', 0),
            'failed_steps': len(execution_result.get('failed_steps', [])),
            'execution_time': self._calculate_execution_time(plan),
            'completed_at': datetime.utcnow().isoformat() + 'Z',
            'step_results': execution_result.get('step_results', [])
        }

    def _create_error_result(self, message: str, error: str) -> Dict[str, Any]:
        """
        Create error result for task failure.
        
        Args:
            message: Error message
            error: Detailed error information
            
        Returns:
            Error result dictionary
        """
        return {
            'success': False,
            'task': self.current_task,
            'status': 'failed',
            'error_message': message,
            'error_details': error,
            'failed_at': datetime.utcnow().isoformat() + 'Z'
        }

    def _calculate_execution_time(self, plan: Dict[str, Any]) -> int:
        """
        Calculate total execution time for the plan.
        
        Args:
            plan: Execution plan
            
        Returns:
            Execution time in seconds
        """
        try:
            created_at = datetime.fromisoformat(plan.get('created_at', '').replace('Z', '+00:00'))
            completed_at = datetime.utcnow()
            return int((completed_at - created_at).total_seconds())
        except Exception:
            return 0

    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get current session statistics.
        
        Returns:
            Session statistics
        """
        return {
            'session_start': self.session_start.isoformat() + 'Z',
            'current_task': self.current_task,
            'current_plan_id': self.current_plan.get('plan_id') if self.current_plan else None,
            'tasks_completed': len([r for r in self.execution_history if r.get('success', False)]),
            'tasks_failed': len([r for r in self.execution_history if not r.get('success', False)]),
            'total_execution_time': self._calculate_session_time()
        }

    def _calculate_session_time(self) -> int:
        """
        Calculate total session time.
        
        Returns:
            Session time in seconds
        """
        try:
            return int((datetime.utcnow() - self.session_start).total_seconds())
        except Exception:
            return 0

    def set_components(self, router=None, planner=None, memory_manager=None):
        """
        Set or update controller components.
        
        Args:
            router: Router instance
            planner: Planner instance
            memory_manager: MemoryManager instance
        """
        if router:
            self.router = router
        if planner:
            self.planner = planner
        if memory_manager:
            self.memory_manager = memory_manager
            self._setup_memory_hooks()
        
        self.logger.info("Controller components updated")

    def save_session_state(self) -> bool:
        """
        Save current session state to memory.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.memory_manager:
                return False
            
            session_state = {
                'session_start': self.session_start.isoformat() + 'Z',
                'current_task': self.current_task,
                'current_plan': self.current_plan,
                'execution_history': self.execution_history,
                'saved_at': datetime.utcnow().isoformat() + 'Z'
            }
            
            self.memory_manager.update_short_term('session_state', session_state)
            return True
            
        except Exception as e:
            self.error_logger.error(f"Failed to save session state: {e}")
            return False 