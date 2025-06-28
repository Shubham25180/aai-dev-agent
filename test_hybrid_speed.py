#!/usr/bin/env python3
"""
Hybrid Speed Testing - Ollama vs Hugging Face Comparison
Tests both backends while preserving coding capabilities.
"""

import asyncio
import json
import time
import yaml
import os
from datetime import datetime
from typing import Dict, Any, List
from agents.hybrid_llm_connector import HybridLLMConnector
from utils.logger import get_action_logger, get_error_logger

class HybridSpeedTester:
    """
    Hybrid speed tester that compares Ollama and Hugging Face
    while preserving the best of both worlds.
    """
    
    def __init__(self, config_path: str = 'config/settings_hybrid.yaml'):
        self.logger = get_action_logger('hybrid_speed_tester')
        self.error_logger = get_error_logger('hybrid_speed_tester')
        self.config_path = config_path
        self.config = self._load_config()
        self.connector = None
        self.results = {}
        
        print("🚀 Hybrid Speed Testing Suite - Ollama vs Hugging Face")
        print("=" * 60)

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
        """Run comprehensive speed testing with hybrid routing."""
        print("\n📊 Starting comprehensive hybrid speed test...")
        
        try:
            # Initialize hybrid connector
            self.connector = HybridLLMConnector(self.config)
            success = await self.connector.start()
            
            if not success:
                print("❌ Failed to initialize hybrid connector")
                return {'success': False, 'error': 'Connector initialization failed'}
            
            print("✅ Hybrid connector initialized successfully")
            
            # Test 1: Direct backend comparison
            print("\n🔍 Test 1: Direct Backend Comparison")
            comparison_results = await self.connector.run_speed_comparison()
            
            # Test 2: Intelligent routing test
            print("\n🧠 Test 2: Intelligent Routing Test")
            routing_results = await self._test_intelligent_routing()
            
            # Test 3: Coding task performance
            print("\n💻 Test 3: Coding Task Performance")
            coding_results = await self._test_coding_tasks()
            
            # Test 4: Simple task performance
            print("\n⚡ Test 4: Simple Task Performance")
            simple_results = await self._test_simple_tasks()
            
            # Compile results
            results = {
                'timestamp': datetime.now().isoformat(),
                'direct_comparison': comparison_results,
                'intelligent_routing': routing_results,
                'coding_tasks': coding_results,
                'simple_tasks': simple_results,
                'performance_metrics': self.connector.get_performance_metrics()
            }
            
            # Generate analysis
            analysis = self._analyze_hybrid_results(results)
            
            # Save results
            speed_config = self.config.get('speed_testing', {})
            if speed_config.get('save_results', True):
                self._save_results(results, analysis)
            
            # Generate report
            if speed_config.get('generate_report', True):
                self._generate_report(results, analysis)
            
            # Display summary
            self._display_hybrid_summary(results, analysis)
            
            return {
                'success': True,
                'results': results,
                'analysis': analysis
            }
            
        except Exception as e:
            self.error_logger.error(f"Hybrid test failed: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}
        
        finally:
            if self.connector:
                await self.connector.stop()

    async def _test_intelligent_routing(self) -> Dict[str, Any]:
        """Test intelligent routing between backends."""
        try:
            test_cases = [
                {
                    'prompt': "Hello, how are you?",
                    'expected_backend': 'huggingface',
                    'task_type': 'simple_qa'
                },
                {
                    'prompt': "Write a Python function to calculate factorial",
                    'expected_backend': 'ollama',
                    'task_type': 'coding'
                },
                {
                    'prompt': "What is the weather like?",
                    'expected_backend': 'huggingface',
                    'task_type': 'simple_qa'
                },
                {
                    'prompt': "Debug this code: print('Hello World'",
                    'expected_backend': 'ollama',
                    'task_type': 'coding'
                },
                {
                    'prompt': "Explain machine learning briefly",
                    'expected_backend': 'huggingface',
                    'task_type': 'simple_qa'
                }
            ]
            
            results = {
                'test_cases': [],
                'routing_accuracy': 0,
                'total_tests': len(test_cases)
            }
            
            correct_routes = 0
            
            for i, test_case in enumerate(test_cases):
                print(f"  Testing case {i+1}: {test_case['prompt'][:50]}...")
                
                start_time = time.time()
                response = await self.connector.send_prompt(
                    test_case['prompt'],
                    task_type=test_case['task_type']
                )
                response_time = time.time() - start_time
                
                actual_backend = response.get('routing_info', {}).get('backend_used', 'unknown')
                routing_reason = response.get('routing_info', {}).get('routing_reason', 'unknown')
                
                is_correct = actual_backend == test_case['expected_backend']
                if is_correct:
                    correct_routes += 1
                
                results['test_cases'].append({
                    'prompt': test_case['prompt'],
                    'expected_backend': test_case['expected_backend'],
                    'actual_backend': actual_backend,
                    'routing_reason': routing_reason,
                    'response_time': response_time,
                    'is_correct': is_correct,
                    'success': response.get('success', False)
                })
                
                print(f"    Expected: {test_case['expected_backend']}, Got: {actual_backend}, Time: {response_time:.3f}s")
            
            results['routing_accuracy'] = correct_routes / len(test_cases)
            print(f"  Routing Accuracy: {results['routing_accuracy']:.1%}")
            
            return results
            
        except Exception as e:
            self.error_logger.error(f"Intelligent routing test failed: {e}")
            return {'error': str(e)}

    async def _test_coding_tasks(self) -> Dict[str, Any]:
        """Test coding task performance with Ollama."""
        try:
            coding_prompts = [
                "Write a Python function to reverse a string",
                "Create a class for a simple calculator",
                "Debug this code: for i in range(10): print(i",
                "Write a function to find the maximum element in a list",
                "Create a simple REST API endpoint in Python"
            ]
            
            results = {
                'prompts': [],
                'total_time': 0,
                'success_rate': 0
            }
            
            successful_tests = 0
            
            for i, prompt in enumerate(coding_prompts):
                print(f"  Coding test {i+1}: {prompt[:50]}...")
                
                start_time = time.time()
                response = await self.connector.send_prompt(
                    prompt,
                    force_backend='ollama',  # Force Ollama for coding
                    temperature=0.3,
                    max_tokens=200
                )
                response_time = time.time() - start_time
                
                results['total_time'] += response_time
                
                if response.get('success'):
                    successful_tests += 1
                
                results['prompts'].append({
                    'prompt': prompt,
                    'response_time': response_time,
                    'success': response.get('success', False),
                    'content_length': len(response.get('content', '')),
                    'backend_used': response.get('routing_info', {}).get('backend_used', 'unknown')
                })
                
                print(f"    Time: {response_time:.3f}s, Success: {response.get('success', False)}")
            
            results['success_rate'] = successful_tests / len(coding_prompts)
            results['avg_time'] = results['total_time'] / len(coding_prompts)
            
            print(f"  Coding Tasks - Avg Time: {results['avg_time']:.3f}s, Success Rate: {results['success_rate']:.1%}")
            
            return results
            
        except Exception as e:
            self.error_logger.error(f"Coding tasks test failed: {e}")
            return {'error': str(e)}

    async def _test_simple_tasks(self) -> Dict[str, Any]:
        """Test simple task performance with Hugging Face."""
        try:
            simple_prompts = [
                "Hello, how are you?",
                "What is the weather like?",
                "Tell me a joke",
                "What time is it?",
                "How are you doing?"
            ]
            
            results = {
                'prompts': [],
                'total_time': 0,
                'success_rate': 0
            }
            
            successful_tests = 0
            
            for i, prompt in enumerate(simple_prompts):
                print(f"  Simple test {i+1}: {prompt[:50]}...")
                
                start_time = time.time()
                response = await self.connector.send_prompt(
                    prompt,
                    force_backend='huggingface',  # Force Hugging Face for speed
                    temperature=0.7,
                    max_tokens=50
                )
                response_time = time.time() - start_time
                
                results['total_time'] += response_time
                
                if response.get('success'):
                    successful_tests += 1
                
                results['prompts'].append({
                    'prompt': prompt,
                    'response_time': response_time,
                    'success': response.get('success', False),
                    'content_length': len(response.get('content', '')),
                    'backend_used': response.get('routing_info', {}).get('backend_used', 'unknown')
                })
                
                print(f"    Time: {response_time:.3f}s, Success: {response.get('success', False)}")
            
            results['success_rate'] = successful_tests / len(simple_prompts)
            results['avg_time'] = results['total_time'] / len(simple_prompts)
            
            print(f"  Simple Tasks - Avg Time: {results['avg_time']:.3f}s, Success Rate: {results['success_rate']:.1%}")
            
            return results
            
        except Exception as e:
            self.error_logger.error(f"Simple tasks test failed: {e}")
            return {'error': str(e)}

    def _analyze_hybrid_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze hybrid test results."""
        try:
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'key_findings': [],
                'recommendations': [],
                'performance_summary': {}
            }
            
            # Analyze direct comparison
            direct_comp = results.get('direct_comparison', {})
            if direct_comp.get('comparison'):
                comp = direct_comp['comparison']
                analysis['performance_summary']['direct_comparison'] = {
                    'ollama_avg_time': comp.get('ollama_avg_time', 0),
                    'hf_avg_time': comp.get('hf_avg_time', 0),
                    'speed_ratio': comp.get('speed_ratio', 0),
                    'faster_backend': comp.get('faster_backend', 'unknown')
                }
                
                if comp.get('faster_backend') == 'huggingface':
                    analysis['key_findings'].append("Hugging Face is faster for general tasks")
                else:
                    analysis['key_findings'].append("Ollama is faster for general tasks")
            
            # Analyze routing accuracy
            routing = results.get('intelligent_routing', {})
            routing_accuracy = routing.get('routing_accuracy', 0)
            analysis['performance_summary']['routing_accuracy'] = routing_accuracy
            
            if routing_accuracy >= 0.8:
                analysis['key_findings'].append("Excellent routing accuracy")
            elif routing_accuracy >= 0.6:
                analysis['key_findings'].append("Good routing accuracy")
            else:
                analysis['key_findings'].append("Routing accuracy needs improvement")
            
            # Analyze coding tasks
            coding = results.get('coding_tasks', {})
            coding_avg_time = coding.get('avg_time', 0)
            coding_success_rate = coding.get('success_rate', 0)
            analysis['performance_summary']['coding_tasks'] = {
                'avg_time': coding_avg_time,
                'success_rate': coding_success_rate
            }
            
            if coding_success_rate >= 0.8:
                analysis['key_findings'].append("Excellent coding task success rate")
            else:
                analysis['key_findings'].append("Coding task success rate needs improvement")
            
            # Analyze simple tasks
            simple = results.get('simple_tasks', {})
            simple_avg_time = simple.get('avg_time', 0)
            simple_success_rate = simple.get('success_rate', 0)
            analysis['performance_summary']['simple_tasks'] = {
                'avg_time': simple_avg_time,
                'success_rate': simple_success_rate
            }
            
            if simple_avg_time < 0.5:
                analysis['key_findings'].append("Very fast simple task responses")
            elif simple_avg_time < 1.0:
                analysis['key_findings'].append("Good simple task response times")
            else:
                analysis['key_findings'].append("Simple task response times could be improved")
            
            # Generate recommendations
            if routing_accuracy < 0.8:
                analysis['recommendations'].append("Improve routing keywords for better accuracy")
            
            if coding_success_rate < 0.8:
                analysis['recommendations'].append("Ensure Ollama is properly configured for coding tasks")
            
            if simple_avg_time > 1.0:
                analysis['recommendations'].append("Consider using smaller Hugging Face models for faster responses")
            
            # Overall recommendation
            if coding_success_rate >= 0.8 and simple_avg_time < 0.5:
                analysis['recommendations'].append("Hybrid system is working optimally - keep current configuration")
            else:
                analysis['recommendations'].append("Consider tuning model configurations for better performance")
            
            return analysis
            
        except Exception as e:
            self.error_logger.error(f"Error analyzing hybrid results: {e}")
            return {'error': str(e)}

    def _save_results(self, results: Dict[str, Any], analysis: Dict[str, Any]):
        """Save test results to file."""
        try:
            speed_config = self.config.get('speed_testing', {})
            results_file = speed_config.get('results_file', 'hybrid_speed_test_results.json')
            
            output_data = {
                'test_results': results,
                'analysis': analysis,
                'config_used': self.config.get('llm', {}),
                'timestamp': datetime.now().isoformat()
            }
            
            with open(results_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            print(f"💾 Results saved to: {results_file}")
            
        except Exception as e:
            self.error_logger.error(f"Failed to save results: {e}")

    def _generate_report(self, results: Dict[str, Any], analysis: Dict[str, Any]):
        """Generate markdown report."""
        try:
            report_content = f"""# Hybrid Speed Test Report - Ollama vs Hugging Face

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Executive Summary

### Routing Accuracy
- **Accuracy**: {analysis.get('performance_summary', {}).get('routing_accuracy', 0):.1%}
- **Status**: {'✅ Excellent' if analysis.get('performance_summary', {}).get('routing_accuracy', 0) >= 0.8 else '⚠️ Needs Improvement'}

### Performance Comparison

#### Direct Backend Comparison
"""
            
            direct_comp = analysis.get('performance_summary', {}).get('direct_comparison', {})
            if direct_comp:
                report_content += f"- **Ollama Average Time**: {direct_comp.get('ollama_avg_time', 0):.3f}s\n"
                report_content += f"- **Hugging Face Average Time**: {direct_comp.get('hf_avg_time', 0):.3f}s\n"
                report_content += f"- **Speed Ratio**: {direct_comp.get('speed_ratio', 0):.2f}x\n"
                report_content += f"- **Faster Backend**: {direct_comp.get('faster_backend', 'unknown').title()}\n"
            
            report_content += "\n#### Task-Specific Performance\n"
            
            coding_perf = analysis.get('performance_summary', {}).get('coding_tasks', {})
            if coding_perf:
                report_content += f"- **Coding Tasks (Ollama)**: {coding_perf.get('avg_time', 0):.3f}s avg, {coding_perf.get('success_rate', 0):.1%} success rate\n"
            
            simple_perf = analysis.get('performance_summary', {}).get('simple_tasks', {})
            if simple_perf:
                report_content += f"- **Simple Tasks (HF)**: {simple_perf.get('avg_time', 0):.3f}s avg, {simple_perf.get('success_rate', 0):.1%} success rate\n"
            
            report_content += "\n## 🔍 Key Findings\n\n"
            
            for finding in analysis.get('key_findings', []):
                report_content += f"- {finding}\n"
            
            report_content += "\n## 💡 Recommendations\n\n"
            
            for recommendation in analysis.get('recommendations', []):
                report_content += f"- {recommendation}\n"
            
            report_content += "\n## 🎯 Benefits of Hybrid Approach\n\n"
            report_content += "- **Coding Excellence**: Ollama handles complex coding tasks\n"
            report_content += "- **Speed Optimization**: Hugging Face for quick responses\n"
            report_content += "- **Intelligent Routing**: Automatic backend selection\n"
            report_content += "- **Fallback Support**: Both systems available as backup\n"
            
            # Save report
            with open('hybrid_speed_test_report.md', 'w') as f:
                f.write(report_content)
            
            print("📄 Report generated: hybrid_speed_test_report.md")
            
        except Exception as e:
            self.error_logger.error(f"Failed to generate report: {e}")

    def _display_hybrid_summary(self, results: Dict[str, Any], analysis: Dict[str, Any]):
        """Display hybrid test summary."""
        print("\n" + "="*70)
        print("📊 HYBRID SPEED TEST SUMMARY")
        print("="*70)
        
        # Routing accuracy
        routing_accuracy = analysis.get('performance_summary', {}).get('routing_accuracy', 0)
        print(f"🧠 Intelligent Routing Accuracy: {routing_accuracy:.1%}")
        
        # Direct comparison
        direct_comp = analysis.get('performance_summary', {}).get('direct_comparison', {})
        if direct_comp:
            print(f"\n⚡ Direct Comparison:")
            print(f"  Ollama: {direct_comp.get('ollama_avg_time', 0):.3f}s avg")
            print(f"  Hugging Face: {direct_comp.get('hf_avg_time', 0):.3f}s avg")
            print(f"  Faster: {direct_comp.get('faster_backend', 'unknown').title()}")
        
        # Task-specific performance
        coding_perf = analysis.get('performance_summary', {}).get('coding_tasks', {})
        if coding_perf:
            print(f"\n💻 Coding Tasks (Ollama):")
            print(f"  Average Time: {coding_perf.get('avg_time', 0):.3f}s")
            print(f"  Success Rate: {coding_perf.get('success_rate', 0):.1%}")
        
        simple_perf = analysis.get('performance_summary', {}).get('simple_tasks', {})
        if simple_perf:
            print(f"\n⚡ Simple Tasks (Hugging Face):")
            print(f"  Average Time: {simple_perf.get('avg_time', 0):.3f}s")
            print(f"  Success Rate: {simple_perf.get('success_rate', 0):.1%}")
        
        # Key findings
        print(f"\n🔍 Key Findings:")
        for finding in analysis.get('key_findings', []):
            print(f"  • {finding}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        for recommendation in analysis.get('recommendations', []):
            print(f"  • {recommendation}")
        
        print("\n" + "="*70)

async def main():
    """Main function to run the hybrid speed test."""
    print("🚀 Starting Hybrid Speed Testing...")
    
    # Check if config file exists
    config_path = 'config/settings_hybrid.yaml'
    if not os.path.exists(config_path):
        print(f"❌ Configuration file not found: {config_path}")
        print("Please create the hybrid configuration file first.")
        return
    
    # Run hybrid speed test
    tester = HybridSpeedTester(config_path)
    results = await tester.run_comprehensive_test()
    
    if results.get('success'):
        print("\n✅ Hybrid speed testing completed successfully!")
        print("🎯 Your coding capabilities are preserved while gaining speed testing!")
    else:
        print(f"\n❌ Hybrid speed testing failed: {results.get('error')}")

if __name__ == "__main__":
    asyncio.run(main()) 