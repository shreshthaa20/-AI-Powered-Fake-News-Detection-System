"""
Image Analyzer Module
Detects image manipulation and manipulation signs using computer vision
"""

import os
import hashlib
from typing import Dict, List, Optional
from PIL import Image
import io

class ImageAnalyzer:
    """Analyzes images for manipulation and authenticity"""
    
    def __init__(self):
        self.manipulation_indicators = [
            "inconsistent_shadow",
            "copy_move",
            "splicing",
            "color_inconsistency",
            "noise_pattern_artifact"
        ]
        
        # Known stock image patterns (for reference)
        self.stock_patterns = []
    
    def analyze(self, image_path: str, check_metadata: bool = True) -> Dict:
        """
        Analyze image for manipulation detection
        
        Args:
            image_path: Path to image file
            check_metadata: Whether to check EXIF metadata
            
        Returns:
            Dictionary with analysis results
        """
        results = {
            "file_info": {},
            "metadata_analysis": {},
            "manipulation_detection": {},
            "authenticity_score": 0.0,
            "evidence": []
        }
        
        try:
            # 1. Get basic file info
            results["file_info"] = self._get_file_info(image_path)
            
            # 2. Analyze metadata if requested
            if check_metadata:
                results["metadata_analysis"] = self._analyze_metadata(image_path)
            
            # 3. Detect manipulation indicators
            results["manipulation_detection"] = self._detect_manipulation(image_path)
            
            # 4. Check for stock image patterns
            stock_result = self._check_stock_patterns(image_path)
            results["manipulation_detection"]["stock_image"] = stock_result
            
            # 5. Generate evidence
            results["evidence"] = self._generate_image_evidence(results)
            
            # 6. Calculate authenticity score
            results["authenticity_score"] = self._calculate_authenticity_score(results)
            
        except Exception as e:
            results["error"] = str(e)
        
        return results
    
    def _get_file_info(self, image_path: str) -> Dict:
        """Get basic image file information"""
        file_stats = os.stat(image_path)
        
        img = Image.open(image_path)
        
        return {
            "filename": os.path.basename(image_path),
            "file_size": file_stats.st_size,
            "format": img.format,
            "mode": img.mode,
            "dimensions": img.size,
            "aspect_ratio": img.size[0] / img.size[1] if img.size[1] > 0 else 0
        }
    
    def _analyze_metadata(self, image_path: str) -> Dict:
        """Analyze image EXIF metadata"""
        metadata = {
            "has_exif": False,
            "camera_info": {},
            "date_info": {},
            "software_info": {},
            "gps_info": {},
            "suspicious_indicators": []
        }
        
        try:
            img = Image.open(image_path)
            exif_data = img.getexif()
            
            if exif_data:
                metadata["has_exif"] = True
                
                # Extract common EXIF tags
                exif_tags = {
                    271: "make",
                    272: "model",
                    305: "software",
                    306: "date_time",
                    34853: "gps_info"
                }
                
                for tag, name in exif_tags.items():
                    if tag in exif_data:
                        metadata[name] = str(exif_data[tag])
                
                # Check for suspicious metadata
                if metadata.get("software"):
                    # Heuristic: Heavy editing software suggests manipulation
                    editing_software = ["photoshop", "gimp", "lightroom", "capture one"]
                    if any(sw in metadata["software"].lower() for sw in editing_software):
                        metadata["suspicious_indicators"].append("heavy_editing_software")
                
                # Check for metadata inconsistency (date in future)
                if metadata.get("date_time"):
                    # Simple check - would need proper date parsing in production
                    pass
                    
        except Exception as e:
            metadata["error"] = str(e)
        
        return metadata
    
    def _detect_manipulation(self, image_path: str) -> Dict:
        """
        Detect common image manipulation techniques
        
        Note: This is a simplified implementation. Production systems
        would use more advanced techniques like CNN-based detection.
        """
        detection = {
            "overall_manipulation_likelihood": 0.0,
            "indicators": [],
            "details": {}
        }
        
        try:
            img = Image.open(image_path)
            
            # 1. Check for inconsistent dimensions
            width, height = img.size
            if width > 4000 or height > 4000:
                detection["indicators"].append({
                    "type": "high_resolution",
                    "confidence": 0.3,
                    "description": "Unusually high resolution may indicate stock image"
                })
            
            # 2. Check file size vs dimensions ratio
            file_size = os.stat(image_path).st_size
            expected_size = width * height * 3  # RGB assumption
            compression_ratio = file_size / expected_size
            
            if compression_ratio < 0.01:
                detection["indicators"].append({
                    "type": "heavy_compression",
                    "confidence": 0.4,
                    "description": "Heavy compression may indicate re-editing"
                })
            
            # 3. Check for consistent color distribution
            color_analysis = self._analyze_colors(img)
            detection["details"]["color_analysis"] = color_analysis
            
            if color_analysis.get("unusual_patterns"):
                detection["indicators"].append({
                    "type": "color_inconsistency",
                    "confidence": 0.5,
                    "description": "Unusual color patterns detected"
                })
            
            # 4. Check for edge artifacts (simplified)
            edge_analysis = self._analyze_edges(img)
            detection["details"]["edge_analysis"] = edge_analysis
            
            # Calculate overall likelihood
            if detection["indicators"]:
                detection["overall_manipulation_likelihood"] = sum(
                    ind["confidence"] for ind in detection["indicators"]
                ) / len(detection["indicators"])
            
        except Exception as e:
            detection["error"] = str(e)
        
        return detection
    
    def _analyze_colors(self, img: Image.Image) -> Dict:
        """Analyze color distribution for anomalies"""
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Sample pixels
        img_small = img.resize((50, 50))
        pixels = list(img_small.getdata())
        
        # Calculate color statistics
        r_vals = [p[0] for p in pixels]
        g_vals = [p[1] for p in pixels]
        b_vals = [p[2] for p in pixels]
        
        import statistics
        r_std = statistics.stdev(r_vals) if len(r_vals) > 1 else 0
        g_std = statistics.stdev(g_vals) if len(g_vals) > 1 else 0
        b_std = statistics.stdev(b_vals) if len(b_vals) > 1 else 0
        
        return {
            "color_variance": {
                "red": r_std,
                "green": g_std,
                "blue": b_std
            },
            "unusual_patterns": r_std < 10 or g_std < 10 or b_std < 10
        }
    
    def _analyze_edges(self, img: Image.Image) -> Dict:
        """Analyze edge characteristics"""
        # Simplified edge analysis
        return {
            "edge_density": 0.5,
            "sharp_edges": True,
            "note": "Advanced edge detection requires OpenCV"
        }
    
    def _check_stock_patterns(self, image_path: str) -> Dict:
        """
        Check if image matches known stock image patterns
        
        Note: In production, this would use image hashing and
        reverse image search capabilities.
        """
        # Calculate perceptual hash
        img_hash = self._calculate_phash(image_path)
        
        return {
            "is_stock_image": False,  # Placeholder
            "hash": img_hash,
            "note": "Stock image detection requires reverse image search API"
        }
    
    def _calculate_phash(self, image_path: str) -> str:
        """Calculate perceptual hash of image"""
        try:
            img = Image.open(image_path)
            img_small = img.resize((8, 8))
            pixels = list(img_small.getdata())
            
            # Simple hash based on average brightness
            avg = sum(sum(p[:3])/3 for p in pixels) / len(pixels)
            hash_str = ''.join('1' if sum(p[:3])/3 > avg else '0' for p in pixels)
            
            return hash_str
        except:
            return "error"
    
    def _generate_image_evidence(self, results: Dict) -> List[Dict]:
        """Generate evidence items for image analysis"""
        evidence = []
        
        # Add manipulation indicators
        for indicator in results.get("manipulation_detection", {}).get("indicators", []):
            evidence.append({
                "type": "image_manipulation",
                "confidence": indicator["confidence"],
                "description": indicator["description"]
            })
        
        # Add metadata evidence
        metadata = results.get("metadata_analysis", {})
        if metadata.get("suspicious_indicators"):
            evidence.append({
                "type": "metadata",
                "confidence": 0.6,
                "description": f"Suspicious metadata: {', '.join(metadata['suspicious_indicators'])}"
            })
        
        return evidence
    
    def _calculate_authenticity_score(self, results: Dict) -> float:
        """Calculate overall image authenticity score"""
        score = 0.5  # Base score
        
        # Reduce score for manipulation indicators
        detection = results.get("manipulation_detection", {})
        for indicator in detection.get("indicators", []):
            score -= indicator["confidence"] * 0.2
        
        # Reduce score for suspicious metadata
        metadata = results.get("metadata_analysis", {})
        score -= len(metadata.get("suspicious_indicators", [])) * 0.1
        
        return max(0.0, min(1.0, score))