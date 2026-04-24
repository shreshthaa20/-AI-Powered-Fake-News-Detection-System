## 🚀 Installation

1. **Clone the repository**
   ```bash
   cd news
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate     # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLTK data** (for text analysis)
   ```python
   import nltk
   nltk.download('punkt')
   nltk.download('stopwords')
   nltk.download('wordnet')
   nltk.download('averaged_perceptron_tagger')
   ```

5. **(Optional) Set up Google Fact Check API**
   ```bash
   cp .env.example .env
   # Edit .env and add your API key
   ```

## 🎯 Usage

### Starting the Backend API

```bash
cd backend
python main.py
```

The API will start at `http://localhost:8000`

### Starting the Frontend

```bash
cd frontend
streamlit run app.py
```

The UI will open at `http://localhost:8501`

### Running Tests

```bash
cd backend
pytest tests/
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/supported-languages` | GET | List supported languages |
| `/analyze/text` | POST | Analyze text content (supports fact_check=true) |
| `/analyze/image` | POST | Analyze image content |
| `/analyze/video` | POST | Analyze video content |
| `/analyze/multimodal` | POST | Analyze combined content |
| `/fact-check` | POST | Standalone claim verification |

### Example: Text Analysis

```bash
curl -X POST "http://localhost:8000/analyze/text" \
  -F "text=Your news text here" \
  -F "language=en" \
  -F "check_sources=true" \
  -F "fact_check=true"
```

### Example: Fact-Check Only

```bash
curl -X POST "http://localhost:8000/fact-check" \
  -F "text=The government announced new policies yesterday."
```

## 🌍 Supported Languages

| Code | Language |
|------|----------|
| en | English |
| hi | Hindi |
| bn | Bengali |
| ta | Tamil |
| te | Telugu |
| mr | Marathi |
| gu | Gujarati |
| kn | Kannada |
| ml | Malayalam |
| pa | Punjabi |
| ur | Urdu |

## ⚙️ Technical Details

### Text Analysis Features
- **BERT-based classification**: Uses `distilbert-base-finetuned-fake-news-detection` model (lazy-loaded)
- Clickbait detection using pattern matching
- Emotional manipulation trigger detection
- Source credibility analysis with domain whitelist
- Text structure analysis (paragraphs, quotes, statistics)
- Unverified claim detection
- **Google Fact Check API integration** for claim verification
- Viral misinformation pattern detection (`fwd:`, `forward this`, etc.)

### Image Analysis Features
- EXIF metadata extraction and analysis
- Manipulation indicator detection
- Color distribution analysis
- Perceptual hashing for stock image detection
- Edge and artifact analysis

### Video Analysis Features
- **Real OpenCV frame extraction** with configurable sampling
- Frame quality analysis (Laplacian variance for sharpness)
- Blur and noise estimation
- **Face detection** with Haar cascades
- **Deepfake heuristic**: Unnatural facial texture smoothness detection
- Frame inconsistency detection (quality, blur, face count variation)
- Visual artifact detection

### Credibility Classification

| Score Range | Classification |
|-------------|----------------|
| 0.8 - 1.0 | Highly Credible |
| 0.6 - 0.8 | Credible |
| 0.4 - 0.6 | Uncertain |
| 0.2 - 0.4 | Questionable |
| 0.0 - 0.2 | Likely False |

## 📱 Frontend Interface

The Streamlit frontend provides:
- Text input with language selection
- Image upload with drag-and-drop
- Video upload support
- Real-time credibility visualization
- Evidence and recommendation display
- API health status indicator

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
API_HOST=0.0.0.0
API_PORT=8000
DATA_DIR=../data
GOOGLE_FACT_CHECK_API_KEY=your_api_key_here
```

## 🧪 Testing

Run the test suite:

```bash
cd backend
pytest tests/ -v
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is for educational and research purposes.

## 🙏 Acknowledgments

- Hugging Face Transformers for BERT models
- OpenCV for video analysis
- NLTK for natural language processing
- FastAPI for the web framework
- Streamlit for the user interface
- Pillow for image processing
