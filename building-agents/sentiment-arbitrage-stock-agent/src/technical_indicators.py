"""
Technical Indicators Module

Provides technical analysis indicators using yfinance data.
Implements RSI, volume analysis, and other technical metrics.
"""

import yfinance as yf
import pandas as pd
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class TechnicalIndicatorCalculator:
    """Calculates technical indicators for stock analysis."""

    def __init__(self, rsi_period: int = 14):
        """
        Initialize the technical indicator calculator.

        Args:
            rsi_period: Period for RSI calculation (default: 14)
        """
        self.rsi_period = rsi_period

    def calculate_rsi(self, prices: pd.Series, period: int = None) -> float:
        """
        Calculate the Relative Strength Index (RSI).

        RSI = 100 - (100 / (1 + RS))
        where RS = Average Gain / Average Loss

        Args:
            prices: Series of closing prices
            period: RSI period (uses instance default if not provided)

        Returns:
            Current RSI value (0-100)
        """
        if period is None:
            period = self.rsi_period

        if len(prices) < period + 1:
            raise ValueError(
                f"Insufficient data for RSI calculation. "
                f"Need at least {period + 1} data points, got {len(prices)}"
            )

        # Calculate price changes
        delta = prices.diff()

        # Separate gains and losses
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        # Calculate RS and RSI
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        # Return the most recent RSI value
        current_rsi = rsi.iloc[-1]

        if pd.isna(current_rsi):
            raise ValueError("RSI calculation resulted in NaN")

        return round(float(current_rsi), 2)

    def get_stock_data(
        self,
        ticker: str,
        period: str = "60d",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch stock data from yfinance.

        Args:
            ticker: Stock symbol (e.g., 'AAPL')
            period: Data period (e.g., '60d', '1mo', '1y')
            interval: Data interval (e.g., '1d', '1h')

        Returns:
            DataFrame with stock data or None if fetch fails
        """
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period=period, interval=interval)

            if data.empty:
                logger.error(f"No data returned for ticker {ticker}")
                return None

            logger.info(f"Fetched {len(data)} data points for {ticker}")
            return data

        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            return None

    def analyze_ticker(self, ticker: str) -> Dict:
        """
        Perform complete technical analysis on a ticker.

        Args:
            ticker: Stock symbol to analyze

        Returns:
            Dictionary containing:
                - rsi: Current RSI value
                - volume: Current volume
                - price: Current closing price
                - avg_volume: Average volume over period
                - status: 'success' or 'error'
                - error: Error message if status is 'error'
        """
        try:
            # Fetch data - need enough for RSI calculation
            data = self.get_stock_data(
                ticker,
                period="60d",  # Get 60 days to ensure enough for RSI
                interval="1d"
            )

            if data is None or data.empty:
                return {
                    "status": "error",
                    "error": f"Unable to fetch data for ticker {ticker}"
                }

            # Calculate RSI
            try:
                rsi = self.calculate_rsi(data['Close'])
            except ValueError as e:
                logger.error(f"RSI calculation error: {e}")
                return {
                    "status": "error",
                    "error": f"RSI calculation failed: {str(e)}"
                }

            # Get current volume and price
            current_volume = int(data['Volume'].iloc[-1])
            current_price = round(float(data['Close'].iloc[-1]), 2)
            avg_volume = int(data['Volume'].mean())

            logger.info(
                f"Technical analysis for {ticker}: "
                f"RSI={rsi}, Volume={current_volume}, Price={current_price}"
            )

            return {
                "status": "success",
                "rsi": rsi,
                "volume": current_volume,
                "price": current_price,
                "avg_volume": avg_volume,
                "data_points": len(data)
            }

        except Exception as e:
            logger.error(f"Error analyzing ticker {ticker}: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
