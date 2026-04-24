"""
Text Analyzer Module
Analyzes text content for fake news detection using NLP and ML techniques
"""

import re
import json
from typing import Dict, List, Optional
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except:
    pass

class TextAnalyzer:
    """Analyzes text content for misinformation patterns"""
    
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Known fake news indicators
        self.sensational_words = [
            'shocking', 'breaking', 'urgent', 'unbelievable', 'mind-blowing',
            'secret', 'exposed', 'conspiracy', 'cover-up', 'they don\'t want you to know',
            'miracle', 'instant', 'free', 'guaranteed', 'clickbait'
        ]
        
        # Credible source patterns
        self.credible_domains = [
            'reuters.com', 'apnews.com', 'bbc.com', 'ndtv.com',
            'thehindu.com', 'hindustantimes.com', 'indianexpress.com'
        ]
        
        # Load fake news patterns
        self.fake_news_patterns = self._load_fake_news_patterns()
        
        # Load BERT-based fake news classifier (lazy)
        self._classifier = None
    
    def _get_classifier(self):
        """Lazy-load transformer pipeline for fake news classification"""
        if self._classifier is None:
            try:
                from transformers import pipeline
                # Use a lightweight fake-news classifier
                self._classifier = pipeline(
                    "text-classification",
                    model="mrm8488/distilbert-base-finetuned-fake-news-detection",
                    tokenizer="mrm8488/distilbert-base-finetuned-fake-news-detection",
                    truncation=True,
                    max_length=512
                )
            except Exception as e:
                print(f"Could not load BERT classifier: {e}")
                self._classifier = False
        return self._classifier if self._classifier is not False else None
    
    def _load_fake_news_patterns(self) -> Dict:
        """Load known fake news patterns"""
        return {
            "clickbait_patterns": [
                r"you won't believe",
                r"what they don't tell you",
                r"shocking truth about",
                r"this one trick",
                r"doctors hate",
                r"make \d+ dollars"
            ],
            "emotional_triggers": [
                r"share before it's gone",
                r"your children are in danger",
                r"government conspiracy",
                r"religious tensions",
                r"communal violence"
            ],
            "unverified_sources": [
                r"anonymous sources say",
                r"according to sources",
                r"it is learned that",
                r"sources reveal"
            ]
        }
    
    def analyze(self, text: str, language: str = "en") -> Dict:
        """
        Perform comprehensive text analysis
        
        Args:
            text: Text content to analyze
            language: Language code
            
        Returns:
            Dictionary with analysis results
        """
        results = {
            "text_length": len(text),
            "word_count": len(text.split()),
            "sentence_count": len(sent_tokenize(text)),
            "language": language,
            "patterns_detected": [],
            "sentiment_analysis": {},
            "credibility_indicators": {},
            "ml_classification": {},
            "evidence": []
        }
        
        # 1. Check for clickbait patterns
        clickbait_score = self._detect_clickbait(text)
        results["patterns_detected"].append({
            "type": "clickbait",
            "score": clickbait_score,
            "details": "Clickbait and sensational language detection"
        })
        
        # 2. Analyze emotional triggers
        emotional_score = self._detect_emotional_triggers(text)
        results["patterns_detected"].append({
            "type": "emotional_manipulation",
            "score": emotional_score,
            "details": "Emotional manipulation indicators"
        })
        
        # 3. Check source credibility
        source_credibility = self._analyze_source_credibility(text)
        results["credibility_indicators"]["source"] = source_credibility
        
        # 4. Analyze text structure
        structure_analysis = self._analyze_text_structure(text)
        results["credibility_indicators"]["structure"] = structure_analysis
        
        # 5. Check for unverified claims
        unverified_score = self._detect_unverified_claims(text)
        results["patterns_detected"].append({
            "type": "unverified_claims",
            "score": unverified_score,
            "details": "Unverified or anonymous source usage"
        })
        
        # 6. BERT-based ML classification
        ml_result = self._ml_classify(text)
        results["ml_classification"] = ml_result
        
        # 7. Generate evidence
        results["evidence"] = self._generate_evidence(results)
        
        # 8. Calculate overall text score
        results["text_credibility_score"] = self._calculate_text_score(results)
        
        return results
    
    def _ml_classify(self, text: str) -> Dict:
        """Run BERT-based fake news classifier"""
        clf = self._get_classifier()
        if clf is None:
            return {"used": False, "reason": "Model not available"}
        
        try:
            # Truncate for safety
            input_text = text[:1500]
            pred = clf(input_text)[0]
            label = pred["label"]
            score = pred["score"]
            
            # Map to credibility: FAKE -> low score, REAL -> high score
            is_fake = label.upper() == "FAKE"
            credibility = 1.0 - score if is_fake else score
            
            return {
                "used": True,
                "label": label,
                "confidence": round(score, 4),
                "credibility_contribution": round(credibility, 4),
                "model": "distilbert-fake-news"
            }
        except Exception as e:
            return {"used": False, "error": str(e)}
    
    def _detect_clickbait(self, text: str) -> float:
        """Detect clickbait patterns in text"""
        text_lower = text.lower()
        clickbait_count = 0
        
        for pattern in self.fake_news_patterns["clickbait_patterns"]:
            if re.search(pattern, text_lower):
                clickbait_count += 1
        
        # Check for sensational words
        for word in self.sensational_words:
            if word in text_lower:
                clickbait_count += 1
        
        # Normalize score (0-1)
        return min(clickbait_count / 5.0, 1.0)
    
    def _detect_emotional_triggers(self, text: str) -> float:
        """Detect emotional manipulation triggers"""
        text_lower = text.lower()
        trigger_count = 0
        
        for pattern in self.fake_news_patterns["emotional_triggers"]:
            if re.search(pattern, text_lower):
                trigger_count += 1
        
        return min(trigger_count / 3.0, 1.0)
    
    def _analyze_source_credibility(self, text: str) -> Dict:
        """Analyze credibility of mentioned sources"""
        text_lower = text.lower()
        
        # Check for URL patterns
        urls = re.findall(r'https?://[^\s]+', text)
        
        credible_count = 0
        for url in urls:
            for domain in self.credible_domains:
                if domain in url:
                    credible_count += 1
        
        # Check for source attribution
        has_attribution = bool(re.search(r'according to|reported by|stated by', text_lower))
        
        return {
            "urls_found": len(urls),
            "credible_urls": credible_count,
            "has_attribution": has_attribution,
            "score": min(credible_count / max(len(urls), 1), 1.0) if urls else 0.5
        }
    
    def _analyze_text_structure(self, text: str) -> Dict:
        """Analyze structural elements of the text"""
        sentences = sent_tokenize(text)
        
        # Check for proper paragraph structure
        has_paragraphs = '\n\n' in text or len(text.split('\n')) > 1
        
        # Check for quote usage (indicates sourcing)
        has_quotes = bool(re.search(r'["\'].*["\']', text))
        
        # Check for statistics or data references
        has_statistics = bool(re.search(r'\d+%|\d+ percent|\d+ people|\d+ cases', text))
        
        return {
            "has_paragraphs": has_paragraphs,
            "has_quotes": has_quotes,
            "has_statistics": has_statistics,
            "avg_sentence_length": sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        }
    
    def _detect_unverified_claims(self, text: str) -> float:
        """Detect unverified or anonymous source claims"""
        text_lower = text.lower()
        unverified_count = 0
        
        for pattern in self.fake_news_patterns["unverified_sources"]:
            if re.search(pattern, text_lower):
                unverified_count += 1
        
        return min(unverified_count / 2.0, 1.0)
    
    def _generate_evidence(self, results: Dict) -> List[Dict]:
        """Generate evidence items for the analysis"""
        evidence = []
        
        # Add clickbait evidence
        for pattern in results.get("patterns_detected", []):
            if pattern["score"] > 0.3:
                evidence.append({
                    "type": pattern["type"],
                    "confidence": pattern["score"],
                    "description": f"Detected {pattern['type']} with {pattern['score']:.2f} confidence"
                })
        
        # Add source credibility evidence
        source = results.get("credibility_indicators", {}).get("source", {})
        if source.get("score", 0) > 0.5:
            evidence.append({
                "type": "credible_source",
                "confidence": source["score"],
                "description": f"Found {source.get('credible_urls', 0)} credible source(s)"
            })
        
        # Add ML evidence
        ml = results.get("ml_classification", {})
        if ml.get("used"):
            evidence.append({
                "type": "ml_classification",
                "confidence": ml["confidence"],
                "description": f"BERT model predicts '{ml['label']}' with {ml['confidence']:.2f} confidence"
            })
        
        return evidence
    
    def _calculate_text_score(self, results: Dict) -> float:
        """Calculate overall text credibility score"""
        scores = []
        weights = []
        
        # Weight different factors
        for pattern in results.get("patterns_detected", []):
            if pattern["type"] == "clickbait":
                scores.append(1 - pattern["score"])
                weights.append(1.0)
            elif pattern["type"] == "emotional_manipulation":
                scores.append(1 - pattern["score"])
                weights.append(1.0)
            elif pattern["type"] == "unverified_claims":
                scores.append(1 - pattern["score"])
                weights.append(1.0)
        
        # Add source credibility
        source = results.get("credibility_indicators", {}).get("source", {})
        if source:
            scores.append(source.get("score", 0.5))
            weights.append(1.5)
        
        # Add structure score
        structure = results.get("credibility_indicators", {}).get("structure", {})
        if structure:
            structure_score = 0.5
            if structure.get("has_quotes"):
                structure_score += 0.2
            if structure.get("has_statistics"):
                structure_score += 0.2
            if structure.get("has_paragraphs"):
                structure_score += 0.1
            scores.append(min(structure_score, 1.0))
            weights.append(1.0)
        
        # Incorporate ML classification if available
        ml = results.get("ml_classification", {})
        if ml.get("used"):
            scores.append(ml["credibility_contribution"])
            weights.append(2.0)  # Higher weight for ML model
        
        if scores:
            return sum(s * w for s, w in zip(scores, weights)) / sum(weights)
        return 0.5
    
    def verify_sources(self, text: str) -> Dict:
        """
        Verify sources mentioned in the text
        
        Args:
            text: Text content to verify
            
        Returns:
            Dictionary with source verification results
        """
        results = {
            "verified_sources": [],
            "unverified_sources": [],
            "evidence": []
        }
        
        # Extract URLs
        urls = re.findall(r'https?://[^\s]+', text)
        
        for url in urls:
            # Check against known credible sources
            is_credible = any(domain in url for domain in self.credible_domains)
            
            if is_credible:
                results["verified_sources"].append(url)
                results["evidence"].append({
                    "type": "verified_source",
                    "confidence": 0.9,
                    "description": f"Verified credible source: {url}"
                })
            else:
                results["unverified_sources"].append(url)
        
        return results
