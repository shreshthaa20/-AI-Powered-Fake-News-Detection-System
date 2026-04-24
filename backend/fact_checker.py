"""
Fact Checker Module
Integrates Google Fact Check Tools API and other claim verification sources
"""

import os
import re
import requests
from typing import Dict, List, Optional
from urllib.parse import quote

class FactChecker:
    """Verifies claims against trusted fact-checking databases"""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_FACT_CHECK_API_KEY", "")
        self.fact_check_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        self.credible_fact_checkers = [
            "reuters",
            "ap",
            "bbc",
            "altnews",
            "boomlive",
            "factly",
            "indiatoday",
            "thequint",
            "newschecker",
            "factcheck.org",
            "snopes",
            "politifact"
        ]
    
    def check_claim(self, text: str) -> Dict:
        """
        Check a claim against Google Fact Check Tools API
        
        Args:
            text: Text containing the claim
            
        Returns:
            Dictionary with fact-check results
        """
        results = {
            "claim_checked": False,
            "matches": [],
            "overall_verdict": "unknown",
            "confidence": 0.0,
            "evidence": []
        }
        
        # Extract likely claims (sentences)
        claims = self._extract_claims(text)
        
        for claim in claims:
            match = self._query_fact_check_api(claim)
            if match:
                results["matches"].append(match)
        
        # Determine overall verdict
        if results["matches"]:
            results["claim_checked"] = True
            results["overall_verdict"] = self._aggregate_verdict(results["matches"])
            results["confidence"] = max(m.get("confidence", 0) for m in results["matches"])
            
            for match in results["matches"]:
                results["evidence"].append({
                    "type": "fact_check",
                    "confidence": match.get("confidence", 0.5),
                    "description": f"Fact-check by {match.get('publisher', 'unknown')}: {match.get('verdict', 'unknown')}"
                })
        
        return results
    
    def _extract_claims(self, text: str) -> List[str]:
        """Extract likely factual claims from text"""
        # Simple sentence extraction
        sentences = re.split(r'[.!?]+', text)
        claims = []
        
        for s in sentences:
            s = s.strip()
            # Filter for claim-like sentences (length, no questions)
            if len(s) > 20 and len(s) < 300 and not s.endswith("?"):
                # Prioritize sentences with statistics, names, or specific assertions
                if re.search(r'\d+|said|reported|according to|claims|announced', s, re.I):
                    claims.append(s)
        
        # Return top 3 most likely claims
        return claims[:3]
    
    def _query_fact_check_api(self, claim: str) -> Optional[Dict]:
        """Query Google Fact Check API for a claim"""
        if not self.api_key:
            return None
        
        try:
            params = {
                "query": claim[:200],  # API limit
                "key": self.api_key,
                "languageCode": "en"
            }
            response = requests.get(self.fact_check_url, params=params, timeout=10)
            data = response.json()
            
            claims = data.get("claims", [])
            if not claims:
                return None
            
            # Take the first/most relevant match
            best = claims[0]
            review = best.get("claimReview", [{}])[0]
            
            publisher = review.get("publisher", {}).get("name", "unknown")
            verdict = review.get("textualRating", "unknown").lower()
            
            # Normalize verdict
            if any(v in verdict for v in ["true", "correct", "accurate"]):
                normalized = "true"
                confidence = 0.9
            elif any(v in verdict for v in ["false", "fake", "incorrect", "misleading"]):
                normalized = "false"
                confidence = 0.9
            else:
                normalized = "mixed"
                confidence = 0.5
            
            return {
                "claim": best.get("text", claim),
                "publisher": publisher,
                "verdict": normalized,
                "original_verdict": review.get("textualRating", "unknown"),
                "url": review.get("url", ""),
                "confidence": confidence
            }
            
        except Exception as e:
            return None
    
    def _aggregate_verdict(self, matches: List[Dict]) -> str:
        """Aggregate multiple fact-check verdicts"""
        verdicts = [m.get("verdict", "unknown") for m in matches]
        
        if all(v == "true" for v in verdicts):
            return "true"
        elif all(v == "false" for v in verdicts):
            return "false"
        elif "false" in verdicts:
            return "likely_false"
        elif "true" in verdicts:
            return "likely_true"
        else:
            return "mixed"
    
    def quick_source_check(self, text: str) -> Dict:
        """
        Quick heuristic check for known misinformation sources
        without external API call
        """
        results = {
            "known_misinfo_patterns": [],
            "suspicious_phrases": [],
            "evidence": []
        }
        
        suspicious = [
            r"fwd:",
            r"forward this",
            r"send to everyone",
            r"don't delete",
            r"whatsapp university",
            r"as received",
            r"copy and paste"
        ]
        
        text_lower = text.lower()
        for pattern in suspicious:
            if re.search(pattern, text_lower):
                results["suspicious_phrases"].append(pattern)
                results["evidence"].append({
                    "type": "viral_misinfo_pattern",
                    "confidence": 0.7,
                    "description": f"Detected viral misinformation pattern: '{pattern}'"
                })
        
        return results
