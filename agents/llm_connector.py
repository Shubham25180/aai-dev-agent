import json
import os
from datetime import datetime
from typing import Optional, Dict, Any
import openai
import time
import requests
from utils.logger import get_action_logger, get_error_logger

class LLMConnector:
    def __init__(self, config):
        self.config = config
        self.provider = config.get('model', {}).get('provider', 'ollama')
        self.logger = get_action_logger('llm_connector')
        self.error_logger = get_error_logger('llm_connector')
        self.logger.info(
            "LLMConnector initialized.",
            extra={'provider': self.provider}
        )

        self.backend = config.get('model', {}).get('provider', 'openai')
        self.model_name = config.get('model', {}).get('model_name', 'gpt-4')
        self.max_tokens = config.get('model', {}).get('max_tokens', 4096)
        
        # Initialize OpenAI if it's the selected backend
        if self.backend == 'openai':
            openai.api_key = os.getenv('OPENAI_API_KEY')
            if not openai.api_key:
                self.error_logger.error("OpenAI API key not found in environment variables")
                raise ValueError("OpenAI API key not found in environment variables")

    def send_prompt(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Send a prompt to the selected LLM backend and return the response.
        
        Args:
            prompt: The prompt text to send
            context: Optional context dictionary for the prompt
            
        Returns:
            Dict containing the response and metadata
        """
        provider_method_map = {
            'ollama': self._send_ollama,
            'huggingface': self._send_huggingface,
            'openai': self._send_openai,
        }

        if self.provider not in provider_method_map:
            error_message = f"Unsupported LLM provider: {self.provider}"
            self.error_logger.error(error_message)
            return {'error': error_message}

        try:
            self.logger.info(
                f"Sending prompt to {self.provider}",
                extra={'prompt': prompt}
            )
            response = provider_method_map[self.provider](prompt, **kwargs)
            self.logger.info(
                f"Received response from {self.provider}",
                extra={'response': response}
            )
            return response
        except requests.exceptions.RequestException as e:
            error_message = f"API request failed for {self.provider}: {e}"
            self.error_logger.error(error_message, exc_info=True)
            return {'error': error_message}
        except Exception as e:
            error_message = f"An unexpected error occurred with {self.provider}: {e}"
            self.error_logger.error(error_message, exc_info=True)
            return {'error': error_message}

    def _send_openai(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Send a prompt to OpenAI's API with retry logic and error handling.
        
        Args:
            prompt: The prompt text to send
            context: Optional context dictionary for the prompt
            
        Returns:
            Dict containing the OpenAI response and metadata
        """
        max_retries = 3
        retry_delay = 1  # Initial delay in seconds
        
        for attempt in range(max_retries):
            try:
                # Prepare messages
                messages = []
                if kwargs.get('system_prompt'):
                    messages.append({
                        "role": "system",
                        "content": kwargs['system_prompt']
                    })
                
                messages.append({
                    "role": "user",
                    "content": prompt
                })

                # Make API call
                response = openai.ChatCompletion.create(
                    model=self.model_name,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=kwargs.get('temperature', 0.7),
                    top_p=kwargs.get('top_p', 1.0),
                    presence_penalty=kwargs.get('presence_penalty', 0.0),
                    frequency_penalty=kwargs.get('frequency_penalty', 0.0)
                )

                # Extract and format response
                result = {
                    'content': response.choices[0].message.content,
                    'model': response.model,
                    'usage': {
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    },
                    'finish_reason': response.choices[0].finish_reason,
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }

                return result

            except openai.error.RateLimitError as e:
                self.error_logger.warning(f"OpenAI rate limit hit. Retrying in {retry_delay}s... (Attempt {attempt + 1})")
                if attempt == max_retries - 1:
                    self.error_logger.error("OpenAI rate limit exceeded after max retries.", exc_info=True)
                    raise
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff

            except openai.error.APIError as e:
                self.error_logger.warning(f"OpenAI API error (HTTP {e.http_status}). Retrying in {retry_delay}s... (Attempt {attempt + 1})")
                if attempt == max_retries - 1:
                    self.error_logger.error("OpenAI API error after max retries.", exc_info=True)
                    raise
                if e.http_status != 500:  # Don't retry if it's not a server error
                    raise
                time.sleep(retry_delay)
                retry_delay *= 2

            except Exception as e:
                self.error_logger.error(f"An unexpected error occurred with the OpenAI API: {e}", exc_info=True)
                raise Exception(f"OpenAI API error: {str(e)}")

    def _send_huggingface(self, prompt: str, **kwargs) -> Dict[str, Any]:
        # TODO: Implement Hugging Face API call
        self.logger.info("Hugging Face provider is not yet implemented.")
        return {'error': 'Hugging Face provider not implemented'}

    def _send_ollama(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Sends a prompt to a local Ollama server.
        """
        model = self.config['model']['model_name']
        url = self.config['model']['endpoint']
        
        self.logger.info(
            "Connecting to Ollama server...", 
            extra={'url': url, 'model': model}
        )

        try:
            # Construct the payload for the Ollama API
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False  # We want the full response at once
            }
            
            # If a system prompt is provided in the context, use the chat endpoint
            if kwargs.get('system_prompt'):
                payload = {
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": kwargs['system_prompt']},
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False
                }
                response = requests.post(f"{url}/api/chat", json=payload, timeout=60)
            else:
                response = requests.post(f"{url}/api/generate", json=payload, timeout=60)

            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            
            # Log the full response for debugging
            self.logger.info(
                "Ollama API call successful.",
                extra={'response_text': response.text}
            )
            
            response_data = response.json()
            
            # The structure of the response differs for /api/generate and /api/chat
            if 'response' in response_data: # /api/generate
                content = response_data.get('response', '')
                usage = {
                    'prompt_tokens': response_data.get('prompt_eval_count', 0),
                    'completion_tokens': response_data.get('eval_count', 0),
                    'total_tokens': response_data.get('prompt_eval_count', 0) + response_data.get('eval_count', 0)
                }
            elif 'message' in response_data: # /api/chat
                content = response_data['message'].get('content', '')
                usage = {
                    'prompt_tokens': response_data.get('prompt_eval_count', 0),
                    'completion_tokens': response_data.get('eval_count', 0),
                    'total_tokens': response_data.get('prompt_eval_count', 0) + response_data.get('eval_count', 0)
                }
            else:
                raise ValueError("Ollama response did not contain 'response' or 'message' key.")


            result = {
                'content': content,
                'model': response_data.get('model', self.model_name),
                'usage': usage,
                'finish_reason': response_data.get('done_reason', 'completed'),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            
            return result

        except requests.exceptions.HTTPError as e:
            self.error_logger.error(f"Ollama API returned an error: {e.response.status_code} {e.response.text}")
            return {'error': f"Ollama API error: {e.response.text}"}
        except requests.exceptions.ConnectionError as e:
            self.error_logger.error(f"Could not connect to Ollama server at {url}. Make sure Ollama is running.")
            return {'error': "Connection to Ollama failed."}
        except json.JSONDecodeError:
            self.error_logger.error(
                "Failed to decode JSON response from Ollama.",
                extra={'response_text': response.text}
            )
            return {'error': 'Invalid JSON response from Ollama'}
        except Exception as e:
            self.error_logger.error(f"Error processing Ollama response: {e}")
            raise 