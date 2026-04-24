"""
Fake News Detection System - Main Backend Application
FastAPI-based REST API for multi-modal fake news detection
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os
import json
from datetime import datetime

# Import analysis modules
from text_analyzer import TextAnalyzer
from image_analyzer import ImageAnalyzer
from video_analyzer import VideoAnalyzer
from credibility_scorer import CredibilityScorer
from multilingual_processor import MultilingualProcessor
from fact_checker import FactChecker

# Initialize FastAPI app
app = FastAPI(
    title="Fake News Detection API",
    description="AI-Powered Multi-Modal Fake News Detection System",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzers
text_analyzer = TextAnalyzer()
image_analyzer = ImageAnalyzer()
video_analyzer = VideoAnalyzer()
credibility_scorer = CredibilityScorer()
multilingual_processor = MultilingualProcessor()
fact_checker = FactChecker()

# Data models
class TextAnalysisRequest(BaseModel):
    text: str
    language: Optional[str] = "en"
    check_sources: Optional[bool] = True

class AnalysisResponse(BaseModel):
    analysis_id: str
    timestamp: str
    content_type: str
    results: dict
    credibility_score: float
    classification: str
    evidence: List[dict]
    recommendations: List[str]

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Fake News Detection API",
        "version": "1.0.0",
        "description": "AI-Powered Multi-Modal Fake News Detection System",
        "endpoints": {
            "POST /analyze/text": "Analyze text content",
            "POST /analyze/image": "Analyze image content",
            "POST /analyze/video": "Analyze video content",
            "POST /analyze/multimodal": "Analyze combined content",
            "POST /fact-check": "Check claims against fact-check databases",
            "GET /health": "Health check",
            "GET /supported-languages": "Get supported languages"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "text_analyzer": "active",
            "image_analyzer": "active",
            "video_analyzer": "active",
            "credibility_scorer": "active",
            "multilingual_processor": "active",
            "fact_checker": "active"
        }
    }

@app.get("/supported-languages")
async def get_supported_languages():
    """Get list of supported languages"""
    return {
        "supported_languages": [
            {"code": "en", "name": "English"},
            {"code": "hi", "name": "Hindi"},
            {"code": "bn", "name": "Bengali"},
            {"code": "ta", "name": "Tamil"},
            {"code": "te", "name": "Telugu"},
            {"code": "mr", "name": "Marathi"},
            {"code": "gu", "name": "Gujarati"},
            {"code": "kn", "name": "Kannada"},
            {"code": "ml", "name": "Malayalam"},
            {"code": "pa", "name": "Punjabi"},
            {"code": "ur", "name": "Urdu"}
        ]
    }

@app.post("/analyze/text")
async def analyze_text(
    text: str = Form(...),
    language: str = Form("en"),
    check_sources: bool = Form(True),
    fact_check: bool = Form(True)
):
    """
    Analyze text content for fake news detection
    
    Args:
        text: Text content to analyze
        language: Language code (default: en)
        check_sources: Whether to verify sources
        fact_check: Whether to check against fact-check databases
    
    Returns:
        Analysis results with credibility score
    """
    try:
        # Detect language if not specified
        if language == "auto":
            detected_lang = multilingual_processor.detect_language(text)
            language = detected_lang
        
        # Process multilingual text
        processed_text = multilingual_processor.process_text(text, language)
        
        # Analyze text content (use original text)
        text_results = text_analyzer.analyze(text, language)
        
        # Check sources if requested
        source_results = {}
        if check_sources:
            source_results = text_analyzer.verify_sources(text)
        
        # Fact-check claims if requested
        fact_check_results = {}
        if fact_check:
            fact_check_results = fact_checker.check_claim(text)
            # Also run quick heuristic check
            quick_check = fact_checker.quick_source_check(text)
            fact_check_results["quick_check"] = quick_check
        
        # Calculate credibility score
        credibility_score = credibility_scorer.calculate_score(
            text_results=text_results,
            source_results=source_results,
            content_type="text"
        )
        
        # Adjust score based on fact-check if available
        if fact_check_results.get("claim_checked"):
            fc_verdict = fact_check_results.get("overall_verdict", "unknown")
            if fc_verdict == "true":
                credibility_score = min(1.0, credibility_score + 0.2)
            elif fc_verdict == "false":
                credibility_score = max(0.0, credibility_score - 0.3)
            elif fc_verdict == "likely_false":
                credibility_score = max(0.0, credibility_score - 0.15)
        
        # Classify content
        classification = credibility_scorer.classify(credibility_score)
        
        # Generate evidence and recommendations
        evidence = text_results.get("evidence", []) + source_results.get("evidence", [])
        if fact_check_results.get("evidence"):
            evidence.extend(fact_check_results["evidence"])
        
        recommendations = credibility_scorer.generate_recommendations(
            classification, credibility_score
        )
        
        return AnalysisResponse(
            analysis_id=f"TXT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            content_type="text",
            results={
                "text_analysis": text_results,
                "source_verification": source_results,
                "fact_check": fact_check_results,
                "language": language
            },
            credibility_score=round(credibility_score, 3),
            classification=classification,
            evidence=evidence,
            recommendations=recommendations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.post("/analyze/image")
async def analyze_image(
    file: UploadFile = File(...),
    check_metadata: bool = Form(True)
):
    """
    Analyze image content for manipulation detection
    
    Args:
        file: Image file to analyze
        check_metadata: Whether to check EXIF metadata
    
    Returns:
        Analysis results with manipulation detection
    """
    try:
        # Save uploaded file temporarily
        temp_path = f"data/temp_{datetime.now().timestamp()}_{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Analyze image
        image_results = image_analyzer.analyze(temp_path, check_metadata)
        
        # Calculate credibility score
        credibility_score = credibility_scorer.calculate_score(
            image_results=image_results,
            content_type="image"
        )
        
        # Classify content
        classification = credibility_scorer.classify(credibility_score)
        
        # Generate evidence and recommendations
        evidence = image_results.get("evidence", [])
        recommendations = credibility_scorer.generate_recommendations(
            classification, credibility_score
        )
        
        # Clean up temp file
        os.remove(temp_path)
        
        return AnalysisResponse(
            analysis_id=f"IMG-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            content_type="image",
            results=image_results,
            credibility_score=round(credibility_score, 3),
            classification=classification,
            evidence=evidence,
            recommendations=recommendations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image analysis error: {str(e)}")

@app.post("/analyze/video")
async def analyze_video(
    file: UploadFile = File(...),
    extract_frames: bool = Form(True),
    max_frames: int = Form(10)
):
    """
    Analyze video content for manipulation detection
    
    Args:
        file: Video file to analyze
        extract_frames: Whether to extract key frames
        max_frames: Maximum frames to analyze
    
    Returns:
        Analysis results with video manipulation detection
    """
    try:
        # Save uploaded file temporarily
        temp_path = f"data/temp_{datetime.now().timestamp()}_{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Analyze video
        video_results = video_analyzer.analyze(
            temp_path, 
            extract_frames=extract_frames,
            max_frames=max_frames
        )
        
        # Calculate credibility score
        credibility_score = credibility_scorer.calculate_score(
            video_results=video_results,
            content_type="video"
        )
        
        # Classify content
        classification = credibility_scorer.classify(credibility_score)
        
        # Generate evidence and recommendations
        evidence = video_results.get("evidence", [])
        recommendations = credibility_scorer.generate_recommendations(
            classification, credibility_score
        )
        
        # Clean up temp file
        os.remove(temp_path)
        
        return AnalysisResponse(
            analysis_id=f"VID-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            content_type="video",
            results=video_results,
            credibility_score=round(credibility_score, 3),
            classification=classification,
            evidence=evidence,
            recommendations=recommendations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video analysis error: {str(e)}")

@app.post("/analyze/multimodal")
async def analyze_multimodal(
    text: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    video: Optional[UploadFile] = File(None),
    language: str = Form("auto"),
    fact_check: bool = Form(True)
):
    """
    Analyze combined multi-modal content
    
    Args:
        text: Optional text content
        image: Optional image file
        video: Optional video file
        language: Primary language for text analysis
        fact_check: Whether to fact-check text claims
    
    Returns:
        Combined analysis results
    """
    try:
        results = {
            "text": None,
            "image": None,
            "video": None
        }
        
        fact_check_results = {}
        
        # Analyze text if provided
        if text:
            if language == "auto":
                language = multilingual_processor.detect_language(text)
            
            processed_text = multilingual_processor.process_text(text, language)
            text_results = text_analyzer.analyze(processed_text["processed_text"], language)
            results["text"] = text_results
            
            if fact_check:
                fact_check_results = fact_checker.check_claim(text)
        
        # Analyze image if provided
        if image:
            temp_img_path = f"data/temp_img_{datetime.now().timestamp()}"
            with open(temp_img_path, "wb") as f:
                content = await image.read()
                f.write(content)
            
            image_results = image_analyzer.analyze(temp_img_path)
            results["image"] = image_results
            os.remove(temp_img_path)
        
        # Analyze video if provided
        if video:
            temp_vid_path = f"data/temp_vid_{datetime.now().timestamp()}"
            with open(temp_vid_path, "wb") as f:
                content = await video.read()
                f.write(content)
            
            video_results = video_analyzer.analyze(temp_vid_path)
            results["video"] = video_results
            os.remove(temp_vid_path)
        
        # Calculate combined credibility score
        credibility_score = credibility_scorer.calculate_multimodal_score(results)
        
        # Adjust based on fact-check
        if fact_check_results.get("claim_checked"):
            fc_verdict = fact_check_results.get("overall_verdict", "unknown")
            if fc_verdict == "true":
                credibility_score = min(1.0, credibility_score + 0.2)
            elif fc_verdict == "false":
                credibility_score = max(0.0, credibility_score - 0.3)
        
        # Classify content
        classification = credibility_scorer.classify(credibility_score)
        
        # Generate evidence and recommendations
        evidence = []
        for content_type, content_results in results.items():
            if content_results and "evidence" in content_results:
                evidence.extend(content_results.get("evidence", []))
        
        if fact_check_results.get("evidence"):
            evidence.extend(fact_check_results["evidence"])
        
        recommendations = credibility_scorer.generate_recommendations(
            classification, credibility_score
        )
        
        return AnalysisResponse(
            analysis_id=f"MMM-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            content_type="multimodal",
            results={**results, "fact_check": fact_check_results},
            credibility_score=round(credibility_score, 3),
            classification=classification,
            evidence=evidence,
            recommendations=recommendations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multimodal analysis error: {str(e)}")

@app.post("/fact-check")
async def fact_check_endpoint(text: str = Form(...)):
    """
    Standalone fact-check endpoint
    
    Args:
        text: Text to fact-check
    
    Returns:
        Fact-check results
    """
    try:
        result = fact_checker.check_claim(text)
        quick = fact_checker.quick_source_check(text)
        return {
            "claim_checked": result["claim_checked"],
            "matches": result["matches"],
            "overall_verdict": result["overall_verdict"],
            "confidence": result["confidence"],
            "quick_heuristics": quick,
            "evidence": result["evidence"] + quick.get("evidence", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fact-check error: {str(e)}")

if __name__ == "__main__":
    # Create data directory if not exists
    os.makedirs("data", exist_ok=True)
    
    # Run the API server
    uvicorn.run(app, host="0.0.0.0", port=8000)
