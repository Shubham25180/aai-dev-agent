#!/usr/bin/env python3
"""
Hybrid LLM Connector - Simplified Version
Routes requests intelligently between different Ollama models
"""

import asyncio
import time
import requests
from typing import Dict, Any, Optional
from utils.logger import get_action_logger, get_error_logger

class OptimizedLLMConnector:
    """
    Optimized LLM connector for Ollama models.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config or {}
        self.logger = get_action_logger('optimized_llm')
        self.error_logger = get_error_logger('optimized_llm')
        
        # Ollama configuration
        self.ollama_url = self.config.get('llm', {}).get('ollama_url', 'http://localhost:11434')
        self.model_name = self.config.get('llm', {}).get('model_name', 'llama3.2:3b')
        self.timeout = self.config.get('llm', {}).get('timeout', 120)
        
        self.logger.info(f"OptimizedLLMConnector initialized with ollama")

    async def start(self) -> bool:
        """Start the connector."""
        try:
            self.logger.info("Starting OptimizedLLMConnector...")
            
            # Check if Ollama is available
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                
                if self.model_name in model_names:
                    self.logger.info(f"Ollama model {self.model_name} is available")
                    return True
                else:
                    self.logger.warning(f"Model {self.model_name} not found in Ollama")
                    return False
            else:
                self.logger.error("Ollama not responding")
                return False
                
        except Exception as e:
            self.error_logger.error(f"Failed to start Ollama connector: {e}")
            return False

    async def stop(self) -> bool:
        """Stop the connector."""
        return True

    async def send_prompt(self, prompt: str, temperature: Optional[float] = None, 
                         max_tokens: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """
        Send prompt to Ollama.
        
        Args:
            prompt: The prompt to send
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            dict: LLM response
        """
        try:
            start_time = time.time()
            
            # Prepare request payload
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
            
            if temperature is not None:
                payload["temperature"] = temperature
            if max_tokens is not None:
                payload["max_tokens"] = max_tokens
            
            # Send request to Ollama
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('response', '')
                
                self.logger.info("Prompt processed successfully")
                
                return {
                    'success': True,
                    'content': content,
                    'response_time': time.time() - start_time,
                    'model_used': self.model_name
                }
            else:
                self.error_logger.error(f"Ollama request failed: {response.status_code}")
                return {
                    'success': False,
                    'error': f"Ollama request failed: {response.status_code}",
                    'content': ''
                }
                
        except Exception as e:
            self.error_logger.error(f"Error in Ollama prompt processing: {e}")
            return {
                'success': False,
                'error': str(e),
                'content': ''
            }

class HuggingFaceConnector:
    """
    Placeholder HuggingFace connector for compatibility.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config or {}
        self.logger = get_action_logger('huggingface_connector')
        self.error_logger = get_error_logger('huggingface_connector')
        
        self.logger.info(f"HuggingFaceConnector initialized with device: cpu")

    async def start(self) -> bool:
        """Start the connector."""
        try:
            self.logger.info("Starting HuggingFaceConnector...")
            # Placeholder - HuggingFace integration removed
            return False
        except Exception as e:
            self.error_logger.error(f"Failed to start HuggingFace connector: {e}")
            return False

    async def stop(self) -> bool:
        """Stop the connector."""
        return True

    async def send_prompt(self, prompt: str, model_type: str = 'fast', 
                         temperature: Optional[float] = None, 
                         max_tokens: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """
        Placeholder send prompt method.
        """
        return {
            'success': False,
            'error': 'HuggingFace connector not available',
            'content': ''
        }

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
        Force all LLM requests to use Ollama, ignoring keywords and config.
        """
        return 'ollama'

    def _get_routing_reason(self, prompt: str, task_type: Optional[str], 
                           force_backend: Optional[str]) -> str:
        """Get the reason for routing decision."""
        if force_backend:
            return f"forced_{force_backend}"
        elif task_type:
            return f"task_type_{task_type}"
        else:
            return "keyword_analysis"

    async def run_speed_comparison(self, test_prompts: list = None) -> Dict[str, Any]:
        """
        Run speed comparison between backends.
        
        Args:
            test_prompts: List of test prompts
            
        Returns:
            dict: Speed comparison results
        """
        if not test_prompts:
            test_prompts = [
                "Hello, how are you?",
                "Write a simple function to calculate factorial",
                "Explain what is machine learning",
                "Create a Python class for a user"
            ]
        
        results = {
            'ollama_times': [],
            'huggingface_times': [],
            'prompts': test_prompts
        }
        
        for prompt in test_prompts:
            # Test Ollama
            start_time = time.time()
            ollama_response = await self.ollama_connector.send_prompt(prompt)
            ollama_time = time.time() - start_time
            results['ollama_times'].append(ollama_time)
            
            # Test HuggingFace (if available)
            start_time = time.time()
            hf_response = await self.hf_connector.send_prompt(prompt)
            hf_time = time.time() - start_time
            results['huggingface_times'].append(hf_time)
        
        # Calculate averages
        if results['ollama_times']:
            results['avg_ollama_time'] = sum(results['ollama_times']) / len(results['ollama_times'])
        if results['huggingface_times']:
            results['avg_huggingface_time'] = sum(results['huggingface_times']) / len(results['huggingface_times'])
        
        return results

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            'ollama_requests': self.ollama_requests,
            'huggingface_requests': self.hf_requests,
            'total_requests': self.ollama_requests + self.hf_requests,
            'routing_decisions': self.routing_decisions
        }

    def get_status(self) -> Dict[str, Any]:
        """Get connector status."""
        return {
            'ollama_available': True,  # Simplified
            'huggingface_available': False,  # Simplified
            'default_backend': self.routing_config.get('default_backend', 'ollama')
        }

    def generate(self, prompt: str, temperature: float = 0.2, max_tokens: int = 256) -> str:
        """
        Synchronous generate method for compatibility with LLMPlanner.
        Calls the Ollama backend and returns the generated text as a string.
        """
        try:
            # Always run the async send_prompt using asyncio
            coro = self.ollama_connector.send_prompt(prompt, temperature=temperature, max_tokens=max_tokens)
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            if loop.is_running():
                # If already running (e.g. in Jupyter), use asyncio.run_coroutine_threadsafe
                import concurrent.futures
                future = asyncio.run_coroutine_threadsafe(coro, loop)
                result = future.result()
            else:
                result = loop.run_until_complete(coro)
            if isinstance(result, dict) and result.get('success'):
                return result.get('content', '')
            else:
                self.error_logger.error(f"LLM generate failed: {result}")
                return ""
        except Exception as e:
            self.error_logger.error(f"Exception in generate: {e}")
            return ""

class LLMConnector(HybridLLMConnector):
    """Alias for backward compatibility."""
    pass 