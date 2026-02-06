#!/bin/bash
#
# Trading Signal Service - cURL Examples
#
# This script demonstrates how to interact with the trading signal API
# using cURL commands. These can be adapted for any HTTP client.
#
# Prerequisites:
#   - Service must be running (python run.py)
#   - jq installed for pretty JSON output (optional)

# Configuration
API_BASE="http://localhost:5000"

echo "======================================================================="
echo "  Trading Signal Service - API Examples"
echo "======================================================================="
echo ""

# Example 1: Health Check
echo "Example 1: Health Check"
echo "-----------------------------------------------------------------------"
echo "GET ${API_BASE}/health"
echo ""
curl -s "${API_BASE}/health" | jq '.' 2>/dev/null || curl -s "${API_BASE}/health"
echo ""
echo ""

# Example 2: Get Configuration
echo "Example 2: Get Current Configuration"
echo "-----------------------------------------------------------------------"
echo "GET ${API_BASE}/api/config"
echo ""
curl -s "${API_BASE}/api/config" | jq '.' 2>/dev/null || curl -s "${API_BASE}/api/config"
echo ""
echo ""

# Example 3: Generate Signal - Bullish Scenario
echo "Example 3: Generate Signal - Bullish Sentiment"
echo "-----------------------------------------------------------------------"
echo "POST ${API_BASE}/api/signal"
echo ""
echo "Request Body:"
cat << 'EOF'
{
  "ticker": "AAPL",
  "reddit_posts": [
    "Apple is crushing it this quarter!",
    "AAPL to the moon! Best tech stock!",
    "Great earnings, buying more shares",
    "iPhone sales are phenomenal",
    "Love Apple products, bullish on the stock"
  ]
}
EOF
echo ""
echo "Response:"
curl -s -X POST "${API_BASE}/api/signal" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "reddit_posts": [
      "Apple is crushing it this quarter!",
      "AAPL to the moon! Best tech stock!",
      "Great earnings, buying more shares",
      "iPhone sales are phenomenal",
      "Love Apple products, bullish on the stock"
    ]
  }' | jq '.' 2>/dev/null || curl -s -X POST "${API_BASE}/api/signal" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "reddit_posts": [
      "Apple is crushing it this quarter!",
      "AAPL to the moon! Best tech stock!",
      "Great earnings, buying more shares",
      "iPhone sales are phenomenal",
      "Love Apple products, bullish on the stock"
    ]
  }'
echo ""
echo ""

# Example 4: Generate Signal - Bearish Scenario
echo "Example 4: Generate Signal - Bearish Sentiment"
echo "-----------------------------------------------------------------------"
echo "POST ${API_BASE}/api/signal"
echo ""
echo "Request Body:"
cat << 'EOF'
{
  "ticker": "TSLA",
  "reddit_posts": [
    "Tesla quality issues getting worse",
    "Overvalued, time to sell",
    "Not impressed with recent developments",
    "Competition is catching up fast"
  ]
}
EOF
echo ""
echo "Response:"
curl -s -X POST "${API_BASE}/api/signal" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "TSLA",
    "reddit_posts": [
      "Tesla quality issues getting worse",
      "Overvalued, time to sell",
      "Not impressed with recent developments",
      "Competition is catching up fast"
    ]
  }' | jq '.' 2>/dev/null || curl -s -X POST "${API_BASE}/api/signal" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "TSLA",
    "reddit_posts": [
      "Tesla quality issues getting worse",
      "Overvalued, time to sell",
      "Not impressed with recent developments",
      "Competition is catching up fast"
    ]
  }'
echo ""
echo ""

# Example 5: Generate Signal - Neutral Scenario
echo "Example 5: Generate Signal - No Sentiment Data"
echo "-----------------------------------------------------------------------"
echo "POST ${API_BASE}/api/signal"
echo ""
echo "Request Body:"
cat << 'EOF'
{
  "ticker": "MSFT",
  "reddit_posts": []
}
EOF
echo ""
echo "Response:"
curl -s -X POST "${API_BASE}/api/signal" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "MSFT",
    "reddit_posts": []
  }' | jq '.' 2>/dev/null || curl -s -X POST "${API_BASE}/api/signal" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "MSFT",
    "reddit_posts": []
  }'
echo ""
echo ""

# Example 6: Error Handling - Missing Ticker
echo "Example 6: Error Handling - Missing Required Field"
echo "-----------------------------------------------------------------------"
echo "POST ${API_BASE}/api/signal"
echo ""
echo "Request Body:"
cat << 'EOF'
{
  "reddit_posts": ["Some comment"]
}
EOF
echo ""
echo "Response:"
curl -s -X POST "${API_BASE}/api/signal" \
  -H "Content-Type: application/json" \
  -d '{
    "reddit_posts": ["Some comment"]
  }' | jq '.' 2>/dev/null || curl -s -X POST "${API_BASE}/api/signal" \
  -H "Content-Type: application/json" \
  -d '{
    "reddit_posts": ["Some comment"]
  }'
echo ""
echo ""

# Example 7: Error Handling - Invalid Ticker
echo "Example 7: Error Handling - Invalid Ticker Symbol"
echo "-----------------------------------------------------------------------"
echo "POST ${API_BASE}/api/signal"
echo ""
echo "Request Body:"
cat << 'EOF'
{
  "ticker": "INVALID123",
  "reddit_posts": ["Great stock!"]
}
EOF
echo ""
echo "Response:"
curl -s -X POST "${API_BASE}/api/signal" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "INVALID123",
    "reddit_posts": ["Great stock!"]
  }' | jq '.' 2>/dev/null || curl -s -X POST "${API_BASE}/api/signal" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "INVALID123",
    "reddit_posts": ["Great stock!"]
  }'
echo ""
echo ""

# Example 8: Extract Specific Fields
echo "Example 8: Extract Specific Fields (using jq)"
echo "-----------------------------------------------------------------------"
echo "Extract just signal, ticker, sentiment, and RSI:"
echo ""
curl -s -X POST "${API_BASE}/api/signal" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "NVDA",
    "reddit_posts": [
      "NVIDIA is dominating AI chips",
      "Best GPU stock for long term"
    ]
  }' | jq '{signal, ticker, sentiment_score, rsi, price}' 2>/dev/null || echo "Install jq for field extraction"
echo ""
echo ""

echo "======================================================================="
echo "  Examples Complete"
echo "======================================================================="
echo ""
echo "Usage Notes:"
echo "  - Replace 'localhost:5000' with your server address"
echo "  - Install jq for pretty JSON formatting: brew install jq"
echo "  - Use -v flag with curl for verbose output: curl -v ..."
echo "  - Save responses to file: curl ... > response.json"
echo ""
echo "For n8n integration, use the HTTP Request node with:"
echo "  - Method: POST"
echo "  - URL: http://your-server:5000/api/signal"
echo "  - Body: JSON format as shown in examples above"
echo ""
