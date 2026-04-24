"""
Credibility Scorer Module
Calculates overall credibility scores and provides classifications
"""

from typing import Dict, List, Optional

class CredibilityScorer:
    """Calculates credibility scores for analyzed content"""
    
    def __init__(self):
        self.classification_thresholds = {
            "highly_credible": 0.8,
            "credible": 0.6,
            "uncertain": 0.4,
            "questionable": 0.2,
            "likely_false": 0.0
        }
        
        self.weight_config = {
            "text": {
                "clickbait": 0.25,
                "emotional_manipulation": 0.20,
                "source_credibility": 0.30,
                "structure": 0.15,
                "unverified_claims": 0.10
            },
            "image": {
                "manipulation": 0.40,
                "metadata": 0.30,
                "stock_image": 0.20,
                "color_analysis": 0.10
            },
            "video": {
                "frame_inconsistency": 0.35,
                "visual_artifacts": 0.25,
                "deepfake_likelihood": 0.25,
                "audio_anomalies": 0.15
            }
        }
    
    def calculate_score(
        self,
        text_results: Optional[Dict] = None,
        image_results: Optional[Dict] = None,
        video_results: Optional[Dict] = None,
        source_results: Optional[Dict] = None,
        content_type: str = "text"
    ) -> float:
        """
        Calculate credibility score based on analysis results
        
        Args:
            text_results: Text analysis results
            image_results: Image analysis results
            video_results: Video analysis results
            source_results: Source verification results
            content_type: Type of content being analyzed
            
        Returns:
            Credibility score (0-1)
        """
        scores = []
        
        if content_type == "text" and text_results:
            text_score = self._calculate_text_score(text_results, source_results)
            scores.append(("text", text_score, 1.0))
        
        elif content_type == "image" and image_results:
            image_score = self._calculate_image_score(image_results)
            scores.append(("image", image_score, 1.0))
        
        elif content_type == "video" and video_results:
            video_score = self._calculate_video_score(video_results)
            scores.append(("video", video_score, 1.0))
        
        # Calculate weighted average
        if scores:
            total_weight = sum(weight for _, _, weight in scores)
            weighted_sum = sum(score * weight for _, score, weight in scores)
            return weighted_sum / total_weight if total_weight > 0 else 0.5
        
        return 0.5
    
    def _calculate_text_score(self, text_results: Dict, source_results: Optional[Dict]) -> float:
        """Calculate text-specific credibility score"""
        weights = self.weight_config["text"]
        score = 0.0
        
        # Get pattern scores
        patterns = text_results.get("patterns_detected", [])
        for pattern in patterns:
            pattern_type = pattern.get("type")
            if pattern_type == "clickbait":
                score += (1 - pattern["score"]) * weights["clickbait"]
            elif pattern_type == "emotional_manipulation":
                score += (1 - pattern["score"]) * weights["emotional_manipulation"]
            elif pattern_type == "unverified_claims":
                score += (1 - pattern["score"]) * weights["unverified_claims"]
        
        # Add source credibility
        source = text_results.get("credibility_indicators", {}).get("source", {})
        if source:
            score += source.get("score", 0.5) * weights["source_credibility"]
        
        # Add structure score
        structure = text_results.get("credibility_indicators", {}).get("structure", {})
        if structure:
            structure_score = 0.5
            if structure.get("has_quotes"):
                structure_score += 0.2
            if structure.get("has_statistics"):
                structure_score += 0.2
            if structure.get("has_paragraphs"):
                structure_score += 0.1
            score += min(structure_score, 1.0) * weights["structure"]
        
        # Add source verification if available
        if source_results:
            verified = len(source_results.get("verified_sources", []))
            unverified = len(source_results.get("unverified_sources", []))
            if verified + unverified > 0:
                source_verify_score = verified / (verified + unverified)
                score += source_verify_score * 0.15
        
        return max(0.0, min(1.0, score))
    
    def _calculate_image_score(self, image_results: Dict) -> float:
        """Calculate image-specific credibility score"""
        weights = self.weight_config["image"]
        score = 0.0
        
        # Add manipulation detection
        detection = image_results.get("manipulation_detection", {})
        score += (1 - detection.get("overall_manipulation_likelihood", 0.5)) * weights["manipulation"]
        
        # Add metadata analysis
        metadata = image_results.get("metadata_analysis", {})
        metadata_score = 1.0 - (len(metadata.get("suspicious_indicators", [])) * 0.2)
        score += max(0.0, metadata_score) * weights["metadata"]
        
        # Add stock image detection
        stock = detection.get("stock_image", {})
        if stock.get("is_stock_image"):
            score += 0.3 * weights["stock_image"]
        
        # Add color analysis
        color = detection.get("details", {}).get("color_analysis", {})
        if not color.get("unusual_patterns", False):
            score += 0.8 * weights["color_analysis"]
        
        return max(0.0, min(1.0, score))
    
    def _calculate_video_score(self, video_results: Dict) -> float:
        """Calculate video-specific credibility score"""
        weights = self.weight_config["video"]
        score = 0.0
        
        # Add manipulation detection
        detection = video_results.get("manipulation_detection", {})
        score += (1 - detection.get("overall_manipulation_likelihood", 0.5)) * 0.4
        
        # Add frame analysis
        frame_analysis = video_results.get("frame_analysis", {})
        frame_inconsistencies = len(frame_analysis.get("inconsistencies", []))
        frame_score = 1.0 - (frame_inconsistencies * 0.2)
        score += max(0.0, frame_score) * weights["frame_inconsistency"]
        
        # Add audio analysis
        audio = video_results.get("audio_analysis", {})
        audio_score = 0.7  # Placeholder
        score += audio_score * weights["audio_anomalies"]
        
        return max(0.0, min(1.0, score))
    
    def calculate_multimodal_score(self, results: Dict) -> float:
        """
        Calculate combined score for multi-modal content
        
        Args:
            results: Dictionary with text, image, and/or video results
            
        Returns:
            Combined credibility score
        """
        scores = []
        weights = []
        
        if results.get("text"):
            text_score = self._calculate_text_score(results["text"], None)
            scores.append(text_score)
            weights.append(0.4)  # Text is weighted higher
        
        if results.get("image"):
            image_score = self._calculate_image_score(results["image"])
            scores.append(image_score)
            weights.append(0.3)
        
        if results.get("video"):
            video_score = self._calculate_video_score(results["video"])
            scores.append(video_score)
            weights.append(0.3)
        
        if scores:
            weighted_sum = sum(s * w for s, w in zip(scores, weights))
            total_weight = sum(weights)
            return weighted_sum / total_weight if total_weight > 0 else 0.5
        
        return 0.5
    
    def classify(self, credibility_score: float) -> str:
        """
        Classify content based on credibility score
        
        Args:
            credibility_score: Score from 0-1
            
        Returns:
            Classification string
        """
        if credibility_score >= self.classification_thresholds["highly_credible"]:
            return "highly_credible"
        elif credibility_score >= self.classification_thresholds["credible"]:
            return "credible"
        elif credibility_score >= self.classification_thresholds["uncertain"]:
            return "uncertain"
        elif credibility_score >= self.classification_thresholds["questionable"]:
            return "questionable"
        else:
            return "likely_false"
    
    def generate_recommendations(self, classification: str, score: float) -> List[str]:
        """
        Generate recommendations based on classification and score
        
        Args:
            classification: Content classification
            credibility_score: Credibility score
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if classification == "highly_credible":
            recommendations.extend([
                "Content appears to be from a credible source",
                "Verified sources and proper attribution found",
                "Information can be considered trustworthy"
            ])
        
        elif classification == "credible":
            recommendations.extend([
                "Content shows some credible elements",
                "Consider verifying with additional sources",
                "Exercise normal caution before sharing"
            ])
        
        elif classification == "uncertain":
            recommendations.extend([
                "Content has mixed credibility indicators",
                "Cross-check information with reliable sources",
                "Avoid sharing until verified"
            ])
        
        elif classification == "questionable":
            recommendations.extend([
                "Multiple credibility issues detected",
                "Verify information from official sources",
                "Do not rely on this content for important decisions"
            ])
        
        else:  # likely_false
            recommendations.extend([
                "High likelihood of misinformation",
                "Do not share this content",
                "Report to platform if applicable",
                "Seek information from verified news sources"
            ])
        
        # Add score-based recommendation
        if score < 0.3:
            recommendations.append("Consider fact-checking with reputable sources")
        
        return recommendations