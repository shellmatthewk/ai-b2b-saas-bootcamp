#!/usr/bin/env python3
"""
Trading Signal Service - Main Entry Point

Simple wrapper to run the Flask API service.
"""

from src.api import app
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()

    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))
    debug = os.getenv("FLASK_ENV", "development") == "development"

    print(f"Starting Trading Signal Service on http://{host}:{port}")
    print(f"Debug mode: {debug}")
    print("\nAvailable endpoints:")
    print(f"  - POST http://{host}:{port}/api/signal")
    print(f"  - GET  http://{host}:{port}/health")
    print(f"  - GET  http://{host}:{port}/api/config")

    app.run(host=host, port=port, debug=debug)
