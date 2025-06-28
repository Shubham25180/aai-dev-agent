#!/usr/bin/env python3
"""
Hybrid LLM Connector - Best of Both Worlds
Routes requests intelligently between Ollama (coding) and Hugging Face (speed testing)
"""

import asyncio
import time
from typing import Dict, Any, Optional
from utils.logger import get_action_logger, get_error_logger

try:
    from agents.llm_connector import OptimizedLLMConnector
    from agents.huggingface_connector import HuggingFaceConnector
    BOTH_AVAILABLE = True
except ImportError:
    BOTH_AVAILABLE = False

class HybridLLMConnector:
    """
    Hybrid LLM connector that intelligently routes requests:
    
    🧠 Ollama (Primary - Coding Tasks):
    - Code generation and analysis
    - Complex problem solving
    - Large context processing
    - High-quality responses
    
    ⚡ Hugging Face (Secondary - Speed Tasks):
    - Simple Q&A
    - Voice command processing
    - Quick responses
    - Speed testing
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config or {}
        self.logger = get_action_logger('hybrid_llm')
        self.error_logger = get_error_logger('hybrid_llm')
        
        if not BOTH_AVAILABLE:
            raise ImportError("Both Ollama and Hugging Face connectors must be available")
        
        # Initialize both connectors
        self.ollama_connector = OptimizedLLMConnector(config)
        self.hf_connector = HuggingFaceConnector(config)
        
        # Routing configuration
        self.routing_config = self.config.get('llm', {}).get('routing', {
            'default_backend': 'ollama',
            'coding_keywords': [
                'code', 'function', 'class', 'algorithm', 'debug', 'refactor',
                'implement', 'optimize', 'architecture', 'design pattern',
                'write', 'create', 'generate', 'solve', 'fix', 'improve'
            ],
            'simple_keywords': [
                'hello', 'hi', 'how are you', 'what is', 'explain briefly',
                'quick', 'simple', 'basic', 'help', 'assist'
            ],
            'force_ollama': [
                'complex', 'detailed', 'analysis', 'review', 'compare',
                'evaluate', 'assess', 'comprehensive', 'thorough'
            ]
        })
        
        # Performance tracking
        self.ollama_requests = 0
        self.hf_requests = 0
        self.routing_decisions = {}
        
        self.logger.info("HybridLLMConnector initialized with intelligent routing")

    async def start(self) -> bool:
        """Start both connectors."""
        try:
            self.logger.info("Starting HybridLLMConnector...")
            
            # Start Ollama connector (primary)
            ollama_success = await self.ollama_connector.start()
            if not ollama_success:
                self.logger.warning("Ollama connector failed to start")
            
            # Start Hugging Face connector (secondary)
            hf_success = await self.hf_connector.start()
            if not hf_success:
                self.logger.warning("Hugging Face connector failed to start")
            
            if not ollama_success and not hf_success:
                self.logger.error("Both connectors failed to start")
                return False
            
            self.logger.info(f"Hybrid connector started - Ollama: {ollama_success}, HF: {hf_success}")
            return True
            
        except Exception as e:
            self.error_logger.error(f"Failed to start hybrid connector: {e}", exc_info=True)
            return False

    async def stop(self) -> bool:
        """Stop both connectors."""
        try:
            self.logger.info("Stopping HybridLLMConnector...")
            
            # Stop both connectors
            ollama_stopped = await self.ollama_connector.stop()
            hf_stopped = await self.hf_connector.stop()
            
            self.logger.info(f"Hybrid connector stopped - Ollama: {ollama_stopped}, HF: {hf_stopped}")
            return ollama_stopped or hf_stopped
            
        except Exception as e:
            self.error_logger.error(f"Failed to stop hybrid connector: {e}", exc_info=True)
            return False

    async def send_prompt(self, prompt: str, task_type: Optional[str] = None,
                         temperature: Optional[float] = None, 
                         max_tokens: Optional[int] = None, 
                         force_backend: Optional[str] = None,
                         **kwargs) -> Dict[str, Any]:
        """
        Send prompt with intelligent routing between Ollama and Hugging Face.
        
        Args:
            prompt: The prompt to send
            task_type: Type of task (coding, simple, complex, etc.)
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
            force_backend: Force specific backend ('ollama' or 'huggingface')
            **kwargs: Additional parameters
            
        Returns:
            dict: LLM response with routing information
        """
        try:
            start_time = time.time()
            
            # Determine which backend to use
            backend = self._determine_backend(prompt, task_type, force_backend)
            
            # Add routing info to response
            routing_info = {
                'backend_used': backend,
                'routing_reason': self._get_routing_reason(prompt, task_type, force_backend),
                'task_type': task_type,
                'force_backend': force_backend
            }
            
            # Send to appropriate backend
            if backend == 'ollama':
                self.ollama_requests += 1
                response = await self.ollama_connector.send_prompt(
                    prompt, temperature, max_tokens, **kwargs
                )
            else:  # huggingface
                self.hf_requests += 1
                # Use fast model for speed
                response = await self.hf_connector.send_prompt(
                    prompt, model_type='fast', temperature=temperature, 
                    max_tokens=max_tokens, **kwargs
                )
            
            # Add routing information to response
            response['routing_info'] = routing_info
            response['hybrid_metrics'] = {
                'ollama_requests': self.ollama_requests,
                'hf_requests': self.hf_requests,
                'total_requests': self.ollama_requests + self.hf_requests
            }
            
            # Log routing decision
            self.logger.info(f"Request routed to {backend}", extra={
                'prompt_length': len(prompt),
                'task_type': task_type,
                'routing_reason': routing_info['routing_reason']
            })
            
            return response
            
        except Exception as e:
            self.error_logger.error(f"Error in hybrid prompt processing: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'content': '',
                'routing_info': {'backend_used': 'none', 'error': str(e)}
            }

    def _determine_backend(self, prompt: str, task_type: Optional[str], 
                          force_backend: Optional[str]) -> str:
        """
        Intelligently determine which backend to use.
        
        Returns:
            str: 'ollama' or 'huggingface'
        """
        # Force specific backend if requested
        if force_backend:
            return force_backend
        
        # Check for task type hints
        if task_type:
            if task_type in ['coding', 'code_generation', 'debug', 'refactor']:
                return 'ollama'
            elif task_type in ['simple_qa', 'voice_command', 'quick_response']:
                return 'huggingface'
        
        # Analyze prompt content
        prompt_lower = prompt.lower()
        
        # Force Ollama for coding tasks
        coding_keywords = self.routing_config.get('coding_keywords', [])
        if any(keyword in prompt_lower for keyword in coding_keywords):
            return 'ollama'
        
        # Force Ollama for complex tasks
        force_ollama_keywords = self.routing_config.get('force_ollama', [])
        if any(keyword in prompt_lower for keyword in force_ollama_keywords):
            return 'ollama'
        
        # Use Hugging Face for simple tasks
        simple_keywords = self.routing_config.get('simple_keywords', [])
        if any(keyword in prompt_lower for keyword in simple_keywords):
            return 'huggingface'
        
        # Default to Ollama for unknown tasks
        return self.routing_config.get('default_backend', 'ollama')

    def _get_routing_reason(self, prompt: str, task_type: Optional[str], 
                           force_backend: Optional[str]) -> str:
        """Get human-readable reason for routing decision."""
        if force_backend:
            return f"Force backend: {force_backend}"
        
        if task_type:
            return f"Task type: {task_type}"
        
        prompt_lower = prompt.lower()
        
        # Check for specific keywords
        coding_keywords = self.routing_config.get('coding_keywords', [])
        if any(keyword in prompt_lower for keyword in coding_keywords):
            return "Coding task detected"
        
        simple_keywords = self.routing_config.get('simple_keywords', [])
        if any(keyword in prompt_lower for keyword in simple_keywords):
            return "Simple task detected"
        
        force_ollama_keywords = self.routing_config.get('force_ollama', [])
        if any(keyword in prompt_lower for keyword in force_ollama_keywords):
            return "Complex task detected"
        
        return "Default routing"

    async def run_speed_comparison(self, test_prompts: list = None) -> Dict[str, Any]:
        """
        Run speed comparison between Ollama and Hugging Face backends.
        
        Args:
            test_prompts: List of prompts to test
            
        Returns:
            dict: Comparison results
        """
        try:
            if test_prompts is None:
                test_prompts = [
                    "Hello, how are you?",
                    "What is the weather like?",
                    "Write a simple Python function to calculate factorial",
                    "Explain machine learning briefly",
                    "Debug this code: print('Hello World'"
                ]
            
            self.logger.info("Starting speed comparison test...")
            
            results = {
                'timestamp': time.time(),
                'test_prompts': test_prompts,
                'ollama_results': [],
                'huggingface_results': [],
                'comparison': {}
            }
            
            # Test Ollama
            print("🧠 Testing Ollama backend...")
            for i, prompt in enumerate(test_prompts):
                start_time = time.time()
                response = await self.ollama_connector.send_prompt(
                    prompt, temperature=0.7, max_tokens=100
                )
                response_time = time.time() - start_time
                
                results['ollama_results'].append({
                    'prompt': prompt,
                    'response_time': response_time,
                    'success': response.get('success', False),
                    'content_length': len(response.get('content', '')),
                    'model': response.get('model', 'unknown')
                })
                
                print(f"  Prompt {i+1}: {response_time:.3f}s")
            
            # Test Hugging Face
            print("⚡ Testing Hugging Face backend...")
            for i, prompt in enumerate(test_prompts):
                start_time = time.time()
                response = await self.hf_connector.send_prompt(
                    prompt, model_type='fast', temperature=0.7, max_tokens=100
                )
                response_time = time.time() - start_time
                
                results['huggingface_results'].append({
                    'prompt': prompt,
                    'response_time': response_time,
                    'success': response.get('success', False),
                    'content_length': len(response.get('content', '')),
                    'model': response.get('model_name', 'unknown')
                })
                
                print(f"  Prompt {i+1}: {response_time:.3f}s")
            
            # Calculate comparison metrics
            ollama_times = [r['response_time'] for r in results['ollama_results']]
            hf_times = [r['response_time'] for r in results['huggingface_results']]
            
            if ollama_times and hf_times:
                results['comparison'] = {
                    'ollama_avg_time': sum(ollama_times) / len(ollama_times),
                    'hf_avg_time': sum(hf_times) / len(hf_times),
                    'speed_ratio': sum(ollama_times) / sum(hf_times) if sum(hf_times) > 0 else 0,
                    'faster_backend': 'huggingface' if sum(hf_times) < sum(ollama_times) else 'ollama'
                }
            
            return results
            
        except Exception as e:
            self.error_logger.error(f"Speed comparison failed: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics for both backends."""
        try:
            ollama_metrics = self.ollama_connector.get_performance_metrics()
            hf_metrics = self.hf_connector.get_performance_metrics()
            
            return {
                'hybrid_metrics': {
                    'ollama_requests': self.ollama_requests,
                    'hf_requests': self.hf_requests,
                    'total_requests': self.ollama_requests + self.hf_requests,
                    'ollama_ratio': self.ollama_requests / (self.ollama_requests + self.hf_requests) if (self.ollama_requests + self.hf_requests) > 0 else 0,
                    'hf_ratio': self.hf_requests / (self.ollama_requests + self.hf_requests) if (self.ollama_requests + self.hf_requests) > 0 else 0
                },
                'ollama_metrics': ollama_metrics,
                'huggingface_metrics': hf_metrics,
                'routing_config': self.routing_config
            }
        except Exception as e:
            self.error_logger.error(f"Error getting performance metrics: {e}")
            return {}

    def get_status(self) -> Dict[str, Any]:
        """Get system status for both backends."""
        return {
            'active': True,
            'model_type': 'hybrid',
            'ollama_status': self.ollama_connector.get_status(),
            'huggingface_status': self.hf_connector.get_status(),
            'routing_stats': {
                'ollama_requests': self.ollama_requests,
                'hf_requests': self.hf_requests,
                'total_requests': self.ollama_requests + self.hf_requests
            }
        }

# Backward compatibility - can be used as drop-in replacement
class LLMConnector(HybridLLMConnector):
    """Backward compatibility wrapper."""
    pass 