#!/usr/bin/env python3
"""
Transcript Processor

Handles post-processing of speech transcripts to improve accuracy,
fix common misrecognitions, and enhance transcription quality.
"""

import re
from typing import Dict, List, Tuple, Optional
import json
import os


class TranscriptProcessor:
    """
    Advanced transcript processing with configurable corrections,
    context awareness, and extensible enhancement pipeline.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the transcript processor.
        
        Args:
            config_file: Optional path to JSON config file with corrections
        """
        self.corrections = self._load_default_corrections()
        self.context_rules = self._load_context_rules()
        self.enhancement_pipeline = []
        
        # Load custom config if provided
        if config_file and os.path.exists(config_file):
            self._load_config(config_file)
    
    def _load_default_corrections(self) -> Dict[str, str]:
        """Load default correction mappings."""
        return {
            # NEXUS-specific corrections
            "next us": "nexus",
            "next is": "nexus", 
            "next as": "nexus",
            "next has": "nexus",
            "next was": "nexus",
            "next this": "nexus",
            "next that": "nexus",
            "next the": "nexus",
            "next a": "nexus",
            "next an": "nexus",
            "next in": "nexus",
            "next on": "nexus",
            "next at": "nexus",
            "next to": "nexus",
            "next for": "nexus",
            "next with": "nexus",
            "next by": "nexus",
            "next from": "nexus",
            "next of": "nexus",
            "next and": "nexus",
            "next or": "nexus",
            "next but": "nexus",
            "next if": "nexus",
            "next when": "nexus",
            "next where": "nexus",
            "next why": "nexus",
            "next how": "nexus",
            "next what": "nexus",
            "next who": "nexus",
            "next which": "nexus",
            "next whose": "nexus",
            "next whom": "nexus",
            
            # Common programming terms
            "git hub": "github",
            "git lab": "gitlab",
            "stack overflow": "stackoverflow",
            "pull request": "pull request",
            "code review": "code review",
            "unit test": "unit test",
            "integration test": "integration test",
            
            # Common tech terms
            "api": "API",
            "url": "URL",
            "http": "HTTP",
            "https": "HTTPS",
            "json": "JSON",
            "xml": "XML",
            "html": "HTML",
            "css": "CSS",
            "js": "JavaScript",
            "python": "Python",
            "java": "Java",
            "javascript": "JavaScript",
            
            # Punctuation and formatting
            "period": ".",
            "comma": ",",
            "question mark": "?",
            "exclamation mark": "!",
            "semicolon": ";",
            "colon": ":",
        }
    
    def _load_context_rules(self) -> List[Dict]:
        """Load context-aware correction rules."""
        return [
            {
                "context": "programming",
                "keywords": ["code", "function", "class", "variable", "debug", "test"],
                "corrections": {
                    "console log": "console.log",
                    "print statement": "print()",
                    "if statement": "if statement",
                    "for loop": "for loop",
                    "while loop": "while loop",
                }
            },
            {
                "context": "file_operations",
                "keywords": ["file", "folder", "directory", "save", "open", "create"],
                "corrections": {
                    "file path": "filepath",
                    "file name": "filename",
                    "file extension": "file extension",
                }
            }
        ]
    
    def _load_config(self, config_file: str):
        """Load custom configuration from JSON file."""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            if 'corrections' in config:
                self.corrections.update(config['corrections'])
            
            if 'context_rules' in config:
                self.context_rules.extend(config['context_rules'])
                
        except Exception as e:
            print(f"[TranscriptProcessor] Warning: Could not load config {config_file}: {e}")
    
    def add_correction(self, wrong: str, right: str):
        """Add a new correction rule."""
        self.corrections[wrong.lower()] = right
    
    def add_enhancement(self, enhancement_func):
        """Add a custom enhancement function to the pipeline."""
        self.enhancement_pipeline.append(enhancement_func)
    
    def process(self, transcript: str) -> str:
        """
        Process a transcript through the full enhancement pipeline.
        
        Args:
            transcript: Raw transcript from speech recognition
            
        Returns:
            Enhanced and corrected transcript
        """
        if not transcript:
            return transcript
        
        # Step 1: Basic corrections
        processed = self._apply_corrections(transcript)
        
        # Step 2: Context-aware corrections
        processed = self._apply_context_corrections(processed)
        
        # Step 3: Custom enhancements
        processed = self._apply_enhancements(processed)
        
        # Step 4: Final cleanup
        processed = self._cleanup(processed)
        
        return processed
    
    def _apply_corrections(self, transcript: str) -> str:
        """Apply basic correction mappings."""
        corrected = transcript.lower()
        
        # Sort corrections by length (longest first) to avoid partial matches
        sorted_corrections = sorted(self.corrections.items(), 
                                  key=lambda x: len(x[0]), reverse=True)
        
        for wrong, right in sorted_corrections:
            corrected = corrected.replace(wrong, right)
        
        # Preserve original case structure
        return self._preserve_case(transcript, corrected)
    
    def _apply_context_corrections(self, transcript: str) -> str:
        """Apply context-aware corrections."""
        words = transcript.lower().split()
        
        for rule in self.context_rules:
            # Check if context keywords are present
            context_keywords = rule.get('keywords', [])
            if any(keyword in words for keyword in context_keywords):
                # Apply context-specific corrections
                corrections = rule.get('corrections', {})
                for wrong, right in corrections.items():
                    transcript = transcript.replace(wrong, right)
        
        return transcript
    
    def _apply_enhancements(self, transcript: str) -> str:
        """Apply custom enhancement functions."""
        processed = transcript
        
        for enhancement_func in self.enhancement_pipeline:
            try:
                processed = enhancement_func(processed)
            except Exception as e:
                print(f"[TranscriptProcessor] Enhancement error: {e}")
        
        return processed
    
    def _preserve_case(self, original: str, corrected: str) -> str:
        """Preserve original capitalization while applying corrections."""
        original_words = original.split()
        corrected_words = corrected.split()
        
        final_words = []
        for i, word in enumerate(original_words):
            if i < len(corrected_words):
                # If the corrected word is different, use it with original case
                if word.lower() != corrected_words[i]:
                    # Try to preserve original case pattern
                    if word.isupper():
                        final_words.append(corrected_words[i].upper())
                    elif word.istitle():
                        final_words.append(corrected_words[i].title())
                    else:
                        final_words.append(corrected_words[i])
                else:
                    final_words.append(word)
            else:
                final_words.append(word)
        
        return " ".join(final_words)
    
    def _cleanup(self, transcript: str) -> str:
        """Final cleanup and formatting."""
        # Remove extra whitespace
        transcript = re.sub(r'\s+', ' ', transcript).strip()
        
        # Fix common punctuation issues
        transcript = re.sub(r'\s+([.,!?;:])', r'\1', transcript)
        
        # Ensure proper sentence capitalization
        sentences = re.split(r'([.!?]+)', transcript)
        processed_sentences = []
        
        for i, sentence in enumerate(sentences):
            if i % 2 == 0:  # Actual sentence content
                if sentence.strip():
                    processed_sentences.append(sentence.strip().capitalize())
                else:
                    processed_sentences.append(sentence)
            else:  # Punctuation
                processed_sentences.append(sentence)
        
        return ''.join(processed_sentences)
    
    def export_config(self, filename: str):
        """Export current configuration to JSON file."""
        config = {
            'corrections': self.corrections,
            'context_rules': self.context_rules
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"[TranscriptProcessor] Configuration exported to {filename}")
        except Exception as e:
            print(f"[TranscriptProcessor] Export error: {e}")


# Convenience function for backward compatibility
def process_transcript(transcript: str) -> str:
    """Simple function to process a transcript with default settings."""
    processor = TranscriptProcessor()
    return processor.process(transcript) 