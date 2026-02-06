"""
Sentiment Analysis Module

Provides sentiment scoring for text content using TextBlob.
Returns normalized sentiment scores on a 0-1 scale.
"""

from textblob import TextBlob
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Analyzes sentiment from text using TextBlob."""

    def __init__(self):
        """Initialize the sentiment analyzer."""
        self.name = "TextBlob"
        self.version = "0.18.0"

    def analyze_text(self, text: str) -> float:
        """
        Analyze sentiment of a single text string.

        Args:
            text: The text to analyze

        Returns:
            Sentiment polarity score from -1 (negative) to 1 (positive)
        """
        if not text or not text.strip():
            return 0.0

        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except Exception as e:
            logger.error(f"Error analyzing text sentiment: {e}")
            return 0.0

    def normalize_score(self, polarity: float) -> float:
        """
        Normalize polarity score from [-1, 1] to [0, 1] scale.

        Args:
            polarity: Sentiment polarity from -1 to 1

        Returns:
            Normalized score from 0 to 1
        """
        # Convert from [-1, 1] to [0, 1]
        return (polarity + 1) / 2

    def aggregate_sentiment(self, texts: List[str]) -> Dict[str, float]:
        """
        Aggregate sentiment across multiple text inputs.

        Args:
            texts: List of text strings to analyze

        Returns:
            Dictionary containing:
                - normalized_score: Aggregated sentiment on 0-1 scale
                - raw_polarity: Average raw polarity score
                - num_texts: Number of texts analyzed
                - valid_texts: Number of non-empty texts
        """
        if not texts:
            logger.warning("No texts provided for sentiment analysis")
            return {
                "normalized_score": 0.5,  # Neutral
                "raw_polarity": 0.0,
                "num_texts": 0,
                "valid_texts": 0
            }

        polarities = []
        valid_count = 0

        for text in texts:
            if text and text.strip():
                polarity = self.analyze_text(text)
                polarities.append(polarity)
                valid_count += 1

        if not polarities:
            logger.warning("No valid texts found for sentiment analysis")
            return {
                "normalized_score": 0.5,  # Neutral
                "raw_polarity": 0.0,
                "num_texts": len(texts),
                "valid_texts": 0
            }

        # Calculate average polarity
        avg_polarity = sum(polarities) / len(polarities)
        normalized = self.normalize_score(avg_polarity)

        logger.info(
            f"Analyzed {valid_count} texts: "
            f"avg_polarity={avg_polarity:.3f}, normalized={normalized:.3f}"
        )

        return {
            "normalized_score": round(normalized, 4),
            "raw_polarity": round(avg_polarity, 4),
            "num_texts": len(texts),
            "valid_texts": valid_count
        }
