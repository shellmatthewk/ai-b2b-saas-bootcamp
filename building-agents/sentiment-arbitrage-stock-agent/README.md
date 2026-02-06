# Trading Signal Service

A modular Python service that generates trading signals by combining Reddit sentiment analysis with technical indicators (RSI, volume). Built for integration with n8n and other automation tools.

## Features

- **Sentiment Analysis**: Aggregate sentiment from Reddit posts using TextBlob
- **Technical Indicators**: Real-time RSI and volume data via yfinance
- **Smart Signal Logic**: BUY signals when high sentiment meets oversold conditions
- **RESTful API**: Flask-based endpoints for easy integration
- **Standardized Output**: Consistent JSON schema for downstream consumption
- **Modular Architecture**: Separate modules for sentiment, technical analysis, and signal generation

## Architecture

```
src/
├── sentiment_analyzer.py      # TextBlob-based sentiment scoring
├── technical_indicators.py    # RSI calculation and yfinance integration
├── signal_generator.py        # Core signal logic combining sentiment + technicals
└── api.py                     # Flask REST API endpoints
```

## Installation

1. **Clone and navigate to the project:**
   ```bash
   cd /Users/matthewkshell/ai-b2b-saas-bootcamp/building-agents/sentiment-arbitrage-stock-agent
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download TextBlob corpora (first time only):**
   ```bash
   python -m textblob.download_corpora
   ```

4. **Configure environment (optional):**
   ```bash
   cp .env.example .env
   # Edit .env to customize thresholds
   ```

## Usage

### Start the Service

```bash
python run.py
```

The service will start on `http://0.0.0.0:5000` by default.

### API Endpoints

#### 1. Generate Trading Signal

**Endpoint:** `POST /api/signal`

**Request:**
```json
{
  "ticker": "AAPL",
  "reddit_posts": [
    "Apple is killing it this quarter!",
    "AAPL to the moon!",
    "Great earnings, buying more"
  ]
}
```

**Response:**
```json
{
  "signal": "BUY",
  "ticker": "AAPL",
  "sentiment_score": 0.85,
  "rsi": 28.5,
  "volume": 85234000,
  "price": 178.45,
  "reason": "Strong bullish sentiment (0.85 > 0.7) combined with oversold conditions (RSI 28.5 < 30). Potential buying opportunity.",
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
      "raw_polarity": 0.7
    },
    "technical_details": {
      "avg_volume": 82500000,
      "data_points": 60
    }
  },
  "errors": []
}
```

#### 2. Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "service": "trading-signal-service",
  "version": "1.0.0"
}
```

#### 3. Get Configuration

**Endpoint:** `GET /api/config`

**Response:**
```json
{
  "sentiment_threshold": 0.7,
  "rsi_buy_threshold": 30,
  "rsi_period": 14,
  "service_version": "1.0.0"
}
```

## Signal Logic

The service generates three types of signals:

1. **BUY**: Sentiment > 0.7 AND RSI < 30
   - High positive sentiment + oversold technical conditions

2. **HOLD**: One condition met but not both
   - Either strong sentiment OR oversold RSI, but not both

3. **NEUTRAL**: Neither condition met
   - No clear trading opportunity

## Testing with cURL

```bash
# Generate a signal
curl -X POST http://localhost:5000/api/signal \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "TSLA",
    "reddit_posts": [
      "Tesla is innovating like crazy",
      "Love my Model 3, stock going up",
      "Elon delivers again!"
    ]
  }'

# Check health
curl http://localhost:5000/health

# View configuration
curl http://localhost:5000/api/config
```

## n8n Integration

1. Add an **HTTP Request** node in n8n
2. Configure:
   - **Method**: POST
   - **URL**: `http://your-server:5000/api/signal`
   - **Body Content Type**: JSON
   - **Body**:
     ```json
     {
       "ticker": "{{ $json.ticker }}",
       "reddit_posts": {{ $json.comments }}
     }
     ```
3. Parse the response to extract `signal`, `sentiment_score`, `rsi`, etc.

## Configuration

All parameters can be customized via environment variables in `.env`:

```bash
# Flask Configuration
FLASK_PORT=5000
FLASK_HOST=0.0.0.0
FLASK_ENV=development

# Service Configuration
SERVICE_VERSION=1.0.0
LOG_LEVEL=INFO

# Technical Indicator Parameters
RSI_PERIOD=14              # RSI calculation period
RSI_BUY_THRESHOLD=30       # RSI threshold for BUY signals

# Sentiment Parameters
SENTIMENT_BUY_THRESHOLD=0.7  # Sentiment threshold for BUY signals (0-1)
```

## Module Documentation

### SentimentAnalyzer (`sentiment_analyzer.py`)

Analyzes text sentiment using TextBlob and normalizes scores to 0-1 scale.

**Key Methods:**
- `analyze_text(text: str) -> float`: Analyze single text
- `aggregate_sentiment(texts: List[str]) -> Dict`: Aggregate multiple texts

### TechnicalIndicatorCalculator (`technical_indicators.py`)

Fetches stock data and calculates technical indicators.

**Key Methods:**
- `calculate_rsi(prices: pd.Series, period: int) -> float`: Calculate RSI
- `get_stock_data(ticker: str, period: str) -> pd.DataFrame`: Fetch yfinance data
- `analyze_ticker(ticker: str) -> Dict`: Complete technical analysis

### SignalGenerator (`signal_generator.py`)

Combines sentiment and technical analysis to generate trading signals.

**Key Methods:**
- `determine_signal(sentiment_score: float, rsi: float) -> tuple`: Apply signal logic
- `generate_signal(ticker: str, reddit_posts: List[str]) -> Dict`: Generate complete signal

## Error Handling

The service handles various error scenarios:

- **Invalid ticker symbols**: Returns error status with message
- **Insufficient market data**: Returns error if not enough data for RSI
- **Empty reddit posts**: Defaults to neutral sentiment (0.5)
- **API failures**: Graceful error responses with details

## Response Schema

All signal responses follow this standardized schema:

```typescript
{
  signal: "BUY" | "HOLD" | "NEUTRAL" | "ERROR",
  ticker: string,
  sentiment_score: number,  // 0-1
  rsi: number | null,       // 0-100
  volume: number | null,
  price: number | null,
  reason: string,
  timestamp: string,        // ISO 8601
  status: "success" | "partial" | "error",
  metadata: {
    sentiment_analyzer: string,
    service_version: string,
    // ... additional context
  },
  errors: Array<{type: string, message: string}>
}
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests (coming soon)
pytest tests/
```

### Adding New Indicators

1. Add calculation method to `TechnicalIndicatorCalculator`
2. Update `analyze_ticker()` to include new indicator
3. Modify signal logic in `SignalGenerator.determine_signal()`
4. Update API response schema

## Production Considerations

- **Rate Limiting**: Consider adding rate limiting for API endpoints
- **Caching**: Cache yfinance data to reduce API calls
- **Authentication**: Add API key authentication for production
- **Monitoring**: Integrate with monitoring tools (Prometheus, DataDog)
- **WSGI Server**: Use Gunicorn or uWSGI instead of Flask development server

## License

MIT

## Support

For issues or questions, please open an issue on the repository.
