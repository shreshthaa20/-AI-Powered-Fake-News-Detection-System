"""
Multilingual Processor Module
Handles text processing for multiple Indian languages
"""

import re
from typing import Dict, Optional

class MultilingualProcessor:
    """Processes and analyzes multilingual content"""
    
    def __init__(self):
        # Language code to name mapping
        self.language_names = {
            "en": "English",
            "hi": "Hindi",
            "bn": "Bengali",
            "ta": "Tamil",
            "te": "Telugu",
            "mr": "Marathi",
            "gu": "Gujarati",
            "kn": "Kannada",
            "ml": "Malayalam",
            "pa": "Punjabi",
            "ur": "Urdu"
        }
        
        # Script patterns for language detection
        self.script_patterns = {
            "hi": r'[\u0900-\u097F]',  # Devanagari
            "bn": r'[\u0980-\u09FF]',  # Bengali
            "ta": r'[\u0B80-\u0BFF]',  # Tamil
            "te": r'[\u0C00-\u0C7F]',  # Telugu
            "mr": r'[\u0900-\u097F]',  # Devanagari (similar to Hindi)
            "gu": r'[\u0A80-\u0AFF]',  # Gujarati
            "kn": r'[\u0C80-\u0CFF]',  # Kannada
            "ml": r'[\u0D00-\u0D7F]',  # Malayalam
            "pa": r'[\u0A00-\u0A7F]',  # Gurmukhi
            "ur": r'[\u0600-\u06FF]',  # Arabic script
        }
        
        # Common Hindi transliteration patterns
        self.hindi_transliteration = {
            "namaste": "नमस्ते",
            "dhanyavad": "धन्यवाद",
            "kaise": "कैसे",
            "acha": "अच्छा",
            "nahi": "नहीं"
        }
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the given text
        
        Args:
            text: Text to detect language for
            
        Returns:
            Language code
        """
        # Check for English patterns
        if self._is_english(text):
            return "en"
        
        # Check for Hindi (Devanagari)
        if re.search(self.script_patterns["hi"], text):
            # Check if it's actually Marathi
            if self._is_marathi(text):
                return "mr"
            return "hi"
        
        # Check for Bengali
        if re.search(self.script_patterns["bn"], text):
            return "bn"
        
        # Check for Tamil
        if re.search(self.script_patterns["ta"], text):
            return "ta"
        
        # Check for Telugu
        if re.search(self.script_patterns["te"], text):
            return "te"
        
        # Check for Gujarati
        if re.search(self.script_patterns["gu"], text):
            return "gu"
        
        # Check for Kannada
        if re.search(self.script_patterns["kn"], text):
            return "kn"
        
        # Check for Malayalam
        if re.search(self.script_patterns["ml"], text):
            return "ml"
        
        # Check for Punjabi (Gurmukhi)
        if re.search(self.script_patterns["pa"], text):
            return "pa"
        
        # Check for Urdu
        if re.search(self.script_patterns["ur"], text):
            return "ur"
        
        # Default to English
        return "en"
    
    def _is_english(self, text: str) -> bool:
        """Check if text is primarily English"""
        # Count ASCII characters
        ascii_count = sum(1 for c in text if ord(c) < 128)
        total_chars = len(text.replace(" ", ""))
        
        if total_chars == 0:
            return True
        
        return ascii_count / total_chars > 0.7
    
    def _is_marathi(self, text: str) -> bool:
        """Distinguish Marathi from Hindi"""
        # Marathi-specific characters
        marathi_chars = set(['ऱ', 'ऴ'])
        return any(char in marathi_chars for char in text)
    
    def process_text(self, text: str, language: str) -> Dict:
        """
        Process text for the specified language
        
        Args:
            text: Text to process
            language: Language code
            
        Returns:
            Processed text information
        """
        processed = {
            "original_text": text,
            "language": language,
            "language_name": self.language_names.get(language, "Unknown"),
            "character_count": len(text),
            "word_count": len(text.split()),
            "needs_transliteration": False,
            "processed_text": text
        }
        
        # Handle RTL languages
        if language in ["ur"]:
            processed["direction"] = "rtl"
        else:
            processed["direction"] = "ltr"
        
        # Check if transliteration is needed
        if language != "en" and self._is_english(text):
            processed["needs_transliteration"] = True
        
        return processed
    
    def translate_to_english(self, text: str, source_lang: str) -> str:
        """
        Translate text to English using googletrans
        
        Args:
            text: Text to translate
            source_lang: Source language code
            
        Returns:
            Translated text or original if translation fails
        """
        if source_lang == "en":
            return text
        
        try:
            from googletrans import Translator
            translator = Translator()
            result = translator.translate(text, src=source_lang, dest="en")
            return result.text if result and result.text else text
        except Exception as e:
            return f"[Translation failed ({source_lang}->en): {str(e)}] {text}"
    
    def get_supported_languages(self) -> Dict:
        """Get list of supported languages"""
        return {
            "languages": [
                {"code": code, "name": name}
                for code, name in self.language_names.items()
            ],
            "total": len(self.language_names)
        }
    
    def preprocess_for_analysis(self, text: str, language: str) -> str:
        """
        Preprocess text for analysis based on language
        
        Args:
            text: Text to preprocess
            language: Language code
            
        Returns:
            Preprocessed text
        """
        # Basic preprocessing
        processed = text
        
        # Remove extra whitespace
        processed = re.sub(r'\s+', ' ', processed)
        
        # Remove URLs (they can be analyzed separately)
        processed = re.sub(r'https?://\S+', '', processed)
        
        # Remove mentions and hashtags
        processed = re.sub(r'[@#]\w+', '', processed)
        
        # Normalize punctuation
        processed = processed.strip()
        
        return processed
