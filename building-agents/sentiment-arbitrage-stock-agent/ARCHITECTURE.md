# Trading Signal Service - Architecture Documentation

## System Overview

The Trading Signal Service is a modular Python backend that combines sentiment analysis from Reddit posts with technical indicators (RSI, volume) to generate actionable trading signals. The service is designed for integration with automation tools like n8n and follows production-ready architectural patterns.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  (n8n, cURL, Python clients, Web browsers, Mobile apps)         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API LAYER                                │
│                      (Flask REST API)                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Endpoints:                                              │   │
│  │  - POST /api/signal     (generate trading signal)       │   │
│  │  - GET  /health         (health check)                  │   │
│  │  - GET  /api/config     (get configuration)             │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BUSINESS LOGIC LAYER                        │
│                     (Signal Generator)                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  - Orchestrates sentiment + technical analysis          │   │
│  │  - Applies signal logic (BUY/HOLD/NEUTRAL)              │   │
│  │  - Formats standardized responses                       │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│   SENTIMENT ANALYSIS     │  │  TECHNICAL INDICATORS    │
│  (Sentiment Analyzer)    │  │  (Technical Calculator)  │
├──────────────────────────┤  ├──────────────────────────┤
│ - TextBlob integration   │  │ - yfinance integration   │
│ - Polarity calculation   │  │ - RSI calculation        │
│ - Score normalization    │  │ - Volume analysis        │
│ - Aggregation logic      │  │ - Price data             │
└──────────────────────────┘  └──────────────────────────┘
         │                              │
         ▼                              ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│   EXTERNAL SERVICES      │  │   EXTERNAL SERVICES      │
│   (TextBlob Corpora)     │  │   (Yahoo Finance API)    │
└──────────────────────────┘  └──────────────────────────┘
```

## Module Architecture

### 1. API Layer (`src/api.py`)

**Responsibility**: HTTP interface for external clients

**Key Components**:
- Flask application instance
- Request validation logic
- Error handling middleware
- Endpoint definitions
- Configuration loading

**Design Patterns**:
- Dependency Injection: `SignalGenerator` injected into Flask app
- Request/Response pattern: Standardized JSON schemas
- Middleware: Error handlers for 404, 405, 500

**Key Functions**:
```python
@app.route("/api/signal", methods=["POST"])
def generate_signal():
    """Main endpoint for signal generation"""
    # 1. Validate request
    # 2. Call SignalGenerator
    # 3. Return standardized response
```

### 2. Business Logic Layer (`src/signal_generator.py`)

**Responsibility**: Core signal generation logic

**Key Components**:
- Signal determination algorithm
- Response formatting
- Error aggregation
- Metadata collection

**Design Patterns**:
- Facade Pattern: Simplifies interaction with sentiment + technical modules
- Strategy Pattern: Configurable thresholds for different trading strategies
- Builder Pattern: Constructs complex response objects

**Signal Logic**:
```python
def determine_signal(sentiment_score, rsi):
    if sentiment_score > threshold AND rsi < buy_threshold:
        return "BUY"
    elif sentiment_score > threshold OR rsi < buy_threshold:
        return "HOLD"
    else:
        return "NEUTRAL"
```

**Data Flow**:
```
Input (ticker, reddit_posts)
    ↓
1. Analyze sentiment → sentiment_score
    ↓
2. Fetch technical data → rsi, volume, price
    ↓
3. Apply signal logic → signal, reason
    ↓
4. Format response → standardized JSON
    ↓
Output (signal response)
```

### 3. Sentiment Analysis Layer (`src/sentiment_analyzer.py`)

**Responsibility**: Text sentiment scoring

**Key Components**:
- TextBlob wrapper
- Polarity extraction
- Score normalization
- Aggregation algorithm

**Design Patterns**:
- Adapter Pattern: Wraps TextBlob API with custom interface
- Aggregator Pattern: Combines multiple text sentiments

**Algorithm**:
```
For each reddit post:
    1. Extract polarity using TextBlob (-1 to 1)
    2. Calculate average polarity across all posts
    3. Normalize to 0-1 scale: (polarity + 1) / 2
    4. Return aggregated score + metadata
```

**Normalization**:
- TextBlob returns: `-1.0` (very negative) to `1.0` (very positive)
- Service returns: `0.0` (very negative) to `1.0` (very positive)
- Formula: `normalized = (polarity + 1) / 2`

### 4. Technical Indicators Layer (`src/technical_indicators.py`)

**Responsibility**: Stock data fetching and indicator calculation

**Key Components**:
- yfinance API wrapper
- RSI calculation algorithm
- Volume analysis
- Price data extraction

**Design Patterns**:
- Adapter Pattern: Wraps yfinance API
- Calculator Pattern: Encapsulates indicator math

**RSI Calculation**:
```
1. Fetch 60 days of price data
2. Calculate price changes (delta)
3. Separate gains and losses
4. Calculate average gain/loss over period (14 days default)
5. Compute RS = avg_gain / avg_loss
6. Compute RSI = 100 - (100 / (1 + RS))
```

**RSI Interpretation**:
- `0-30`: Oversold (potential buy opportunity)
- `30-70`: Neutral zone
- `70-100`: Overbought (potential sell signal)

## Data Flow

### Complete Request Flow

```
1. CLIENT REQUEST
   POST /api/signal
   {
     "ticker": "AAPL",
     "reddit_posts": ["Great stock!", "Love it!"]
   }

2. API LAYER (api.py)
   ├─ Validate request payload
   ├─ Extract ticker and posts
   └─ Call signal_generator.generate_signal()

3. SIGNAL GENERATOR (signal_generator.py)
   ├─ Call sentiment_analyzer.aggregate_sentiment()
   │  └─ Returns: {normalized_score: 0.82, ...}
   │
   ├─ Call technical_calculator.analyze_ticker()
   │  ├─ Fetch yfinance data
   │  ├─ Calculate RSI
   │  └─ Returns: {rsi: 28.5, volume: 85M, price: 178.45}
   │
   ├─ Call determine_signal(sentiment, rsi)
   │  └─ Returns: ("BUY", "reason...")
   │
   └─ Build standardized response

4. API LAYER (api.py)
   ├─ Return JSON response
   └─ Set appropriate HTTP status code

5. CLIENT RECEIVES
   {
     "signal": "BUY",
     "ticker": "AAPL",
     "sentiment_score": 0.82,
     "rsi": 28.5,
     "volume": 85234000,
     "price": 178.45,
     "reason": "Strong bullish sentiment...",
     "timestamp": "2026-02-05T12:34:56Z",
     "status": "success",
     "metadata": {...},
     "errors": []
   }
```

## Response Schema Design

### Standardized Signal Response

Every response follows the Signal Architect's standardized schema:

```typescript
{
  // SIGNAL IDENTIFICATION
  signal_type: "trading_signal",           // Implicit type
  signal: "BUY" | "HOLD" | "NEUTRAL" | "ERROR",
  ticker: string,                          // Stock symbol

  // CALCULATED VALUES
  sentiment_score: number,                 // 0-1 scale
  rsi: number | null,                      // 0-100 scale
  volume: number | null,
  price: number | null,

  // INTERPRETATION
  reason: string,                          // Human-readable explanation

  // TEMPORAL DATA
  timestamp: string,                       // ISO 8601 format

  // STATUS TRACKING
  status: "success" | "partial" | "error",
  errors: Array<{
    type: string,
    message: string
  }>,

  // METADATA (for observability)
  metadata: {
    sentiment_analyzer: string,            // "TextBlob"
    service_version: string,               // "1.0.0"
    rsi_period: number,                    // 14
    sentiment_threshold: number,           // 0.7
    rsi_buy_threshold: number,             // 30
    sentiment_details: {
      num_posts: number,
      valid_posts: number,
      raw_polarity: number
    },
    technical_details: {
      avg_volume: number,
      data_points: number
    }
  }
}
```

### Status Codes

- `success`: All components executed successfully
- `partial`: Some data available but not complete
- `error`: Critical failure, no signal generated

### Error Response Format

```json
{
  "signal": "ERROR",
  "ticker": "INVALID",
  "sentiment_score": 0.5,
  "rsi": null,
  "volume": null,
  "price": null,
  "reason": "Unable to fetch technical data: ...",
  "timestamp": "2026-02-05T12:34:56Z",
  "status": "error",
  "metadata": {...},
  "errors": [
    {
      "type": "technical_data_error",
      "message": "No data returned for ticker INVALID"
    }
  ]
}
```

## Configuration Architecture

### Environment-Based Configuration

All tunable parameters are externalized to environment variables:

```bash
# .env file structure
FLASK_PORT=5000                    # API server port
FLASK_HOST=0.0.0.0                # Bind address
FLASK_ENV=development             # Environment mode

SERVICE_VERSION=1.0.0             # Version tracking
LOG_LEVEL=INFO                    # Logging verbosity

RSI_PERIOD=14                     # Technical indicator period
RSI_BUY_THRESHOLD=30              # Oversold threshold

SENTIMENT_BUY_THRESHOLD=0.7       # Sentiment threshold
```

### Configuration Loading

```python
# api.py
signal_generator = SignalGenerator(
    sentiment_threshold=float(os.getenv("SENTIMENT_BUY_THRESHOLD", "0.7")),
    rsi_buy_threshold=float(os.getenv("RSI_BUY_THRESHOLD", "30")),
    rsi_period=int(os.getenv("RSI_PERIOD", "14"))
)
```

**Design Pattern**: Environment-based dependency injection with sensible defaults

## Error Handling Architecture

### Layered Error Handling

```
┌─────────────────────────────────────┐
│  API Layer                           │
│  - HTTP-level errors (404, 405)     │
│  - Request validation errors (400)   │
│  - Unexpected exceptions (500)       │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Signal Generator Layer              │
│  - Aggregates errors from modules    │
│  - Returns ERROR signal on failure   │
│  - Preserves partial results         │
└─────────────────────────────────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐  ┌────────┐
│ Sent.  │  │ Tech.  │
│ Layer  │  │ Layer  │
│ - Text │  │ - API  │
│ errors │  │ errors │
└────────┘  └────────┘
```

### Error Propagation Strategy

1. **Bottom-up**: Modules catch and log errors
2. **Graceful degradation**: Return null/default values
3. **Error accumulation**: Collect errors in list
4. **Structured responses**: Always return valid JSON

### Example Error Scenarios

**Scenario 1: Invalid Ticker**
- Technical layer: Returns `status: "error"`
- Signal generator: Returns ERROR signal with details
- API layer: Returns 500 status with error message

**Scenario 2: Empty Reddit Posts**
- Sentiment layer: Returns neutral score (0.5)
- Signal generator: Continues with neutral sentiment
- Result: Signal based on technicals only

**Scenario 3: API Rate Limit**
- Technical layer: Catches exception, returns error
- Signal generator: Returns ERROR signal
- Client: Receives error response with retry guidance

## Extensibility Points

### Adding New Indicators

1. **Add calculation method** to `TechnicalIndicatorCalculator`:
```python
def calculate_macd(self, prices: pd.Series) -> Dict:
    """Calculate MACD indicator."""
    # Implementation
    return {"macd": value, "signal": signal_line, "histogram": hist}
```

2. **Update `analyze_ticker()`** to include it:
```python
def analyze_ticker(self, ticker: str) -> Dict:
    # ... existing code ...
    macd = self.calculate_macd(data['Close'])
    return {
        # ... existing fields ...
        "macd": macd
    }
```

3. **Update signal logic** in `SignalGenerator`:
```python
def determine_signal(self, sentiment_score, rsi, macd):
    if sentiment_score > 0.7 and rsi < 30 and macd['histogram'] > 0:
        return "BUY", "..."
```

### Adding New Sentiment Sources

1. **Create new analyzer** class:
```python
class TwitterSentimentAnalyzer:
    def analyze_tweets(self, tweets: List[str]) -> Dict:
        # Implementation similar to SentimentAnalyzer
        pass
```

2. **Update `SignalGenerator`** to support multiple sources:
```python
def __init__(self, sentiment_sources: List[str]):
    self.analyzers = {
        'reddit': SentimentAnalyzer(),
        'twitter': TwitterSentimentAnalyzer()
    }
```

### Adding New Signal Types

Current: `BUY`, `HOLD`, `NEUTRAL`, `ERROR`

To add `SELL` signal:

1. **Update signal logic**:
```python
def determine_signal(self, sentiment_score, rsi):
    if sentiment_score < 0.3 and rsi > 70:
        return "SELL", "Negative sentiment + overbought"
    # ... existing logic ...
```

2. **Update API documentation**
3. **Update client expectations**

## Performance Considerations

### Bottlenecks

1. **yfinance API calls**: 1-3 seconds per ticker
2. **TextBlob processing**: ~100ms for 100 posts
3. **RSI calculation**: Negligible (<10ms)

### Optimization Strategies

**Current State** (No caching):
- Each request fetches fresh data
- No state maintained between requests
- Simple but potentially slow

**Recommended Optimizations**:

1. **Redis Caching**:
```python
def get_stock_data(self, ticker: str) -> pd.DataFrame:
    cache_key = f"stock_data:{ticker}:{today}"
    cached = redis.get(cache_key)
    if cached:
        return pickle.loads(cached)

    data = yf.Ticker(ticker).history(period="60d")
    redis.setex(cache_key, 3600, pickle.dumps(data))
    return data
```

2. **Async Processing**:
```python
async def generate_signal(self, ticker: str, posts: List[str]):
    sentiment_task = asyncio.create_task(self.analyze_sentiment(posts))
    technical_task = asyncio.create_task(self.analyze_technical(ticker))

    sentiment, technical = await asyncio.gather(
        sentiment_task,
        technical_task
    )
```

3. **Rate Limiting**:
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@app.route("/api/signal", methods=["POST"])
@limiter.limit("10 per minute")
def generate_signal():
    # ...
```

## Security Considerations

### Current State

- No authentication required
- No rate limiting
- All endpoints publicly accessible
- No input sanitization beyond type checking

### Production Recommendations

1. **API Key Authentication**:
```python
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get('X-API-Key')
        if not key or key not in valid_keys:
            return jsonify({"error": "Invalid API key"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route("/api/signal", methods=["POST"])
@require_api_key
def generate_signal():
    # ...
```

2. **Rate Limiting**:
```python
limiter = Limiter(
    app,
    key_func=lambda: request.headers.get('X-API-Key'),
    default_limits=["100 per hour"]
)
```

3. **Input Validation**:
```python
from marshmallow import Schema, fields, ValidationError

class SignalRequestSchema(Schema):
    ticker = fields.Str(required=True, validate=validate_ticker)
    reddit_posts = fields.List(fields.Str(), required=True)

def validate_ticker(ticker):
    if not re.match(r'^[A-Z]{1,5}$', ticker):
        raise ValidationError("Invalid ticker format")
```

## Deployment Architecture

### Development

```bash
python run.py
# Flask development server on port 5000
```

### Production (Gunicorn)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 src.api:app
```

**Configuration**:
- 4 workers (adjust based on CPU cores)
- 120s timeout (for slow yfinance calls)
- Bind to all interfaces

### Docker Deployment

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn
RUN python -m textblob.download_corpora

# Copy application
COPY . .

# Run with gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "120", "src.api:app"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: trading-signal-service
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: api
        image: trading-signal-service:1.0.0
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
        - name: LOG_LEVEL
          value: "WARNING"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
```

## Monitoring and Observability

### Logging Strategy

**Current Implementation**:
```python
import logging

logger = logging.getLogger(__name__)
logger.info(f"Processing signal for {ticker}")
logger.error(f"Error: {e}", exc_info=True)
```

**Recommended Enhancements**:

1. **Structured Logging**:
```python
import structlog

logger = structlog.get_logger()
logger.info("signal_generated",
    ticker=ticker,
    signal=signal,
    sentiment=sentiment_score,
    rsi=rsi,
    duration_ms=elapsed
)
```

2. **Distributed Tracing**:
```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("generate_signal")
def generate_signal(ticker, posts):
    # ...
```

### Metrics to Track

- Request rate (requests/minute)
- Response time (p50, p95, p99)
- Error rate (%)
- Signal distribution (% BUY/HOLD/NEUTRAL)
- yfinance API latency
- Cache hit rate (if caching implemented)

## Testing Strategy

### Unit Tests

```python
# tests/test_sentiment_analyzer.py
def test_positive_sentiment():
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze_text("This is amazing!")
    assert result > 0.5

# tests/test_technical_indicators.py
def test_rsi_calculation():
    calc = TechnicalIndicatorCalculator()
    prices = pd.Series([100, 105, 103, 108, 107])
    rsi = calc.calculate_rsi(prices, period=2)
    assert 0 <= rsi <= 100
```

### Integration Tests

```python
# tests/test_signal_generator.py
def test_buy_signal_generation():
    generator = SignalGenerator()
    result = generator.generate_signal(
        "AAPL",
        ["Amazing stock!", "To the moon!"]
    )
    assert result['status'] == 'success'
    assert 'signal' in result
```

### API Tests

```python
# tests/test_api.py
def test_signal_endpoint():
    response = client.post('/api/signal', json={
        'ticker': 'AAPL',
        'reddit_posts': ['Great!']
    })
    assert response.status_code == 200
    assert 'signal' in response.json()
```

## Conclusion

This architecture demonstrates the Signal Architect's core principles:

1. **Modularity**: Each component has a single, well-defined responsibility
2. **Reliability**: Graceful error handling at every layer
3. **Standardization**: Consistent JSON schemas for all responses
4. **Observability**: Comprehensive logging and metadata
5. **Extensibility**: Clear patterns for adding new features

The service is production-ready and can be extended to support:
- Multiple sentiment sources (Twitter, news, etc.)
- Additional technical indicators (MACD, Bollinger Bands, etc.)
- Different trading strategies (day trading, swing trading, etc.)
- Advanced features (backtesting, portfolio optimization, etc.)
