#!/usr/bin/env python3
"""
Task Router & Model Selector - The "Brain" of the AI Dev Agent
Analyzes user input and intelligently routes tasks to specialized models.
"""

import json
import re
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from utils.logger import get_action_logger, get_error_logger
from memory.memory_manager import MemoryManager

class TaskRouter:
    """
    The "brain" of the AI Dev Agent that:
    1. Analyzes user input (voice/text)
    2. Determines task type and complexity
    3. Selects the most appropriate specialized model
    4. Generates optimized prompts for each model
    5. Manages conversation flow and memory
    """
    
    def __init__(self, config: Dict[str, Any], memory_manager: MemoryManager):
        self.config = config
        self.memory_manager = memory_manager
        self.logger = get_action_logger('task_router')
        self.error_logger = get_error_logger('task_router')
        
        # Task classification patterns
        self.task_patterns = {
            'code_generation': {
                'keywords': ['create', 'write', 'generate', 'build', 'implement', 'code', 'function', 'class', 'module'],
                'patterns': [
                    r'create\s+(?:a\s+)?(?:new\s+)?(?:function|class|module|file)',
                    r'write\s+(?:some\s+)?(?:code|function|class)',
                    r'generate\s+(?:a\s+)?(?:function|class|module)',
                    r'build\s+(?:a\s+)?(?:feature|component|system)',
                    r'implement\s+(?:a\s+)?(?:feature|function|class)'
                ],
                'model': 'code_generator',
                'priority': 'high'
            },
            'code_review': {
                'keywords': ['review', 'check', 'analyze', 'examine', 'audit', 'test', 'debug'],
                'patterns': [
                    r'review\s+(?:the\s+)?(?:code|file|function)',
                    r'check\s+(?:for\s+)?(?:bugs|errors|issues)',
                    r'analyze\s+(?:the\s+)?(?:code|performance|security)',
                    r'examine\s+(?:the\s+)?(?:code|function|class)',
                    r'debug\s+(?:the\s+)?(?:code|function|issue)'
                ],
                'model': 'code_reviewer',
                'priority': 'medium'
            },
            'refactoring': {
                'keywords': ['refactor', 'optimize', 'improve', 'clean', 'restructure', 'reorganize'],
                'patterns': [
                    r'refactor\s+(?:the\s+)?(?:code|function|class)',
                    r'optimize\s+(?:the\s+)?(?:performance|code|function)',
                    r'improve\s+(?:the\s+)?(?:code|function|class)',
                    r'clean\s+(?:up\s+)?(?:the\s+)?(?:code|function)',
                    r'restructure\s+(?:the\s+)?(?:code|project)'
                ],
                'model': 'code_refactorer',
                'priority': 'medium'
            },
            'file_operations': {
                'keywords': ['open', 'create', 'delete', 'move', 'copy', 'rename', 'save'],
                'patterns': [
                    r'open\s+(?:the\s+)?(?:file|folder)',
                    r'create\s+(?:a\s+)?(?:new\s+)?(?:file|folder)',
                    r'delete\s+(?:the\s+)?(?:file|folder)',
                    r'move\s+(?:the\s+)?(?:file|folder)',
                    r'copy\s+(?:the\s+)?(?:file|folder)'
                ],
                'model': 'file_manager',
                'priority': 'low'
            },
            'git_operations': {
                'keywords': ['commit', 'push', 'pull', 'branch', 'merge', 'git'],
                'patterns': [
                    r'commit\s+(?:the\s+)?(?:changes|files)',
                    r'push\s+(?:to\s+)?(?:remote|repository)',
                    r'pull\s+(?:from\s+)?(?:remote|repository)',
                    r'create\s+(?:a\s+)?(?:new\s+)?(?:branch)',
                    r'merge\s+(?:the\s+)?(?:branch)'
                ],
                'model': 'git_manager',
                'priority': 'medium'
            },
            'testing': {
                'keywords': ['test', 'run', 'execute', 'validate', 'verify', 'unit', 'integration'],
                'patterns': [
                    r'run\s+(?:the\s+)?(?:tests|test\s+suite)',
                    r'execute\s+(?:the\s+)?(?:tests|test\s+suite)',
                    r'validate\s+(?:the\s+)?(?:function|class|module)',
                    r'verify\s+(?:the\s+)?(?:function|class|module)',
                    r'create\s+(?:a\s+)?(?:test|unit\s+test)'
                ],
                'model': 'test_runner',
                'priority': 'medium'
            },
            'documentation': {
                'keywords': ['document', 'doc', 'readme', 'comment', 'explain', 'describe'],
                'patterns': [
                    r'create\s+(?:the\s+)?(?:documentation|docs)',
                    r'write\s+(?:the\s+)?(?:readme|documentation)',
                    r'add\s+(?:comments|documentation)',
                    r'explain\s+(?:the\s+)?(?:code|function|class)',
                    r'describe\s+(?:the\s+)?(?:function|class|module)'
                ],
                'model': 'documentation_generator',
                'priority': 'low'
            },
            'conversation': {
                'keywords': ['hello', 'hi', 'how', 'what', 'why', 'explain', 'help', 'thanks'],
                'patterns': [
                    r'hello|hi|hey',
                    r'how\s+(?:are\s+)?(?:you|things)',
                    r'what\s+(?:is|are|do|can)',
                    r'why\s+(?:is|are|do|can)',
                    r'thanks|thank\s+you'
                ],
                'model': 'conversation_agent',
                'priority': 'low'
            },
            'system_operations': {
                'keywords': ['install', 'setup', 'configure', 'start', 'stop', 'restart'],
                'patterns': [
                    r'install\s+(?:the\s+)?(?:package|dependency)',
                    r'setup\s+(?:the\s+)?(?:project|environment)',
                    r'configure\s+(?:the\s+)?(?:system|tool)',
                    r'start\s+(?:the\s+)?(?:server|service)',
                    r'stop\s+(?:the\s+)?(?:server|service)'
                ],
                'model': 'system_manager',
                'priority': 'high'
            }
        }
        
        # Model configurations
        self.model_configs = {
            'code_generator': {
                'description': 'Specialized for generating new code, functions, classes, and modules',
                'prompt_template': 'You are an expert code generator. Generate clean, efficient, and well-documented code for: {task}',
                'temperature': 0.3,
                'max_tokens': 2000
            },
            'code_reviewer': {
                'description': 'Specialized for code analysis, bug detection, and performance review',
                'prompt_template': 'You are an expert code reviewer. Analyze this code for issues, bugs, and improvements: {task}',
                'temperature': 0.1,
                'max_tokens': 1500
            },
            'code_refactorer': {
                'description': 'Specialized for code optimization, refactoring, and restructuring',
                'prompt_template': 'You are an expert code refactorer. Optimize and improve this code: {task}',
                'temperature': 0.2,
                'max_tokens': 2000
            },
            'file_manager': {
                'description': 'Specialized for file and directory operations',
                'prompt_template': 'You are a file system expert. Perform this file operation safely: {task}',
                'temperature': 0.1,
                'max_tokens': 500
            },
            'git_manager': {
                'description': 'Specialized for Git operations and version control',
                'prompt_template': 'You are a Git expert. Execute this Git operation: {task}',
                'temperature': 0.1,
                'max_tokens': 800
            },
            'test_runner': {
                'description': 'Specialized for testing, validation, and quality assurance',
                'prompt_template': 'You are a testing expert. Create or run tests for: {task}',
                'temperature': 0.2,
                'max_tokens': 1500
            },
            'documentation_generator': {
                'description': 'Specialized for creating documentation, comments, and explanations',
                'prompt_template': 'You are a documentation expert. Create clear documentation for: {task}',
                'temperature': 0.4,
                'max_tokens': 1000
            },
            'conversation_agent': {
                'description': 'Specialized for friendly conversation and general assistance',
                'prompt_template': 'You are a friendly AI development assistant. Help with: {task}',
                'temperature': 0.7,
                'max_tokens': 800
            },
            'system_manager': {
                'description': 'Specialized for system operations and environment management',
                'prompt_template': 'You are a system administration expert. Handle this system task: {task}',
                'temperature': 0.1,
                'max_tokens': 1000
            }
        }
        
        self.logger.info("TaskRouter initialized successfully")

    def analyze_input(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze user input to determine task type and complexity.
        
        Args:
            user_input: User's voice or text input
            context: Additional context (language, confidence, etc.)
            
        Returns:
            dict: Analysis result with task classification and routing info
        """
        try:
            self.logger.info(f"Analyzing input: '{user_input}'", extra={
                'input_length': len(user_input),
                'context': context
            })
            
            # Normalize input
            normalized_input = user_input.lower().strip()
            
            # Classify task
            task_classification = self._classify_task(normalized_input)
            
            # Determine complexity
            complexity = self._assess_complexity(normalized_input, task_classification)
            
            # Select appropriate model
            model_selection = self._select_model(task_classification, complexity)
            
            # Generate optimized prompt
            optimized_prompt = self._generate_prompt(normalized_input, model_selection, context)
            
            # Update memory with this interaction
            self._update_memory(user_input, task_classification, model_selection)
            
            result = {
                'original_input': user_input,
                'normalized_input': normalized_input,
                'task_classification': task_classification,
                'complexity': complexity,
                'model_selection': model_selection,
                'optimized_prompt': optimized_prompt,
                'confidence': self._calculate_confidence(task_classification, complexity),
                'timestamp': datetime.utcnow().isoformat(),
                'context': context or {}
            }
            
            self.logger.info("Input analysis completed", extra={
                'task_type': task_classification['primary_type'],
                'model': model_selection['selected_model'],
                'confidence': result['confidence']
            })
            
            return result
            
        except Exception as e:
            self.error_logger.error(f"Error analyzing input: {e}", exc_info=True)
            return {
                'error': str(e),
                'original_input': user_input,
                'fallback_model': 'conversation_agent'
            }

    def _classify_task(self, normalized_input: str) -> Dict[str, Any]:
        """
        Classify the task based on keywords and patterns.
        
        Args:
            normalized_input: Normalized user input
            
        Returns:
            dict: Task classification with primary type and confidence scores
        """
        scores = {}
        
        for task_type, config in self.task_patterns.items():
            score = 0
            
            # Check keywords
            for keyword in config['keywords']:
                if keyword in normalized_input:
                    score += 2
            
            # Check patterns
            for pattern in config['patterns']:
                if re.search(pattern, normalized_input, re.IGNORECASE):
                    score += 5
            
            scores[task_type] = score
        
        # Find primary type
        primary_type = max(scores, key=scores.get) if scores else 'conversation'
        primary_score = scores.get(primary_type, 0)
        
        # Get secondary types (scores > 0)
        secondary_types = {k: v for k, v in scores.items() if v > 0 and k != primary_type}
        
        return {
            'primary_type': primary_type,
            'primary_score': primary_score,
            'secondary_types': secondary_types,
            'all_scores': scores
        }

    def _assess_complexity(self, normalized_input: str, classification: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess task complexity based on various factors.
        
        Args:
            normalized_input: Normalized user input
            classification: Task classification result
            
        Returns:
            dict: Complexity assessment
        """
        complexity_factors = {
            'input_length': len(normalized_input),
            'word_count': len(normalized_input.split()),
            'has_technical_terms': self._has_technical_terms(normalized_input),
            'has_file_paths': self._has_file_paths(normalized_input),
            'has_code_snippets': self._has_code_snippets(normalized_input),
            'task_priority': self.task_patterns.get(classification['primary_type'], {}).get('priority', 'low')
        }
        
        # Calculate overall complexity score
        complexity_score = 0
        complexity_score += complexity_factors['input_length'] * 0.1
        complexity_score += complexity_factors['word_count'] * 0.5
        complexity_score += 3 if complexity_factors['has_technical_terms'] else 0
        complexity_score += 2 if complexity_factors['has_file_paths'] else 0
        complexity_score += 4 if complexity_factors['has_code_snippets'] else 0
        
        # Priority multiplier
        priority_multipliers = {'low': 1, 'medium': 1.5, 'high': 2}
        complexity_score *= priority_multipliers.get(complexity_factors['task_priority'], 1)
        
        # Determine complexity level
        if complexity_score < 5:
            complexity_level = 'simple'
        elif complexity_score < 15:
            complexity_level = 'moderate'
        else:
            complexity_level = 'complex'
        
        return {
            'level': complexity_level,
            'score': complexity_score,
            'factors': complexity_factors
        }

    def _select_model(self, classification: Dict[str, Any], complexity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select the most appropriate model for the task.
        
        Args:
            classification: Task classification result
            complexity: Complexity assessment
            
        Returns:
            dict: Model selection with configuration
        """
        primary_type = classification['primary_type']
        task_config = self.task_patterns.get(primary_type, {})
        selected_model = task_config.get('model', 'conversation_agent')
        
        # Get model configuration
        model_config = self.model_configs.get(selected_model, self.model_configs['conversation_agent'])
        
        # Adjust parameters based on complexity
        adjusted_config = model_config.copy()
        if complexity['level'] == 'complex':
            adjusted_config['max_tokens'] = min(adjusted_config['max_tokens'] * 1.5, 4000)
            adjusted_config['temperature'] = max(adjusted_config['temperature'] * 0.8, 0.05)
        elif complexity['level'] == 'simple':
            adjusted_config['max_tokens'] = max(adjusted_config['max_tokens'] * 0.7, 500)
            adjusted_config['temperature'] = min(adjusted_config['temperature'] * 1.2, 0.9)
        
        return {
            'selected_model': selected_model,
            'model_config': adjusted_config,
            'reasoning': f"Selected {selected_model} for {primary_type} task (complexity: {complexity['level']})",
            'fallback_model': 'conversation_agent'
        }

    def _generate_prompt(self, user_input: str, model_selection: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """
        Generate an optimized prompt for the selected model.
        
        Args:
            user_input: Original user input
            model_selection: Model selection result
            context: Additional context
            
        Returns:
            str: Optimized prompt
        """
        model_config = model_selection['model_config']
        template = model_config['prompt_template']
        
        # Get memory context
        memory_context = self._get_memory_context()
        
        # Build enhanced prompt
        enhanced_prompt = template.format(task=user_input)
        
        if memory_context:
            enhanced_prompt += f"\n\nContext from previous interactions:\n{memory_context}"
        
        if context:
            if context.get('language'):
                enhanced_prompt += f"\n\nUser is speaking in: {context['language']}"
            if context.get('confidence'):
                enhanced_prompt += f"\n\nVoice recognition confidence: {context['confidence']:.2f}"
        
        return enhanced_prompt

    def _calculate_confidence(self, classification: Dict[str, Any], complexity: Dict[str, Any]) -> float:
        """
        Calculate confidence in the analysis.
        
        Args:
            classification: Task classification result
            complexity: Complexity assessment
            
        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        base_confidence = min(classification['primary_score'] / 10.0, 1.0)
        
        # Adjust based on complexity
        if complexity['level'] == 'simple':
            base_confidence *= 1.2
        elif complexity['level'] == 'complex':
            base_confidence *= 0.8
        
        # Adjust based on secondary types
        if classification['secondary_types']:
            base_confidence *= 0.9  # Slight reduction if multiple types detected
        
        return min(base_confidence, 1.0)

    def _has_technical_terms(self, text: str) -> bool:
        """Check if text contains technical programming terms."""
        technical_terms = [
            'function', 'class', 'module', 'import', 'export', 'variable', 'array', 'object',
            'string', 'integer', 'boolean', 'null', 'undefined', 'async', 'await', 'promise',
            'callback', 'event', 'api', 'database', 'server', 'client', 'framework', 'library'
        ]
        return any(term in text.lower() for term in technical_terms)

    def _has_file_paths(self, text: str) -> bool:
        """Check if text contains file paths."""
        path_patterns = [
            r'[a-zA-Z]:\\',  # Windows paths
            r'\/[a-zA-Z0-9_\/\-\.]+',  # Unix paths
            r'\.(py|js|ts|java|cpp|c|h|html|css|json|yaml|yml|md|txt)$'  # File extensions
        ]
        return any(re.search(pattern, text) for pattern in path_patterns)

    def _has_code_snippets(self, text: str) -> bool:
        """Check if text contains code snippets."""
        code_indicators = [
            'function(', 'class ', 'def ', 'const ', 'let ', 'var ', 'if (', 'for (', 'while (',
            'return ', 'import ', 'export ', 'console.log', 'print(', 'System.out.println'
        ]
        return any(indicator in text for indicator in code_indicators)

    def _get_memory_context(self) -> str:
        """Get relevant context from memory."""
        try:
            short_term = self.memory_manager.get_short_term_memory()
            long_term = self.memory_manager.get_long_term_memory()
            
            context_parts = []
            
            # Add recent interactions
            if short_term.get('recent_interactions'):
                recent = short_term['recent_interactions'][-3:]  # Last 3 interactions
                context_parts.append(f"Recent interactions: {', '.join(recent)}")
            
            # Add user preferences
            if long_term.get('user_preferences'):
                prefs = long_term['user_preferences']
                if prefs.get('preferred_language'):
                    context_parts.append(f"User prefers: {prefs['preferred_language']}")
                if prefs.get('coding_style'):
                    context_parts.append(f"Coding style: {prefs['coding_style']}")
            
            return '; '.join(context_parts) if context_parts else ""
            
        except Exception as e:
            self.error_logger.error(f"Error getting memory context: {e}")
            return ""

    def _update_memory(self, user_input: str, classification: Dict[str, Any], model_selection: Dict[str, Any]):
        """Update memory with this interaction."""
        try:
            interaction_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'input': user_input,
                'task_type': classification['primary_type'],
                'model_used': model_selection['selected_model'],
                'confidence': classification['primary_score']
            }
            
            # Update short-term memory
            self.memory_manager.add_to_short_term('recent_interactions', interaction_data)
            
            # Update long-term patterns
            if classification['primary_score'] > 5:  # Significant interaction
                self.memory_manager.add_to_long_term('task_patterns', {
                    'type': classification['primary_type'],
                    'frequency': 1,
                    'last_used': datetime.utcnow().isoformat()
                })
            
        except Exception as e:
            self.error_logger.error(f"Error updating memory: {e}")

    def get_model_info(self, model_name: str = None) -> Dict[str, Any]:
        """
        Get information about available models or a specific model.
        
        Args:
            model_name: Specific model name, or None for all models
            
        Returns:
            dict: Model information
        """
        if model_name:
            return self.model_configs.get(model_name, {})
        else:
            return {
                'available_models': list(self.model_configs.keys()),
                'model_configs': self.model_configs,
                'task_patterns': self.task_patterns
            }

    def get_statistics(self) -> Dict[str, Any]:
        """Get usage statistics and performance metrics."""
        try:
            short_term = self.memory_manager.get_short_term_memory()
            long_term = self.memory_manager.get_long_term_memory()
            
            return {
                'total_interactions': len(short_term.get('recent_interactions', [])),
                'task_distribution': self._get_task_distribution(long_term),
                'model_usage': self._get_model_usage(long_term),
                'average_confidence': self._get_average_confidence(short_term)
            }
        except Exception as e:
            self.error_logger.error(f"Error getting statistics: {e}")
            return {}

    def _get_task_distribution(self, long_term: Dict[str, Any]) -> Dict[str, int]:
        """Get distribution of task types."""
        patterns = long_term.get('task_patterns', [])
        distribution = {}
        for pattern in patterns:
            task_type = pattern.get('type', 'unknown')
            distribution[task_type] = distribution.get(task_type, 0) + pattern.get('frequency', 1)
        return distribution

    def _get_model_usage(self, long_term: Dict[str, Any]) -> Dict[str, int]:
        """Get model usage statistics."""
        interactions = long_term.get('interactions', [])
        usage = {}
        for interaction in interactions:
            model = interaction.get('model_used', 'unknown')
            usage[model] = usage.get(model, 0) + 1
        return usage

    def _get_average_confidence(self, short_term: Dict[str, Any]) -> float:
        """Get average confidence score."""
        interactions = short_term.get('recent_interactions', [])
        if not interactions:
            return 0.0
        
        total_confidence = sum(interaction.get('confidence', 0) for interaction in interactions)
        return total_confidence / len(interactions) 