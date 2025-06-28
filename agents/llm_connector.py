#!/usr/bin/env python3
"""
Optimized LLM Connector - Fast Local Model Integration
Supports persistent model loading, prompt caching, and multiple local backends.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
import openai
import time
import requests
import hashlib
from utils.logger import get_action_logger, get_error_logger

class OptimizedLLMConnector:
    """
    Optimized LLM connector for maximum speed:
    1. Persistent model loading (load once, reuse)
    2. Prompt caching for repeated requests
    3. Multiple local model backends (Ollama, GPT4All, LLaMA.cpp)
    4. Async processing with timeouts
    5. Fallback mechanisms for reliability
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config or {}
        self.logger = get_action_logger('optimized_llm')
        self.error_logger = get_error_logger('optimized_llm')
        
        # Model configuration
        self.model_type = self.config.get('llm', {}).get('model_type', 'ollama')
        self.model_name = self.config.get('llm', {}).get('model_name', 'llama3.2:3b')
        self.api_url = self.config.get('llm', {}).get('api_url', 'http://localhost:11434')
        
        # Performance settings
        self.max_tokens = self.config.get('llm', {}).get('max_tokens', 1000)
        self.temperature = self.config.get('llm', {}).get('temperature', 0.7)
        self.timeout = self.config.get('llm', {}).get('timeout', 30)
        
        # Caching settings
        self.cache_enabled = self.config.get('llm', {}).get('cache_enabled', True)
        self.max_cache_size = self.config.get('llm', {}).get('max_cache_size', 1000)
        self.cache_ttl = self.config.get('llm', {}).get('cache_ttl', 3600)  # 1 hour
        
        # Model state
        self.model_loaded = False
        self.model_process = None
        self.last_health_check = 0
        self.health_check_interval = 60  # seconds
        
        # Performance metrics
        self.request_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.average_response_time = 0
        self.response_times = []
        
        # Prompt cache
        self.prompt_cache = {}
        self.cache_timestamps = {}
        
        # Fallback models
        self.fallback_models = [
            'llama3.2:3b',
            'mistral:7b',
            'phi3:mini',
            'gpt4all:j'
        ]
        
        self.logger.info(f"OptimizedLLMConnector initialized with {self.model_type}")

    async def start(self) -> bool:
        """Start the LLM connector with persistent model loading."""
        try:
            self.logger.info("Starting OptimizedLLMConnector...")
            
            # Initialize model based on type
            if self.model_type == 'ollama':
                success = await self._initialize_ollama()
            elif self.model_type == 'gpt4all':
                success = await self._initialize_gpt4all()
            elif self.model_type == 'llama_cpp':
                success = await self._initialize_llama_cpp()
            else:
                success = await self._initialize_ollama()  # Default fallback
            
            if success:
                self.model_loaded = True
                self.logger.info(f"LLM connector started successfully with {self.model_name}")
                return True
            else:
                # Try fallback models
                return await self._try_fallback_models()
                
        except Exception as e:
            self.error_logger.error(f"Failed to start LLM connector: {e}", exc_info=True)
            return await self._try_fallback_models()

    async def stop(self) -> bool:
        """Stop the LLM connector gracefully."""
        try:
            self.logger.info("Stopping OptimizedLLMConnector...")
            
            # Clear cache
            self.prompt_cache.clear()
            self.cache_timestamps.clear()
            
            # Stop model process if running
            if self.model_process:
                self.model_process.terminate()
                try:
                    await asyncio.wait_for(self.model_process.wait(), timeout=5)
                except asyncio.TimeoutError:
                    self.model_process.kill()
            
            self.model_loaded = False
            self.logger.info("OptimizedLLMConnector stopped successfully")
            return True
            
        except Exception as e:
            self.error_logger.error(f"Failed to stop LLM connector: {e}", exc_info=True)
            return False

    async def send_prompt(self, prompt: str, temperature: Optional[float] = None, 
                         max_tokens: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """
        Send prompt to LLM with caching and optimization.
        
        Args:
            prompt: The prompt to send
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            dict: LLM response with metadata
        """
        try:
            start_time = time.time()
            
            # Check cache first
            if self.cache_enabled:
                cache_key = self._generate_cache_key(prompt, temperature, max_tokens)
                cached_response = self._get_cached_response(cache_key)
                if cached_response:
                    self.cache_hits += 1
                    self.logger.info("Using cached response", extra={'cache_hit': True})
                    return cached_response
            
            self.cache_misses += 1
            
            # Validate model health
            if not await self._check_model_health():
                self.logger.warning("Model health check failed, attempting restart")
                await self._restart_model()
            
            # Send request based on model type
            if self.model_type == 'ollama':
                response = await self._send_ollama_request(prompt, temperature, max_tokens, **kwargs)
            elif self.model_type == 'gpt4all':
                response = await self._send_gpt4all_request(prompt, temperature, max_tokens, **kwargs)
            elif self.model_type == 'llama_cpp':
                response = await self._send_llama_cpp_request(prompt, temperature, max_tokens, **kwargs)
            else:
                response = await self._send_ollama_request(prompt, temperature, max_tokens, **kwargs)
            
            # Calculate response time
            response_time = time.time() - start_time
            self.response_times.append(response_time)
            self.average_response_time = sum(self.response_times) / len(self.response_times)
            
            # Update request count
            self.request_count += 1
            
            # Cache response if successful
            if response.get('success') and self.cache_enabled:
                cache_key = self._generate_cache_key(prompt, temperature, max_tokens)
                self._cache_response(cache_key, response)
            
            self.logger.info("Prompt processed successfully", extra={
                'response_time': response_time,
                'tokens_generated': len(response.get('content', '').split()),
                'cache_hit': False
            })
            
            return response
            
        except Exception as e:
            self.error_logger.error(f"Error sending prompt: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'content': '',
                'response_time': time.time() - start_time if 'start_time' in locals() else 0
            }

    async def _initialize_ollama(self) -> bool:
        """Initialize Ollama backend."""
        try:
            import aiohttp
            
            # Check if Ollama is running
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(f"{self.api_url}/api/tags", timeout=5) as response:
                        if response.status == 200:
                            # Check if model is available
                            models_data = await response.json()
                            available_models = [model['name'] for model in models_data.get('models', [])]
                            
                            if self.model_name in available_models:
                                self.logger.info(f"Ollama model {self.model_name} is available")
                                return True
                            else:
                                self.logger.warning(f"Model {self.model_name} not found, available: {available_models}")
                                return False
                        else:
                            self.logger.error(f"Ollama API returned status {response.status}")
                            return False
                except Exception as e:
                    self.logger.error(f"Failed to connect to Ollama: {e}")
                    return False
                    
        except ImportError:
            self.logger.error("aiohttp not available for Ollama integration")
            return False
        except Exception as e:
            self.error_logger.error(f"Error initializing Ollama: {e}")
            return False

    async def _initialize_gpt4all(self) -> bool:
        """Initialize GPT4All backend."""
        try:
            # Lazy import for performance
            from gpt4all import GPT4All
            
            # Load model
            self.gpt4all_model = GPT4All(self.model_name)
            self.logger.info(f"GPT4All model {self.model_name} loaded successfully")
            return True
            
        except ImportError:
            self.logger.error("GPT4All not available")
            return False
        except Exception as e:
            self.error_logger.error(f"Error initializing GPT4All: {e}")
            return False

    async def _initialize_llama_cpp(self) -> bool:
        """Initialize LLaMA.cpp backend."""
        try:
            # Lazy import for performance
            from llama_cpp import Llama
            
            # Load model
            model_path = self.config.get('llm', {}).get('model_path', f'./models/{self.model_name}.gguf')
            self.llama_model = Llama(
                model_path=model_path,
                n_ctx=2048,
                n_threads=4,
                n_gpu_layers=1 if self.config.get('llm', {}).get('use_gpu', False) else 0
            )
            
            self.logger.info(f"LLaMA.cpp model loaded from {model_path}")
            return True
            
        except ImportError:
            self.logger.error("llama-cpp-python not available")
            return False
        except Exception as e:
            self.error_logger.error(f"Error initializing LLaMA.cpp: {e}")
            return False

    async def _send_ollama_request(self, prompt: str, temperature: Optional[float] = None,
                                 max_tokens: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """Send request to Ollama API."""
        try:
            import aiohttp
            
            # Prepare request payload
            payload = {
                'model': self.model_name,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': temperature or self.temperature,
                    'num_predict': max_tokens or self.max_tokens
                }
            }
            
            # Send request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'success': True,
                            'content': data.get('response', ''),
                            'model': self.model_name,
                            'tokens_used': data.get('eval_count', 0),
                            'response_time': data.get('total_duration', 0) / 1e9  # Convert from nanoseconds
                        }
                    else:
                        return {
                            'success': False,
                            'error': f"Ollama API returned status {response.status}",
                            'content': ''
                        }
                        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'content': ''
            }

    async def _send_gpt4all_request(self, prompt: str, temperature: Optional[float] = None,
                                  max_tokens: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """Send request to GPT4All."""
        try:
            # Generate response
            response = self.gpt4all_model.generate(
                prompt,
                max_tokens=max_tokens or self.max_tokens,
                temp=temperature or self.temperature,
                **kwargs
            )
            
            return {
                'success': True,
                'content': response,
                'model': self.model_name,
                'tokens_used': len(response.split()),
                'response_time': 0  # GPT4All doesn't provide timing info
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'content': ''
            }

    async def _send_llama_cpp_request(self, prompt: str, temperature: Optional[float] = None,
                                    max_tokens: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """Send request to LLaMA.cpp."""
        try:
            # Generate response
            response = self.llama_model(
                prompt,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
                **kwargs
            )
            
            return {
                'success': True,
                'content': response['choices'][0]['text'],
                'model': self.model_name,
                'tokens_used': response['usage']['total_tokens'],
                'response_time': 0  # LLaMA.cpp doesn't provide timing info
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'content': ''
            }

    async def _check_model_health(self) -> bool:
        """Check if the model is healthy and responsive."""
        try:
            current_time = time.time()
            if current_time - self.last_health_check < self.health_check_interval:
                return True  # Skip if checked recently
            
            self.last_health_check = current_time
            
            # Send a simple health check prompt
            health_response = await self.send_prompt(
                "Hello",
                temperature=0.1,
                max_tokens=10
            )
            
            return health_response.get('success', False)
            
        except Exception as e:
            self.error_logger.error(f"Health check failed: {e}")
            return False

    async def _restart_model(self) -> bool:
        """Restart the model connection."""
        try:
            self.logger.info("Restarting model connection...")
            
            # Stop current connection
            await self.stop()
            
            # Wait a moment
            await asyncio.sleep(2)
            
            # Restart
            return await self.start()
            
        except Exception as e:
            self.error_logger.error(f"Failed to restart model: {e}")
            return False

    async def _try_fallback_models(self) -> bool:
        """Try fallback models if primary model fails."""
        try:
            self.logger.info("Trying fallback models...")
            
            for fallback_model in self.fallback_models:
                self.logger.info(f"Trying fallback model: {fallback_model}")
                
                # Update model name
                original_model = self.model_name
                self.model_name = fallback_model
                
                # Try to initialize
                if self.model_type == 'ollama':
                    success = await self._initialize_ollama()
                elif self.model_type == 'gpt4all':
                    success = await self._initialize_gpt4all()
                elif self.model_type == 'llama_cpp':
                    success = await self._initialize_llama_cpp()
                else:
                    success = await self._initialize_ollama()
                
                if success:
                    self.logger.info(f"Successfully loaded fallback model: {fallback_model}")
                    return True
                else:
                    # Restore original model name
                    self.model_name = original_model
            
            self.logger.error("All fallback models failed")
            return False
            
        except Exception as e:
            self.error_logger.error(f"Error trying fallback models: {e}")
            return False

    def _generate_cache_key(self, prompt: str, temperature: Optional[float] = None,
                           max_tokens: Optional[int] = None) -> str:
        """Generate cache key for prompt caching."""
        try:
            # Create cache key from prompt and parameters
            key_data = {
                'prompt': prompt,
                'temperature': temperature or self.temperature,
                'max_tokens': max_tokens or self.max_tokens,
                'model': self.model_name
            }
            
            key_string = json.dumps(key_data, sort_keys=True)
            return hashlib.md5(key_string.encode()).hexdigest()
            
        except Exception as e:
            self.error_logger.error(f"Error generating cache key: {e}")
            return hashlib.md5(prompt.encode()).hexdigest()

    def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response if available and not expired."""
        try:
            if cache_key not in self.prompt_cache:
                return None
            
            # Check if cache entry is expired
            timestamp = self.cache_timestamps.get(cache_key, 0)
            if time.time() - timestamp > self.cache_ttl:
                # Remove expired entry
                del self.prompt_cache[cache_key]
                del self.cache_timestamps[cache_key]
                return None
            
            return self.prompt_cache[cache_key]
            
        except Exception as e:
            self.error_logger.error(f"Error getting cached response: {e}")
            return None

    def _cache_response(self, cache_key: str, response: Dict[str, Any]):
        """Cache response with timestamp."""
        try:
            # Check cache size limit
            if len(self.prompt_cache) >= self.max_cache_size:
                # Remove oldest entry
                oldest_key = min(self.cache_timestamps.keys(), key=lambda k: self.cache_timestamps[k])
                del self.prompt_cache[oldest_key]
                del self.cache_timestamps[oldest_key]
            
            # Add new entry
            self.prompt_cache[cache_key] = response
            self.cache_timestamps[cache_key] = time.time()
            
        except Exception as e:
            self.error_logger.error(f"Error caching response: {e}")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        try:
            return {
                'request_count': self.request_count,
                'cache_hits': self.cache_hits,
                'cache_misses': self.cache_misses,
                'cache_hit_rate': self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0,
                'average_response_time': self.average_response_time,
                'cache_size': len(self.prompt_cache),
                'model_loaded': self.model_loaded,
                'model_type': self.model_type,
                'model_name': self.model_name,
                'last_health_check': self.last_health_check
            }
        except Exception as e:
            self.error_logger.error(f"Error getting performance metrics: {e}")
            return {}

    def get_status(self) -> Dict[str, Any]:
        """Get system status."""
        return {
            'active': self.model_loaded,
            'model_type': self.model_type,
            'model_name': self.model_name,
            'cache_enabled': self.cache_enabled,
            'optimizations': {
                'persistent_loading': True,
                'prompt_caching': self.cache_enabled,
                'health_monitoring': True,
                'fallback_models': len(self.fallback_models)
            },
            'performance': self.get_performance_metrics()
        }

# Backward compatibility
class LLMConnector(OptimizedLLMConnector):
    """Backward compatibility wrapper."""
    pass 