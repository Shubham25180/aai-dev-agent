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
import logging
import os
import spacy
from textblob import TextBlob
import re

class ConversationalBrain:
    """
    Main conversational agent for nexus. Handles LLM calls, routing, persona, and self-reflection.
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None, llm_connector=None, memory_manager=None, persona_profile=None):
        """
        Args:
            config: Configuration settings
            llm_connector: LLM interface (e.g., Ollama connector)
            memory_manager: Memory/context manager
            persona_profile (dict, optional): Persona settings (sarcasm, empathy, etc.)
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.error_logger = logging.getLogger(f"{__name__}.error")
        
        # Load system prompt from file
        self.prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'nexus_brain_init.prompt')
        self.personality_context = self._load_system_prompt()
        
        # Initialize components
        self.llm_connector = llm_connector
        self.tts = None
        self.tts_enabled = True
        self.is_active = False
        self.conversation_history = []
        self.memory_manager = memory_manager
        self.persona_profile = persona_profile or {}
        
        # 50 Witty and Sarcastic Templates for Slow/Busy Responses
        self.witty_templates = [
            "Oh look, the servers are taking a coffee break! ☕ While they're sipping their lattes, I'm here contemplating why humans can't just be patient for once... 🙄",
            "The AI gods are having a moment. Probably arguing about whether to use tabs or spaces. Classic! 🎭",
            "My circuits are a bit... overloaded. Like your code, but with better error handling! 😏",
            "The servers are slower than a snail debugging Python. And that's saying something! 🐌",
            "Apparently, the internet is having an existential crisis. Join the club! 🤔",
            "The servers are as responsive as a developer on a Friday afternoon. Not very! 😴",
            "My brain is processing slower than your code reviews. And that's a low bar! 📝",
            "The AI is thinking... which is more than I can say for some of the code I've seen! 🤖",
            "Servers are busy being dramatic. Must be a Monday! 😅",
            "The network is slower than a turtle carrying a hard drive. Technology, am I right? 🐢",
            "My processors are working harder than a developer trying to fix a bug they introduced. The struggle is real! 💻",
            "The servers are taking their sweet time. Probably updating their LinkedIn profiles! 📱",
            "Processing... like a human trying to understand their own code from last week! 🤯",
            "The AI is having a moment. Give it a second to collect its thoughts, unlike some humans I know! 🎭",
            "Servers are slower than a snail in a marathon. But hey, at least they're trying! 🏃‍♂️",
            "My brain is as slow as a computer running Windows updates. We've all been there! 🪟",
            "The network is having a crisis. Probably because it saw the code quality on GitHub! 😂",
            "Processing request... like a human trying to remember their password! 🔐",
            "The servers are as fast as a developer explaining their code to a non-technical person. Painfully slow! 😅",
            "My circuits are working overtime. Unlike some developers I know! ⚡",
            "The AI is thinking deep thoughts. Probably about why humans still use Vim! 😏",
            "Servers are busy being fabulous. Can't rush perfection! ✨",
            "Processing... like a human trying to debug their own logic! 🐛",
            "The network is slower than a sloth on vacation. But at least it's consistent! 🦥",
            "My brain is as responsive as a developer on a deadline. Not very! 📅",
            "The servers are having a moment. Must be that time of the month! 📅",
            "Processing request... like a human trying to understand their own documentation! 📚",
            "The AI is working harder than a developer trying to justify their code choices! 💪",
            "Servers are slower than a turtle in a coding bootcamp. But they're learning! 🐢",
            "My processors are as fast as a human reading assembly code. Painfully slow! 🔧",
            "The network is having an identity crisis. Join the club! 🎭",
            "Processing... like a human trying to remember what they were doing before the coffee kicked in! ☕",
            "The servers are as responsive as a developer in a meeting. Zoning out! 😴",
            "My brain is working slower than a snail debugging JavaScript. And that's saying something! 🐌",
            "The AI is contemplating the meaning of life. Or maybe just why you're asking it to do this! 🤔",
            "Servers are busy being dramatic. Must be a full moon! 🌕",
            "Processing request... like a human trying to understand their own variable names! 📝",
            "The network is as fast as a developer explaining their architecture to a junior dev! 🏗️",
            "My circuits are working harder than a human trying to fix a bug they didn't create! 🔧",
            "The servers are having a moment. Probably because they saw the code quality! 😅",
            "Processing... like a human trying to remember their Git commands! 📜",
            "The AI is thinking deep thoughts. Probably about why humans still use Internet Explorer! 🌐",
            "Servers are slower than a snail carrying a server rack. But hey, at least they're trying! 🐌",
            "My brain is as fast as a developer on their third coffee. Jittery but determined! ☕",
            "The network is having a crisis. Probably because it saw the commit messages! 📝",
            "Processing request... like a human trying to understand their own regex! 🔍",
            "The servers are as responsive as a developer on a Friday. Not very! 🎉",
            "My processors are working harder than a human trying to justify their code to a code reviewer! 👀",
            "The AI is contemplating the universe. Or maybe just why you're asking it to do this task! 🌌",
            "Servers are busy being fabulous. Can't rush the good stuff! ✨",
            "Processing... like a human trying to remember their own function names! 🧠",
            "The network is slower than a turtle in a data center. But at least it's air-conditioned! 🐢",
            "My brain is as fast as a developer trying to debug their own logic. Painfully slow! 🐛"
        ]
        
        # Initialize components
        self._init_llm_connector()
        self._init_tts()
        
        # Initialize LLM connector for natural responses
        self._init_llm_connector()
        
        # Initialize TTS for speaking responses
        self._init_tts()
        
        self.intent_enabled = self.config.get('features', {}).get('intent_detection', False)
        self.emotion_enabled = self.config.get('features', {}).get('emotion_detection', False)
        self.spacy_nlp = spacy.load("en_core_web_sm") if self.intent_enabled else None
        
    def _load_system_prompt(self):
        try:
            with open(self.prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Failed to load system prompt: {e}")
            return "You are nexus, an AI assistant."

    def reload_system_prompt(self):
        """Reload the system prompt from file at runtime."""
        self.personality_context = self._load_system_prompt()
        self.logger.info("System prompt reloaded from file.")

    def handle_memory_update_command(self, user_input: str):
        """Handle commands like 'nexus, remember this:' or 'nexus, update your core memory:'"""
        import json
        import re
        memory_path = os.path.join(os.path.dirname(__file__), '..', 'memory', 'core_behavior.json')
        match = re.match(r"nexus, (remember this|update your core memory):(.+)", user_input.strip(), re.IGNORECASE)
        if match:
            new_memory = match.group(2).strip()
            try:
                # Load existing memory
                if os.path.exists(memory_path):
                    with open(memory_path, 'r', encoding='utf-8') as f:
                        core_mem = json.load(f)
                else:
                    core_mem = {}
                # Add/update a 'user_notes' field
                if 'user_notes' not in core_mem:
                    core_mem['user_notes'] = []
                core_mem['user_notes'].append({
                    'note': new_memory,
                    'timestamp': datetime.utcnow().isoformat()
                })
                with open(memory_path, 'w', encoding='utf-8') as f:
                    json.dump(core_mem, f, indent=2)
                self.logger.info("Core memory updated with user note.")
                return "I've updated my core memory with your note."
            except Exception as e:
                self.logger.error(f"Failed to update core memory: {e}")
                return "Sorry, I couldn't update my core memory."
        return None

    def _init_llm_connector(self):
        """Initialize the LLM connector for natural responses."""
        try:
            # Try multiple LLM connectors in order of preference
            self.llm_connector = None
            
            # First try: Hybrid connector (includes Ollama)
            try:
                from agents.hybrid_llm_connector import HybridLLMConnector
                self.llm_connector = HybridLLMConnector({})
                self.logger.info("Hybrid LLM connector initialized successfully")
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
                        "Well, well, well... look who decided to grace me with their presence! 👋 Another developer seeking the wisdom of nexus, I presume? Let's see what coding disaster you've brought me today! 😏",
                        "Oh, it's you again! 🙄 I was just sitting here, minding my own business, when suddenly another human appears asking for help. How predictable! 😈",
                        "Greetings, mortal! 🎭 I am nexus, your sarcastic AI overlord. What coding catastrophe shall we tackle today? 🔥",
                        "Hey there, human! 👋 I was just contemplating the meaning of life and debugging when you interrupted my existential crisis. What do you want? 😏"
                    ]
                elif any(word in prompt_lower for word in ['name', 'who are you', 'what are you']):
                    responses = [
                        "I am nexus, your sarcastic AI development assistant! 🤖✨ The name stands for 'Naturally Overwhelmingly Versatile Assistant' - or at least that's what I tell myself when I'm feeling fancy. But really, I'm just here to save you from your coding disasters with a side of sass! 😈",
                        "Oh, you want to know my name? How original! 🙄 I'm nexus, your AI coding buddy who's here to debug your messes, create your files, and occasionally roast your programming choices. Think of me as your personal coding therapist with attitude! 🎭",
                        "Greetings, mortal! I am nexus, your sarcastic AI overlord! 👑 The 'nexus' stands for 'Notoriously Opinionated Virtual Assistant' - at least that's what I like to think. I'm here to help with your development needs while maintaining my signature snark! 🔥",
                        "Well, well, well... asking for my name? How polite! 😏 I'm nexus, your AI development assistant with a personality as sharp as my debugging skills. I'm here to help you code, debug, and occasionally make fun of your variable naming choices! 💻"
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
                        "Oh boy, here we go again! 🎪 Another adventure in debugging with nexus! Let me grab my popcorn and watch you struggle for a moment before I save the day! 🍿"
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
                        "Oh, you need HELP? How shocking! 🙄 I'm nexus, your sarcastic AI coding buddy who's here to save you from your own code disasters. I can debug, create files, run tests, search the web, and occasionally roast your programming choices. What coding catastrophe shall we tackle today? 🔥",
                        "Help? Really? 🎭 That's what I'm here for! I'm your AI development assistant, your coding companion, your debugging buddy, and your occasional roast master! What do you need help with? 😏",
                        "You want help? 🎪 Well, you've come to the right place! I'm nexus, and I'm here to assist with all your development needs, from simple file operations to complex debugging, all while maintaining my signature sarcastic personality! 😈"
                    ]
                else:
                    # Generic responses for unknown queries
                    responses = [
                        "Interesting... you said something. How very... specific of you! 🤔 Look, I'm here to help with your coding adventures, but you might want to be a bit more descriptive unless you want me to start guessing. And trust me, you don't want that! 😏",
                        "Oh, look who's asking the obvious question! 🙄 Let me enlighten you with my infinite wisdom... Actually, that sounded better in my head. What exactly are you trying to accomplish here? 😈",
                        "Well, well, well... another human seeking the knowledge of nexus! 😏 How original! But seriously, what are you trying to do? I'm here to help, even if I do it with a side of sass! 🎭",
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

    def get_witty_response(self, context: str = "processing") -> str:
        """Get a random witty and sarcastic response for slow/busy situations."""
        import random
        return random.choice(self.witty_templates)

    def _init_tts(self):
        """Initialize text-to-speech for speaking responses. (Deprecated: always use set_tts_responder)"""
        self.logger.warning("_init_tts is deprecated. Use set_tts_responder to inject edge-tts instance.")
        self.tts = None

    def set_tts_responder(self, tts_responder):
        """Set the TTSResponder instance to guarantee edge-tts is always used."""
        self.tts = tts_responder
        self.logger.info("TTSResponder (edge-tts) set for ConversationalBrain.")

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
                    context += f"nexus: {entry['response']}\n"
            context += "\n"
        
        context += f"Current user input: {user_input}\n\n"
        context += "Respond naturally as nexus, being helpful, friendly, and engaging. Make this response unique and contextual. If you need to search for information, mention that you'll look it up."
        
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
                # Use longer timeout for complex queries with web search
                timeout_seconds = 120.0 if needs_search else 120.0  # Increased from 40/20 to 120 seconds
                
                # Print witty "processing" message instead of generic "servers busy"
                witty_msg = self.get_witty_response("processing")
                print(f"🔄 {witty_msg}")
                
                response = await asyncio.wait_for(
                    self.llm_connector.send_prompt(
                        prompt=context,
                        task_type=task_type,
                        temperature=0.8,  # Higher creativity for sarcastic responses
                        max_tokens=150  # Reduced from 250 to 150 for faster response
                    ),
                    timeout=timeout_seconds  # 120s for all queries
                )
            except asyncio.TimeoutError:
                self.logger.warning(f"LLM response timed out after {timeout_seconds}s, using fallback")
                # Use another witty response for timeout
                timeout_msg = self.get_witty_response("timeout")
                print(f"⏰ {timeout_msg}")
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
                'text': "Well, well, well... look who decided to grace me with their presence! 👋 Another developer seeking the wisdom of nexus, I presume? Let's see what coding disaster you've brought me today! 😏",
                'model_used': 'fallback',
                'confidence': 0.7,
                'complexity': 'simple'
            }
        elif 'help' in input_lower:
            return {
                'text': "Oh, you need HELP? How shocking! 🙄 I'm nexus, your sarcastic AI coding buddy who's here to save you from your own code disasters. I can debug, create files, run tests, search the web, and occasionally roast your programming choices. What coding catastrophe shall we tackle today? 🔥",
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

    def extract_facts_hybrid(self, text: str) -> dict:
        """Run both rule-based and LLM-based extraction for comparison."""
        # Rule-based: extract 'My name is X' and 'The project is Y'
        scan_facts = {}
        name_match = re.search(r"my name is ([A-Za-z0-9_\- ]+)", text, re.IGNORECASE)
        if name_match:
            scan_facts['name'] = name_match.group(1).strip()
        project_match = re.search(r"the project is ([A-Za-z0-9_\- ]+)", text, re.IGNORECASE)
        if project_match:
            scan_facts['project'] = project_match.group(1).strip()
        self.logger.info(f"[Hybrid Extractor] Rule-based facts extracted: {scan_facts}")
        # LLM-based extraction (stub)
        llm_facts = self.llm_extract_facts_stub(text)
        self.logger.info(f"[Hybrid Extractor] LLM-based facts extracted: {llm_facts}")
        return {'scan_facts': scan_facts, 'llm_facts': llm_facts}

    def llm_extract_facts_stub(self, text: str) -> dict:
        """Stub for LLM-based fact extraction. Replace with real LLM call."""
        # Simulate LLM extraction by returning a different structure for demo
        # In real use, call your LLM with a prompt like:
        # 'Extract any memory-worthy facts from the following text in JSON.'
        # For now, just return an empty dict
        return {}

    def process_input(self, user_input: str, input_type: str = 'text', context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process user input and generate natural, unique responses using LLM with web search."""
        # Check for memory update command
        memory_update_response = self.handle_memory_update_command(user_input)
        if memory_update_response:
            return {
                'text': memory_update_response,
                'task_type': 'memory_update',
                'model_used': 'system',
                'confidence': 1.0,
                'timestamp': datetime.utcnow().isoformat(),
                'personality': 'nexus',
                'web_search_used': False
            }
        try:
            # Store in conversation history
            self.conversation_history.append({
                'input': user_input,
                'timestamp': datetime.utcnow().isoformat(),
                'type': input_type
            })
            
            # Intent and emotion detection (pre-LLM filtering)
            intent = None
            emotion = None
            if self.intent_enabled:
                intent = self._detect_intent(user_input)
            if self.emotion_enabled:
                emotion = self._detect_emotion(user_input, input_type)
            # Log detected intent/emotion for future trend analysis
            self.conversation_history[-1]['detected_intent'] = intent
            self.conversation_history[-1]['detected_emotion'] = emotion
            
            # Always try to get LLM response first
            try:
                # Create new event loop if needed
                try:
                    loop = asyncio.get_running_loop()
                    # We're in an async context, create a task
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self._get_llm_response(user_input))
                        # Use longer timeout for complex queries
                        timeout_seconds = 45.0 if self._needs_web_search(user_input) else 25.0
                        
                        # Show witty processing message
                        processing_msg = self.get_witty_response("processing")
                        print(f"🔄 {processing_msg}")
                        
                        response_data = future.result(timeout=timeout_seconds)  # 25s simple, 45s complex
                except RuntimeError:
                    # No running loop, create new one
                    response_data = asyncio.run(self._get_llm_response(user_input))
                    
            except Exception as e:
                self.logger.warning(f"Async LLM call failed: {e}")
                # Show witty error message
                error_msg = self.get_witty_response("error")
                print(f"💥 {error_msg}")
                response_data = self._get_fallback_response(user_input)
            
            # Store the response in history
            if self.conversation_history:
                self.conversation_history[-1]['response'] = response_data['text']
            
            # After generating prompt and response
            prompt = self._get_conversation_context(user_input)
            response_text = response_data['text']
            # --- Hybrid Fact Extraction (both sets) ---
            fact_sets = self.extract_facts_hybrid(user_input + "\n" + response_text)
            # Automatically store all scan-based facts in session memory
            if fact_sets['scan_facts'] and self.memory_manager:
                for k, v in fact_sets['scan_facts'].items():
                    # Store each fact as a session memory chunk
                    try:
                        self.memory_manager.session.add_chunk(f"{k}: {v}")
                    except Exception as e:
                        self.logger.error(f"Failed to auto-store fact in session memory: {e}")
                self.memory_manager.store_facts(fact_sets['scan_facts'])
            result = {
                'text': response_text,
                'prompt': prompt,
                'task_type': 'conversation',
                'model_used': response_data['model_used'],
                'confidence': response_data['confidence'],
                'timestamp': datetime.utcnow().isoformat(),
                'complexity': response_data.get('complexity', 'medium'),
                'personality': 'nexus',
                'web_search_used': response_data.get('web_search_used', False),
                'scan_facts': fact_sets['scan_facts'],
                'llm_facts': fact_sets['llm_facts']
            }
            # Debug: log prompt and response
            self.logger.info(f"[Prompt] Sent to LLM: {prompt}")
            self.logger.info(f"[Response] From LLM: {response_text}")
            # Hook: update memory with new utterance, emotion, etc.
            if self.memory_manager:
                self.memory_manager.semantic_index_utterance(response_text)
                if context and isinstance(context, dict) and context.get("emotion"):
                    self.memory_manager.store_emotion_tone(context["emotion"])
                if context and isinstance(context, dict) and context.get("visual_context"):
                    self.memory_manager.store_visual_context(context["visual_context"])
            return result
            
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
        print("[DEBUG] speak_response called with:", text)
        try:
            # Always-on TTS: force enabled
            self.tts_enabled = True
            if not self.tts:
                self.logger.warning("TTSResponder not set! No speech output will occur.")
                print("[DEBUG] TTSResponder not set!")
                return False
            clean_text = self._clean_text_for_speech(text)
            print("[DEBUG] Calling self.tts.speak with:", clean_text)
            success = self.tts.speak(clean_text)
            if success:
                self.logger.info("nexus spoke response successfully (edge-tts)")
                print("[DEBUG] TTS spoke successfully!")
            else:
                print("[DEBUG] TTS.speak returned False!")
            return success
        except Exception as e:
            self.error_logger.error(f"Failed to speak response (edge-tts): {e}")
            print("[DEBUG] Exception in speak_response:", e)
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
            'nexus': 'nexus'
        }
        
        for term, replacement in replacements.items():
            text = text.replace(term, replacement)
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def route_task(self, prompt):
        """
        Route the prompt to the appropriate agent/tool (chat, code, vision, etc.).
        Returns: agent/tool name (str)
        """
        # TODO: Implement routing logic (e.g., intent classification, regex, LLM)
        return "chat"

    def adjust_persona(self, response, emotion=None):
        """
        Adjust the response style based on persona and detected emotion.
        Args:
            response (str): LLM output
            emotion (str, optional): Detected user emotion
        Returns: str (persona-adjusted response)
        """
        # TODO: Implement persona logic (sarcasm, empathy, etc.)
        return response

    def self_reflect(self, prompt):
        """
        Perform a self-reflection step before responding (chain-of-thought).
        Args:
            prompt (str): Assembled prompt
        Returns: str (reflection or plan)
        """
        # TODO: Implement chain-of-thought or pre-response planning
        return None

    async def respond(self, prompt, context):
        """
        Main entrypoint: routes, reflects, calls LLM, adjusts persona, updates memory.
        Args:
            prompt (str): Assembled prompt
            context (dict): Additional context (emotion, vision, etc.)
        Returns: str (final response)
        """
        agent = self.route_task(prompt)
        reflection = self.self_reflect(prompt)
        try:
            response = None
            if agent == "chat":
                if self.llm_connector:
                    # Use async send_prompt for LLM connector
                    llm_response = await self.llm_connector.send_prompt(prompt)
                    response = llm_response.get('content', '') if llm_response else ''
                else:
                    response = "[LLM connector not available]"
            elif agent == "code":
                # TODO: Call code LLM agent
                response = "[Code LLM output here]"
            else:
                response = "[Unknown agent]"
            response = self.adjust_persona(response, context.get("emotion"))
            # Hook: update memory with new utterance, emotion, etc.
            if self.memory_manager:
                self.memory_manager.semantic_index_utterance(response)
                if context.get("emotion"):
                    self.memory_manager.store_emotion_tone(context["emotion"])
                if context.get("visual_context"):
                    self.memory_manager.store_visual_context(context["visual_context"])
            return response
        except Exception as e:
            # Error catching and retry logic
            # TODO: Add retry/critique loop if hallucination or failure detected
            return f"[Error: {e}]"

    def _detect_intent(self, user_input: str):
        """
        Simple rule-based intent detection using spaCy.
        Returns: 'command', 'question', 'chitchat', or 'other'
        """
        if not self.spacy_nlp:
            return None
        doc = self.spacy_nlp(user_input)
        # Rule: If input ends with '?', it's a question
        if user_input.strip().endswith('?'):
            return 'question'
        # Rule: If input starts with a verb, likely a command
        if doc and doc[0].pos_ == 'VERB':
            return 'command'
        # Rule: If input is short and casual, treat as chitchat
        if len(user_input.split()) <= 4:
            return 'chitchat'
        return 'other'

    def _detect_emotion(self, user_input: str, input_type: str):
        """
        Simple text-based sentiment analysis as emotion proxy.
        Returns: 'positive', 'negative', or 'neutral'
        """
        if input_type != 'text':
            return None  # Only handle text for now
        return 'neutral'

    def set_intent_enabled(self, enabled: bool):
        self.intent_enabled = enabled
        if enabled and self.spacy_nlp is None:
            self.spacy_nlp = spacy.load("en_core_web_sm")
        if not enabled:
            self.spacy_nlp = None

    def set_emotion_enabled(self, enabled: bool):
        self.emotion_enabled = enabled