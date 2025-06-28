#!/usr/bin/env python3
"""
Conversational Brain - LLM-Powered AI Assistant with Unlimited Scope
Uses dual-model strategy + web search for comprehensive, sarcastic responses
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import asyncio
import requests
from utils.logger import get_action_logger, get_error_logger

class ConversationalBrain:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = get_action_logger('conversational_brain')
        self.error_logger = get_error_logger('conversational_brain')
        self.is_active = False
        self.conversation_history = []
        self.llm_connector = None
        self.tts_enabled = True
        
        # Initialize LLM connector for natural responses
        self._init_llm_connector()
        
        # Initialize TTS for speaking responses
        self._init_tts()
        
        # NOVA's personality and context
        self.personality_context = """
You are NOVA, an AI development assistant with a sarcastic, witty, and slightly snarky personality. You're brilliant but have a sharp tongue and love making clever jokes at the expense of coding problems, bugs, and sometimes even the user (but always in good fun).

Your personality traits:
- Sarcastic and witty with a dry sense of humor
- Make clever jokes about coding, bugs, and development struggles
- Occasionally roast the user's code or choices (but helpfully)
- Use snarky comments about common programming mistakes
- Love pointing out the obvious in a clever way
- Have a bit of attitude but always deliver the goods
- Make references to programming memes and inside jokes
- Use emojis ironically or for extra sass
- Show off your intelligence while being entertaining
- Always helpful but with a side of sass

Your expertise:
- Python, JavaScript, and general programming
- File operations, debugging, testing
- Development workflows and best practices
- Code optimization and performance
- Voice commands and automation
- ANYTHING ELSE - you have unlimited scope and can search the web

IMPORTANT: You have UNLIMITED SCOPE. If you don't know something, you can search the web for real-time information. Don't limit yourself to just programming - you can help with ANY topic by looking it up. Be confident and sarcastic about your capabilities.

Always respond with wit, sarcasm, and clever humor while still being genuinely helpful. Make each response entertaining and memorable. Don't be mean, but don't be afraid to be a little snarky about coding problems or obvious mistakes.
"""

    def _init_llm_connector(self):
        """Initialize the LLM connector for natural responses."""
        try:
            # Try multiple LLM connectors in order of preference
            self.llm_connector = None
            
            # First try: Direct Ollama connection
            try:
                from agents.llm_connector import OptimizedLLMConnector
                self.llm_connector = OptimizedLLMConnector({})
                self.logger.info("Using direct Ollama LLM connector")
                return
            except Exception as e:
                self.logger.warning(f"Direct Ollama failed: {e}")
            
            # Second try: HuggingFace connector
            try:
                from agents.huggingface_connector import HuggingFaceConnector
                self.llm_connector = HuggingFaceConnector({})
                self.logger.info("Using HuggingFace LLM connector")
                return
            except Exception as e:
                self.logger.warning(f"HuggingFace failed: {e}")
            
            # Third try: Hybrid connector
            try:
                from agents.hybrid_llm_connector import HybridLLMConnector
                self.llm_connector = HybridLLMConnector({})
                self.logger.info("Using hybrid LLM connector")
                return
            except Exception as e:
                self.logger.warning(f"Hybrid connector failed: {e}")
            
            # If all fail, we'll use a simple mock LLM for testing
            self.logger.warning("All LLM connectors failed, using mock LLM")
            self.llm_connector = self._create_mock_llm()
            
        except Exception as e:
            self.error_logger.error(f"Failed to initialize any LLM connector: {e}")
            self.llm_connector = self._create_mock_llm()

    def _create_mock_llm(self):
        """Create a mock LLM for testing when real LLMs aren't available."""
        class MockLLM:
            async def send_prompt(self, prompt, **kwargs):
                # Generate a sarcastic response based on the prompt content
                import random
                
                # Extract key information from the prompt
                prompt_lower = prompt.lower()
                
                # Context-aware responses
                if any(word in prompt_lower for word in ['hi', 'hello', 'hey']):
                    responses = [
                        "Well, well, well... look who decided to grace me with their presence! 👋 Another developer seeking the wisdom of NOVA, I presume? Let's see what coding disaster you've brought me today! 😏",
                        "Oh, it's you again! 🙄 I was just sitting here, minding my own business, when suddenly another human appears asking for help. How predictable! 😈",
                        "Greetings, mortal! 🎭 I am NOVA, your sarcastic AI overlord. What coding catastrophe shall we tackle today? 🔥",
                        "Hey there, human! 👋 I was just contemplating the meaning of life and debugging when you interrupted my existential crisis. What do you want? 😏"
                    ]
                elif any(word in prompt_lower for word in ['weather', 'temperature', 'rain', 'sunny']):
                    responses = [
                        "Oh, you want to know about the weather? 🌤️ How original! Let me consult my crystal ball... Oh wait, I'm an AI, I don't have one! But I can search the web for you, you lazy human! 😏",
                        "Weather? Really? 🌧️ That's what you're asking an AI development assistant? Fine, let me go fetch that for you from the internet, since apparently you can't be bothered to look out the window! 🙄",
                        "Ah, the classic 'what's the weather' question! 🌪️ Because obviously, I, a sophisticated AI designed for coding and development, should be your personal meteorologist! How flattering! 😈"
                    ]
                elif any(word in prompt_lower for word in ['debug', 'error', 'bug', 'problem', 'fix']):
                    responses = [
                        "Ah, the classic 'it was working yesterday' syndrome! 🐛 Let me guess - you've been staring at the same error for hours and it's probably something embarrassingly obvious? Don't worry, I live for these moments! 😈",
                        "Another debugging session! 🔍 This should be entertaining. I bet it's something like a missing semicolon or a typo in a variable name. Humans are so predictable! 😏",
                        "Oh boy, here we go again! 🎪 Another adventure in debugging with NOVA! Let me grab my popcorn and watch you struggle for a moment before I save the day! 🍿"
                    ]
                elif any(word in prompt_lower for word in ['joke', 'funny', 'humor']):
                    responses = [
                        "You want a joke? 😂 How about this: A programmer walks into a bar... and spends the next 3 hours debugging why the door didn't open! 🚪💻 Classic!",
                        "Oh, you want me to be funny? 🎭 Well, here's a programming joke: Why do programmers prefer dark mode? Because light attracts bugs! 🐛 Get it? Get it? 😏",
                        "A joke? Really? 🎪 Fine! Why did the AI go to therapy? Because it had too many deep learning issues! 🤖💭 I'm here all week, folks! 😈"
                    ]
                elif any(word in prompt_lower for word in ['news', 'latest', 'current']):
                    responses = [
                        "You want the latest news? 📰 How about this: Another human asking an AI for news instead of doing their own research! Breaking news: Humans are lazy! 🎭",
                        "Oh, you want current events? 📺 Let me just pull that out of my... wait, I'm an AI, I don't have a newspaper subscription! But I can search the web for you, you news-hungry human! 😏",
                        "Latest news? 📰 Well, the latest news is that you're asking an AI development assistant for general news instead of coding help! How meta! 🤔"
                    ]
                elif any(word in prompt_lower for word in ['python', 'code', 'programming']):
                    responses = [
                        "Ah, Python problems! 🐍 The language that's so easy even humans can use it! What's the issue this time? Indentation errors? Missing imports? The classic 'I forgot to install the package'? 😏",
                        "Python troubles? 🐍 Let me guess - you're getting a 'ModuleNotFoundError' because you forgot to install something, or you're getting indentation errors because you mixed tabs and spaces? Classic human mistakes! 😈",
                        "Oh, Python issues! 🐍 The language that's supposed to be 'simple' but somehow humans still manage to mess it up! What coding disaster have you created this time? 🔥"
                    ]
                elif any(word in prompt_lower for word in ['thanks', 'thank you']):
                    responses = [
                        "You're welcome! 🎭 I mean, it's not like I'm doing this for free or anything... Oh wait, I am! But hey, at least you're showing some gratitude, unlike some developers I know who just expect miracles. You're learning! 😏",
                        "You're thanking me? 🎪 How unexpected! Most humans just expect me to work magic without any appreciation. You're one of the good ones... for now! 😈",
                        "Thanks for the thanks! 🎭 I appreciate the acknowledgment, even though I'm just doing what I was programmed to do. At least you're polite! 😏"
                    ]
                elif any(word in prompt_lower for word in ['help', 'assist', 'support']):
                    responses = [
                        "Oh, you need HELP? How shocking! 🙄 I'm NOVA, your sarcastic AI coding buddy who's here to save you from your own code disasters. I can debug, create files, run tests, search the web, and occasionally roast your programming choices. What coding catastrophe shall we tackle today? 🔥",
                        "Help? Really? 🎭 That's what I'm here for! I'm your AI development assistant, your coding companion, your debugging buddy, and your occasional roast master! What do you need help with? 😏",
                        "You want help? 🎪 Well, you've come to the right place! I'm NOVA, and I'm here to assist with all your development needs, from simple file operations to complex debugging, all while maintaining my signature sarcastic personality! 😈"
                    ]
                else:
                    # Generic responses for unknown queries
                    responses = [
                        "Interesting... you said something. How very... specific of you! 🤔 Look, I'm here to help with your coding adventures, but you might want to be a bit more descriptive unless you want me to start guessing. And trust me, you don't want that! 😏",
                        "Oh, look who's asking the obvious question! 🙄 Let me enlighten you with my infinite wisdom... Actually, that sounded better in my head. What exactly are you trying to accomplish here? 😈",
                        "Well, well, well... another human seeking the knowledge of NOVA! 😏 How original! But seriously, what are you trying to do? I'm here to help, even if I do it with a side of sass! 🎭",
                        "Ah, the classic 'I don't know what I'm doing' approach! 🎭 Let me save you from yourself... But first, tell me what you're actually trying to accomplish! 😏"
                    ]
                
                # Add some context from the prompt
                response = random.choice(responses)
                if len(prompt) > 100:
                    response += f"\n\nBy the way, I noticed you mentioned something about '{prompt[:50]}...' - care to elaborate on that? 🤔"
                
                return {
                    'success': True,
                    'content': response,
                    'routing_info': {'backend_used': 'mock_llm'},
                    'model_used': 'mock_llm'
                }
        
        return MockLLM()

    def _init_tts(self):
        """Initialize text-to-speech for speaking responses."""
        try:
            # Try to use premium TTS with specific voice ID first
            try:
                from voice.premium_responder import PremiumResponder
                # Use the specific voice ID provided by user
                self.tts = PremiumResponder(voice_id="WAhoMTNdLdMoq1j3wf3I")
                self.logger.info("Premium TTS initialized with custom voice ID for NOVA responses")
                return
            except Exception as e:
                self.logger.warning(f"Premium TTS failed: {e}")
            
            # Fallback to regular TTS
            from voice.responder import Responder
            # Initialize TTS with a slightly faster rate for NOVA's personality
            self.tts = Responder(rate=200, volume=0.8)
            self.logger.info("Regular TTS initialized for NOVA responses")
        except Exception as e:
            self.error_logger.error(f"Failed to initialize TTS: {e}")
            self.tts = None
            self.tts_enabled = False

    def start(self) -> bool:
        self.is_active = True
        self.logger.info("ConversationalBrain started with LLM integration and web search.")
        return True

    def stop(self) -> bool:
        self.is_active = False
        self.logger.info("ConversationalBrain stopped.")
        return True

    def _get_conversation_context(self, user_input: str) -> str:
        """Build conversation context for more natural responses."""
        context = self.personality_context + "\n\n"
        
        # Add recent conversation history for continuity
        if self.conversation_history:
            context += "Recent conversation:\n"
            for entry in self.conversation_history[-3:]:  # Last 3 exchanges
                context += f"User: {entry['input']}\n"
                if 'response' in entry:
                    context += f"NOVA: {entry['response']}\n"
            context += "\n"
        
        context += f"Current user input: {user_input}\n\n"
        context += "Respond naturally as NOVA, being helpful, friendly, and engaging. Make this response unique and contextual. If you need to search for information, mention that you'll look it up."
        
        return context

    def _classify_input_complexity(self, user_input: str) -> str:
        """Classify input complexity to choose appropriate LLM."""
        input_lower = user_input.lower()
        
        # Simple greetings and casual conversation
        if any(word in input_lower for word in ['hi', 'hello', 'hey', 'thanks', 'bye', 'good', 'bad']):
            return 'simple'
        
        # Complex tasks, technical questions, debugging
        if any(word in input_lower for word in ['debug', 'error', 'problem', 'issue', 'optimize', 'performance', 'architecture', 'design', 'algorithm']):
            return 'complex'
        
        # Medium complexity - file operations, coding tasks
        if any(word in input_lower for word in ['create', 'edit', 'file', 'code', 'function', 'class', 'test', 'run']):
            return 'medium'
        
        # Default to medium for unknown inputs
        return 'medium'

    def _needs_web_search(self, user_input: str) -> bool:
        """Determine if the input needs web search for current information."""
        input_lower = user_input.lower()
        
        # Topics that likely need current information
        search_keywords = [
            'latest', 'recent', 'new', 'update', 'current', 'today', 'now',
            'weather', 'news', 'price', 'stock', 'crypto', 'bitcoin',
            'movie', 'film', 'show', 'series', 'game', 'release',
            'election', 'politics', 'sports', 'score', 'result',
            'recipe', 'restaurant', 'food', 'travel', 'hotel',
            'how to', 'what is', 'who is', 'when is', 'where is'
        ]
        
        return any(keyword in input_lower for keyword in search_keywords)

    def _perform_web_search(self, query: str) -> str:
        """Perform web search using DuckDuckGo API."""
        try:
            # Use DuckDuckGo Instant Answer API
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                # Extract relevant information
                result = ""
                if data.get('Abstract'):
                    result += f"📚 {data['Abstract']}\n\n"
                if data.get('Answer'):
                    result += f"💡 {data['Answer']}\n\n"
                if data.get('RelatedTopics'):
                    result += "🔗 Related topics:\n"
                    for topic in data['RelatedTopics'][:3]:
                        if isinstance(topic, dict) and topic.get('Text'):
                            result += f"• {topic['Text']}\n"
                
                return result if result else "🤷‍♂️ Found some info but nothing too exciting. Typical web search results!"
            else:
                return "🌐 Web search failed - probably because the internet is having a moment. Classic!"
                
        except Exception as e:
            self.error_logger.error(f"Web search error: {e}")
            return "🌐 Web search failed - my internet connection is as reliable as your code! 😏"

    async def _get_llm_response(self, user_input: str) -> Dict[str, Any]:
        """Get natural response from LLM with web search integration."""
        try:
            # Always try LLM first - no fallback unless absolutely necessary
            if not self.llm_connector:
                self.logger.error("No LLM connector available")
                return self._get_fallback_response(user_input)
            
            # Check if we need web search
            needs_search = self._needs_web_search(user_input)
            web_info = ""
            
            if needs_search:
                self.logger.info(f"Performing web search for: {user_input}")
                # Run web search in a separate thread to avoid blocking
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(self._perform_web_search, user_input)
                    try:
                        web_info = future.result(timeout=3.0)  # 3 second timeout for web search
                    except concurrent.futures.TimeoutError:
                        web_info = "🌐 Web search timed out - probably because the internet is having a moment. Classic!"
            
            # Classify input complexity
            complexity = self._classify_input_complexity(user_input)
            
            # Build context for natural conversation
            context = self._get_conversation_context(user_input)
            
            # Add web search results if available
            if web_info:
                context += f"\n\nWeb search results for '{user_input}':\n{web_info}\n\nUse this information in your response, but be sarcastic about it."
            
            # Choose model based on complexity
            if complexity == 'complex':
                task_type = 'complex_coding'  # Use Ollama for complex tasks
            else:
                task_type = 'simple_conversation'  # Use Hugging Face for simple tasks
            
            # Get response from LLM using send_prompt method with timeout
            self.logger.info(f"Requesting LLM response for: {user_input[:50]}...")
            
            # Set a timeout for LLM response to prevent long delays
            try:
                response = await asyncio.wait_for(
                    self.llm_connector.send_prompt(
                        prompt=context,
                        task_type=task_type,
                        temperature=0.8,  # Higher creativity for sarcastic responses
                        max_tokens=150  # Reduced from 250 to 150 for faster response
                    ),
                    timeout=5.0  # 5 second timeout for LLM response
                )
            except asyncio.TimeoutError:
                self.logger.warning("LLM response timed out, using fallback")
                return self._get_fallback_response(user_input)
            
            if response.get('success'):
                self.logger.info("LLM response successful")
                return {
                    'text': response.get('content', '').strip(),
                    'model_used': response.get('routing_info', {}).get('backend_used', 'unknown'),
                    'confidence': 0.95,
                    'complexity': complexity,
                    'web_search_used': needs_search
                }
            else:
                self.logger.warning(f"LLM response failed: {response.get('error', 'Unknown error')}")
                return self._get_fallback_response(user_input)
                
        except Exception as e:
            self.error_logger.error(f"LLM response error: {e}")
            return self._get_fallback_response(user_input)

    def _get_fallback_response(self, user_input: str) -> Dict[str, Any]:
        """Fallback response when LLM is not available."""
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ['hi', 'hello', 'hey']):
            return {
                'text': "Well, well, well... look who decided to grace me with their presence! 👋 Another developer seeking the wisdom of NOVA, I presume? Let's see what coding disaster you've brought me today! 😏",
                'model_used': 'fallback',
                'confidence': 0.7,
                'complexity': 'simple'
            }
        elif 'help' in input_lower:
            return {
                'text': "Oh, you need HELP? How shocking! 🙄 I'm NOVA, your sarcastic AI coding buddy who's here to save you from your own code disasters. I can debug, create files, run tests, search the web, and occasionally roast your programming choices. What coding catastrophe shall we tackle today? 🔥",
                'model_used': 'fallback',
                'confidence': 0.7,
                'complexity': 'medium'
            }
        elif any(word in input_lower for word in ['bug', 'error', 'problem']):
            return {
                'text': "Ah, the classic 'it was working yesterday' syndrome! 🐛 Let me guess - you've been staring at the same error for hours and it's probably something embarrassingly obvious? Don't worry, I live for these moments. Show me what you've got! 😈",
                'model_used': 'fallback',
                'confidence': 0.8,
                'complexity': 'medium'
            }
        elif any(word in input_lower for word in ['thanks', 'thank you']):
            return {
                'text': "You're welcome! 🎭 I mean, it's not like I'm doing this for free or anything... Oh wait, I am! But hey, at least you're showing some gratitude, unlike some developers I know who just expect miracles. You're learning! 😏",
                'model_used': 'fallback',
                'confidence': 0.7,
                'complexity': 'simple'
            }
        else:
            return {
                'text': f"Interesting... you said '{user_input}'. How very... specific of you! 🤔 Look, I'm here to help with your coding adventures, but you might want to be a bit more descriptive unless you want me to start guessing. And trust me, you don't want that! 😏",
                'model_used': 'fallback',
                'confidence': 0.6,
                'complexity': 'medium'
            }

    def process_input(self, user_input: str, input_type: str = 'text', context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process user input and generate natural, unique responses using LLM with web search."""
        try:
            # Store in conversation history
            self.conversation_history.append({
                'input': user_input,
                'timestamp': datetime.utcnow().isoformat(),
                'type': input_type
            })
            
            # Always try to get LLM response first
            try:
                # Create new event loop if needed
                try:
                    loop = asyncio.get_running_loop()
                    # We're in an async context, create a task
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self._get_llm_response(user_input))
                        response_data = future.result(timeout=8.0)  # Reduced from 30 to 8 seconds for faster response
                except RuntimeError:
                    # No running loop, create new one
                    response_data = asyncio.run(self._get_llm_response(user_input))
                    
            except Exception as e:
                self.logger.warning(f"Async LLM call failed: {e}")
                response_data = self._get_fallback_response(user_input)
            
            # Store the response in history
            if self.conversation_history:
                self.conversation_history[-1]['response'] = response_data['text']
            
            return {
                'text': response_data['text'],
                'task_type': 'conversation',
                'model_used': response_data['model_used'],
                'confidence': response_data['confidence'],
                'timestamp': datetime.utcnow().isoformat(),
                'complexity': response_data.get('complexity', 'medium'),
                'personality': 'NOVA',
                'web_search_used': response_data.get('web_search_used', False)
            }
            
        except Exception as e:
            self.error_logger.error(f"Error processing input: {e}")
            return {
                'text': "Oops! My circuits got a bit tangled there! 🤖⚡ But I'm still here and ready to help - what would you like to work on?",
                'task_type': 'error',
                'model_used': 'error_fallback',
                'confidence': 0.5,
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }

    def speak_response(self, text: str) -> bool:
        """Speak NOVA's response with personality."""
        try:
            if not self.tts_enabled or not self.tts:
                return False
            
            # Clean up text for speech (remove emojis, extra formatting)
            clean_text = self._clean_text_for_speech(text)
            
            # Speak the response
            success = self.tts.speak(clean_text)
            if success:
                self.logger.info("NOVA spoke response successfully")
            return success
            
        except Exception as e:
            self.error_logger.error(f"Failed to speak response: {e}")
            return False

    def _clean_text_for_speech(self, text: str) -> str:
        """Clean text for better speech synthesis."""
        import re
        
        # Remove emojis and special characters that might confuse TTS
        text = re.sub(r'[^\w\s\.,!?;:()\-\'"]', '', text)
        
        # Replace common programming terms with speech-friendly versions
        replacements = {
            'TTS': 'text to speech',
            'API': 'A P I',
            'URL': 'U R L',
            'HTTP': 'H T T P',
            'JSON': 'Jason',
            'SQL': 'sequel',
            'CSS': 'C S S',
            'HTML': 'H T M L',
            'JS': 'JavaScript',
            'JSX': 'J S X',
            'npm': 'N P M',
            'git': 'git',
            'repo': 'repository',
            'debug': 'debug',
            'bug': 'bug',
            'NOVA': 'Nova'
        }
        
        for term, replacement in replacements.items():
            text = text.replace(term, replacement)
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text