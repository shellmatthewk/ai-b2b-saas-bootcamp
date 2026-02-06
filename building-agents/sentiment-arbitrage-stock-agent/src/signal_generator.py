"""
Signal Generation Module

Combines sentiment analysis and technical indicators to generate trading signals.
Implements the core signal logic and decision-making process.
"""

from typing import Dict, List
from datetime import datetime
import logging

from src.sentiment_analyzer import SentimentAnalyzer
from src.technical_indicators import TechnicalIndicatorCalculator

logger = logging.getLogger(__name__)


class SignalGenerator:
    """Generates trading signals based on sentiment and technical analysis."""

    def __init__(
        self,
        sentiment_threshold: float = 0.7,
        rsi_buy_threshold: float = 30,
        rsi_period: int = 14
    ):
        """
        Initialize the signal generator.

        Args:
            sentiment_threshold: Minimum sentiment score for BUY signal (0-1)
            rsi_buy_threshold: Maximum RSI for BUY signal (0-100)
            rsi_period: Period for RSI calculation
        """
        self.sentiment_threshold = sentiment_threshold
        self.rsi_buy_threshold = rsi_buy_threshold

        # Initialize analyzers
        self.sentiment_analyzer = SentimentAnalyzer()
        self.technical_calculator = TechnicalIndicatorCalculator(rsi_period)

        logger.info(
            f"SignalGenerator initialized: "
            f"sentiment_threshold={sentiment_threshold}, "
            f"rsi_buy_threshold={rsi_buy_threshold}"
        )

    def determine_signal(
        self,
        sentiment_score: float,
        rsi: float
    ) -> tuple[str, str]:
        """
        Determine trading signal based on sentiment and RSI.

        Signal Logic:
        - BUY: sentiment > threshold AND rsi < buy_threshold
        - HOLD: Either condition met but not both
        - NEUTRAL: Neither condition met

        Args:
            sentiment_score: Normalized sentiment (0-1)
            rsi: Current RSI value (0-100)

        Returns:
            Tuple of (signal, reason)
        """
        sentiment_bullish = sentiment_score > self.sentiment_threshold
        rsi_oversold = rsi < self.rsi_buy_threshold

        if sentiment_bullish and rsi_oversold:
            reason = (
                f"Strong bullish sentiment ({sentiment_score:.2f} > {self.sentiment_threshold}) "
                f"combined with oversold conditions (RSI {rsi:.2f} < {self.rsi_buy_threshold}). "
                f"Potential buying opportunity."
            )
            return "BUY", reason

        elif sentiment_bullish:
            reason = (
                f"Bullish sentiment ({sentiment_score:.2f}) but RSI ({rsi:.2f}) "
                f"not oversold. Wait for better entry point."
            )
            return "HOLD", reason

        elif rsi_oversold:
            reason = (
                f"RSI oversold ({rsi:.2f}) but sentiment weak ({sentiment_score:.2f}). "
                f"Technical setup present but lacking sentiment confirmation."
            )
            return "HOLD", reason

        else:
            reason = (
                f"Neutral conditions: sentiment={sentiment_score:.2f}, RSI={rsi:.2f}. "
                f"No clear trading opportunity."
            )
            return "NEUTRAL", reason

    def generate_signal(
        self,
        ticker: str,
        reddit_posts: List[str]
    ) -> Dict:
        """
        Generate a complete trading signal for a ticker.

        Args:
            ticker: Stock symbol (e.g., 'AAPL')
            reddit_posts: List of Reddit comment strings for sentiment analysis

        Returns:
            Standardized signal dictionary containing:
                - signal: BUY, HOLD, or NEUTRAL
                - ticker: Stock symbol
                - sentiment_score: Aggregated sentiment (0-1)
                - rsi: Current RSI value
                - volume: Current trading volume
                - reason: Explanation of the signal
                - timestamp: ISO 8601 timestamp
                - status: success, partial, or error
                - metadata: Additional context
                - errors: List of errors if any
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        errors = []

        # Step 1: Analyze sentiment
        logger.info(f"Analyzing sentiment for {ticker} from {len(reddit_posts)} posts")
        sentiment_result = self.sentiment_analyzer.aggregate_sentiment(reddit_posts)
        sentiment_score = sentiment_result["normalized_score"]

        # Step 2: Fetch technical indicators
        logger.info(f"Fetching technical indicators for {ticker}")
        technical_result = self.technical_calculator.analyze_ticker(ticker)

        if technical_result["status"] == "error":
            # Cannot generate signal without technical data
            logger.error(f"Technical analysis failed for {ticker}: {technical_result.get('error')}")
            return {
                "signal": "ERROR",
                "ticker": ticker.upper(),
                "sentiment_score": sentiment_score,
                "rsi": None,
                "volume": None,
                "price": None,
                "reason": f"Unable to fetch technical data: {technical_result.get('error')}",
                "timestamp": timestamp,
                "status": "error",
                "metadata": {
                    "sentiment_analyzer": self.sentiment_analyzer.name,
                    "service_version": "1.0.0",
                    "sentiment_details": sentiment_result
                },
                "errors": [
                    {
                        "type": "technical_data_error",
                        "message": technical_result.get('error')
                    }
                ]
            }

        rsi = technical_result["rsi"]
        volume = technical_result["volume"]
        price = technical_result["price"]

        # Step 3: Generate signal
        signal, reason = self.determine_signal(sentiment_score, rsi)

        logger.info(f"Generated {signal} signal for {ticker}: {reason}")

        return {
            "signal": signal,
            "ticker": ticker.upper(),
            "sentiment_score": sentiment_score,
            "rsi": rsi,
            "volume": volume,
            "price": price,
            "reason": reason,
            "timestamp": timestamp,
            "status": "success",
            "metadata": {
                "sentiment_analyzer": self.sentiment_analyzer.name,
                "service_version": "1.0.0",
                "rsi_period": self.technical_calculator.rsi_period,
                "sentiment_threshold": self.sentiment_threshold,
                "rsi_buy_threshold": self.rsi_buy_threshold,
                "sentiment_details": {
                    "num_posts": sentiment_result["num_texts"],
                    "valid_posts": sentiment_result["valid_texts"],
                    "raw_polarity": sentiment_result["raw_polarity"]
                },
                "technical_details": {
                    "avg_volume": technical_result.get("avg_volume"),
                    "data_points": technical_result.get("data_points")
                }
            },
            "errors": errors if errors else []
        }
