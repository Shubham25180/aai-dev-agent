#!/usr/bin/env python3
"""
NOVA Speed Optimization Demo
Demonstrates all speed optimizations in action with real-time metrics.
"""

import asyncio
import time
import json
from typing import Dict, Any
from datetime import datetime

# Import optimized components
from voice.fast_voice_system import FastVoiceSystem
from agents.llm_connector import OptimizedLLMConnector
from executor.file_ops import OptimizedFileOps
from agents.nova_brain import NovaBrain

class SpeedOptimizationDemo:
    """
    Live demonstration of NOVA speed optimizations:
    1. Voice system with Whisper.cpp and VAD
    2. LLM connector with persistent models and caching
    3. File operations with async I/O and batching
    4. NOVA brain with intelligent routing
    """
    
    def __init__(self):
        self.config = {
            'voice': {
                'model_size': 'base.en',
                'threads': 4,
                'use_gpu': False,
                'tts_engine': 'pyttsx3'
            },
            'llm': {
                'model_type': 'ollama',
                'model_name': 'llama3.2:3b',
                'api_url': 'http://localhost:11434',
                'cache_enabled': True,
                'max_cache_size': 1000,
                'timeout': 30
            },
            'file_ops': {
                'cache_enabled': True,
                'max_cache_size': 100,
                'batch_size': 10,
                'batch_timeout': 1.0
            }
        }
        
        self.components = {}
        self.demo_results = {}
        
        print("🚀 NOVA Speed Optimization Demo")
        print("=" * 50)
        print("Demonstrating Jarvis-like performance optimizations...")

    async def run_demo(self):
        """Run the complete speed optimization demo."""
        print("\n🎯 Starting Speed Optimization Demo...")
        
        # Initialize all components
        await self.initialize_components()
        
        # Run individual demos
        await self.demo_voice_system()
        await self.demo_llm_connector()
        await self.demo_file_operations()
        await self.demo_nova_brain()
        
        # Run integrated demo
        await self.demo_integrated_system()
        
        # Show final results
        await self.show_demo_results()

    async def initialize_components(self):
        """Initialize all optimized components."""
        print("\n🔧 Initializing Optimized Components...")
        
        try:
            # Initialize voice system
            print("  🎤 Initializing Fast Voice System...")
            voice_system = FastVoiceSystem(self.config)
            start_time = time.time()
            success = await voice_system.start()
            startup_time = time.time() - start_time
            
            if success:
                self.components['voice_system'] = voice_system
                print(f"    ✅ Started in {startup_time:.2f}s")
            else:
                print("    ❌ Failed to start voice system")
            
            # Initialize LLM connector
            print("  🧠 Initializing Optimized LLM Connector...")
            llm_connector = OptimizedLLMConnector(self.config)
            start_time = time.time()
            success = await llm_connector.start()
            startup_time = time.time() - start_time
            
            if success:
                self.components['llm_connector'] = llm_connector
                print(f"    ✅ Started in {startup_time:.2f}s")
            else:
                print("    ❌ Failed to start LLM connector")
            
            # Initialize file operations
            print("  📁 Initializing Optimized File Operations...")
            file_ops = OptimizedFileOps(self.config)
            start_time = time.time()
            success = await file_ops.start()
            startup_time = time.time() - start_time
            
            if success:
                self.components['file_ops'] = file_ops
                print(f"    ✅ Started in {startup_time:.2f}s")
            else:
                print("    ❌ Failed to start file operations")
            
            # Initialize NOVA brain
            print("  🤖 Initializing NOVA Brain...")
            nova_brain = NovaBrain(self.config)
            start_time = time.time()
            success = await nova_brain.start()
            startup_time = time.time() - start_time
            
            if success:
                self.components['nova_brain'] = nova_brain
                print(f"    ✅ Started in {startup_time:.2f}s")
            else:
                print("    ❌ Failed to start NOVA brain")
            
            print(f"\n✅ All components initialized successfully!")
            
        except Exception as e:
            print(f"❌ Error initializing components: {e}")

    async def demo_voice_system(self):
        """Demonstrate voice system optimizations."""
        print("\n🎤 Voice System Speed Demo...")
        
        if 'voice_system' not in self.components:
            print("  ❌ Voice system not available")
            return
        
        voice_system = self.components['voice_system']
        results = []
        
        # Demo 1: Listening performance
        print("  📡 Testing listening performance...")
        for i in range(3):
            start_time = time.time()
            result = await voice_system.listen_once(duration=2.0)
            listen_time = time.time() - start_time
            
            results.append({
                'test': f'listen_{i+1}',
                'time': listen_time,
                'chunks_per_second': result.get('chunks_per_second', 0),
                'vad_detections': result.get('vad_detections', 0)
            })
            
            print(f"    Listen {i+1}: {listen_time:.2f}s, {result.get('chunks_per_second', 0):.1f} chunks/s")
        
        # Demo 2: Speech performance
        print("  🔊 Testing speech performance...")
        test_texts = [
            "Hello, this is a speed test.",
            "Nova is running optimizations.",
            "The system is performing well."
        ]
        
        for i, text in enumerate(test_texts):
            start_time = time.time()
            success = await voice_system.speak(text, interrupt=True)
            speech_time = time.time() - start_time
            
            results.append({
                'test': f'speech_{i+1}',
                'time': speech_time,
                'success': success,
                'text_length': len(text)
            })
            
            print(f"    Speech {i+1}: {speech_time:.2f}s")
        
        # Get performance metrics
        metrics = voice_system.get_performance_metrics()
        results.append({
            'test': 'metrics',
            'cache_hit_rate': metrics.get('cache_hit_rate', 0),
            'average_processing_time': metrics.get('average_processing_time', 0)
        })
        
        self.demo_results['voice_system'] = results
        print(f"  ✅ Voice system demo completed - Cache hit rate: {metrics.get('cache_hit_rate', 0):.1%}")

    async def demo_llm_connector(self):
        """Demonstrate LLM connector optimizations."""
        print("\n🧠 LLM Connector Speed Demo...")
        
        if 'llm_connector' not in self.components:
            print("  ❌ LLM connector not available")
            return
        
        llm_connector = self.components['llm_connector']
        results = []
        
        # Demo 1: Prompt processing
        print("  💭 Testing prompt processing...")
        test_prompts = [
            "Hello, how are you?",
            "What is the weather like?",
            "Can you help me with coding?",
            "Explain machine learning briefly.",
            "Write a simple Python function."
        ]
        
        for i, prompt in enumerate(test_prompts):
            start_time = time.time()
            response = await llm_connector.send_prompt(prompt, temperature=0.7, max_tokens=100)
            processing_time = time.time() - start_time
            
            results.append({
                'test': f'prompt_{i+1}',
                'time': processing_time,
                'success': response.get('success', False),
                'content_length': len(response.get('content', '')),
                'prompt': prompt[:50] + "..." if len(prompt) > 50 else prompt
            })
            
            print(f"    Prompt {i+1}: {processing_time:.2f}s, {len(response.get('content', ''))} chars")
        
        # Demo 2: Caching performance
        print("  💾 Testing caching performance...")
        test_prompt = "This is a cache test prompt for demonstration."
        
        for i in range(5):
            start_time = time.time()
            response = await llm_connector.send_prompt(test_prompt, temperature=0.7, max_tokens=50)
            processing_time = time.time() - start_time
            
            results.append({
                'test': f'cache_{i+1}',
                'time': processing_time,
                'cache_hit': i > 0  # First call is cache miss
            })
            
            print(f"    Cache test {i+1}: {processing_time:.2f}s")
        
        # Get performance metrics
        metrics = llm_connector.get_performance_metrics()
        results.append({
            'test': 'metrics',
            'cache_hit_rate': metrics.get('cache_hit_rate', 0),
            'average_response_time': metrics.get('average_response_time', 0),
            'request_count': metrics.get('request_count', 0)
        })
        
        self.demo_results['llm_connector'] = results
        print(f"  ✅ LLM connector demo completed - Cache hit rate: {metrics.get('cache_hit_rate', 0):.1%}")

    async def demo_file_operations(self):
        """Demonstrate file operations optimizations."""
        print("\n📁 File Operations Speed Demo...")
        
        if 'file_ops' not in self.components:
            print("  ❌ File operations not available")
            return
        
        file_ops = self.components['file_ops']
        results = []
        
        # Demo 1: Single file operations
        print("  📄 Testing single file operations...")
        test_files = [
            ('demo1.txt', 'This is demo file 1 with some content for testing.'),
            ('demo2.txt', 'This is demo file 2 with different content for testing.'),
            ('demo3.txt', 'This is demo file 3 with more content for testing file operations.')
        ]
        
        for filename, content in test_files:
            # Test write
            start_time = time.time()
            write_result = await file_ops.write_file(filename, content)
            write_time = time.time() - start_time
            
            # Test read
            start_time = time.time()
            read_result = await file_ops.read_file(filename)
            read_time = time.time() - start_time
            
            results.append({
                'test': f'file_{filename}',
                'write_time': write_time,
                'read_time': read_time,
                'content_length': len(content),
                'write_success': write_result.get('success', False),
                'read_success': read_result.get('success', False)
            })
            
            print(f"    {filename}: write {write_time:.3f}s, read {read_time:.3f}s")
        
        # Demo 2: Batch operations
        print("  📦 Testing batch operations...")
        batch_files = []
        for i in range(10):
            filename = f'batch_demo_{i}.txt'
            content = f'This is batch demo file {i} with content for testing batch operations.'
            batch_files.append({'path': filename, 'content': content})
        
        # Test batch write
        start_time = time.time()
        batch_write_results = await file_ops.batch_write_files(batch_files)
        batch_write_time = time.time() - start_time
        
        # Test batch read
        file_paths = [f['path'] for f in batch_files]
        start_time = time.time()
        batch_read_results = await file_ops.batch_read_files(file_paths)
        batch_read_time = time.time() - start_time
        
        results.append({
            'test': 'batch_operations',
            'batch_write_time': batch_write_time,
            'batch_read_time': batch_read_time,
            'files_processed': len(batch_files),
            'write_success_rate': sum(1 for r in batch_write_results if r.get('success', False)) / len(batch_write_results),
            'read_success_rate': sum(1 for r in batch_read_results if r.get('success', False)) / len(batch_read_results)
        })
        
        print(f"    Batch write: {batch_write_time:.3f}s, Batch read: {batch_read_time:.3f}s")
        
        # Demo 3: Caching performance
        print("  💾 Testing file caching...")
        test_file = 'cache_demo.txt'
        test_content = 'This is a cache demo file with content for testing caching performance.'
        
        await file_ops.write_file(test_file, test_content)
        
        for i in range(5):
            start_time = time.time()
            result = await file_ops.read_file(test_file)
            read_time = time.time() - start_time
            
            results.append({
                'test': f'cache_read_{i+1}',
                'time': read_time,
                'cache_hit': i > 0  # First read is cache miss
            })
            
            print(f"    Cache read {i+1}: {read_time:.3f}s")
        
        # Get performance metrics
        metrics = file_ops.get_performance_metrics()
        results.append({
            'test': 'metrics',
            'cache_hit_rate': metrics.get('cache_hit_rate', 0),
            'average_read_time': metrics.get('average_read_time', 0),
            'average_write_time': metrics.get('average_write_time', 0)
        })
        
        self.demo_results['file_ops'] = results
        print(f"  ✅ File operations demo completed - Cache hit rate: {metrics.get('cache_hit_rate', 0):.1%}")
        
        # Cleanup demo files
        for filename, _ in test_files:
            await file_ops.delete_file(filename, backup=False)
        for f in batch_files:
            await file_ops.delete_file(f['path'], backup=False)
        await file_ops.delete_file(test_file, backup=False)

    async def demo_nova_brain(self):
        """Demonstrate NOVA brain optimizations."""
        print("\n🤖 NOVA Brain Speed Demo...")
        
        if 'nova_brain' not in self.components:
            print("  ❌ NOVA brain not available")
            return
        
        nova_brain = self.components['nova_brain']
        results = []
        
        # Demo: Input processing performance
        print("  🧠 Testing input processing...")
        test_inputs = [
            "Hello Nova, how are you?",
            "Can you help me write some code?",
            "What's the weather like today?",
            "Open VS Code for me please.",
            "Create a new Python project."
        ]
        
        for i, user_input in enumerate(test_inputs):
            start_time = time.time()
            response = await nova_brain.process_input(user_input, input_type='text')
            processing_time = time.time() - start_time
            
            results.append({
                'test': f'input_{i+1}',
                'time': processing_time,
                'intent': response.get('intent', ''),
                'execution_plan_length': len(response.get('execution_plan', [])),
                'response_length': len(response.get('natural_reply', '')),
                'input': user_input[:50] + "..." if len(user_input) > 50 else user_input
            })
            
            print(f"    Input {i+1}: {processing_time:.2f}s, intent: {response.get('intent', '')}")
        
        # Get conversation summary
        summary = nova_brain.get_conversation_summary()
        results.append({
            'test': 'summary',
            'total_messages': summary.get('total_messages', 0),
            'user_messages': summary.get('user_messages', 0),
            'nova_messages': summary.get('nova_messages', 0),
            'cache_size': summary.get('cache_size', 0)
        })
        
        self.demo_results['nova_brain'] = results
        print(f"  ✅ NOVA brain demo completed - Processed {summary.get('total_messages', 0)} messages")

    async def demo_integrated_system(self):
        """Demonstrate integrated system performance."""
        print("\n🚀 Integrated System Speed Demo...")
        
        if not all(component in self.components for component in ['voice_system', 'llm_connector', 'file_ops', 'nova_brain']):
            print("  ❌ Not all components available for integrated demo")
            return
        
        results = []
        
        # Demo: End-to-end processing
        print("  🔄 Testing end-to-end processing...")
        
        # Simulate a complete user interaction
        user_input = "Create a new Python file and write a hello world function"
        
        start_time = time.time()
        
        # Step 1: Process input through NOVA brain
        nova_response = await self.components['nova_brain'].process_input(user_input, input_type='text')
        nova_time = time.time() - start_time
        
        # Step 2: Simulate file creation
        file_content = 'def hello_world():\n    print("Hello, World!")\n\nif __name__ == "__main__":\n    hello_world()'
        file_start = time.time()
        file_result = await self.components['file_ops'].write_file('hello_world.py', file_content)
        file_time = time.time() - file_start
        
        # Step 3: Simulate LLM response
        llm_start = time.time()
        llm_response = await self.components['llm_connector'].send_prompt(
            "Explain what this Python code does: " + file_content,
            temperature=0.7,
            max_tokens=100
        )
        llm_time = time.time() - llm_start
        
        total_time = time.time() - start_time
        
        results.append({
            'test': 'end_to_end',
            'total_time': total_time,
            'nova_processing_time': nova_time,
            'file_operation_time': file_time,
            'llm_response_time': llm_time,
            'intent': nova_response.get('intent', ''),
            'execution_plan_length': len(nova_response.get('execution_plan', [])),
            'file_success': file_result.get('success', False),
            'llm_success': llm_response.get('success', False)
        })
        
        print(f"    End-to-end: {total_time:.2f}s total")
        print(f"      NOVA processing: {nova_time:.2f}s")
        print(f"      File operation: {file_time:.2f}s")
        print(f"      LLM response: {llm_time:.2f}s")
        print(f"      Intent: {nova_response.get('intent', '')}")
        
        # Cleanup
        await self.components['file_ops'].delete_file('hello_world.py', backup=False)
        
        self.demo_results['integrated_system'] = results
        print(f"  ✅ Integrated system demo completed")

    async def show_demo_results(self):
        """Show comprehensive demo results."""
        print("\n📊 Demo Results Summary")
        print("=" * 50)
        
        # Calculate overall metrics
        total_tests = 0
        total_time = 0
        cache_hit_rates = []
        
        for component, results in self.demo_results.items():
            print(f"\n{component.upper().replace('_', ' ')}:")
            
            for result in results:
                if 'time' in result:
                    total_tests += 1
                    total_time += result['time']
                
                if 'cache_hit_rate' in result:
                    cache_hit_rates.append(result['cache_hit_rate'])
                
                # Show key metrics
                if result['test'] == 'metrics':
                    if 'cache_hit_rate' in result:
                        print(f"  Cache Hit Rate: {result['cache_hit_rate']:.1%}")
                    if 'average_response_time' in result:
                        print(f"  Avg Response Time: {result['average_response_time']:.2f}s")
                    if 'average_read_time' in result:
                        print(f"  Avg Read Time: {result['average_read_time']:.3f}s")
                    if 'average_write_time' in result:
                        print(f"  Avg Write Time: {result['average_write_time']:.3f}s")
        
        # Overall performance
        if total_tests > 0:
            avg_time = total_time / total_tests
            print(f"\n🎯 Overall Performance:")
            print(f"  Total Tests: {total_tests}")
            print(f"  Average Time: {avg_time:.3f}s")
            print(f"  Total Time: {total_time:.2f}s")
        
        if cache_hit_rates:
            avg_cache_hit_rate = sum(cache_hit_rates) / len(cache_hit_rates)
            print(f"  Average Cache Hit Rate: {avg_cache_hit_rate:.1%}")
        
        # Performance assessment
        print(f"\n🚀 Performance Assessment:")
        if avg_time < 0.5:
            print(f"  ⚡ EXCELLENT - Sub-second performance achieved!")
        elif avg_time < 1.0:
            print(f"  🟢 GOOD - Fast performance achieved!")
        elif avg_time < 2.0:
            print(f"  🟡 ACCEPTABLE - Reasonable performance")
        else:
            print(f"  🔴 NEEDS IMPROVEMENT - Performance optimization needed")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"demo_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(self.demo_results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed results saved to: {results_file}")
        print("\n✅ Speed optimization demo completed!")

    async def cleanup(self):
        """Clean up all components."""
        print("\n🧹 Cleaning up components...")
        
        for component_name, component in self.components.items():
            try:
                if hasattr(component, 'stop'):
                    await component.stop()
                print(f"  ✅ {component_name} stopped")
            except Exception as e:
                print(f"  ❌ Error stopping {component_name}: {e}")

async def main():
    """Main demo runner."""
    demo = SpeedOptimizationDemo()
    
    try:
        await demo.run_demo()
    finally:
        await demo.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 