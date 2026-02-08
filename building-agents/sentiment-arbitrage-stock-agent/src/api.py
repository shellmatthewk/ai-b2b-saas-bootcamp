"""
Flask API Module

Exposes trading signal generation via RESTful endpoints.
Designed for integration with n8n and other automation tools.
"""

from flask import Flask, request, jsonify
from typing import Dict
import logging
import os
from dotenv import load_dotenv
import yfinance as yf

from src.signal_generator import SignalGenerator

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize signal generator with configuration from environment
signal_generator = SignalGenerator(
    sentiment_threshold=float(os.getenv("SENTIMENT_BUY_THRESHOLD", "0.7")),
    rsi_buy_threshold=float(os.getenv("RSI_BUY_THRESHOLD", "30")),
    rsi_period=int(os.getenv("RSI_PERIOD", "14"))
)


def validate_request_payload(data: Dict) -> tuple[bool, str]:
    """
    Validate the incoming request payload.

    Args:
        data: Request payload dictionary

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not data:
        return False, "Request body is empty"

    if "ticker" not in data:
        return False, "Missing required field: ticker"

    if "reddit_posts" not in data:
        return False, "Missing required field: reddit_posts"

    if not isinstance(data["ticker"], str):
        return False, "ticker must be a string"

    if not isinstance(data["reddit_posts"], list):
        return False, "reddit_posts must be a list"

    if not data["ticker"].strip():
        return False, "ticker cannot be empty"

    return True, ""


@app.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint for monitoring.

    Returns:
        JSON response with service status
    """
    return jsonify({
        "status": "healthy",
        "service": "trading-signal-service",
        "version": os.getenv("SERVICE_VERSION", "1.0.0")
    }), 200


@app.route("/api/signal", methods=["POST"])
def generate_signal():
    """
    Generate a trading signal based on sentiment and technical analysis.

    Request Body:
        {
            "ticker": "AAPL",
            "reddit_posts": ["Great stock!", "To the moon!", ...]
        }

    Returns:
        JSON response with trading signal and analysis details
    """
    try:
        # Parse request
        data = request.get_json()

        # Validate payload
        is_valid, error_message = validate_request_payload(data)
        if not is_valid:
            logger.warning(f"Invalid request: {error_message}")
            return jsonify({
                "status": "error",
                "error": error_message
            }), 400

        ticker = data["ticker"].strip().upper()
        reddit_posts = data["reddit_posts"]

        logger.info(f"Processing signal request for {ticker} with {len(reddit_posts)} posts")

        # Generate signal
        signal_result = signal_generator.generate_signal(ticker, reddit_posts)

        # Return appropriate status code based on result
        if signal_result["status"] == "error":
            status_code = 500
        elif signal_result["status"] == "partial":
            status_code = 206
        else:
            status_code = 200

        return jsonify(signal_result), status_code

    except Exception as e:
        logger.error(f"Unexpected error processing request: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "error": "Internal server error",
            "message": str(e)
        }), 500


@app.route("/api/config", methods=["GET"])
def get_configuration():
    """
    Get current service configuration.

    Returns:
        JSON response with configuration parameters
    """
    return jsonify({
        "sentiment_threshold": signal_generator.sentiment_threshold,
        "rsi_buy_threshold": signal_generator.rsi_buy_threshold,
        "rsi_period": signal_generator.technical_calculator.rsi_period,
        "service_version": os.getenv("SERVICE_VERSION", "1.0.0")
    }), 200


@app.route("/api/validate/<ticker>", methods=["GET"])
def validate_ticker(ticker):
    """
    Validate if a ticker symbol exists in yfinance.

    Use this as a filter node in n8n before calling /api/signal.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, TSLA, MSFT)

    Returns:
        200 with {"valid": True, "ticker": "AAPL", "price": 150.00} if valid
        404 with {"valid": False, "ticker": "XYZ"} if invalid
    """
    ticker = ticker.strip().upper()
    logger.info(f"Validating ticker: {ticker}")

    try:
        stock = yf.Ticker(ticker)
        # Use history with short period - more reliable than fast_info
        hist = stock.history(period="5d")

        if not hist.empty and len(hist) > 0:
            return jsonify({
                "valid": True,
                "ticker": ticker,
            }), 200
        else:
            return jsonify({
                "valid": False,
                "ticker": ticker,
            }), 404

    except Exception as e:
        logger.warning(f"Ticker validation failed for {ticker}: {e}")
        return jsonify({
            "valid": False,
            "ticker": ticker,
            "reason": str(e)
        }), 404


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "status": "error",
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({
        "status": "error",
        "error": "Method not allowed"
    }), 405


if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))
    debug = os.getenv("FLASK_ENV", "development") == "development"

    logger.info(f"Starting Trading Signal Service on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
