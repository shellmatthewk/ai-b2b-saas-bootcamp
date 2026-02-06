#!/bin/bash
# Test script for the Trading Signal API
# Run this after starting the service with: python run.py

API_URL="http://localhost:5000"

echo "=========================================="
echo "Trading Signal Service API Test"
echo "=========================================="
echo ""

# Test 1: Health Check
echo "Test 1: Health Check"
echo "--------------------"
curl -s "${API_URL}/health" | python -m json.tool
echo ""
echo ""

# Test 2: Configuration
echo "Test 2: Get Configuration"
echo "-------------------------"
curl -s "${API_URL}/api/config" | python -m json.tool
echo ""
echo ""

# Test 3: Generate Signal for AAPL with bullish sentiment
echo "Test 3: AAPL with Bullish Sentiment"
echo "------------------------------------"
curl -s -X POST "${API_URL}/api/signal" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "reddit_posts": [
      "Apple is crushing it! Best tech stock ever!",
      "AAPL to the moon! Tim Cook delivers again!",
      "Just bought more Apple shares, feeling bullish",
      "iPhone sales are incredible this quarter",
      "Love my MacBook, Apple quality is unmatched"
    ]
  }' | python -m json.tool
echo ""
echo ""

# Test 4: Generate Signal for TSLA with negative sentiment
echo "Test 4: TSLA with Bearish Sentiment"
echo "------------------------------------"
curl -s -X POST "${API_URL}/api/signal" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "TSLA",
    "reddit_posts": [
      "Tesla quality is getting worse",
      "Overvalued, time to sell",
      "Not impressed with recent updates"
    ]
  }' | python -m json.tool
echo ""
echo ""

# Test 5: Invalid request (missing ticker)
echo "Test 5: Invalid Request (Missing Ticker)"
echo "----------------------------------------"
curl -s -X POST "${API_URL}/api/signal" \
  -H "Content-Type: application/json" \
  -d '{
    "reddit_posts": ["Some comment"]
  }' | python -m json.tool
echo ""
echo ""

# Test 6: Invalid request (empty ticker)
echo "Test 6: Invalid Request (Empty Ticker)"
echo "--------------------------------------"
curl -s -X POST "${API_URL}/api/signal" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "",
    "reddit_posts": ["Some comment"]
  }' | python -m json.tool
echo ""
echo ""

echo "=========================================="
echo "Tests completed!"
echo "=========================================="
