"""
Unit tests for TextAnalyzer
"""

import pytest
from backend.text_analyzer import TextAnalyzer

@pytest.fixture
def analyzer():
    return TextAnalyzer()

def test_detect_clickbait(analyzer):
