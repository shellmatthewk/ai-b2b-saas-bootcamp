#!/usr/bin/env python3
"""
Test script to verify the trading signal service works correctly.
Can be run standalone without starting the Flask server.
"""

import sys
from src.signal_generator import SignalGenerator

def test_signal_generation():
    """Test signal generation with sample data."""

    print("=" * 60)
    print("Trading Signal Service - Standalone Test")
    print("=" * 60)

    # Initialize signal generator
    generator = SignalGenerator(
        sentiment_threshold=0.7,
        rsi_buy_threshold=30,
        rsi_period=14
    )

    # Test Case 1: Apple with bullish sentiment
    print("\nTest Case 1: AAPL with bullish Reddit sentiment")
    print("-" * 60)

    ticker = "AAPL"
    reddit_posts = [
        "Apple's new products are amazing!",
        "AAPL to the moon! Best stock ever!",
        "Just bought more Apple shares, feeling great",
        "iPhone sales are crushing it",
        "Tim Cook is a genius, bullish on Apple"
    ]

    print(f"Ticker: {ticker}")
    print(f"Reddit posts: {len(reddit_posts)} comments")
    print("\nGenerating signal...")

    result = generator.generate_signal(ticker, reddit_posts)

    print(f"\n{'Signal:':<20} {result['signal']}")
    print(f"{'Sentiment Score:':<20} {result['sentiment_score']}")
    print(f"{'RSI:':<20} {result['rsi']}")
    print(f"{'Volume:':<20} {result['volume']:,}")
    print(f"{'Price:':<20} ${result['price']}")
    print(f"\nReason: {result['reason']}")
    print(f"\nStatus: {result['status']}")

    # Test Case 2: Tesla with negative sentiment
    print("\n" + "=" * 60)
    print("\nTest Case 2: TSLA with negative Reddit sentiment")
    print("-" * 60)

    ticker = "TSLA"
    reddit_posts = [
        "Tesla quality issues are getting worse",
        "Overvalued, time to sell",
        "Don't like the direction this company is going"
    ]

    print(f"Ticker: {ticker}")
    print(f"Reddit posts: {len(reddit_posts)} comments")
    print("\nGenerating signal...")

    result = generator.generate_signal(ticker, reddit_posts)

    print(f"\n{'Signal:':<20} {result['signal']}")
    print(f"{'Sentiment Score:':<20} {result['sentiment_score']}")
    print(f"{'RSI:':<20} {result['rsi']}")
    print(f"{'Volume:':<20} {result['volume']:,}")
    print(f"{'Price:':<20} ${result['price']}")
    print(f"\nReason: {result['reason']}")
    print(f"\nStatus: {result['status']}")

    # Test Case 3: Empty posts (neutral sentiment)
    print("\n" + "=" * 60)
    print("\nTest Case 3: MSFT with no Reddit posts (neutral)")
    print("-" * 60)

    ticker = "MSFT"
    reddit_posts = []

    print(f"Ticker: {ticker}")
    print(f"Reddit posts: {len(reddit_posts)} comments")
    print("\nGenerating signal...")

    result = generator.generate_signal(ticker, reddit_posts)

    print(f"\n{'Signal:':<20} {result['signal']}")
    print(f"{'Sentiment Score:':<20} {result['sentiment_score']}")
    print(f"{'RSI:':<20} {result['rsi']}")
    print(f"{'Volume:':<20} {result['volume']:,}")
    print(f"{'Price:':<20} ${result['price']}")
    print(f"\nReason: {result['reason']}")
    print(f"\nStatus: {result['status']}")

    print("\n" + "=" * 60)
    print("Test completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_signal_generation()
    except Exception as e:
        print(f"\nError during testing: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
