#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Dict, List, TypedDict, Optional
import os
from dotenv import load_dotenv
from utils.logger import logger

class CryptoInfo(TypedDict):
    id: str
    symbol: str
    name: str
    tvl: float

class MarketAnalysisConfig(TypedDict):
    correlation_sensitivity: float
    volatility_threshold: float
    volume_significance: int
    historical_periods: List[int]
    min_tvl: float
    significant_move_threshold: float

class DatabaseConfig(TypedDict):
    path: str
    snapshot_retention_days: int
    analysis_retention_days: int

class CoinGeckoParams(TypedDict):
    vs_currency: str
    order: str
    per_page: int
    page: int
    sparkline: bool
    price_change_percentage: str

@dataclass
class Config:
    def __init__(self) -> None:
        # Get the absolute path to the .env file
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
        logger.logger.info(f"Loading .env from: {env_path}")

        # Load environment variables
        load_dotenv(env_path)
        logger.logger.info("Environment variables loaded")
        
        # Debug loaded variables
        logger.logger.info(f"CLAUDE_API_KEY Present: {bool(os.getenv('CLAUDE_API_KEY'))}")
        
        # Claude API Configuration
        self.CLAUDE_API_KEY: str = os.getenv('CLAUDE_API_KEY', '')
        self.CLAUDE_MODEL: str = 'claude-3-sonnet-20240229'  # Updated to Sonnet
        
        # Data Collection Configuration
        self.COLLECTION_INTERVAL: int = 60  # seconds
        self.ANALYSIS_INTERVAL: int = 300  # seconds
        self.MAX_RETRIES: int = int(os.getenv('MAX_RETRIES', '3'))
        
        # Database Configuration
        self.DATABASE_CONFIG: DatabaseConfig = {
            'path': 'market_data.db',
            'snapshot_retention_days': 30,
            'analysis_retention_days': 90
        }
        
        # Market Analysis Parameters
        self.MARKET_ANALYSIS_CONFIG: MarketAnalysisConfig = {
            'correlation_sensitivity': 0.7,
            'volatility_threshold': 1.5,
            'volume_significance': 1000000,
            'historical_periods': [5, 15, 30, 60],  # minutes
            'min_tvl': 100000000,  # $100M minimum TVL
            'significant_move_threshold': 1.0  # 1% move is significant
        }
        
        # API Endpoints
        self.COINGECKO_BASE_URL: str = "https://api.coingecko.com/api/v3"
        
        # CoinGecko API Request Settings
        self.COINGECKO_PARAMS: CoinGeckoParams = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 20,  # Top 20 tokens
            "page": 1,
            "sparkline": False,
            "price_change_percentage": "1h,24h,7d"
        }
        
        # Initial Token List (will be updated dynamically)
        self.TRACKED_CRYPTO: Dict[str, CryptoInfo] = {
            'bitcoin': {
                'id': 'bitcoin',
                'symbol': 'btc',
                'name': 'Bitcoin',
                'tvl': 0
            },
            'ethereum': {
                'id': 'ethereum', 
                'symbol': 'eth',
                'name': 'Ethereum',
                'tvl': 0
            }
            # Additional tokens will be added dynamically based on TVL
        }
        
        # Claude Analysis Prompt Template
        self.CLAUDE_ANALYSIS_PROMPT: str = """Analyze the current crypto market state and provide detailed insights:

Market Overview (Last 5 Minutes):
{market_data}

Please provide a comprehensive analysis covering:

1. Significant Price Movements
- Identify tokens with notable price changes
- Analyze potential catalysts for these movements
- Compare with broader market trends

2. Market Correlations
- Highlight strong positive and negative correlations
- Identify divergent price movements
- Analyze sector-specific trends

3. Volume Analysis
- Compare volume patterns across tokens
- Identify unusual trading activity
- Assess liquidity conditions

4. Technical Signals
- Key support/resistance levels
- Short-term momentum indicators
- Potential breakout/breakdown patterns

5. Risk Assessment
- Market volatility measures
- Concentration of movements
- Systemic risk indicators

6. Trading Implications
- Potential opportunities
- Risk management considerations
- Market microstructure insights

Focus on actionable insights and causal relationships between token movements. 
Highlight any patterns that could indicate emerging trends or market shifts."""
        
        # Validation
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate required configuration settings"""
        required_settings: List[tuple[str, str]] = [
            ('CLAUDE_API_KEY', self.CLAUDE_API_KEY)
        ]
        
        missing_settings: List[str] = []
        for setting_name, setting_value in required_settings:
            if not setting_value or setting_value.strip() == '':
                missing_settings.append(setting_name)
        
        if missing_settings:
            error_msg = f"Missing required configuration: {', '.join(missing_settings)}"
            logger.log_error("Config", error_msg)
            raise ValueError(error_msg)

    def get_coingecko_markets_url(self) -> str:
        """Get CoinGecko markets API endpoint"""
        return f"{self.COINGECKO_BASE_URL}/coins/markets"

    def get_coingecko_params(self, **kwargs) -> Dict:
        """Get CoinGecko API parameters with optional overrides"""
        params = self.COINGECKO_PARAMS.copy()
        params.update(kwargs)
        return params

# Create singleton instance
config = Config()
