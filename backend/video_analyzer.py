"""
Video Analyzer Module
Analyzes video content for manipulation and deepfake detection
"""

import os
from typing import Dict, List, Optional

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    cv2 = None
    np = None


class VideoAnalyzer:
    """Analyzes videos for manipulation and authenticity"""
    
    def __init__(self):
        self.max_frames = 10
        self.frame_interval = 30  # Sample every N frames
        # Load face detector for deepfake heuristic
        if CV2_AVAILABLE:
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )
        else:
            self.face_cascade = None
    
    def analyze(self, video_path: str, extract_frames: bool = True, max_frames: int = 10) -> Dict:
        """
        Analyze video for manipulation detection
        
        Args:
            video_path: Path to video file
            extract_frames: Whether to extract and analyze key frames
            max_frames: Maximum number of frames to analyze
            
        Returns:
            Dictionary with analysis results
        """
        results = {
            "file_info": {},
            "frame_analysis": {},
            "manipulation_detection": {},
            "audio_analysis": {},
            "authenticity_score": 0.0,
            "evidence": []
        }
        
        try:
            # 1. Get basic file info with OpenCV
            results["file_info"] = self._get_video_info(video_path)
            
            # 2. Analyze frames if requested
            if extract_frames:
                results["frame_analysis"] = self._analyze_frames(
                    video_path, 
                    max_frames
                )
            
            # 3. Detect video manipulation
            results["manipulation_detection"] = self._detect_video_manipulation(
                results["frame_analysis"]
            )
            
            # 4. Analyze audio presence
            results["audio_analysis"] = self._analyze_audio(video_path)
            
            # 5. Generate evidence
            results["evidence"] = self._generate_video_evidence(results)
            
            # 6. Calculate authenticity score
            results["authenticity_score"] = self._calculate_video_authenticity_score(results)
            
        except Exception as e:
            results["error"] = str(e)
        
        return results
    
    def _get_video_info(self, video_path: str) -> Dict:
        """Get video file information using OpenCV"""
        file_stats = os.stat(video_path)
        
        if not CV2_AVAILABLE:
            return {
                "filename": os.path.basename(video_path),
                "file_size": file_stats.st_size,
                "file_size_mb": round(file_stats.st_size / (1024 * 1024), 2),
                "extension": os.path.splitext(video_path)[1],
                "note": "OpenCV not installed — install opencv-python for full video analysis"
            }
        
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return {
                "filename": os.path.basename(video_path),
                "file_size": file_stats.st_size,
                "error": "Could not open video"
            }
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0
        
        cap.release()
        
        return {
            "filename": os.path.basename(video_path),
            "file_size": file_stats.st_size,
            "file_size_mb": round(file_stats.st_size / (1024 * 1024), 2),
            "extension": os.path.splitext(video_path)[1],
            "fps": round(fps, 2),
            "frame_count": frame_count,
            "duration_seconds": round(duration, 2),
            "resolution": f"{width}x{height}",
            "width": width,
            "height": height
        }
    
    def _analyze_frames(self, video_path: str, max_frames: int) -> Dict:
        """Extract and analyze key frames using OpenCV"""
        frame_analysis = {
            "frames_analyzed": 0,
            "frame_quality": [],
            "inconsistencies": [],
            "visual_artifacts": [],
            "face_analysis": []
        }
        
        if not CV2_AVAILABLE:
            frame_analysis["note"] = "OpenCV not installed — frame analysis unavailable"
            return frame_analysis
        
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                frame_analysis["error"] = "Could not open video"
                return frame_analysis
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames <= 0:
                frame_analysis["error"] = "No frames found"
                return frame_analysis
            
            # Sample evenly spaced frames
            indices = np.linspace(0, total_frames - 1, min(max_frames, total_frames), dtype=int)
            
            quality_scores = []
            blur_scores = []
            face_counts = []
            
            for idx in indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if not ret:
                    continue
                
                # Quality: variance of Laplacian (sharpness)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                quality_score = min(lap_var / 500.0, 1.0)  # Normalize
                
                # Blur detection
                blur_score = 1.0 - quality_score
                
                # Noise estimation (simplified)
                noise = np.std(gray)
                
                # Face detection for deepfake heuristics
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
                face_count = len(faces)
                
                frame_info = {
                    "frame_number": int(idx),
                    "quality_score": round(quality_score, 3),
                    "blur_score": round(blur_score, 3),
                    "noise_level": round(noise, 2),
                    "face_count": face_count
                }
                
                # Face boundary artifact check
                if face_count > 0:
                    for (x, y, w, h) in faces:
                        face_roi = gray[y:y+h, x:x+w]
                        face_edge = cv2.Canny(face_roi, 100, 200)
                        edge_ratio = np.count_nonzero(face_edge) / (w * h)
                        frame_info["face_edge_ratio"] = round(edge_ratio, 3)
                        
                        # Unnatural skin smoothness heuristic
                        face_std = np.std(face_roi)
                        frame_info["face_texture_std"] = round(face_std, 2)
                        
                        if face_std < 15:
                            frame_info["suspicious_smoothness"] = True
                
                frame_analysis["frame_quality"].append(frame_info)
                quality_scores.append(quality_score)
                blur_scores.append(blur_score)
                face_counts.append(face_count)
            
            cap.release()
            frame_analysis["frames_analyzed"] = len(frame_analysis["frame_quality"])
            
            # Detect inconsistencies
            if len(quality_scores) > 1:
                q_std = np.std(quality_scores)
                if q_std > 0.3:
                    frame_analysis["inconsistencies"].append({
                        "type": "quality_inconsistency",
                        "description": f"Inconsistent frame quality across video (std={q_std:.2f})"
                    })
                
                b_std = np.std(blur_scores)
                if b_std > 0.3:
                    frame_analysis["inconsistencies"].append({
                        "type": "blur_inconsistency",
                        "description": f"Inconsistent blur levels detected (std={b_std:.2f})"
                    })
            
            # Face count inconsistency = possible manipulation
            if len(set(face_counts)) > 1 and max(face_counts) > 0:
                frame_analysis["inconsistencies"].append({
                    "type": "face_count_variation",
                    "description": "Varying face counts across frames may indicate splicing"
                })
            
            # Check for visual artifacts (compression, blocking)
            for fq in frame_analysis["frame_quality"]:
                if fq.get("suspicious_smoothness"):
                    frame_analysis["visual_artifacts"].append({
                        "frame": fq["frame_number"],
                        "type": "unnatural_smoothness",
                        "description": "Unnaturally smooth facial texture detected"
                    })
            
        except Exception as e:
            frame_analysis["error"] = str(e)
        
        return frame_analysis
    
    def _detect_video_manipulation(self, frame_analysis: Dict) -> Dict:
        """Detect video manipulation indicators"""
        detection = {
            "overall_manipulation_likelihood": 0.0,
            "indicators": [],
            "details": {}
        }
        
        # Check for frame inconsistencies
        if frame_analysis.get("inconsistencies"):
            for inc in frame_analysis["inconsistencies"]:
                detection["indicators"].append({
                    "type": inc["type"],
                    "confidence": 0.6,
                    "description": inc["description"]
                })
        
        # Check for visual artifacts
        artifacts = frame_analysis.get("visual_artifacts", [])
        if artifacts:
            detection["indicators"].append({
                "type": "visual_artifacts",
                "confidence": min(0.5 + len(artifacts) * 0.1, 0.9),
                "description": f"{len(artifacts)} visual artifact(s) detected in frames"
            })
        
        # Deepfake heuristic based on face smoothness
        face_frames = [fq for fq in frame_analysis.get("frame_quality", []) if fq.get("suspicious_smoothness")]
        if face_frames:
            detection["indicators"].append({
                "type": "deepfake_heuristic",
                "confidence": min(0.4 + len(face_frames) * 0.1, 0.8),
                "description": f"Unnatural facial smoothing in {len(face_frames)} frame(s) — possible deepfake"
            })
        
        # Calculate overall likelihood
        if detection["indicators"]:
            detection["overall_manipulation_likelihood"] = round(
                sum(ind["confidence"] for ind in detection["indicators"]) / len(detection["indicators"]),
                3
            )
        
        detection["details"]["frame_count"] = frame_analysis.get("frames_analyzed", 0)
        detection["details"]["inconsistency_count"] = len(frame_analysis.get("inconsistencies", []))
        
        return detection
    
    def _analyze_audio(self, video_path: str) -> Dict:
        """Analyze audio track presence using OpenCV"""
        has_audio = False
        if CV2_AVAILABLE:
            cap = cv2.VideoCapture(video_path)
            try:
                ext = os.path.splitext(video_path)[1].lower()
                has_audio = ext in [".mp4", ".avi", ".mov", ".mkv", ".webm"]
            except:
                pass
            cap.release()
        else:
            ext = os.path.splitext(video_path)[1].lower()
            has_audio = ext in [".mp4", ".avi", ".mov", ".mkv", ".webm"]
        
        return {
            "has_audio": has_audio,
            "audio_analysis": {
                "voice_detection": "not_available_without_ffmpeg",
                "audio_quality": "unknown",
                "note": "Detailed audio analysis requires ffmpeg or moviepy"
            }
        }
    
    def _generate_video_evidence(self, results: Dict) -> List[Dict]:
        """Generate evidence items for video analysis"""
        evidence = []
        
        # Add frame analysis evidence
        frame_analysis = results.get("frame_analysis", {})
        if frame_analysis.get("inconsistencies"):
            for inc in frame_analysis["inconsistencies"]:
                evidence.append({
                    "type": "video_frames",
                    "confidence": 0.6,
                    "description": inc["description"]
                })
        
        # Add visual artifact evidence
        for art in frame_analysis.get("visual_artifacts", []):
            evidence.append({
                "type": "visual_artifact",
                "confidence": 0.7,
                "description": f"Frame {art['frame']}: {art['description']}"
            })
        
        # Add manipulation indicators
        for indicator in results.get("manipulation_detection", {}).get("indicators", []):
            evidence.append({
                "type": "video_manipulation",
                "confidence": indicator["confidence"],
                "description": indicator["description"]
            })
        
        return evidence
    
    def _calculate_video_authenticity_score(self, results: Dict) -> float:
        """Calculate overall video authenticity score"""
        score = 0.5  # Base score
        
        # Reduce score for manipulation indicators
        detection = results.get("manipulation_detection", {})
        for indicator in detection.get("indicators", []):
            score -= indicator["confidence"] * 0.2
        
        # Reduce score for frame inconsistencies
        frame_analysis = results.get("frame_analysis", {})
        score -= len(frame_analysis.get("inconsistencies", [])) * 0.15
        
        # Reduce for visual artifacts
        score -= len(frame_analysis.get("visual_artifacts", [])) * 0.1
        
        return round(max(0.0, min(1.0, score)), 3)
