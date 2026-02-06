# Project File Structure

```
sentiment-arbitrage-stock-agent/
│
├── .claude/                          # Claude Code configuration
│   ├── agents/                       # Custom agent definitions
│   │   ├── signal-architect.md       # Backend builder agent
│   │   ├── quant-auditor.md          # Trading signal validator
│   │   └── context-janitor.md        # Reddit data cleaner
│   └── settings.local.json           # Local Claude settings
│
├── src/                              # Core application modules
│   ├── __init__.py                   # Package initializer
│   ├── sentiment_analyzer.py         # TextBlob sentiment scoring
│   ├── technical_indicators.py       # RSI & Volume via yfinance
│   ├── signal_generator.py           # BUY/HOLD signal logic
│   └── api.py                        # Flask API endpoints
│
├── examples/                         # Example payloads
│   └── n8n_example_payload.json      # Sample n8n request
│
├── venv/                             # Python virtual environment
│
├── .env                              # Environment variables
├── requirements.txt                  # Python dependencies
├── run.py                            # Application entry point
├── test_signal.py                    # Test script
│
├── README.md                         # Project overview
├── QUICKSTART.md                     # Quick setup guide
├── SETUP_AND_USAGE.md                # Detailed setup instructions
├── ARCHITECTURE.md                   # System architecture docs
└── FILE_STRUCTURE.md                 # This file
```

## Module Descriptions

| File | Purpose |
|------|---------|
| `src/sentiment_analyzer.py` | Analyzes Reddit posts using TextBlob, returns 0-1 sentiment score |
| `src/technical_indicators.py` | Fetches RSI(14) and volume data from yfinance |
| `src/signal_generator.py` | Core logic: if sentiment > 0.7 AND RSI < 30 → BUY |
| `src/api.py` | Flask REST API with `/analyze` POST endpoint |
| `run.py` | Starts the Flask server on port 5000 |
| `test_signal.py` | Standalone test with sample data |

## API Endpoint

```
POST /analyze
Content-Type: application/json

{
  "ticker": "AAPL",
  "reddit_posts": [
    "This stock is going to the moon!",
    "Very bullish on this one"
  ]
}
```

## Quick Start

```bash
source venv/bin/activate
python run.py
```
