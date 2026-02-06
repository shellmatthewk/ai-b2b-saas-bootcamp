#!/usr/bin/env python3
"""
Python Client Example for Trading Signal Service

This script demonstrates how to integrate the trading signal service
into your own Python applications or automation workflows.

Two integration methods are shown:
1. Direct module usage (no API server needed)
2. HTTP API client (requires running server)
"""

import requests
import json
from typing import List, Dict, Optional


class TradingSignalClient:
    """
    HTTP client for the Trading Signal Service API.

    Use this when the service is running as a standalone API server.
    """

    def __init__(self, base_url: str = "http://localhost:5000"):
        """
        Initialize the client.

        Args:
            base_url: Base URL of the trading signal API
        """
        self.base_url = base_url.rstrip('/')

    def health_check(self) -> Dict:
        """
        Check if the service is healthy.

        Returns:
            Health status response
        """
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def get_config(self) -> Dict:
        """
        Get current service configuration.

        Returns:
            Configuration parameters
        """
        response = requests.get(f"{self.base_url}/api/config")
        response.raise_for_status()
        return response.json()

    def generate_signal(
        self,
        ticker: str,
        reddit_posts: List[str]
    ) -> Dict:
        """
        Generate a trading signal for a ticker.

        Args:
            ticker: Stock symbol (e.g., 'AAPL')
            reddit_posts: List of Reddit comment strings

        Returns:
            Signal response with analysis details

        Raises:
            requests.HTTPError: If the API request fails
        """
        payload = {
            "ticker": ticker,
            "reddit_posts": reddit_posts
        }

        response = requests.post(
            f"{self.base_url}/api/signal",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        # Don't raise for 500 errors (still return the error response)
        if response.status_code >= 400 and response.status_code < 500:
            response.raise_for_status()

        return response.json()


# Example 1: Using the HTTP API Client
def example_api_client():
    """Demonstrate using the HTTP API client."""
    print("=" * 70)
    print("Example 1: Using HTTP API Client")
    print("=" * 70)

    # Initialize client
    client = TradingSignalClient("http://localhost:5000")

    try:
        # Check service health
        print("\n1. Checking service health...")
        health = client.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Service: {health['service']}")
        print(f"   Version: {health['version']}")

        # Get configuration
        print("\n2. Getting service configuration...")
        config = client.get_config()
        print(f"   Sentiment Threshold: {config['sentiment_threshold']}")
        print(f"   RSI Buy Threshold: {config['rsi_buy_threshold']}")

        # Generate signal
        print("\n3. Generating signal for AAPL...")
        signal = client.generate_signal(
            ticker="AAPL",
            reddit_posts=[
                "Apple is crushing it this quarter!",
                "AAPL is the best tech stock right now",
                "Great earnings, buying more shares"
            ]
        )

        print(f"\n   Signal: {signal['signal']}")
        print(f"   Sentiment: {signal['sentiment_score']}")
        print(f"   RSI: {signal['rsi']}")
        print(f"   Price: ${signal['price']}")
        print(f"   Reason: {signal['reason']}")

    except requests.exceptions.ConnectionError:
        print("\n   ERROR: Could not connect to API server.")
        print("   Make sure the server is running: python run.py")
    except Exception as e:
        print(f"\n   ERROR: {e}")


# Example 2: Using Direct Module Import (No API Required)
def example_direct_import():
    """Demonstrate using the service modules directly."""
    print("\n" + "=" * 70)
    print("Example 2: Using Direct Module Import (No API Required)")
    print("=" * 70)

    try:
        # Import the signal generator
        from src.signal_generator import SignalGenerator

        print("\n1. Initializing SignalGenerator...")
        generator = SignalGenerator(
            sentiment_threshold=0.7,
            rsi_buy_threshold=30,
            rsi_period=14
        )
        print("   Generator initialized successfully")

        print("\n2. Generating signal for NVDA...")
        result = generator.generate_signal(
            ticker="NVDA",
            reddit_posts=[
                "NVIDIA is dominating the AI chip market",
                "Best GPU stock for the long term",
                "Jensen Huang is a visionary leader"
            ]
        )

        print(f"\n   Signal: {result['signal']}")
        print(f"   Sentiment: {result['sentiment_score']}")
        print(f"   RSI: {result['rsi']}")
        print(f"   Price: ${result['price']}")
        print(f"   Reason: {result['reason']}")

    except ImportError as e:
        print(f"\n   ERROR: Could not import modules: {e}")
        print("   Make sure you're in the project directory")


# Example 3: Batch Processing Multiple Tickers
def example_batch_processing():
    """Demonstrate batch processing of multiple tickers."""
    print("\n" + "=" * 70)
    print("Example 3: Batch Processing Multiple Tickers")
    print("=" * 70)

    try:
        from src.signal_generator import SignalGenerator

        # Define watchlist
        watchlist = {
            "AAPL": [
                "Apple is crushing it!",
                "Best tech stock right now"
            ],
            "TSLA": [
                "Tesla quality issues",
                "Overvalued stock"
            ],
            "MSFT": [
                "Microsoft is solid",
                "Good long-term hold"
            ],
            "NVDA": [
                "NVIDIA dominating AI",
                "Best GPU stock"
            ]
        }

        print(f"\n Processing {len(watchlist)} tickers...")

        generator = SignalGenerator()
        results = []

        for ticker, posts in watchlist.items():
            print(f"\n   Analyzing {ticker}...", end=" ")
            signal = generator.generate_signal(ticker, posts)
            results.append(signal)
            print(f"{signal['signal']}")

        # Summarize results
        buy_signals = [r for r in results if r['signal'] == 'BUY']
        hold_signals = [r for r in results if r['signal'] == 'HOLD']
        neutral_signals = [r for r in results if r['signal'] == 'NEUTRAL']

        print(f"\n Summary:")
        print(f"   BUY signals: {len(buy_signals)}")
        print(f"   HOLD signals: {len(hold_signals)}")
        print(f"   NEUTRAL signals: {len(neutral_signals)}")

        if buy_signals:
            print(f"\n   BUY Opportunities:")
            for signal in buy_signals:
                print(f"     - {signal['ticker']}: "
                      f"RSI={signal['rsi']:.1f}, "
                      f"Sentiment={signal['sentiment_score']:.2f}")

    except Exception as e:
        print(f"\n   ERROR: {e}")


# Example 4: Custom Signal Logic
def example_custom_logic():
    """Demonstrate using custom thresholds and logic."""
    print("\n" + "=" * 70)
    print("Example 4: Custom Signal Logic (Conservative Strategy)")
    print("=" * 70)

    try:
        from src.signal_generator import SignalGenerator

        # Create two generators with different strategies
        aggressive = SignalGenerator(
            sentiment_threshold=0.6,   # Lower threshold
            rsi_buy_threshold=35       # Higher threshold
        )

        conservative = SignalGenerator(
            sentiment_threshold=0.8,   # Higher threshold
            rsi_buy_threshold=25       # Lower threshold
        )

        ticker = "AAPL"
        posts = ["Apple is doing well", "Good company"]

        print(f"\n Comparing strategies for {ticker}:")

        print(f"\n   Aggressive Strategy (easier to trigger BUY):")
        print(f"     Sentiment > 0.6, RSI < 35")
        agg_result = aggressive.generate_signal(ticker, posts)
        print(f"     Result: {agg_result['signal']}")

        print(f"\n   Conservative Strategy (harder to trigger BUY):")
        print(f"     Sentiment > 0.8, RSI < 25")
        con_result = conservative.generate_signal(ticker, posts)
        print(f"     Result: {con_result['signal']}")

        print(f"\n   Analysis:")
        print(f"     Sentiment Score: {agg_result['sentiment_score']}")
        print(f"     RSI: {agg_result['rsi']}")
        print(f"     Same data, different signals based on strategy!")

    except Exception as e:
        print(f"\n   ERROR: {e}")


# Example 5: Error Handling
def example_error_handling():
    """Demonstrate proper error handling."""
    print("\n" + "=" * 70)
    print("Example 5: Error Handling")
    print("=" * 70)

    try:
        from src.signal_generator import SignalGenerator

        generator = SignalGenerator()

        # Test 1: Invalid ticker
        print("\n 1. Testing invalid ticker symbol...")
        result = generator.generate_signal("INVALIDTICKER123", ["Great stock"])
        print(f"     Signal: {result['signal']}")
        print(f"     Status: {result['status']}")
        if result['errors']:
            print(f"     Error: {result['errors'][0]['message']}")

        # Test 2: Empty posts
        print("\n 2. Testing empty reddit posts...")
        result = generator.generate_signal("AAPL", [])
        print(f"     Signal: {result['signal']}")
        print(f"     Sentiment: {result['sentiment_score']} (defaults to neutral)")

        # Test 3: Mixed empty and valid posts
        print("\n 3. Testing mixed empty and valid posts...")
        result = generator.generate_signal(
            "AAPL",
            ["Great stock!", "", "   ", "Love it!"]
        )
        details = result['metadata']['sentiment_details']
        print(f"     Total posts: {details['num_posts']}")
        print(f"     Valid posts: {details['valid_posts']}")
        print(f"     Sentiment: {result['sentiment_score']}")

    except Exception as e:
        print(f"\n   ERROR: {e}")
        import traceback
        traceback.print_exc()


# Example 6: Integration with Data Pipeline
def example_data_pipeline():
    """Demonstrate integration into a data pipeline."""
    print("\n" + "=" * 70)
    print("Example 6: Integration into Data Pipeline")
    print("=" * 70)

    try:
        from src.signal_generator import SignalGenerator

        # Simulate data pipeline
        print("\n Simulating a data pipeline workflow:")

        # Step 1: Fetch data (simulated)
        print("\n   [1] Fetching Reddit data...")
        reddit_data = {
            "AAPL": ["Apple rocks!", "Best stock ever"],
            "TSLA": ["Tesla is overvalued"],
            "NVDA": ["NVIDIA is amazing"]
        }
        print(f"       Found {len(reddit_data)} tickers with Reddit mentions")

        # Step 2: Generate signals
        print("\n   [2] Generating trading signals...")
        generator = SignalGenerator()
        signals = {}

        for ticker, posts in reddit_data.items():
            signals[ticker] = generator.generate_signal(ticker, posts)
            print(f"       {ticker}: {signals[ticker]['signal']}")

        # Step 3: Filter for actionable signals
        print("\n   [3] Filtering for BUY signals...")
        buy_opportunities = {
            ticker: signal for ticker, signal in signals.items()
            if signal['signal'] == 'BUY' and signal['status'] == 'success'
        }
        print(f"       Found {len(buy_opportunities)} BUY opportunities")

        # Step 4: Export results
        print("\n   [4] Exporting results...")
        output_file = "/tmp/trading_signals.json"
        with open(output_file, 'w') as f:
            json.dump(signals, f, indent=2)
        print(f"       Saved to: {output_file}")

        # Step 5: Generate alert (simulated)
        print("\n   [5] Generating alerts...")
        for ticker, signal in buy_opportunities.items():
            print(f"       ALERT: BUY opportunity for {ticker}")
            print(f"              RSI: {signal['rsi']:.1f}")
            print(f"              Sentiment: {signal['sentiment_score']:.2f}")
            print(f"              Reason: {signal['reason'][:60]}...")

        print("\n   Pipeline completed successfully!")

    except Exception as e:
        print(f"\n   ERROR: {e}")
        import traceback
        traceback.print_exc()


# Main execution
def main():
    """Run all examples."""
    print("\n")
    print("*" * 70)
    print("*" + " TRADING SIGNAL SERVICE - PYTHON CLIENT EXAMPLES".center(68) + "*")
    print("*" * 70)

    # Run examples that don't require API server
    example_direct_import()
    example_batch_processing()
    example_custom_logic()
    example_error_handling()
    example_data_pipeline()

    # Try API client example (may fail if server not running)
    example_api_client()

    print("\n" + "*" * 70)
    print("*" + " EXAMPLES COMPLETED".center(68) + "*")
    print("*" * 70)
    print("\nNext Steps:")
    print("  - Adapt these examples for your use case")
    print("  - Integrate into your existing workflows")
    print("  - Customize thresholds for your strategy")
    print("  - Add additional data sources")
    print("\n")


if __name__ == "__main__":
    main()
