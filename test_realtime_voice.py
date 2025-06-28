#!/usr/bin/env python3
"""
Real-Time Voice System Test
Demonstrates the multi-threaded pipeline for Alexa/Siri-like responsiveness.
"""

import asyncio
import time
import yaml
import json
from datetime import datetime
from typing import Dict, Any
from voice.realtime_voice_system import RealTimeVoiceSystem
from agents.hybrid_llm_connector import HybridLLMConnector
from utils.logger import get_action_logger, get_error_logger

class RealTimeVoiceTester:
    """
    Comprehensive tester for the real-time voice system.
    Tests the multi-threaded pipeline and performance metrics.
    """
    
    def __init__(self, config_path: str = 'config/settings_hybrid.yaml'):
        self.logger = get_action_logger('realtime_voice_tester')
        self.error_logger = get_error_logger('realtime_voice_tester')
        self.config_path = config_path
        self.config = self._load_config()
        self.voice_system = None
        self.llm_connector = None
        self.test_results = {}
        
        print("🚀 Real-Time Voice System Test Suite")
        print("=" * 50)

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration file."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            self.logger.info(f"Configuration loaded from {self.config_path}")
            return config
        except Exception as e:
            self.error_logger.error(f"Failed to load config: {e}")
            return {}

    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive real-time voice system test."""
        print("\n📊 Starting comprehensive real-time voice test...")
        
        try:
            # Initialize components
            await self._initialize_components()
            
            # Test 1: System startup and initialization
            print("\n🔧 Test 1: System Initialization")
            startup_results = await self._test_system_startup()
            
            # Test 2: Performance baseline
            print("\n⚡ Test 2: Performance Baseline")
            performance_results = await self._test_performance_baseline()
            
            # Test 3: Real-time responsiveness
            print("\n🎯 Test 3: Real-time Responsiveness")
            responsiveness_results = await self._test_real_time_responsiveness()
            
            # Test 4: Multi-threading stability
            print("\n🧵 Test 4: Multi-threading Stability")
            threading_results = await self._test_multi_threading_stability()
            
            # Test 5: Voice command processing
            print("\n🎤 Test 5: Voice Command Processing")
            command_results = await self._test_voice_command_processing()
            
            # Test 6: End-to-end latency
            print("\n⏱️ Test 6: End-to-End Latency")
            latency_results = await self._test_end_to_end_latency()
            
            # Compile results
            results = {
                'timestamp': datetime.now().isoformat(),
                'startup': startup_results,
                'performance': performance_results,
                'responsiveness': responsiveness_results,
                'threading': threading_results,
                'commands': command_results,
                'latency': latency_results,
                'summary': {}
            }
            
            # Generate summary
            summary = self._generate_summary(results)
            results['summary'] = summary
            
            # Save results
            self._save_results(results)
            
            # Display summary
            self._display_summary(results)
            
            return results
            
        except Exception as e:
            self.error_logger.error(f"Comprehensive test failed: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}
        
        finally:
            # Cleanup
            if self.voice_system:
                await self.voice_system.stop()

    async def _initialize_components(self):
        """Initialize voice system and LLM connector."""
        try:
            print("🔧 Initializing components...")
            
            # Initialize LLM connector
            self.llm_connector = HybridLLMConnector(self.config)
            llm_success = await self.llm_connector.start()
            
            if not llm_success:
                print("❌ Failed to initialize LLM connector")
                return False
            
            # Initialize voice system
            self.voice_system = RealTimeVoiceSystem(self.config)
            
            # Set LLM processor
            self.voice_system.set_llm_processor(self._process_with_llm)
            
            print("✅ Components initialized successfully")
            return True
            
        except Exception as e:
            self.error_logger.error(f"Component initialization failed: {e}")
            return False

    async def _process_with_llm(self, text: str) -> Dict[str, Any]:
        """Process text with LLM (for voice system)."""
        try:
            response = await self.llm_connector.send_prompt(
                text,
                task_type='voice_command',
                max_tokens=100
            )
            return response
        except Exception as e:
            self.error_logger.error(f"LLM processing error: {e}")
            return {'content': 'Sorry, I could not process that request.'}

    async def _test_system_startup(self) -> Dict[str, Any]:
        """Test system startup and initialization."""
        try:
            print("  Testing system startup...")
            
            start_time = time.time()
            
            # Start voice system
            success = await self.voice_system.start()
            startup_time = time.time() - start_time
            
            if not success:
                return {'success': False, 'error': 'Failed to start voice system'}
            
            # Check thread status
            status = self.voice_system.get_status()
            active_threads = sum(1 for is_alive in status['threads'].values() if is_alive)
            
            return {
                'success': True,
                'startup_time': startup_time,
                'active_threads': active_threads,
                'total_threads': len(status['threads']),
                'thread_status': status['threads']
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _test_performance_baseline(self) -> Dict[str, Any]:
        """Test performance baseline metrics."""
        try:
            print("  Testing performance baseline...")
            
            # Wait for system to stabilize
            await asyncio.sleep(5)
            
            # Get initial metrics
            initial_metrics = self.voice_system.get_performance_metrics()
            
            # Run for 30 seconds to establish baseline
            print("  Running 30-second baseline test...")
            await asyncio.sleep(30)
            
            # Get final metrics
            final_metrics = self.voice_system.get_performance_metrics()
            
            return {
                'initial_metrics': initial_metrics,
                'final_metrics': final_metrics,
                'throughput': final_metrics['throughput'],
                'latency': final_metrics['latency']
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _test_real_time_responsiveness(self) -> Dict[str, Any]:
        """Test real-time responsiveness."""
        try:
            print("  Testing real-time responsiveness...")
            
            # Test queue processing speeds
            queue_tests = []
            
            for i in range(5):
                start_time = time.time()
                
                # Simulate audio input
                status = self.voice_system.get_status()
                queue_size_before = status['queue_sizes']['audio']
                
                # Wait a bit
                await asyncio.sleep(1)
                
                status = self.voice_system.get_status()
                queue_size_after = status['queue_sizes']['audio']
                
                processing_time = time.time() - start_time
                queue_processed = queue_size_before - queue_size_after
                
                queue_tests.append({
                    'test_number': i + 1,
                    'processing_time': processing_time,
                    'queue_processed': queue_processed,
                    'processing_rate': queue_processed / processing_time if processing_time > 0 else 0
                })
            
            return {
                'queue_tests': queue_tests,
                'avg_processing_rate': sum(t['processing_rate'] for t in queue_tests) / len(queue_tests)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _test_multi_threading_stability(self) -> Dict[str, Any]:
        """Test multi-threading stability."""
        try:
            print("  Testing multi-threading stability...")
            
            # Monitor thread health for 60 seconds
            thread_health = []
            
            for i in range(12):  # 12 checks over 60 seconds
                status = self.voice_system.get_status()
                
                thread_health.append({
                    'timestamp': time.time(),
                    'active_threads': sum(1 for is_alive in status['threads'].values() if is_alive),
                    'total_threads': len(status['threads']),
                    'queue_sizes': status['queue_sizes']
                })
                
                await asyncio.sleep(5)
            
            # Analyze stability
            active_thread_counts = [h['active_threads'] for h in thread_health]
            avg_active_threads = sum(active_thread_counts) / len(active_thread_counts)
            thread_stability = min(active_thread_counts) == max(active_thread_counts)
            
            return {
                'thread_health': thread_health,
                'avg_active_threads': avg_active_threads,
                'thread_stability': thread_stability,
                'min_active_threads': min(active_thread_counts),
                'max_active_threads': max(active_thread_counts)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _test_voice_command_processing(self) -> Dict[str, Any]:
        """Test voice command processing."""
        try:
            print("  Testing voice command processing...")
            
            # Note: This is a simulation since we can't actually speak
            # In a real test, you would speak commands
            
            test_commands = [
                "Hello Nova",
                "What time is it",
                "Open main.py",
                "Create a new function",
                "Run the tests"
            ]
            
            command_results = []
            
            for command in test_commands:
                start_time = time.time()
                
                # Simulate command processing
                response = await self._process_with_llm(command)
                
                processing_time = time.time() - start_time
                
                command_results.append({
                    'command': command,
                    'processing_time': processing_time,
                    'response_length': len(response.get('content', '')),
                    'success': response.get('success', False)
                })
            
            return {
                'commands_tested': len(test_commands),
                'command_results': command_results,
                'avg_processing_time': sum(r['processing_time'] for r in command_results) / len(command_results),
                'success_rate': sum(1 for r in command_results if r['success']) / len(command_results)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _test_end_to_end_latency(self) -> Dict[str, Any]:
        """Test end-to-end latency."""
        try:
            print("  Testing end-to-end latency...")
            
            # Get current performance metrics
            metrics = self.voice_system.get_performance_metrics()
            
            # Calculate end-to-end latency
            total_latency = (
                metrics['latency']['avg_transcription_latency'] +
                metrics['latency']['avg_llm_latency'] +
                metrics['latency']['avg_tts_latency']
            )
            
            # Latency benchmarks
            latency_benchmarks = {
                'excellent': 1.0,  # < 1 second
                'good': 2.0,       # < 2 seconds
                'acceptable': 3.0,  # < 3 seconds
                'poor': 5.0        # > 5 seconds
            }
            
            # Determine latency rating
            if total_latency < latency_benchmarks['excellent']:
                rating = 'excellent'
            elif total_latency < latency_benchmarks['good']:
                rating = 'good'
            elif total_latency < latency_benchmarks['acceptable']:
                rating = 'acceptable'
            else:
                rating = 'poor'
            
            return {
                'total_latency': total_latency,
                'component_latencies': metrics['latency'],
                'rating': rating,
                'benchmarks': latency_benchmarks,
                'throughput': metrics['throughput']
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test summary."""
        try:
            summary = {
                'overall_success': True,
                'key_metrics': {},
                'recommendations': []
            }
            
            # Check startup
            if not results.get('startup', {}).get('success', False):
                summary['overall_success'] = False
                summary['recommendations'].append("System startup failed - check configuration")
            
            # Performance metrics
            performance = results.get('performance', {})
            if 'final_metrics' in performance:
                final_metrics = performance['final_metrics']
                summary['key_metrics']['throughput'] = final_metrics['throughput']
                summary['key_metrics']['latency'] = final_metrics['latency']
            
            # Threading stability
            threading = results.get('threading', {})
            if threading.get('thread_stability', False):
                summary['key_metrics']['threading'] = 'stable'
            else:
                summary['key_metrics']['threading'] = 'unstable'
                summary['recommendations'].append("Threading instability detected")
            
            # Command processing
            commands = results.get('commands', {})
            success_rate = commands.get('success_rate', 0)
            summary['key_metrics']['command_success_rate'] = f"{success_rate:.1%}"
            
            if success_rate < 0.8:
                summary['recommendations'].append("Low command success rate - improve LLM processing")
            
            # Latency rating
            latency = results.get('latency', {})
            rating = latency.get('rating', 'unknown')
            summary['key_metrics']['latency_rating'] = rating
            
            if rating in ['poor', 'acceptable']:
                summary['recommendations'].append(f"Latency is {rating} - optimize pipeline")
            
            return summary
            
        except Exception as e:
            return {'error': str(e)}

    def _save_results(self, results: Dict[str, Any]):
        """Save test results to file."""
        try:
            filename = f"realtime_voice_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"💾 Results saved to: {filename}")
            
        except Exception as e:
            self.error_logger.error(f"Failed to save results: {e}")

    def _display_summary(self, results: Dict[str, Any]):
        """Display test summary."""
        print("\n" + "="*70)
        print("📊 REAL-TIME VOICE SYSTEM TEST SUMMARY")
        print("="*70)
        
        summary = results.get('summary', {})
        
        # Overall status
        status = "✅ PASSED" if summary.get('overall_success', False) else "❌ FAILED"
        print(f"Overall Status: {status}")
        
        # Key metrics
        print("\n📈 Key Metrics:")
        key_metrics = summary.get('key_metrics', {})
        
        if 'throughput' in key_metrics:
            throughput = key_metrics['throughput']
            print(f"  • Audio Chunks/sec: {throughput.get('audio_chunks_per_second', 0):.1f}")
            print(f"  • Transcriptions/sec: {throughput.get('transcriptions_per_second', 0):.1f}")
            print(f"  • Commands/sec: {throughput.get('commands_per_second', 0):.1f}")
        
        if 'latency' in key_metrics:
            latency = key_metrics['latency']
            print(f"  • Transcription Latency: {latency.get('avg_transcription_latency', 0):.3f}s")
            print(f"  • LLM Latency: {latency.get('avg_llm_latency', 0):.3f}s")
            print(f"  • TTS Latency: {latency.get('avg_tts_latency', 0):.3f}s")
            print(f"  • Total Pipeline: {latency.get('total_pipeline_latency', 0):.3f}s")
        
        print(f"  • Threading: {key_metrics.get('threading', 'unknown')}")
        print(f"  • Command Success Rate: {key_metrics.get('command_success_rate', 'unknown')}")
        print(f"  • Latency Rating: {key_metrics.get('latency_rating', 'unknown')}")
        
        # Recommendations
        recommendations = summary.get('recommendations', [])
        if recommendations:
            print("\n💡 Recommendations:")
            for rec in recommendations:
                print(f"  • {rec}")
        else:
            print("\n🎉 No issues detected - system is performing well!")
        
        print("\n" + "="*70)

async def main():
    """Main function to run the real-time voice test."""
    print("🚀 Starting Real-Time Voice System Test...")
    
    # Check if config file exists
    config_path = 'config/settings_hybrid.yaml'
    if not os.path.exists(config_path):
        print(f"❌ Configuration file not found: {config_path}")
        print("Please create the hybrid configuration file first.")
        return
    
    # Run real-time voice test
    tester = RealTimeVoiceTester(config_path)
    results = await tester.run_comprehensive_test()
    
    if results.get('summary', {}).get('overall_success', False):
        print("\n✅ Real-time voice system test completed successfully!")
        print("🎯 Your system is ready for Alexa/Siri-like responsiveness!")
    else:
        print(f"\n❌ Real-time voice system test failed")
        print("Check the recommendations above for improvements.")

if __name__ == "__main__":
    import os
    asyncio.run(main()) 