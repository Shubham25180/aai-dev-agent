#!/usr/bin/env python3
"""
Hugging Face Speed Testing Script
Comprehensive speed testing for Hugging Face models with detailed metrics and reporting.
"""

import asyncio
import json
import time
import yaml
import os
from datetime import datetime
from typing import Dict, Any, List
from agents.huggingface_connector import HuggingFaceConnector
from utils.logger import get_action_logger, get_error_logger

class HuggingFaceSpeedTester:
    """
    Comprehensive speed tester for Hugging Face models.
    Tests different model sizes, quantization levels, and configurations.
    """
    
    def __init__(self, config_path: str = 'config/settings_huggingface.yaml'):
        self.logger = get_action_logger('hf_speed_tester')
        self.error_logger = get_error_logger('hf_speed_tester')
        self.config_path = config_path
        self.config = self._load_config()
        self.connector = None
        self.results = {}
        
        print("🚀 Hugging Face Speed Testing Suite")
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
        """Run comprehensive speed testing across all configurations."""
        print("\n📊 Starting comprehensive Hugging Face speed test...")
        
        try:
            # Initialize connector
            self.connector = HuggingFaceConnector(self.config)
            success = await self.connector.start()
            
            if not success:
                print("❌ Failed to initialize Hugging Face connector")
                return {'success': False, 'error': 'Connector initialization failed'}
            
            print("✅ Hugging Face connector initialized successfully")
            
            # Get test configuration
            speed_config = self.config.get('speed_testing', {})
            test_models = speed_config.get('test_models', ['fast', 'balanced', 'quality', 'code'])
            test_prompts = speed_config.get('test_prompts', [
                "Hello, how are you?",
                "What is the weather like?",
                "Can you help me with coding?",
                "Explain machine learning briefly.",
                "Write a simple Python function."
            ])
            
            # Run speed test
            print(f"\n🧪 Testing {len(test_models)} models with {len(test_prompts)} prompts each...")
            results = await self.connector.run_speed_test(test_prompts, test_models)
            
            if results.get('success') is False:
                print(f"❌ Speed test failed: {results.get('error')}")
                return results
            
            # Generate detailed analysis
            analysis = self._analyze_results(results)
            
            # Save results
            if speed_config.get('save_results', True):
                self._save_results(results, analysis)
            
            # Generate report
            if speed_config.get('generate_report', True):
                self._generate_report(results, analysis)
            
            # Display summary
            self._display_summary(results, analysis)
            
            return {
                'success': True,
                'results': results,
                'analysis': analysis
            }
            
        except Exception as e:
            self.error_logger.error(f"Comprehensive test failed: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}
        
        finally:
            if self.connector:
                await self.connector.stop()

    def _analyze_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze speed test results and generate insights."""
        try:
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'model_rankings': {},
                'performance_insights': {},
                'recommendations': []
            }
            
            # Rank models by different metrics
            model_metrics = {}
            
            for model_type, model_results in results.get('results', {}).items():
                summary = model_results.get('summary', {})
                model_metrics[model_type] = {
                    'avg_response_time': summary.get('avg_response_time', float('inf')),
                    'avg_tokens_per_second': summary.get('avg_tokens_per_second', 0),
                    'avg_memory_usage_mb': summary.get('avg_memory_usage_mb', 0),
                    'total_tests': summary.get('total_tests', 0)
                }
            
            # Rank by speed (response time)
            speed_ranking = sorted(
                model_metrics.items(), 
                key=lambda x: x[1]['avg_response_time']
            )
            analysis['model_rankings']['by_speed'] = [
                {'model': model, 'response_time': metrics['avg_response_time']} 
                for model, metrics in speed_ranking
            ]
            
            # Rank by throughput (tokens per second)
            throughput_ranking = sorted(
                model_metrics.items(), 
                key=lambda x: x[1]['avg_tokens_per_second'], 
                reverse=True
            )
            analysis['model_rankings']['by_throughput'] = [
                {'model': model, 'tokens_per_second': metrics['avg_tokens_per_second']} 
                for model, metrics in throughput_ranking
            ]
            
            # Rank by memory efficiency
            memory_ranking = sorted(
                model_metrics.items(), 
                key=lambda x: x[1]['avg_memory_usage_mb']
            )
            analysis['model_rankings']['by_memory'] = [
                {'model': model, 'memory_usage_mb': metrics['avg_memory_usage_mb']} 
                for model, metrics in memory_ranking
            ]
            
            # Generate insights
            fastest_model = speed_ranking[0][0] if speed_ranking else None
            most_efficient_model = throughput_ranking[0][0] if throughput_ranking else None
            most_memory_efficient = memory_ranking[0][0] if memory_ranking else None
            
            analysis['performance_insights'] = {
                'fastest_model': fastest_model,
                'most_efficient_model': most_efficient_model,
                'most_memory_efficient': most_memory_efficient,
                'speed_range': {
                    'fastest': speed_ranking[0][1]['avg_response_time'] if speed_ranking else 0,
                    'slowest': speed_ranking[-1][1]['avg_response_time'] if speed_ranking else 0
                },
                'throughput_range': {
                    'highest': throughput_ranking[0][1]['avg_tokens_per_second'] if throughput_ranking else 0,
                    'lowest': throughput_ranking[-1][1]['avg_tokens_per_second'] if throughput_ranking else 0
                }
            }
            
            # Generate recommendations
            recommendations = []
            
            if fastest_model:
                recommendations.append(f"🏆 Fastest model: {fastest_model} - Use for real-time applications")
            
            if most_efficient_model and most_efficient_model != fastest_model:
                recommendations.append(f"⚡ Most efficient: {most_efficient_model} - Best tokens/second ratio")
            
            if most_memory_efficient and most_memory_efficient != fastest_model:
                recommendations.append(f"💾 Most memory efficient: {most_memory_efficient} - Best for limited RAM")
            
            # Check for significant differences
            if len(speed_ranking) > 1:
                fastest_time = speed_ranking[0][1]['avg_response_time']
                slowest_time = speed_ranking[-1][1]['avg_response_time']
                speed_ratio = slowest_time / fastest_time if fastest_time > 0 else 1
                
                if speed_ratio > 2:
                    recommendations.append(f"⚠️  Speed difference: {speed_ratio:.1f}x between fastest and slowest models")
            
            analysis['recommendations'] = recommendations
            
            return analysis
            
        except Exception as e:
            self.error_logger.error(f"Error analyzing results: {e}")
            return {'error': str(e)}

    def _save_results(self, results: Dict[str, Any], analysis: Dict[str, Any]):
        """Save test results to file."""
        try:
            speed_config = self.config.get('speed_testing', {})
            results_file = speed_config.get('results_file', 'speed_test_results.json')
            
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
            speed_config = self.config.get('speed_testing', {})
            report_format = speed_config.get('report_format', 'markdown')
            
            if report_format == 'markdown':
                self._generate_markdown_report(results, analysis)
            
        except Exception as e:
            self.error_logger.error(f"Failed to generate report: {e}")

    def _generate_markdown_report(self, results: Dict[str, Any], analysis: Dict[str, Any]):
        """Generate markdown report."""
        try:
            report_content = f"""# Hugging Face Speed Test Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Executive Summary

### Fastest Model
- **Model**: {analysis.get('performance_insights', {}).get('fastest_model', 'N/A')}
- **Response Time**: {analysis.get('model_rankings', {}).get('by_speed', [{}])[0].get('response_time', 0):.3f}s

### Most Efficient Model
- **Model**: {analysis.get('performance_insights', {}).get('most_efficient_model', 'N/A')}
- **Throughput**: {analysis.get('model_rankings', {}).get('by_throughput', [{}])[0].get('tokens_per_second', 0):.1f} tokens/sec

### Most Memory Efficient
- **Model**: {analysis.get('performance_insights', {}).get('most_memory_efficient', 'N/A')}
- **Memory Usage**: {analysis.get('model_rankings', {}).get('by_memory', [{}])[0].get('memory_usage_mb', 0):.1f} MB

## 🏆 Model Rankings

### By Speed (Response Time)
"""
            
            for i, ranking in enumerate(analysis.get('model_rankings', {}).get('by_speed', []), 1):
                report_content += f"{i}. **{ranking['model']}**: {ranking['response_time']:.3f}s\n"
            
            report_content += "\n### By Throughput (Tokens/Second)\n"
            
            for i, ranking in enumerate(analysis.get('model_rankings', {}).get('by_throughput', []), 1):
                report_content += f"{i}. **{ranking['model']}**: {ranking['tokens_per_second']:.1f} tokens/sec\n"
            
            report_content += "\n### By Memory Efficiency\n"
            
            for i, ranking in enumerate(analysis.get('model_rankings', {}).get('by_memory', []), 1):
                report_content += f"{i}. **{ranking['model']}**: {ranking['memory_usage_mb']:.1f} MB\n"
            
            report_content += "\n## 📈 Detailed Results\n\n"
            
            for model_type, model_results in results.get('results', {}).items():
                summary = model_results.get('summary', {})
                report_content += f"### {model_type.title()} Model\n"
                report_content += f"- **Average Response Time**: {summary.get('avg_response_time', 0):.3f}s\n"
                report_content += f"- **Average Throughput**: {summary.get('avg_tokens_per_second', 0):.1f} tokens/sec\n"
                report_content += f"- **Average Memory Usage**: {summary.get('avg_memory_usage_mb', 0):.1f} MB\n"
                report_content += f"- **Total Tests**: {summary.get('total_tests', 0)}\n\n"
            
            report_content += "## 💡 Recommendations\n\n"
            
            for recommendation in analysis.get('recommendations', []):
                report_content += f"- {recommendation}\n"
            
            report_content += "\n## ⚙️ Test Configuration\n\n"
            report_content += f"- **Test Models**: {', '.join(results.get('test_config', {}).get('models', []))}\n"
            report_content += f"- **Test Prompts**: {len(results.get('test_config', {}).get('prompts', []))} prompts\n"
            report_content += f"- **Total Tests**: {results.get('summary', {}).get('total_tests', 0)}\n"
            report_content += f"- **Cache Hit Rate**: {results.get('summary', {}).get('cache_hit_rate', 0):.1%}\n"
            
            # Save report
            with open('speed_test_report.md', 'w') as f:
                f.write(report_content)
            
            print("📄 Report generated: speed_test_report.md")
            
        except Exception as e:
            self.error_logger.error(f"Failed to generate markdown report: {e}")

    def _display_summary(self, results: Dict[str, Any], analysis: Dict[str, Any]):
        """Display test summary."""
        print("\n" + "="*60)
        print("📊 SPEED TEST SUMMARY")
        print("="*60)
        
        # Overall summary
        summary = results.get('summary', {})
        print(f"Total Tests: {summary.get('total_tests', 0)}")
        print(f"Average Response Time: {summary.get('avg_response_time', 0):.3f}s")
        print(f"Average Throughput: {summary.get('avg_tokens_per_second', 0):.1f} tokens/sec")
        print(f"Cache Hit Rate: {summary.get('cache_hit_rate', 0):.1%}")
        
        print("\n🏆 MODEL RANKINGS:")
        
        # Speed ranking
        print("\nBy Speed (Response Time):")
        for i, ranking in enumerate(analysis.get('model_rankings', {}).get('by_speed', [])[:3], 1):
            print(f"  {i}. {ranking['model']}: {ranking['response_time']:.3f}s")
        
        # Throughput ranking
        print("\nBy Throughput (Tokens/Second):")
        for i, ranking in enumerate(analysis.get('model_rankings', {}).get('by_throughput', [])[:3], 1):
            print(f"  {i}. {ranking['model']}: {ranking['tokens_per_second']:.1f} tokens/sec")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        for recommendation in analysis.get('recommendations', []):
            print(f"  • {recommendation}")
        
        print("\n" + "="*60)

async def main():
    """Main function to run the speed test."""
    print("🚀 Starting Hugging Face Speed Testing...")
    
    # Check if config file exists
    config_path = 'config/settings_huggingface.yaml'
    if not os.path.exists(config_path):
        print(f"❌ Configuration file not found: {config_path}")
        print("Please create the configuration file first.")
        return
    
    # Run speed test
    tester = HuggingFaceSpeedTester(config_path)
    results = await tester.run_comprehensive_test()
    
    if results.get('success'):
        print("\n✅ Speed testing completed successfully!")
    else:
        print(f"\n❌ Speed testing failed: {results.get('error')}")

if __name__ == "__main__":
    asyncio.run(main()) 