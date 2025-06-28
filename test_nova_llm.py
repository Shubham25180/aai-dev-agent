#!/usr/bin/env python3
"""
Test script to verify NOVA's LLM integration and sarcastic personality
"""

import asyncio
from agents.conversational_brain import ConversationalBrain

async def test_nova():
    print("🧠 Testing NOVA's LLM Integration...")
    print("=" * 50)
    
    # Initialize NOVA
    nova = ConversationalBrain()
    nova.start()
    
    # Test questions
    test_questions = [
        "hi",
        "what's the weather like?",
        "help me debug this code",
        "tell me a joke",
        "what's the latest AI news?",
        "I'm having trouble with Python",
        "thanks for your help"
    ]
    
    for question in test_questions:
        print(f"\n🤖 User: {question}")
        print("-" * 30)
        
        # Get NOVA's response
        response = nova.process_input(question, 'text')
        
        print(f"💡 NOVA: {response['text']}")
        print(f"🧠 Model: {response['model_used']}")
        print(f"📊 Confidence: {response['confidence']:.1%}")
        
        if response.get('web_search_used'):
            print("🌐 Web search was used!")
        
        print("=" * 50)
    
    nova.stop()
    print("\n✅ NOVA LLM test completed!")

if __name__ == "__main__":
    asyncio.run(test_nova()) 