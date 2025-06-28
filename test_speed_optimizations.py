#!/usr/bin/env python3
"""
Speed Optimization Test Suite for NOVA AI Development Assistant
Tests all implemented speed optimizations and provides performance metrics.
"""

import asyncio
import time
import json
import os
from typing import Dict, Any, List
from datetime import datetime

# Import optimized components
from voice.fast_voice_system import FastVoiceSystem
from agents.llm_connector import OptimizedLLMConnector
from executor.file_ops import OptimizedFileOps
from agents.nova_brain import NovaBrain
from memory.memory_manager import MemoryManager

class SpeedOptimizationTester:
    """
    Comprehensive test suite for NOVA speed optimizations:
    1. Voice system performance (Whisper.cpp, VAD, caching)
    2. LLM connector speed (persistent models, prompt caching)
    3. File operations efficiency (async I/O, batch processing)
    4. Memory management optimization
    5. Overall system performance metrics
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
        
        self.results = {
            'voice_system': {},
            'llm_connector': {},
            'file_ops': {},
            'memory_manager': {},
            'nova_brain': {},
            'overall': {}
        }
        
        print("🚀 NOVA Speed Optimization Test Suite")
        print("=" * 50)

    async def run_all_tests(self):
        """Run all speed optimization tests."""
        print("\n📊 Starting comprehensive speed tests...")
        
        # Test voice system optimizations
        await self.test_voice_system_optimizations()
        
        # Test LLM connector optimizations
        await self.test_llm_connector_optimizations()
        
        # Test file operations optimizations
        await self.test_file_ops_optimizations()
        
        # Test memory manager optimizations
        await self.test_memory_manager_optimizations()
        
        # Test NOVA brain integration
        await self.test_nova_brain_integration()
        
        # Generate performance report
        await self.generate_performance_report()

    async def test_voice_system_optimizations(self):
        """Test voice system speed optimizations."""
        print("\n🎤 Testing Voice System Optimizations...")
        
        try:
            # Initialize fast voice system
            voice_system = FastVoiceSystem(self.config)
            
            # Test startup time
            start_time = time.time()
            success = await voice_system.start()
            startup_time = time.time() - start_time
            
            if not success:
                print("❌ Voice system failed to start")
                return
            
            self.results['voice_system']['startup_time'] = startup_time
            print(f"✅ Voice system started in {startup_time:.2f}s")
            
            # Test listening performance
            print("Testing listening performance...")
            listen_results = []
            
            for i in range(3):
                start_time = time.time()
                result = await voice_system.listen_once(duration=2.0)
                listen_time = time.time() - start_time
                
                listen_results.append({
                    'iteration': i + 1,
                    'listen_time': listen_time,
                    'processing_time': result.get('processing_time', 0),
                    'chunks_per_second': result.get('chunks_per_second', 0),
                    'vad_detections': result.get('vad_detections', 0),
                    'cache_hit': result.get('cache_hit', False)
                })
                
                print(f"  Listen {i+1}: {listen_time:.2f}s, {result.get('chunks_per_second', 0):.1f} chunks/s")
            
            self.results['voice_system']['listen_tests'] = listen_results
            self.results['voice_system']['average_listen_time'] = sum(r['listen_time'] for r in listen_results) / len(listen_results)
            
            # Test speech performance
            print("Testing speech performance...")
            speech_results = []
            
            test_texts = [
                "Hello, this is a test.",
                "Nova is running fast voice optimizations.",
                "The system is performing well."
            ]
            
            for i, text in enumerate(test_texts):
                start_time = time.time()
                success = await voice_system.speak(text, interrupt=True)
                speech_time = time.time() - start_time
                
                speech_results.append({
                    'text': text,
                    'speech_time': speech_time,
                    'success': success
                })
                
                print(f"  Speech {i+1}: {speech_time:.2f}s")
            
            self.results['voice_system']['speech_tests'] = speech_results
            self.results['voice_system']['average_speech_time'] = sum(r['speech_time'] for r in speech_results) / len(speech_results)
            
            # Get performance metrics
            metrics = voice_system.get_performance_metrics()
            self.results['voice_system']['metrics'] = metrics
            
            print(f"✅ Voice system optimizations: {metrics.get('cache_hit_rate', 0):.1%} cache hit rate")
            
            # Stop voice system
            await voice_system.stop()
            
        except Exception as e:
            print(f"❌ Voice system test failed: {e}")
            self.results['voice_system']['error'] = str(e)

    async def test_llm_connector_optimizations(self):
        """Test LLM connector speed optimizations."""
        print("\n🧠 Testing LLM Connector Optimizations...")
        
        try:
            # Initialize optimized LLM connector
            llm_connector = OptimizedLLMConnector(self.config)
            
            # Test startup time
            start_time = time.time()
            success = await llm_connector.start()
            startup_time = time.time() - start_time
            
            if not success:
                print("❌ LLM connector failed to start")
                return
            
            self.results['llm_connector']['startup_time'] = startup_time
            print(f"✅ LLM connector started in {startup_time:.2f}s")
            
            # Test prompt processing performance
            print("Testing prompt processing...")
            prompt_results = []
            
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
                
                prompt_results.append({
                    'prompt': prompt,
                    'processing_time': processing_time,
                    'success': response.get('success', False),
                    'content_length': len(response.get('content', '')),
                    'response_time': response.get('response_time', 0)
                })
                
                print(f"  Prompt {i+1}: {processing_time:.2f}s, {len(response.get('content', ''))} chars")
            
            self.results['llm_connector']['prompt_tests'] = prompt_results
            self.results['llm_connector']['average_processing_time'] = sum(r['processing_time'] for r in prompt_results) / len(prompt_results)
            
            # Test caching performance
            print("Testing caching performance...")
            cache_results = []
            
            # Send same prompt multiple times to test caching
            test_prompt = "This is a cache test prompt."
            
            for i in range(5):
                start_time = time.time()
                response = await llm_connector.send_prompt(test_prompt, temperature=0.7, max_tokens=50)
                processing_time = time.time() - start_time
                
                cache_results.append({
                    'iteration': i + 1,
                    'processing_time': processing_time,
                    'cache_hit': i > 0  # First call is cache miss, rest are hits
                })
                
                print(f"  Cache test {i+1}: {processing_time:.2f}s")
            
            self.results['llm_connector']['cache_tests'] = cache_results
            
            # Get performance metrics
            metrics = llm_connector.get_performance_metrics()
            self.results['llm_connector']['metrics'] = metrics
            
            print(f"✅ LLM connector optimizations: {metrics.get('cache_hit_rate', 0):.1%} cache hit rate")
            
            # Stop LLM connector
            await llm_connector.stop()
            
        except Exception as e:
            print(f"❌ LLM connector test failed: {e}")
            self.results['llm_connector']['error'] = str(e)

    async def test_file_ops_optimizations(self):
        """Test file operations speed optimizations."""
        print("\n📁 Testing File Operations Optimizations...")
        
        try:
            # Initialize optimized file ops
            file_ops = OptimizedFileOps(self.config)
            
            # Test startup time
            start_time = time.time()
            success = await file_ops.start()
            startup_time = time.time() - start_time
            
            if not success:
                print("❌ File ops failed to start")
                return
            
            self.results['file_ops']['startup_time'] = startup_time
            print(f"✅ File ops started in {startup_time:.2f}s")
            
            # Test single file operations
            print("Testing single file operations...")
            single_file_results = []
            
            test_files = [
                ('test1.txt', 'This is test file 1 with some content.'),
                ('test2.txt', 'This is test file 2 with different content.'),
                ('test3.txt', 'This is test file 3 with more content for testing.')
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
                
                single_file_results.append({
                    'filename': filename,
                    'write_time': write_time,
                    'read_time': read_time,
                    'write_success': write_result.get('success', False),
                    'read_success': read_result.get('success', False),
                    'content_length': len(content)
                })
                
                print(f"  {filename}: write {write_time:.3f}s, read {read_time:.3f}s")
            
            self.results['file_ops']['single_file_tests'] = single_file_results
            
            # Test batch operations
            print("Testing batch operations...")
            batch_results = []
            
            # Create multiple test files
            batch_files = []
            for i in range(10):
                filename = f'batch_test_{i}.txt'
                content = f'This is batch test file {i} with content for testing batch operations.'
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
            
            batch_results = {
                'batch_write_time': batch_write_time,
                'batch_read_time': batch_read_time,
                'files_processed': len(batch_files),
                'write_success_rate': sum(1 for r in batch_write_results if r.get('success', False)) / len(batch_write_results),
                'read_success_rate': sum(1 for r in batch_read_results if r.get('success', False)) / len(batch_read_results)
            }
            
            self.results['file_ops']['batch_tests'] = batch_results
            print(f"  Batch write: {batch_write_time:.3f}s, Batch read: {batch_read_time:.3f}s")
            
            # Test caching performance
            print("Testing file caching...")
            cache_results = []
            
            # Read same file multiple times
            test_file = 'cache_test.txt'
            test_content = 'This is a cache test file with content.'
            
            await file_ops.write_file(test_file, test_content)
            
            for i in range(5):
                start_time = time.time()
                result = await file_ops.read_file(test_file)
                read_time = time.time() - start_time
                
                cache_results.append({
                    'iteration': i + 1,
                    'read_time': read_time,
                    'cache_hit': i > 0  # First read is cache miss
                })
                
                print(f"  Cache read {i+1}: {read_time:.3f}s")
            
            self.results['file_ops']['cache_tests'] = cache_results
            
            # Get performance metrics
            metrics = file_ops.get_performance_metrics()
            self.results['file_ops']['metrics'] = metrics
            
            print(f"✅ File ops optimizations: {metrics.get('cache_hit_rate', 0):.1%} cache hit rate")
            
            # Cleanup test files
            for filename, _ in test_files:
                await file_ops.delete_file(filename, backup=False)
            for f in batch_files:
                await file_ops.delete_file(f['path'], backup=False)
            await file_ops.delete_file(test_file, backup=False)
            
            # Stop file ops
            await file_ops.stop()
            
        except Exception as e:
            print(f"❌ File ops test failed: {e}")
            self.results['file_ops']['error'] = str(e)

    async def test_memory_manager_optimizations(self):
        """Test memory manager optimizations."""
        print("\n🧠 Testing Memory Manager Optimizations...")
        
        try:
            # Initialize memory manager
            memory_manager = MemoryManager(self.config)
            
            # Test memory operations performance
            print("Testing memory operations...")
            memory_results = []
            
            # Test short-term memory operations
            start_time = time.time()
            for i in range(100):
                memory_manager.update_short_term(f'key_{i}', f'value_{i}')
            short_term_time = time.time() - start_time
            
            # Test long-term memory operations
            start_time = time.time()
            for i in range(50):
                memory_manager.update_long_term(f'pattern_{i}', {'frequency': i, 'last_used': datetime.utcnow().isoformat()})
            long_term_time = time.time() - start_time
            
            # Test memory retrieval
            start_time = time.time()
            short_term = memory_manager.get_short_term_memory()
            long_term = memory_manager.get_long_term_memory()
            retrieval_time = time.time() - start_time
            
            memory_results = {
                'short_term_operations': 100,
                'short_term_time': short_term_time,
                'long_term_operations': 50,
                'long_term_time': long_term_time,
                'retrieval_time': retrieval_time,
                'short_term_size': len(short_term),
                'long_term_size': len(long_term)
            }
            
            self.results['memory_manager'] = memory_results
            
            print(f"  Short-term: {short_term_time:.3f}s for 100 ops")
            print(f"  Long-term: {long_term_time:.3f}s for 50 ops")
            print(f"  Retrieval: {retrieval_time:.3f}s")
            
        except Exception as e:
            print(f"❌ Memory manager test failed: {e}")
            self.results['memory_manager']['error'] = str(e)

    async def test_nova_brain_integration(self):
        """Test NOVA brain integration with all optimizations."""
        print("\n🤖 Testing NOVA Brain Integration...")
        
        try:
            # Initialize NOVA brain
            nova_brain = NovaBrain(self.config)
            
            # Test startup time
            start_time = time.time()
            success = await nova_brain.start()
            startup_time = time.time() - start_time
            
            if not success:
                print("❌ NOVA brain failed to start")
                return
            
            self.results['nova_brain']['startup_time'] = startup_time
            print(f"✅ NOVA brain started in {startup_time:.2f}s")
            
            # Test input processing performance
            print("Testing input processing...")
            processing_results = []
            
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
                
                processing_results.append({
                    'input': user_input,
                    'processing_time': processing_time,
                    'intent': response.get('intent', ''),
                    'execution_plan_length': len(response.get('execution_plan', [])),
                    'response_length': len(response.get('natural_reply', ''))
                })
                
                print(f"  Input {i+1}: {processing_time:.2f}s, intent: {response.get('intent', '')}")
            
            self.results['nova_brain']['processing_tests'] = processing_results
            self.results['nova_brain']['average_processing_time'] = sum(r['processing_time'] for r in processing_results) / len(processing_results)
            
            # Get conversation summary
            summary = nova_brain.get_conversation_summary()
            self.results['nova_brain']['summary'] = summary
            
            print(f"✅ NOVA brain processed {summary.get('total_messages', 0)} messages")
            
            # Stop NOVA brain
            await nova_brain.stop()
            
        except Exception as e:
            print(f"❌ NOVA brain test failed: {e}")
            self.results['nova_brain']['error'] = str(e)

    async def generate_performance_report(self):
        """Generate comprehensive performance report."""
        print("\n📊 Generating Performance Report...")
        print("=" * 50)
        
        # Calculate overall metrics
        overall_metrics = {
            'total_startup_time': 0,
            'total_processing_time': 0,
            'average_cache_hit_rate': 0,
            'optimization_effectiveness': {}
        }
        
        # Voice system metrics
        if 'voice_system' in self.results and 'error' not in self.results['voice_system']:
            voice_metrics = self.results['voice_system'].get('metrics', {})
            overall_metrics['total_startup_time'] += self.results['voice_system'].get('startup_time', 0)
            overall_metrics['average_cache_hit_rate'] += voice_metrics.get('cache_hit_rate', 0)
            print(f"🎤 Voice System:")
            print(f"   Startup: {self.results['voice_system'].get('startup_time', 0):.2f}s")
            print(f"   Avg Listen: {self.results['voice_system'].get('average_listen_time', 0):.2f}s")
            print(f"   Cache Hit Rate: {voice_metrics.get('cache_hit_rate', 0):.1%}")
        
        # LLM connector metrics
        if 'llm_connector' in self.results and 'error' not in self.results['llm_connector']:
            llm_metrics = self.results['llm_connector'].get('metrics', {})
            overall_metrics['total_startup_time'] += self.results['llm_connector'].get('startup_time', 0)
            overall_metrics['total_processing_time'] += self.results['llm_connector'].get('average_processing_time', 0)
            overall_metrics['average_cache_hit_rate'] += llm_metrics.get('cache_hit_rate', 0)
            print(f"🧠 LLM Connector:")
            print(f"   Startup: {self.results['llm_connector'].get('startup_time', 0):.2f}s")
            print(f"   Avg Processing: {self.results['llm_connector'].get('average_processing_time', 0):.2f}s")
            print(f"   Cache Hit Rate: {llm_metrics.get('cache_hit_rate', 0):.1%}")
        
        # File ops metrics
        if 'file_ops' in self.results and 'error' not in self.results['file_ops']:
            file_metrics = self.results['file_ops'].get('metrics', {})
            overall_metrics['total_startup_time'] += self.results['file_ops'].get('startup_time', 0)
            overall_metrics['average_cache_hit_rate'] += file_metrics.get('cache_hit_rate', 0)
            print(f"📁 File Operations:")
            print(f"   Startup: {self.results['file_ops'].get('startup_time', 0):.2f}s")
            print(f"   Avg Read: {file_metrics.get('average_read_time', 0):.3f}s")
            print(f"   Cache Hit Rate: {file_metrics.get('cache_hit_rate', 0):.1%}")
        
        # NOVA brain metrics
        if 'nova_brain' in self.results and 'error' not in self.results['nova_brain']:
            overall_metrics['total_startup_time'] += self.results['nova_brain'].get('startup_time', 0)
            overall_metrics['total_processing_time'] += self.results['nova_brain'].get('average_processing_time', 0)
            print(f"🤖 NOVA Brain:")
            print(f"   Startup: {self.results['nova_brain'].get('startup_time', 0):.2f}s")
            print(f"   Avg Processing: {self.results['nova_brain'].get('average_processing_time', 0):.2f}s")
        
        # Calculate averages
        component_count = sum(1 for component in ['voice_system', 'llm_connector', 'file_ops'] 
                            if component in self.results and 'error' not in self.results[component])
        if component_count > 0:
            overall_metrics['average_cache_hit_rate'] /= component_count
        
        self.results['overall'] = overall_metrics
        
        print(f"\n🚀 Overall Performance:")
        print(f"   Total Startup Time: {overall_metrics['total_startup_time']:.2f}s")
        print(f"   Total Processing Time: {overall_metrics['total_processing_time']:.2f}s")
        print(f"   Average Cache Hit Rate: {overall_metrics['average_cache_hit_rate']:.1%}")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"speed_test_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed results saved to: {results_file}")
        print("\n✅ Speed optimization tests completed!")

async def main():
    """Main test runner."""
    tester = SpeedOptimizationTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 