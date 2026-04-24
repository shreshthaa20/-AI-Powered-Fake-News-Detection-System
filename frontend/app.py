"""
Fake News Detection System - Streamlit Frontend
User-friendly interface for the fake news detection API
"""

import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd

# Configure page
st.set_page_config(
    page_title="Fake News Detector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8001"

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        padding: 10px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .credibility-high {
        color: #2ecc71;
        font-weight: bold;
    }
    .credibility-medium {
        color: #f39c12;
        font-weight: bold;
    }
    .credibility-low {
        color: #e74c3c;
        font-weight: bold;
    }
    .evidence-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def analyze_text(text, language="auto", check_sources=True, fact_check=True):
    """Send text for analysis"""
    try:
        files = {
            "text": (None, text),
            "language": (None, language),
            "check_sources": (None, str(check_sources)),
            "fact_check": (None, str(fact_check))
        }
        response = requests.post(f"{API_BASE_URL}/analyze/text", files=files)
        return response.json()
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return None

def fact_check_text(text):
    """Send text for standalone fact-check"""
    try:
        files = {"text": (None, text)}
        response = requests.post(f"{API_BASE_URL}/fact-check", files=files)
        return response.json()
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return None

def analyze_image(uploaded_file):
    """Send image for analysis"""
    try:
        files = {"file": uploaded_file}
        data = {"check_metadata": "true"}
        response = requests.post(f"{API_BASE_URL}/analyze/image", files=files, data=data)
        return response.json()
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return None

def analyze_video(uploaded_file):
    """Send video for analysis"""
    try:
        files = {"file": uploaded_file}
        data = {"extract_frames": "true", "max_frames": "10"}
        response = requests.post(f"{API_BASE_URL}/analyze/video", files=files, data=data)
        return response.json()
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return None

def display_credibility_score(score, classification):
    """Display credibility score with visual indicator"""
    # Determine color based on score
    if score >= 0.8:
        color = "green"
        label = "Highly Credible"
    elif score >= 0.6:
        color = "blue"
        label = "Credible"
    elif score >= 0.4:
        color = "orange"
        label = "Uncertain"
    elif score >= 0.2:
        color = "red"
        label = "Questionable"
    else:
        color = "darkred"
        label = "Likely False"
    
    # Create progress bar
    st.markdown(f"""
    <div style='background-color: #f0f0f0; border-radius: 10px; padding: 20px; margin: 20px 0;'>
        <h3 style='color: {color}; text-align: center;'>{label}</h3>
        <div style='background-color: #e0e0e0; border-radius: 5px; height: 30px;'>
            <div style='background-color: {color}; border-radius: 5px; height: 100%; width: {score*100}%;'></div>
        <p style='text-align: center; margin-top: 10px;'>Credibility Score: {score:.2f}</p>
    </div>
    """, unsafe_allow_html=True)

def display_evidence(evidence):
    """Display evidence items"""
    if not evidence:
        st.info("No specific evidence found")
        return
    
    st.subheader("📋 Evidence")
    for i, item in enumerate(evidence, 1):
        confidence = item.get("confidence", 0)
        evidence_type = item.get("type", "unknown")
        description = item.get("description", "")
        
        st.markdown(f"""
        <div class='evidence-card'>
            <strong>Evidence {i}</strong><br>
            <em>Type: {evidence_type.replace('_', ' ').title()}</em><br>
            <p>{description}</p>
            <small>Confidence: {confidence:.2f}</small>
        </div>
        """, unsafe_allow_html=True)

def display_recommendations(recommendations):
    """Display recommendations"""
    if not recommendations:
        return
    
    st.subheader("💡 Recommendations")
    for rec in recommendations:
        st.markdown(f"- {rec}")

def main():
    """Main application"""
    
    # Header
    st.title("🔍 AI-Powered Fake News Detection System")
    st.markdown("---")
    
    # Sidebar
    st.sidebar.title("Options")
    st.sidebar.markdown("### About")
    st.sidebar.info("""
    This system analyzes content across multiple formats:
    - 📝 Text articles and posts
    - 🖼️ Images
    - 🎥 Videos
    - ✅ Fact-check claims
    
    It provides credibility scores and explanations.
    """)
    
    # Check API health
    api_healthy = check_api_health()
    if not api_healthy:
        st.warning("⚠️ API is not running. Please start the backend server.")
        st.code("cd backend\npython main.py", language="bash")
        st.markdown("---")
    else:
        st.success("✅ API connected")
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Text Analysis", 
        "🖼️ Image Analysis", 
        "🎥 Video Analysis", 
        "✅ Fact Check",
        "ℹ️ Info"
    ])
    
    # Tab 1: Text Analysis
    with tab1:
        st.header("Text Content Analysis")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            text_input = st.text_area(
                "Enter text to analyze:",
                height=200,
                placeholder="Paste article text, news headline, or social media post here..."
            )
        
        with col2:
            st.write("### Settings")
            language = st.selectbox(
                "Language",
                ["auto", "en", "hi", "bn", "ta", "te", "mr", "gu", "kn", "ml", "pa", "ur"],
                format_func=lambda x: {
                    "auto": "Auto-detect",
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
                }.get(x, x)
            )
            check_sources = st.checkbox("Verify sources", value=True)
            fact_check = st.checkbox("Fact-check claims", value=True)
        
        if st.button("Analyze Text", disabled=not api_healthy):
            if text_input:
                with st.spinner("Analyzing text..."):
                    result = analyze_text(text_input, language, check_sources, fact_check)
                    
                    if result:
                        st.markdown("---")
                        display_credibility_score(
                            result.get("credibility_score", 0),
                            result.get("classification", "unknown")
                        )
                        
                        st.subheader("📊 Analysis Results")
                        st.json(result.get("results", {}))
                        
                        display_evidence(result.get("evidence", []))
                        display_recommendations(result.get("recommendations", []))
            else:
                st.warning("Please enter text to analyze")
    
    # Tab 2: Image Analysis
    with tab2:
        st.header("Image Manipulation Detection")
        
        uploaded_image = st.file_uploader(
            "Upload an image to analyze:",
            type=["png", "jpg", "jpeg", "webp"]
        )
        
        if uploaded_image:
            st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)
            
            if st.button("Analyze Image", disabled=not api_healthy):
                with st.spinner("Analyzing image..."):
                    result = analyze_image(uploaded_image)
                    
                    if result:
                        st.markdown("---")
                        display_credibility_score(
                            result.get("credibility_score", 0),
                            result.get("classification", "unknown")
                        )
                        
                        st.subheader("📊 Analysis Results")
                        st.json(result.get("results", {}))
                        
                        display_evidence(result.get("evidence", []))
                        display_recommendations(result.get("recommendations", []))
    
    # Tab 3: Video Analysis
    with tab3:
        st.header("Video Content Analysis")
        
        uploaded_video = st.file_uploader(
            "Upload a video to analyze:",
            type=["mp4", "avi", "mov", "webm"]
        )
        
        if uploaded_video:
            st.video(uploaded_video)
            st.info(f"File: {uploaded_video.name}")
            
            if st.button("Analyze Video", disabled=not api_healthy):
                with st.spinner("Analyzing video..."):
                    result = analyze_video(uploaded_video)
                    
                    if result:
                        st.markdown("---")
                        display_credibility_score(
                            result.get("credibility_score", 0),
                            result.get("classification", "unknown")
                        )
                        
                        st.subheader("📊 Analysis Results")
                        st.json(result.get("results", {}))
                        
                        display_evidence(result.get("evidence", []))
                        display_recommendations(result.get("recommendations", []))
    
    # Tab 4: Fact Check
    with tab4:
        st.header("Standalone Fact Check")
        st.markdown("Quickly verify a claim against fact-checking databases.")
        
        fact_text = st.text_area(
            "Enter a claim to fact-check:",
            height=150,
            placeholder="e.g., 'The government announced free vaccines for all citizens yesterday.'"
        )
        
        if st.button("Fact Check", disabled=not api_healthy):
            if fact_text:
                with st.spinner("Checking claim..."):
                    result = fact_check_text(fact_text)
                    
                    if result:
                        st.markdown("---")
                        
                        verdict = result.get("overall_verdict", "unknown")
                        confidence = result.get("confidence", 0)
                        
                        if verdict == "true":
                            st.success(f"✅ Verdict: {verdict.upper()} (confidence: {confidence:.2f})")
                        elif verdict == "false":
                            st.error(f"❌ Verdict: {verdict.upper()} (confidence: {confidence:.2f})")
                        else:
                            st.info(f"ℹ️ Verdict: {verdict.upper()} (confidence: {confidence:.2f})")
                        
                        if result.get("matches"):
                            st.subheader("📰 Fact-Check Matches")
                            for match in result["matches"]:
                                st.markdown(f"""
                                - **Publisher**: {match.get('publisher', 'unknown')}
                                - **Verdict**: {match.get('original_verdict', 'unknown')}
                                - [Read more]({match.get('url', '#')})
                                """)
                        
                        if result.get("quick_heuristics", {}).get("suspicious_phrases"):
                            st.warning("⚠️ Viral misinformation patterns detected!")
                        
                        st.subheader("📊 Full Response")
                        st.json(result)
            else:
                st.warning("Please enter a claim to check")
    
    # Tab 5: Info
    with tab5:
        st.header("ℹ️ System Information")
        
        st.markdown("""
        ### About This System
        
        This AI-Powered Fake News Detection System is designed to:
        
        - **Analyze multi-modal content**: Text, Images, and Videos
        - **Support multiple languages**: Including Indian languages (Hindi, Bengali, Tamil, etc.)
        - **Provide credibility scores**: Clear assessment of content reliability
        - **Explain decisions**: Show evidence supporting the analysis
        - **Fact-check claims**: Integration with Google Fact Check Tools
        
        ### Features
        
        | Feature | Description |
        |---------|-------------|
        | Text Analysis | BERT classification, clickbait, emotional manipulation, unverified claims |
        | Image Analysis | EXIF metadata, manipulation, color inconsistencies |
        | Video Analysis | Frame extraction, face detection, deepfake heuristics |
        | Fact Check | Google Fact Check API + viral pattern detection |
        | Multilingual | Supports 11 Indian languages plus English |
        | Credibility Score | 0-1 score with classification (Highly Credible to Likely False) |
        
        ### How to Use
        
        1. Start the backend server: `cd backend && python main.py`
        2. Start the frontend: `cd frontend && streamlit run app.py`
        3. Select the type of content to analyze
        4. Upload or enter content
        5. Click Analyze to get results
        """)
        
        if api_healthy:
            st.success("✅ API is connected and running")
        else:
            st.error("❌ API is not connected")

if __name__ == "__main__":
    main()
