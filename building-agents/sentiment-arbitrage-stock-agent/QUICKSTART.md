# Quick Start Guide

Get the trading signal service up and running in 3 minutes.

## 1. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Download TextBlob corpora (required for sentiment analysis)
python -m textblob.download_corpora
```

## 2. Test the Service (Standalone)

Test without starting the server:

```bash
python test_signal.py
```

This will generate signals for AAPL, TSLA, and MSFT to verify everything works.

## 3. Start the API Server

```bash
python run.py
```

You should see:
```
Starting Trading Signal Service on http://0.0.0.0:5000
Debug mode: True

Available endpoints:
  - POST http://0.0.0.0:5000/api/signal
  - GET  http://0.0.0.0:5000/health
  - GET  http://0.0.0.0:5000/api/config
```

## 4. Test the API

In a new terminal window:

```bash
# Make the test script executable (first time only)
chmod +x examples/test_api.sh

# Run API tests
./examples/test_api.sh
```

Or test manually with curl:

```bash
curl -X POST http://localhost:5000/api/signal \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "reddit_posts": [
      "Apple is killing it!",
      "AAPL to the moon!",
      "Best tech stock ever"
    ]
  }'
```

## 5. Use in n8n

1. Add an **HTTP Request** node
2. Set **Method**: POST
3. Set **URL**: `http://localhost:5000/api/signal`
4. Set **Body Content Type**: JSON
5. Set **Body**:
   ```json
   {
     "ticker": "{{ $json.ticker }}",
     "reddit_posts": {{ $json.comments }}
   }
   ```

See `/examples/n8n_example_payload.json` for a complete example.

## Understanding the Output

```json
{
  "signal": "BUY",           // BUY, HOLD, or NEUTRAL
  "ticker": "AAPL",
  "sentiment_score": 0.85,   // 0-1 scale (higher = more positive)
  "rsi": 28.5,               // 0-100 (< 30 = oversold)
  "volume": 85234000,
  "price": 178.45,
  "reason": "Explanation...",
  "timestamp": "2026-02-05T12:34:56.789Z"
}
```

### Signal Logic

- **BUY**: `sentiment > 0.7` AND `RSI < 30`
- **HOLD**: One condition met but not both
- **NEUTRAL**: Neither condition met

## Troubleshooting

### "ModuleNotFoundError: No module named 'textblob'"
Run: `pip install -r requirements.txt`

### "Resource punkt not found"
Run: `python -m textblob.download_corpora`

### "No data returned for ticker"
- Check if the ticker symbol is valid
- Ensure you have internet connectivity
- Try a different ticker (AAPL, MSFT, TSLA)

### "Connection refused" when testing API
Make sure the server is running: `python run.py`

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Customize thresholds in `.env` file
- Integrate with your n8n workflows
- Add more technical indicators in `src/technical_indicators.py`

## Configuration

Edit `.env` to customize:

```bash
SENTIMENT_BUY_THRESHOLD=0.7  # Sentiment threshold (0-1)
RSI_BUY_THRESHOLD=30         # RSI threshold (0-100)
RSI_PERIOD=14                # RSI calculation period
FLASK_PORT=5000              # API port
```
