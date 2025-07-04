import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from utils.logger import get_action_logger, get_error_logger

class Planner:
    """
    Task planning and decomposition system for AI Dev Agent.
    Integrates with memory system to provide context-aware planning.
    Follows AGENT_MANIFEST.md principles for automatic planning and memory integration.
    """
    
    def __init__(self, config: Dict[str, Any], memory_manager=None):
        """
        Initialize Planner with configuration and optional memory manager.
        
        Args:
            config: Application configuration
            memory_manager: Optional MemoryManager instance for context-aware planning
        """
        self.config = config
        self.logger = get_action_logger('planner', subsystem='core')
        self.error_logger = get_error_logger('planner', subsystem='core')
        self.memory_manager = memory_manager
        
        # Planning configuration
        self.max_steps = config.get('planning', {}).get('max_steps', 10)
        self.step_timeout = config.get('planning', {}).get('step_timeout', 300)
        self.planning_strategy = config.get('planning', {}).get('strategy', 'sequential')
        
        # Plan storage
        self.plans_path = config.get('paths', {}).get('logs', 'logs') + '/plans'
        os.makedirs(self.plans_path, exist_ok=True)
        
        self.logger.info("Planner initialized with memory integration")

    def create_plan(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a comprehensive plan for the given task.
        
        Args:
            task: High-level task description
            context: Additional context for planning
            
        Returns:
            Complete plan with steps, metadata, and memory context
        """
        try:
            # Get memory context if available
            memory_context = None
            if self.memory_manager:
                memory_context = self.memory_manager.get_memory_context()
                self.logger.info("Retrieved memory context for planning", 
                               extra={'memory_keys': memory_context.get('short_term', {}).get('keys', [])})
            
            # Create plan structure
            plan = {
                'task': task,
                'created_at': datetime.utcnow().isoformat() + 'Z',
                'plan_id': self._generate_plan_id(),
                'status': 'created',
                'strategy': self.planning_strategy,
                'max_steps': self.max_steps,
                'memory_context': memory_context,
                'user_context': context or {},
                'steps': [],
                'metadata': {
                    'total_steps': 0,
                    'estimated_duration': 0,
                    'complexity': 'medium',
                    'risk_level': 'low'
                }
            }
            
            # Decompose task into steps
            steps = self._decompose_task(task, memory_context, context)
            plan['steps'] = steps
            plan['metadata']['total_steps'] = len(steps)
            
            # Analyze plan complexity and risk
            plan['metadata'].update(self._analyze_plan_complexity(steps))
            
            # Save plan
            self._save_plan(plan)
            
            # Update memory with plan creation
            if self.memory_manager:
                self.memory_manager.update_short_term('current_plan', {
                    'plan_id': plan['plan_id'],
                    'task': task,
                    'status': 'created',
                    'step_count': len(steps)
                })
            
            self.logger.info("Plan created successfully", 
                           extra={'plan_id': plan['plan_id'], 'steps': len(steps)})
            
            return plan
            
        except Exception as e:
            self.error_logger.error(f"Failed to create plan: {e}")
            return {
                'error': str(e),
                'task': task,
                'status': 'failed',
                'created_at': datetime.utcnow().isoformat() + 'Z'
            }

    def _decompose_task(self, task: str, memory_context: Optional[Dict[str, Any]] = None, 
                       user_context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Decompose high-level task into executable steps.
        
        Args:
            task: High-level task description
            memory_context: Memory context for planning
            user_context: User-provided context
            
        Returns:
            List of executable steps
        """
        steps = []
        
        # Analyze task type and complexity
        task_analysis = self._analyze_task(task)
        
        # Apply memory-aware planning
        if memory_context:
            steps = self._apply_memory_context(task_analysis, memory_context)
        else:
            steps = self._create_basic_steps(task_analysis)
        
        # Add user context considerations
        if user_context:
            steps = self._apply_user_context(steps, user_context)
        
        # Validate and optimize steps
        steps = self._validate_and_optimize_steps(steps)
        
        return steps

    def _analyze_task(self, task: str) -> Dict[str, Any]:
        """
        Analyze task to determine type, complexity, and requirements.
        
        Args:
            task: Task description
            
        Returns:
            Task analysis dictionary
        """
        task_lower = task.lower()
        
        analysis = {
            'type': 'general',
            'complexity': 'medium',
            'estimated_steps': 3,
            'requirements': [],
            'risks': [],
            'dependencies': []
        }
        
        # Determine task type
        if any(keyword in task_lower for keyword in ['file', 'create', 'edit', 'delete']):
            analysis['type'] = 'file_operation'
            analysis['requirements'].append('file_ops')
        elif any(keyword in task_lower for keyword in ['code', 'program', 'script']):
            analysis['type'] = 'code_development'
            analysis['requirements'].extend(['code_editor', 'file_ops'])
        elif any(keyword in task_lower for keyword in ['gui', 'interface', 'click', 'window']):
            analysis['type'] = 'gui_automation'
            analysis['requirements'].append('gui_ops')
        elif any(keyword in task_lower for keyword in ['shell', 'command', 'terminal']):
            analysis['type'] = 'shell_operation'
            analysis['requirements'].append('shell_ops')
        elif any(keyword in task_lower for keyword in ['voice', 'speech', 'audio']):
            analysis['type'] = 'voice_operation'
            analysis['requirements'].extend(['voice_recognizer', 'voice_responder'])
        
        # Assess complexity
        if len(task.split()) > 20 or any(keyword in task_lower for keyword in ['complex', 'multiple', 'advanced']):
            analysis['complexity'] = 'high'
            analysis['estimated_steps'] = 8
        elif len(task.split()) < 5 or any(keyword in task_lower for keyword in ['simple', 'basic', 'quick']):
            analysis['complexity'] = 'low'
            analysis['estimated_steps'] = 2
        
        # Identify risks
        if any(keyword in task_lower for keyword in ['delete', 'remove', 'uninstall']):
            analysis['risks'].append('data_loss')
        if any(keyword in task_lower for keyword in ['admin', 'elevate', 'sudo']):
            analysis['risks'].append('elevated_privileges')
        if any(keyword in task_lower for keyword in ['network', 'internet', 'download']):
            analysis['risks'].append('network_operation')
        
        return analysis

    def _apply_memory_context(self, task_analysis: Dict[str, Any], 
                            memory_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Apply memory context to enhance planning.
        
        Args:
            task_analysis: Task analysis results
            memory_context: Memory context from MemoryManager
            
        Returns:
            Enhanced steps with memory context
        """
        steps = []
        
        # Check for similar recent tasks
        recent_tasks = memory_context.get('short_term', {}).get('recent_updates', [])
        similar_tasks = [task for task in recent_tasks if task_analysis['type'] in str(task)]
        
        if similar_tasks:
            # Use recent successful patterns
            steps.append({
                'action': 'check_recent_patterns',
                'description': f"Check recent {task_analysis['type']} patterns",
                'module': 'memory',
                'priority': 'high',
                'estimated_time': 30,
                'memory_context': 'recent_patterns'
            })
        
        # Check long-term preferences
        long_term_keys = memory_context.get('long_term', {}).get('keys', [])
        if 'preferences' in long_term_keys or 'workflow_patterns' in long_term_keys:
            steps.append({
                'action': 'apply_preferences',
                'description': "Apply user preferences and workflow patterns",
                'module': 'memory',
                'priority': 'medium',
                'estimated_time': 60,
                'memory_context': 'user_preferences'
            })
        
        # Add core behavior considerations
        core_behavior_keys = memory_context.get('core_behavior', {}).get('keys', [])
        if core_behavior_keys:
            steps.append({
                'action': 'apply_behavior_patterns',
                'description': "Apply learned behavior patterns",
                'module': 'memory',
                'priority': 'medium',
                'estimated_time': 45,
                'memory_context': 'core_behavior'
            })
        
        return steps

    def _create_basic_steps(self, task_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create basic steps for task execution.
        
        Args:
            task_analysis: Task analysis results
            
        Returns:
            List of basic execution steps
        """
        steps = []
        
        # Add validation step
        steps.append({
            'action': 'validate_task',
            'description': f"Validate {task_analysis['type']} task requirements",
            'module': 'planner',
            'priority': 'high',
            'estimated_time': 30,
            'validation_type': task_analysis['type']
        })
        
        # Add execution step based on task type
        if task_analysis['type'] == 'file_operation':
            steps.append({
                'action': 'execute_file_operation',
                'description': "Execute file operation",
                'module': 'file_ops',
                'priority': 'high',
                'estimated_time': 120,
                'operation_type': 'file_operation'
            })
        elif task_analysis['type'] == 'code_development':
            steps.append({
                'action': 'execute_code_development',
                'description': "Execute code development task",
                'module': 'code_editor',
                'priority': 'high',
                'estimated_time': 300,
                'development_type': 'code_development'
            })
        elif task_analysis['type'] == 'gui_automation':
            steps.append({
                'action': 'execute_gui_automation',
                'description': "Execute GUI automation task",
                'module': 'gui_ops',
                'priority': 'high',
                'estimated_time': 180,
                'automation_type': 'gui_automation'
            })
        elif task_analysis['type'] == 'shell_operation':
            steps.append({
                'action': 'execute_shell_operation',
                'description': "Execute shell operation",
                'module': 'shell_ops',
                'priority': 'high',
                'estimated_time': 90,
                'operation_type': 'shell_operation'
            })
        elif task_analysis['type'] == 'voice_operation':
            steps.append({
                'action': 'execute_voice_operation',
                'description': "Execute voice operation",
                'module': 'voice_recognizer',
                'priority': 'high',
                'estimated_time': 150,
                'operation_type': 'voice_operation'
            })
        else:
            steps.append({
                'action': 'execute_general_task',
                'description': "Execute general task",
                'module': 'router',
                'priority': 'high',
                'estimated_time': 120,
                'operation_type': 'general'
            })
        
        # Add verification step
        steps.append({
            'action': 'verify_execution',
            'description': "Verify task execution success",
            'module': 'planner',
            'priority': 'high',
            'estimated_time': 60,
            'verification_type': 'post_execution'
        })
        
        return steps

    def _apply_user_context(self, steps: List[Dict[str, Any]], 
                           user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Apply user context to modify steps.
        
        Args:
            steps: Current execution steps
            user_context: User-provided context
            
        Returns:
            Modified steps with user context
        """
        modified_steps = steps.copy()
        
        # Add user preferences
        if 'preferences' in user_context:
            modified_steps.insert(0, {
                'action': 'apply_user_preferences',
                'description': "Apply user-specific preferences",
                'module': 'planner',
                'priority': 'high',
                'estimated_time': 30,
                'preferences': user_context['preferences']
            })
        
        # Add safety checks if requested
        if user_context.get('safety_level', 'normal') == 'high':
            for step in modified_steps:
                if step.get('priority') == 'high':
                    step['safety_check'] = True
                    step['estimated_time'] += 30
        
        # Add logging preferences
        if user_context.get('verbose_logging', False):
            for step in modified_steps:
                step['verbose_logging'] = True
        
        return modified_steps

    def _validate_and_optimize_steps(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate and optimize execution steps.
        
        Args:
            steps: Raw execution steps
            
        Returns:
            Validated and optimized steps
        """
        validated_steps = []
        
        for i, step in enumerate(steps):
            # Add step ID and sequence
            step['step_id'] = i + 1
            step['sequence'] = i + 1
            
            # Validate required fields
            if 'action' not in step:
                step['action'] = 'unknown_action'
            if 'description' not in step:
                step['description'] = f"Step {i + 1}"
            if 'module' not in step:
                step['module'] = 'planner'
            if 'priority' not in step:
                step['priority'] = 'medium'
            if 'estimated_time' not in step:
                step['estimated_time'] = 60
            
            # Add safety defaults
            step['safety_check'] = step.get('safety_check', False)
            step['can_undo'] = step.get('can_undo', True)
            step['requires_confirmation'] = step.get('requires_confirmation', False)
            
            # Add status tracking
            step['status'] = 'pending'
            step['started_at'] = None
            step['completed_at'] = None
            step['error'] = None
            
            validated_steps.append(step)
        
        # Limit steps if exceeding maximum
        if len(validated_steps) > self.max_steps:
            self.logger.warning(f"Plan exceeds max steps ({self.max_steps}), truncating")
            validated_steps = validated_steps[:self.max_steps]
        
        return validated_steps

    def _analyze_plan_complexity(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze plan complexity and risk level.
        
        Args:
            steps: Execution steps
            
        Returns:
            Complexity analysis
        """
        total_time = sum(step.get('estimated_time', 60) for step in steps)
        high_priority_steps = len([s for s in steps if s.get('priority') == 'high'])
        risky_operations = len([s for s in steps if s.get('safety_check', False)])
        
        complexity = 'low'
        if total_time > 600 or len(steps) > 5:
            complexity = 'high'
        elif total_time > 300 or len(steps) > 3:
            complexity = 'medium'
        
        risk_level = 'low'
        if risky_operations > 2 or high_priority_steps > 3:
            risk_level = 'high'
        elif risky_operations > 0 or high_priority_steps > 1:
            risk_level = 'medium'
        
        return {
            'complexity': complexity,
            'risk_level': risk_level,
            'estimated_duration': total_time,
            'high_priority_steps': high_priority_steps,
            'risky_operations': risky_operations
        }

    def _generate_plan_id(self) -> str:
        """
        Generate unique plan ID.
        
        Returns:
            Unique plan identifier
        """
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        return f"plan_{timestamp}"

    def _save_plan(self, plan: Dict[str, Any]) -> bool:
        """
        Save plan to file for persistence and audit.
        
        Args:
            plan: Plan to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            plan_file = os.path.join(self.plans_path, f"{plan['plan_id']}.json")
            with open(plan_file, 'w', encoding='utf-8') as f:
                json.dump(plan, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Plan saved successfully", extra={'plan_file': plan_file})
            return True
            
        except Exception as e:
            self.error_logger.error(f"Failed to save plan: {e}")
            return False

    def load_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """
        Load plan from file.
        
        Args:
            plan_id: Plan identifier
            
        Returns:
            Loaded plan or None if not found
        """
        try:
            plan_file = os.path.join(self.plans_path, f"{plan_id}.json")
            if os.path.exists(plan_file):
                with open(plan_file, 'r', encoding='utf-8') as f:
                    plan = json.load(f)
                self.logger.info("Plan loaded successfully", extra={'plan_id': plan_id})
                return plan
            else:
                self.logger.warning("Plan not found", extra={'plan_id': plan_id})
                return None
                
        except Exception as e:
            self.error_logger.error(f"Failed to load plan: {e}")
            return None

    def update_plan_status(self, plan_id: str, status: str, step_results: Optional[List[Dict[str, Any]]] = None) -> bool:
        """
        Update plan status and step results.
        
        Args:
            plan_id: Plan identifier
            status: New status ('in_progress', 'completed', 'failed')
            step_results: Optional step execution results
            
        Returns:
            True if successful, False otherwise
        """
        try:
            plan = self.load_plan(plan_id)
            if not plan:
                return False
            
            plan['status'] = status
            plan['updated_at'] = datetime.utcnow().isoformat() + 'Z'
            
            if step_results:
                plan['step_results'] = step_results
            
            # Update memory with plan status
            if self.memory_manager:
                self.memory_manager.update_short_term('plan_status', {
                    'plan_id': plan_id,
                    'status': status,
                    'updated_at': plan['updated_at']
                })
            
            return self._save_plan(plan)
            
        except Exception as e:
            self.error_logger.error(f"Failed to update plan status: {e}")
            return False

    def get_plan_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent plan history.
        
        Args:
            limit: Maximum number of plans to return
            
        Returns:
            List of recent plans
        """
        try:
            plans = []
            for filename in os.listdir(self.plans_path):
                if filename.endswith('.json'):
                    plan_file = os.path.join(self.plans_path, filename)
                    try:
                        with open(plan_file, 'r', encoding='utf-8') as f:
                            plan = json.load(f)
                            plans.append(plan)
                    except Exception as e:
                        self.error_logger.error(f"Failed to load plan file {filename}: {e}")
            
            # Sort by creation date and return most recent
            plans.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            return plans[:limit]
            
        except Exception as e:
            self.error_logger.error(f"Failed to get plan history: {e}")
            return []

    def set_memory_manager(self, memory_manager):
        """
        Set memory manager for context-aware planning.
        
        Args:
            memory_manager: MemoryManager instance
        """
        self.memory_manager = memory_manager
        self.logger.info("Memory manager set for planner") 