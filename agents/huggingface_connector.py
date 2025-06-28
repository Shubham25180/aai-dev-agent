#!/usr/bin/env python3
"""
Hugging Face LLM Connector - Optimized for Speed Testing
Supports multiple model sizes, quantization, and performance monitoring.
"""

import asyncio
import json
import os
import time
import psutil
import threading
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from utils.logger import get_action_logger, get_error_logger

try:
    import torch
    from transformers import (
        AutoTokenizer, 
        AutoModelForCausalLM, 
        BitsAndBytesConfig,
        pipeline
    )
    from accelerate import Accelerator
    import huggingface_hub
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

@dataclass
class ModelConfig:
    """Configuration for a Hugging Face model."""
    model_name: str
    model_id: str
    max_tokens: int
    temperature: float
    load_in_8bit: bool = True
    device_map: str = "auto"
    trust_remote_code: bool = False

@dataclass
class SpeedMetrics:
    """Speed testing metrics."""
    response_time: float
    tokens_per_second: float
    memory_usage_mb: float
    gpu_usage_percent: Optional[float] = None
    cache_hit: bool = False
    model_size_mb: Optional[float] = None

class HuggingFaceConnector:
    """
    Optimized Hugging Face LLM connector with:
    1. Multiple model support (fast, balanced, quality, code)
    2. Quantization for speed optimization
    3. Comprehensive speed testing
    4. Model caching and lazy loading
    5. Performance monitoring
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config or {}
        self.logger = get_action_logger('huggingface_connector')
        self.error_logger = get_error_logger('huggingface_connector')
        
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("Transformers library not available. Install with: pip install transformers torch accelerate")
        
        # Model configurations
        self.models_config = self.config.get('llm', {}).get('models', {})
        self.performance_config = self.config.get('llm', {}).get('performance', {})
        self.quantization_config = self.config.get('llm', {}).get('quantization', {})
        self.device_config = self.config.get('llm', {}).get('device', {})
        self.loading_config = self.config.get('llm', {}).get('loading', {})
        
        # Model instances
        self.loaded_models = {}
        self.model_tokens = {}
        self.model_pipelines = {}
        
        # Performance tracking
        self.speed_metrics = []
        self.cache_hits = 0
        self.cache_misses = 0
        self.prompt_cache = {}
        
        # Device setup
        self.device = self._setup_device()
        self.accelerator = Accelerator() if self.device_config.get('use_gpu', True) else None
        
        # Threading
        self.model_lock = threading.Lock()
        
        self.logger.info(f"HuggingFaceConnector initialized with device: {self.device}")

    def _setup_device(self) -> str:
        """Setup the best available device."""
        if torch.cuda.is_available() and self.device_config.get('use_gpu', True):
            return "cuda"
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available() and self.device_config.get('use_mps', False):
            return "mps"
        else:
            return "cpu"

    async def start(self) -> bool:
        """Start the Hugging Face connector with model preloading."""
        try:
            self.logger.info("Starting HuggingFaceConnector...")
            
            # Preload specified models
            preload_models = self.loading_config.get('preload_models', ['fast'])
            
            for model_type in preload_models:
                if model_type in self.models_config:
                    success = await self._load_model(model_type)
                    if success:
                        self.logger.info(f"Preloaded model: {model_type}")
                    else:
                        self.logger.warning(f"Failed to preload model: {model_type}")
            
            return len(self.loaded_models) > 0
            
        except Exception as e:
            self.error_logger.error(f"Failed to start HuggingFaceConnector: {e}", exc_info=True)
            return False

    async def stop(self) -> bool:
        """Stop the connector and free model memory."""
        try:
            self.logger.info("Stopping HuggingFaceConnector...")
            
            # Clear loaded models
            with self.model_lock:
                for model_type, model in self.loaded_models.items():
                    del model
                self.loaded_models.clear()
                
                for model_type, tokenizer in self.model_tokens.items():
                    del tokenizer
                self.model_tokens.clear()
                
                for model_type, pipeline in self.model_pipelines.items():
                    del pipeline
                self.model_pipelines.clear()
            
            # Clear cache
            self.prompt_cache.clear()
            
            # Force garbage collection
            import gc
            gc.collect()
            
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            self.logger.info("HuggingFaceConnector stopped successfully")
            return True
            
        except Exception as e:
            self.error_logger.error(f"Failed to stop HuggingFaceConnector: {e}", exc_info=True)
            return False

    async def send_prompt(self, prompt: str, model_type: str = "fast", 
                         temperature: Optional[float] = None, 
                         max_tokens: Optional[int] = None, 
                         **kwargs) -> Dict[str, Any]:
        """
        Send prompt to specified Hugging Face model with speed tracking.
        
        Args:
            prompt: The prompt to send
            model_type: Type of model to use (fast, balanced, quality, code)
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            dict: LLM response with speed metrics
        """
        try:
            start_time = time.time()
            start_memory = psutil.virtual_memory().used
            
            # Check cache first
            cache_key = self._generate_cache_key(prompt, model_type, temperature, max_tokens)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                self.cache_hits += 1
                return cached_response
            
            self.cache_misses += 1
            
            # Ensure model is loaded
            if model_type not in self.loaded_models:
                success = await self._load_model(model_type)
                if not success:
                    return {
                        'success': False,
                        'error': f"Failed to load model: {model_type}",
                        'content': ''
                    }
            
            # Get model configuration
            model_config = self.models_config.get(model_type, {})
            if not model_config:
                return {
                    'success': False,
                    'error': f"Model configuration not found: {model_type}",
                    'content': ''
                }
            
            # Prepare generation parameters
            gen_params = {
                'max_new_tokens': max_tokens or model_config.get('max_tokens', 512),
                'temperature': temperature or model_config.get('temperature', 0.7),
                'do_sample': True,
                'pad_token_id': self.model_tokens[model_type].eos_token_id,
                **kwargs
            }
            
            # Generate response
            with self.model_lock:
                inputs = self.model_tokens[model_type](prompt, return_tensors="pt").to(self.device)
                
                with torch.no_grad():
                    outputs = self.loaded_models[model_type].generate(
                        **inputs,
                        **gen_params
                    )
                
                response_text = self.model_tokens[model_type].decode(
                    outputs[0][inputs['input_ids'].shape[1]:], 
                    skip_special_tokens=True
                )
            
            # Calculate metrics
            end_time = time.time()
            end_memory = psutil.virtual_memory().used
            
            response_time = end_time - start_time
            memory_usage = (end_memory - start_memory) / (1024 * 1024)  # MB
            tokens_per_second = len(response_text.split()) / response_time if response_time > 0 else 0
            
            # GPU usage if available
            gpu_usage = None
            if self.device == "cuda" and torch.cuda.is_available():
                gpu_usage = torch.cuda.memory_allocated() / torch.cuda.max_memory_allocated() * 100
            
            # Create speed metrics
            metrics = SpeedMetrics(
                response_time=response_time,
                tokens_per_second=tokens_per_second,
                memory_usage_mb=memory_usage,
                gpu_usage_percent=gpu_usage,
                cache_hit=False,
                model_size_mb=self._get_model_size(model_type)
            )
            
            # Store metrics
            self.speed_metrics.append(metrics)
            
            # Create response
            response = {
                'success': True,
                'content': response_text,
                'model': model_type,
                'model_name': model_config.get('model_name', 'unknown'),
                'tokens_used': len(response_text.split()),
                'response_time': response_time,
                'speed_metrics': {
                    'response_time': response_time,
                    'tokens_per_second': tokens_per_second,
                    'memory_usage_mb': memory_usage,
                    'gpu_usage_percent': gpu_usage,
                    'model_size_mb': metrics.model_size_mb
                }
            }
            
            # Cache response
            self._cache_response(cache_key, response)
            
            self.logger.info(f"Prompt processed successfully with {model_type} model", extra={
                'response_time': response_time,
                'tokens_per_second': tokens_per_second,
                'memory_usage_mb': memory_usage
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

    async def _load_model(self, model_type: str) -> bool:
        """Load a specific model type."""
        try:
            if model_type in self.loaded_models:
                return True  # Already loaded
            
            model_config = self.models_config.get(model_type, {})
            if not model_config:
                self.logger.error(f"Model configuration not found: {model_type}")
                return False
            
            model_id = model_config.get('model_id')
            if not model_id:
                self.logger.error(f"Model ID not found for: {model_type}")
                return False
            
            self.logger.info(f"Loading model: {model_id}")
            
            # Setup quantization if enabled
            quantization_config = None
            if model_config.get('load_in_8bit', True):
                quantization_config = BitsAndBytesConfig(
                    load_in_8bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                model_id,
                trust_remote_code=model_config.get('trust_remote_code', False)
            )
            
            # Add padding token if not present
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # Load model
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                quantization_config=quantization_config,
                device_map=model_config.get('device_map', 'auto'),
                trust_remote_code=model_config.get('trust_remote_code', False),
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            
            # Move to device if not using device_map
            if model_config.get('device_map') != 'auto':
                model = model.to(self.device)
            
            # Store loaded model
            with self.model_lock:
                self.loaded_models[model_type] = model
                self.model_tokens[model_type] = tokenizer
            
            self.logger.info(f"Model {model_type} loaded successfully")
            return True
            
        except Exception as e:
            self.error_logger.error(f"Failed to load model {model_type}: {e}", exc_info=True)
            return False

    def _get_model_size(self, model_type: str) -> Optional[float]:
        """Get model size in MB."""
        try:
            if model_type in self.loaded_models:
                model = self.loaded_models[model_type]
                param_size = sum(p.numel() * p.element_size() for p in model.parameters())
                return param_size / (1024 * 1024)  # Convert to MB
            return None
        except Exception:
            return None

    def _generate_cache_key(self, prompt: str, model_type: str, 
                           temperature: Optional[float], max_tokens: Optional[int]) -> str:
        """Generate cache key for prompt caching."""
        import hashlib
        key_data = {
            'prompt': prompt,
            'model_type': model_type,
            'temperature': temperature,
            'max_tokens': max_tokens
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response if available."""
        return self.prompt_cache.get(cache_key)

    def _cache_response(self, cache_key: str, response: Dict[str, Any]):
        """Cache response."""
        max_cache_size = self.performance_config.get('max_cache_size', 1000)
        if len(self.prompt_cache) >= max_cache_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self.prompt_cache))
            del self.prompt_cache[oldest_key]
        
        self.prompt_cache[cache_key] = response

    async def run_speed_test(self, test_prompts: Optional[List[str]] = None, 
                           test_models: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run comprehensive speed test across models and prompts.
        
        Args:
            test_prompts: List of prompts to test
            test_models: List of model types to test
            
        Returns:
            dict: Speed test results
        """
        try:
            self.logger.info("Starting speed test...")
            
            # Use default test prompts if not provided
            if test_prompts is None:
                test_prompts = [
                    "Hello, how are you?",
                    "What is the weather like?",
                    "Can you help me with coding?",
                    "Explain machine learning briefly.",
                    "Write a simple Python function."
                ]
            
            # Use default test models if not provided
            if test_models is None:
                test_models = list(self.models_config.keys())
            
            results = {
                'timestamp': datetime.now().isoformat(),
                'test_config': {
                    'prompts': test_prompts,
                    'models': test_models
                },
                'results': {},
                'summary': {}
            }
            
            # Test each model
            for model_type in test_models:
                if model_type not in self.models_config:
                    continue
                
                self.logger.info(f"Testing model: {model_type}")
                model_results = []
                
                # Test each prompt
                for prompt in test_prompts:
                    response = await self.send_prompt(
                        prompt, 
                        model_type=model_type,
                        temperature=0.7,
                        max_tokens=100
                    )
                    
                    if response.get('success'):
                        model_results.append({
                            'prompt': prompt,
                            'response_time': response.get('response_time', 0),
                            'tokens_per_second': response.get('speed_metrics', {}).get('tokens_per_second', 0),
                            'memory_usage_mb': response.get('speed_metrics', {}).get('memory_usage_mb', 0),
                            'gpu_usage_percent': response.get('speed_metrics', {}).get('gpu_usage_percent'),
                            'content_length': len(response.get('content', ''))
                        })
                
                # Calculate model summary
                if model_results:
                    avg_response_time = sum(r['response_time'] for r in model_results) / len(model_results)
                    avg_tokens_per_second = sum(r['tokens_per_second'] for r in model_results) / len(model_results)
                    avg_memory_usage = sum(r['memory_usage_mb'] for r in model_results) / len(model_results)
                    
                    results['results'][model_type] = {
                        'detailed_results': model_results,
                        'summary': {
                            'avg_response_time': avg_response_time,
                            'avg_tokens_per_second': avg_tokens_per_second,
                            'avg_memory_usage_mb': avg_memory_usage,
                            'total_tests': len(model_results)
                        }
                    }
            
            # Calculate overall summary
            all_response_times = []
            all_tokens_per_second = []
            all_memory_usage = []
            
            for model_results in results['results'].values():
                for result in model_results['detailed_results']:
                    all_response_times.append(result['response_time'])
                    all_tokens_per_second.append(result['tokens_per_second'])
                    all_memory_usage.append(result['memory_usage_mb'])
            
            if all_response_times:
                results['summary'] = {
                    'total_tests': len(all_response_times),
                    'avg_response_time': sum(all_response_times) / len(all_response_times),
                    'min_response_time': min(all_response_times),
                    'max_response_time': max(all_response_times),
                    'avg_tokens_per_second': sum(all_tokens_per_second) / len(all_tokens_per_second),
                    'avg_memory_usage_mb': sum(all_memory_usage) / len(all_memory_usage),
                    'cache_hit_rate': self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0
                }
            
            self.logger.info("Speed test completed successfully")
            return results
            
        except Exception as e:
            self.error_logger.error(f"Speed test failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        try:
            if not self.speed_metrics:
                return {}
            
            response_times = [m.response_time for m in self.speed_metrics]
            tokens_per_second = [m.tokens_per_second for m in self.speed_metrics]
            memory_usage = [m.memory_usage_mb for m in self.speed_metrics]
            
            return {
                'total_requests': len(self.speed_metrics),
                'cache_hits': self.cache_hits,
                'cache_misses': self.cache_misses,
                'cache_hit_rate': self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0,
                'avg_response_time': sum(response_times) / len(response_times),
                'min_response_time': min(response_times),
                'max_response_time': max(response_times),
                'avg_tokens_per_second': sum(tokens_per_second) / len(tokens_per_second),
                'avg_memory_usage_mb': sum(memory_usage) / len(memory_usage),
                'loaded_models': list(self.loaded_models.keys()),
                'device': self.device
            }
        except Exception as e:
            self.error_logger.error(f"Error getting performance metrics: {e}")
            return {}

    def get_status(self) -> Dict[str, Any]:
        """Get system status."""
        return {
            'active': len(self.loaded_models) > 0,
            'model_type': 'huggingface',
            'loaded_models': list(self.loaded_models.keys()),
            'device': self.device,
            'cache_enabled': True,
            'cache_size': len(self.prompt_cache),
            'performance': self.get_performance_metrics()
        } 