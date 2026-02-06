#!/usr/bin/env python3
"""
Demonstration script showing how to use the trading signal service.

This script demonstrates:
1. Direct usage of the SignalGenerator (no API required)
2. How to interpret different signal types
3. How to access detailed metadata
4. Error handling scenarios
"""

from src.signal_generator import SignalGenerator
import json


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_signal_result(result: dict):
    """Print signal result in a formatted way."""
    print(f"\nSignal Type: {result['signal']}")
    print(f"Ticker: {result['ticker']}")
    print(f"Status: {result['status']}")
    print(f"\nMetrics:")
    print(f"  Sentiment Score: {result['sentiment_score']} (0=negative, 1=positive)")
    print(f"  RSI: {result['rsi']} (0-100, <30=oversold, >70=overbought)")
    print(f"  Volume: {result['volume']:,}" if result['volume'] else "  Volume: N/A")
    print(f"  Price: ${result['price']}" if result['price'] else "  Price: N/A")
    print(f"\nReason:")
    print(f"  {result['reason']}")
    print(f"\nSentiment Details:")
    print(f"  Posts Analyzed: {result['metadata']['sentiment_details']['num_posts']}")
    print(f"  Valid Posts: {result['metadata']['sentiment_details']['valid_posts']}")
    print(f"  Raw Polarity: {result['metadata']['sentiment_details']['raw_polarity']}")

    if result['errors']:
        print(f"\nErrors:")
        for error in result['errors']:
            print(f"  [{error['type']}] {error['message']}")


def demo_buy_signal():
    """Demonstrate a BUY signal scenario."""
    print_section("Example 1: BUY Signal - High Sentiment + Oversold RSI")

    generator = SignalGenerator(
        sentiment_threshold=0.7,
        rsi_buy_threshold=30,
        rsi_period=14
    )

    ticker = "AAPL"
    reddit_posts = [
        "Apple absolutely crushing it with iPhone sales!",
        "AAPL is the best tech stock right now, buying more shares",
        "Amazing earnings report, this company is unstoppable",
        "Tim Cook is a genius, love this stock",
        "Apple services revenue is phenomenal, very bullish"
    ]

    print(f"\nInput:")
    print(f"  Ticker: {ticker}")
    print(f"  Reddit Posts: {len(reddit_posts)} highly positive comments")
    print(f"\nSample posts:")
    for i, post in enumerate(reddit_posts[:3], 1):
        print(f"  {i}. \"{post}\"")

    print(f"\nGenerating signal...")
    result = generator.generate_signal(ticker, reddit_posts)
    print_signal_result(result)

    print(f"\nInterpretation:")
    if result['signal'] == 'BUY':
        print(f"  This is a STRONG BUY signal because:")
        print(f"  - High positive sentiment ({result['sentiment_score']}) indicates market enthusiasm")
        print(f"  - Low RSI ({result['rsi']}) suggests the stock is oversold")
        print(f"  - Combination of both factors suggests a potential buying opportunity")

    return result


def demo_hold_signal():
    """Demonstrate a HOLD signal scenario."""
    print_section("Example 2: HOLD Signal - Positive Sentiment but RSI Not Oversold")

    generator = SignalGenerator(
        sentiment_threshold=0.7,
        rsi_buy_threshold=30,
        rsi_period=14
    )

    ticker = "NVDA"
    reddit_posts = [
        "NVIDIA is dominating the AI chip market",
        "Best GPU stock for the long term",
        "Jensen Huang is incredible, bullish on NVDA"
    ]

    print(f"\nInput:")
    print(f"  Ticker: {ticker}")
    print(f"  Reddit Posts: {len(reddit_posts)} positive comments")

    print(f"\nGenerating signal...")
    result = generator.generate_signal(ticker, reddit_posts)
    print_signal_result(result)

    print(f"\nInterpretation:")
    if result['signal'] == 'HOLD':
        print(f"  This is a HOLD signal because:")
        print(f"  - Sentiment is positive, showing market interest")
        print(f"  - But RSI is not oversold, so no clear entry point")
        print(f"  - Consider waiting for a better technical setup")

    return result


def demo_neutral_signal():
    """Demonstrate a NEUTRAL signal scenario."""
    print_section("Example 3: NEUTRAL Signal - Low Sentiment")

    generator = SignalGenerator(
        sentiment_threshold=0.7,
        rsi_buy_threshold=30,
        rsi_period=14
    )

    ticker = "MSFT"
    reddit_posts = [
        "Microsoft is okay I guess",
        "Not sure about this stock",
        "MSFT has some issues with competition"
    ]

    print(f"\nInput:")
    print(f"  Ticker: {ticker}")
    print(f"  Reddit Posts: {len(reddit_posts)} neutral/negative comments")

    print(f"\nGenerating signal...")
    result = generator.generate_signal(ticker, reddit_posts)
    print_signal_result(result)

    print(f"\nInterpretation:")
    if result['signal'] == 'NEUTRAL':
        print(f"  This is a NEUTRAL signal because:")
        print(f"  - Sentiment is not strong enough to justify entry")
        print(f"  - No clear trading opportunity at this time")
        print(f"  - Consider monitoring for changes in sentiment or technicals")

    return result


def demo_empty_posts():
    """Demonstrate handling of empty posts."""
    print_section("Example 4: Empty Posts - No Sentiment Data")

    generator = SignalGenerator()

    ticker = "TSLA"
    reddit_posts = []  # No posts

    print(f"\nInput:")
    print(f"  Ticker: {ticker}")
    print(f"  Reddit Posts: {len(reddit_posts)} (empty)")

    print(f"\nGenerating signal...")
    result = generator.generate_signal(ticker, reddit_posts)
    print_signal_result(result)

    print(f"\nInterpretation:")
    print(f"  When no posts are provided:")
    print(f"  - Sentiment defaults to neutral (0.5)")
    print(f"  - Signal is based primarily on technical indicators")

    return result


def demo_custom_thresholds():
    """Demonstrate using custom thresholds."""
    print_section("Example 5: Custom Thresholds - More Conservative Settings")

    # More conservative settings
    generator = SignalGenerator(
        sentiment_threshold=0.8,   # Higher sentiment required
        rsi_buy_threshold=25,      # Lower RSI required (more oversold)
        rsi_period=14
    )

    ticker = "AAPL"
    reddit_posts = [
        "Apple is doing well",
        "Positive outlook for AAPL",
        "Good company, good stock"
    ]

    print(f"\nCustom Configuration:")
    print(f"  Sentiment Threshold: 0.8 (vs default 0.7)")
    print(f"  RSI Buy Threshold: 25 (vs default 30)")
    print(f"  This makes the signal MORE CONSERVATIVE (fewer BUY signals)")

    print(f"\nInput:")
    print(f"  Ticker: {ticker}")
    print(f"  Reddit Posts: {len(reddit_posts)} moderately positive comments")

    print(f"\nGenerating signal...")
    result = generator.generate_signal(ticker, reddit_posts)
    print_signal_result(result)

    return result


def demo_json_export():
    """Demonstrate exporting signal as JSON."""
    print_section("Example 6: JSON Export - Ready for API Integration")

    generator = SignalGenerator()
    result = generator.generate_signal(
        "AAPL",
        ["Great stock!", "Love Apple products"]
    )

    print(f"\nComplete JSON Response:")
    print(json.dumps(result, indent=2))

    print(f"\n\nThis JSON format is:")
    print(f"  - Ready for n8n HTTP Request nodes")
    print(f"  - Compatible with any REST API client")
    print(f"  - Includes all metadata for auditing")
    print(f"  - Follows standardized schema for consistency")

    return result


def demo_programmatic_usage():
    """Demonstrate programmatic usage patterns."""
    print_section("Example 7: Programmatic Usage Patterns")

    generator = SignalGenerator()

    # Simulate processing multiple tickers
    watchlist = [
        ("AAPL", ["Apple is amazing!", "Best stock ever"]),
        ("TSLA", ["Tesla quality issues", "Overvalued"]),
        ("MSFT", ["Solid company", "Good long-term hold"])
    ]

    buy_signals = []
    hold_signals = []
    neutral_signals = []

    print(f"\nProcessing watchlist of {len(watchlist)} tickers...")

    for ticker, posts in watchlist:
        result = generator.generate_signal(ticker, posts)

        if result['status'] == 'success':
            if result['signal'] == 'BUY':
                buy_signals.append(result)
            elif result['signal'] == 'HOLD':
                hold_signals.append(result)
            else:
                neutral_signals.append(result)

    print(f"\n\nResults Summary:")
    print(f"  BUY signals: {len(buy_signals)}")
    print(f"  HOLD signals: {len(hold_signals)}")
    print(f"  NEUTRAL signals: {len(neutral_signals)}")

    if buy_signals:
        print(f"\n\nBUY Opportunities:")
        for signal in buy_signals:
            print(f"  - {signal['ticker']}: RSI={signal['rsi']}, Sentiment={signal['sentiment_score']}")

    return {
        'buy': buy_signals,
        'hold': hold_signals,
        'neutral': neutral_signals
    }


def main():
    """Run all demonstrations."""
    print("\n")
    print("*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  TRADING SIGNAL SERVICE - COMPREHENSIVE DEMONSTRATION".center(68) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)

    try:
        # Run demonstrations
        demo_buy_signal()
        demo_hold_signal()
        demo_neutral_signal()
        demo_empty_posts()
        demo_custom_thresholds()
        demo_json_export()
        demo_programmatic_usage()

        # Final summary
        print_section("Summary")
        print(f"""
The Trading Signal Service provides:

1. MODULAR DESIGN
   - Separate modules for sentiment, technical analysis, and signal logic
   - Easy to test, extend, and maintain
   - Each component can be used independently

2. ROBUST ERROR HANDLING
   - Graceful handling of missing data
   - Clear error messages
   - Never crashes on bad input

3. STANDARDIZED OUTPUT
   - Consistent JSON schema
   - All responses include metadata
   - Ready for automation workflows

4. FLEXIBLE CONFIGURATION
   - Adjust thresholds via environment variables
   - Customize signal logic
   - Support for different trading strategies

5. PRODUCTION READY
   - Comprehensive logging
   - Health check endpoints
   - Docker and Gunicorn compatible

Next Steps:
  - Install dependencies: pip install -r requirements.txt
  - Download TextBlob data: python -m textblob.download_corpora
  - Test the service: python test_signal.py
  - Start the API: python run.py
  - Integrate with n8n: See SETUP_AND_USAGE.md

For API usage, see:
  - README.md (complete documentation)
  - SETUP_AND_USAGE.md (setup guide)
  - examples/ directory (integration examples)
        """)

        print("\n" + "*" * 70)
        print("*" + "  ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY".center(68) + "*")
        print("*" * 70 + "\n")

    except Exception as e:
        print(f"\n\nERROR during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
