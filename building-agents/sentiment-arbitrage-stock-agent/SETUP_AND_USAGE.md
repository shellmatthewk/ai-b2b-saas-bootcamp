# Trading Signal Service - Setup and Usage Guide

## Quick Start

This is a complete, production-ready trading signal service that combines Reddit sentiment analysis with technical indicators (RSI, volume) to generate BUY/HOLD/NEUTRAL signals.

### 1. Install Dependencies

```bash
cd /Users/matthewkshell/ai-b2b-saas-bootcamp/building-agents/sentiment-arbitrage-stock-agent

# Install Python packages
pip install -r requirements.txt

# Download TextBlob corpora (required for sentiment analysis)
python -m textblob.download_corpora
```

### 2. Configure Environment (Optional)

The service works out-of-the-box with sensible defaults. To customize:

```bash
cp .env.example .env
# Edit .env to adjust thresholds
```

### 3. Test the Service

Before starting the API, test the core functionality:

```bash
python test_signal.py
```

This will test signal generation for AAPL, TSLA, and MSFT with different sentiment scenarios.

### 4. Start the API Server

```bash
python run.py
```

The service will start on `http://0.0.0.0:5000`

---

## API Usage Examples

### Generate a Trading Signal

**Request:**
```bash
curl -X POST http://localhost:5000/api/signal \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "reddit_posts": [
      "Apple is crushing it this quarter!",
      "AAPL to the moon!",
      "Best tech stock right now"
    ]
  }'
```

**Response:**
```json
{
  "signal": "BUY",
  "ticker": "AAPL",
  "sentiment_score": 0.82,
  "rsi": 28.5,
  "volume": 85234000,
  "price": 178.45,
  "reason": "Strong bullish sentiment (0.82 > 0.7) combined with oversold conditions (RSI 28.5 < 30). Potential buying opportunity.",
  "timestamp": "2026-02-05T12:34:56.789Z",
  "status": "success",
  "metadata": {
    "sentiment_analyzer": "TextBlob",
    "service_version": "1.0.0",
    "rsi_period": 14,
    "sentiment_threshold": 0.7,
    "rsi_buy_threshold": 30,
    "sentiment_details": {
      "num_posts": 3,
      "valid_posts": 3,
      "raw_polarity": 0.64
    },
    "technical_details": {
      "avg_volume": 82500000,
      "data_points": 60
    }
  },
  "errors": []
}
```

### Check Service Health

```bash
curl http://localhost:5000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "trading-signal-service",
  "version": "1.0.0"
}
```

### View Configuration

```bash
curl http://localhost:5000/api/config
```

**Response:**
```json
{
  "sentiment_threshold": 0.7,
  "rsi_buy_threshold": 30,
  "rsi_period": 14,
  "service_version": "1.0.0"
}
```

---

## Signal Logic

The service generates signals based on two key factors:

### BUY Signal
- **Condition**: Sentiment > 0.7 AND RSI < 30
- **Interpretation**: Strong positive sentiment + oversold technical conditions = potential buying opportunity

### HOLD Signal
- **Condition**: Either sentiment OR RSI condition met, but not both
- **Interpretation**: One factor is favorable, but waiting for confirmation from the other

### NEUTRAL Signal
- **Condition**: Neither condition met
- **Interpretation**: No clear trading opportunity

---

## Integration with n8n

### Method 1: HTTP Request Node

1. Add **HTTP Request** node
2. Configure:
   - **Method**: POST
   - **URL**: `http://your-server:5000/api/signal`
   - **Body Content Type**: JSON
   - **JSON/RAW Parameters**:
     ```json
     {
       "ticker": "{{ $json.ticker }}",
       "reddit_posts": {{ $json.comments }}
     }
     ```

### Method 2: Webhook Trigger → Signal Service

```
Webhook (receive ticker + posts)
  ↓
HTTP Request (call /api/signal)
  ↓
Switch (route by signal type)
  ├─ BUY → Send alert / Execute trade
  ├─ HOLD → Log for monitoring
  └─ NEUTRAL → No action
```

### Example n8n Workflow

```json
{
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "trading-signal",
        "responseMode": "responseNode"
      }
    },
    {
      "name": "Get Trading Signal",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "http://localhost:5000/api/signal",
        "jsonParameters": true,
        "options": {},
        "bodyParametersJson": "={{ JSON.stringify($json) }}"
      }
    },
    {
      "name": "Route by Signal",
      "type": "n8n-nodes-base.switch",
      "parameters": {
        "rules": {
          "rules": [
            {
              "conditions": {
                "conditions": [
                  {
                    "value1": "={{ $json.signal }}",
                    "operation": "equals",
                    "value2": "BUY"
                  }
                ]
              }
            }
          ]
        }
      }
    }
  ]
}
```

---

## Architecture Overview

```
├── src/
│   ├── sentiment_analyzer.py      # TextBlob-based sentiment scoring
│   ├── technical_indicators.py    # RSI calculation + yfinance integration
│   ├── signal_generator.py        # Core signal logic (combines sentiment + technicals)
│   └── api.py                     # Flask REST API endpoints
├── run.py                         # Main entry point
├── test_signal.py                 # Standalone testing script
├── requirements.txt               # Python dependencies
├── .env.example                   # Configuration template
└── README.md                      # Full documentation
```

### Module Responsibilities

**sentiment_analyzer.py**
- Analyzes text sentiment using TextBlob
- Normalizes sentiment from [-1, 1] to [0, 1] scale
- Aggregates sentiment across multiple posts

**technical_indicators.py**
- Fetches stock data from yfinance
- Calculates RSI (Relative Strength Index)
- Provides volume and price data

**signal_generator.py**
- Coordinates sentiment + technical analysis
- Applies signal logic (BUY/HOLD/NEUTRAL)
- Returns standardized JSON response

**api.py**
- Exposes Flask REST endpoints
- Handles request validation
- Provides health check and config endpoints

---

## Testing

### Standalone Test (No Server Required)

```bash
python test_signal.py
```

This tests signal generation for:
- AAPL (bullish sentiment)
- TSLA (bearish sentiment)
- MSFT (neutral sentiment)

### API Test (Server Running)

```bash
# Terminal 1: Start server
python run.py

# Terminal 2: Test API
curl -X POST http://localhost:5000/api/signal \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "NVDA",
    "reddit_posts": [
      "NVIDIA is dominating AI chips",
      "Best GPU stock, buying more",
      "Jensen Huang is a visionary"
    ]
  }'
```

---

## Configuration Parameters

All parameters can be customized via `.env` file:

```bash
# Flask Configuration
FLASK_PORT=5000              # API port
FLASK_HOST=0.0.0.0          # Bind address (0.0.0.0 = all interfaces)
FLASK_ENV=development       # development or production

# Service Configuration
SERVICE_VERSION=1.0.0       # Version identifier
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR

# Technical Indicator Parameters
RSI_PERIOD=14               # RSI calculation period (default: 14 days)
RSI_BUY_THRESHOLD=30        # RSI threshold for BUY signals (0-100)

# Sentiment Parameters
SENTIMENT_BUY_THRESHOLD=0.7 # Sentiment threshold for BUY signals (0-1)
```

### Adjusting Signal Sensitivity

**More aggressive (more BUY signals):**
```bash
RSI_BUY_THRESHOLD=35         # Higher RSI threshold
SENTIMENT_BUY_THRESHOLD=0.6  # Lower sentiment requirement
```

**More conservative (fewer BUY signals):**
```bash
RSI_BUY_THRESHOLD=25         # Lower RSI threshold
SENTIMENT_BUY_THRESHOLD=0.75 # Higher sentiment requirement
```

---

## Response Schema

All signal responses follow this standardized format:

```typescript
{
  signal: "BUY" | "HOLD" | "NEUTRAL" | "ERROR",
  ticker: string,              // Stock symbol (uppercase)
  sentiment_score: number,     // 0-1 scale (0=negative, 1=positive)
  rsi: number | null,          // 0-100 (null if error)
  volume: number | null,       // Current trading volume
  price: number | null,        // Current stock price
  reason: string,              // Human-readable explanation
  timestamp: string,           // ISO 8601 format
  status: "success" | "partial" | "error",
  metadata: {
    sentiment_analyzer: string,
    service_version: string,
    rsi_period: number,
    sentiment_threshold: number,
    rsi_buy_threshold: number,
    sentiment_details: {
      num_posts: number,
      valid_posts: number,
      raw_polarity: number
    },
    technical_details: {
      avg_volume: number,
      data_points: number
    }
  },
  errors: Array<{type: string, message: string}>
}
```

---

## Error Handling

The service handles various error scenarios gracefully:

### Invalid Ticker
```json
{
  "signal": "ERROR",
  "ticker": "INVALID",
  "sentiment_score": 0.65,
  "rsi": null,
  "volume": null,
  "price": null,
  "reason": "Unable to fetch technical data: No data returned for ticker INVALID",
  "status": "error",
  "errors": [
    {
      "type": "technical_data_error",
      "message": "No data returned for ticker INVALID"
    }
  ]
}
```

### Missing Required Fields
```json
{
  "status": "error",
  "error": "Missing required field: ticker"
}
```

### Empty Reddit Posts
- Defaults to neutral sentiment (0.5)
- Still generates signal based on technical indicators

---

## Production Deployment

### Using Gunicorn (Recommended)

```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 src.api:app
```

### Using Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m textblob.download_corpora

COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src.api:app"]
```

### Environment Variables for Production

```bash
FLASK_ENV=production
LOG_LEVEL=WARNING
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

---

## Extending the Service

### Add New Technical Indicators

1. Add calculation method to `TechnicalIndicatorCalculator`:
```python
def calculate_macd(self, prices: pd.Series) -> Dict:
    """Calculate MACD indicator."""
    # Implementation
    pass
```

2. Update `analyze_ticker()` to include it:
```python
def analyze_ticker(self, ticker: str) -> Dict:
    # ... existing code ...
    macd = self.calculate_macd(data['Close'])
    return {
        # ... existing fields ...
        "macd": macd
    }
```

3. Update signal logic in `SignalGenerator`

### Add Sentiment Sources

Create new analyzer classes following the same pattern:
```python
class TwitterSentimentAnalyzer:
    def analyze_tweets(self, tweets: List[str]) -> float:
        # Implementation
        pass
```

---

## Troubleshooting

### Issue: "No module named 'textblob'"
**Solution**: Run `pip install -r requirements.txt` and `python -m textblob.download_corpora`

### Issue: "No data returned for ticker"
**Solution**:
- Verify ticker symbol is correct (use uppercase)
- Check if market is open
- Ensure internet connection is available

### Issue: "RSI calculation failed"
**Solution**: Some stocks may not have enough historical data. The service requires at least 15 days of trading data.

### Issue: Port 5000 already in use
**Solution**: Either kill the process using port 5000 or change `FLASK_PORT` in `.env`

---

## Performance Considerations

- **yfinance API**: Typically takes 1-3 seconds per request
- **TextBlob**: Processes ~100 posts in <100ms
- **Caching**: Consider implementing Redis caching for frequently queried tickers
- **Rate Limiting**: yfinance has no official rate limits, but be respectful

---

## Security Notes

- This service does NOT implement authentication (add API keys for production)
- No rate limiting implemented (add nginx/cloudflare in production)
- All calculations run synchronously (consider async for high concurrency)

---

## Support and Contribution

For issues, improvements, or questions:
- Review the code in `src/` directory
- Check logs for detailed error messages
- Test with `test_signal.py` to isolate issues

## License

MIT
