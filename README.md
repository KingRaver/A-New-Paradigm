# Market Analysis Agent

A Python-based bot that monitors and analyzes the correlation between Ethereum (ETH) and Bitcoin (BTC) prices, providing automated market insights via Twitter posts.

## Features

- Real-time cryptocurrency price monitoring via CoinGecko API
- Automated market sentiment analysis using Claude AI
- Automated Twitter posting with detailed market insights
- Robust error handling and retry mechanisms
- Comprehensive logging system

## Prerequisites

- Python 3.7+
- Chrome/Chromium browser
- Twitter account
- Anthropic API key (for Claude)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ETHBTCCorrelationBot.git
cd ETHBTCCorrelationBot
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
TWITTER_USERNAME=your_twitter_username
TWITTER_PASSWORD=your_twitter_password
CLAUDE_API_KEY=your_claude_api_key
```

## Configuration

The bot's behavior can be customized through the `config.py` file:

- `CORRELATION_INTERVAL`: Time between analysis cycles (in minutes)
- `MAX_RETRIES`: Maximum number of retry attempts for operations
- `TWEET_CONSTRAINTS`: Character limits for tweets
- `CLAUDE_MODEL`: Specify which Claude model to use
- `CLAUDE_ANALYSIS_PROMPT`: Customize the prompt for market analysis

## Usage

Run the bot:
```bash
python3 ethbtc_correlation_bot.py
```

The bot will:
1. Initialize and log in to Twitter
2. Fetch cryptocurrency data from CoinGecko
3. Generate market analysis using Claude
4. Post insights to Twitter
5. Repeat the cycle based on the configured interval

## Error Handling

The bot includes comprehensive error handling for:
- Network connectivity issues
- API rate limits
- Browser automation challenges
- Twitter login/posting failures
- Invalid or missing data

All errors are logged with detailed information for troubleshooting.

## Logging

Logs are maintained for:
- Bot startup/shutdown events
- API requests and responses
- Twitter interactions
- Error events and stack traces
- Performance metrics

## Security Notes

- Store sensitive credentials in environment variables
- Use 2FA for Twitter account security
- Regularly rotate API keys
- Monitor bot activity for unusual behavior

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This bot is for educational and research purposes only. Cryptocurrency trading involves significant risks. Always conduct your own research before making investment decisions.
