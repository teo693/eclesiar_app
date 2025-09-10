# Eclesiar Currency Arbitrage Application

## Description

Application for analyzing and detecting arbitrage opportunities in the Eclesiar game currency market. The application analyzes buy and sell prices of all currencies, takes into account transaction costs (tickets) and suggests the best profit strategies.

## Features

### 🎯 Main Functions
- **Simple arbitrage analysis** - Gold ↔ Currency
- **Cross arbitrage analysis** - Currency A ↔ Currency B
- **Triangular arbitrage analysis** - A→B→C→A
- **Risk analysis** - assessment of market volatility and liquidity
- **Portfolio optimization** - intelligent selection of best opportunities
- **Backtesting** - testing strategies on historical data
- **Reports** - detailed analyses in TXT and CSV formats

### 📊 Analysis Metrics
- **Profit percentage** - potential profit from transaction
- **Risk score** - transaction risk assessment (0-1)
- **Confidence level** - transaction execution confidence
- **Volume score** - market liquidity assessment
- **Liquidity score** - offer availability assessment
- **Execution time** - estimated execution time

### 🔧 Configuration
- **Ticket cost** - transaction cost in gold
- **Minimum profit threshold** - minimum profit to consider
- **API limits** - control of API call count
- **Cache parameters** - memory data management
- **Optimization options** - analysis preferences

## Installation

### Requirements
- Python 3.8+
- Eclesiar API authorization token
- Internet access

### Install dependencies
```bash
pip install -r requirements.txt
```

### Configuration
1. Copy `.env.example` to `.env`
2. Set your authorization token:
```bash
AUTH_TOKEN=your_token_here
```

## Usage

### Basic application
```bash
python currency_arbitrage.py
```

### Advanced application
```bash
python advanced_currency_arbitrage.py
```

### Parameter configuration
```bash
# Set ticket cost
export TICKET_COST_GOLD=0.1

# Set minimum profit threshold
export MIN_PROFIT_THRESHOLD=1.0

# Set API thread count
export API_WORKERS_MARKET=8

# Run application
python advanced_currency_arbitrage.py
```

## Profit Strategies

### 1. Simple Arbitrage (Gold ↔ Currency)
- **Description**: Buy currency for gold at low price, sell at high price
- **Advantages**: Lowest risk, fastest execution
- **Disadvantages**: Lower potential profit
- **Cost**: 2 tickets (buy + sell)

### 2. Cross Arbitrage (Currency A ↔ Currency B)
- **Description**: Buy currency A for gold → exchange for currency B → sell currency B for gold
- **Advantages**: Higher potential profit
- **Disadvantages**: Higher risk, more costs
- **Cost**: 3 tickets (buy + exchange + sell)

### 3. Time Arbitrage
- **Description**: Exploit price fluctuations over time
- **Advantages**: Can generate large profits
- **Disadvantages**: Requires monitoring, higher risk
- **Cost**: Variable (depends on strategy)

### 4. Triangular Arbitrage
- **Description**: Exploit exchange rate differences between three currencies
- **Advantages**: Can generate profits without using gold
- **Disadvantages**: Very complex, high risk
- **Cost**: 3+ tickets

## Risk Analysis

### Risk factors
1. **Market volatility** - price fluctuations
2. **Liquidity** - offer availability
3. **Spread** - difference between buy and sell price
4. **Volume** - amount of available offers
5. **Execution time** - transaction execution speed

### Risk score (0-1)
- **0.0-0.3**: Low risk - safe transactions
- **0.3-0.6**: Medium risk - moderate transactions
- **0.6-1.0**: High risk - risky transactions

## Advanced Configuration

### Environment parameters
```bash
# Costs and thresholds
TICKET_COST_GOLD=0.1                    # Ticket cost in gold
MIN_PROFIT_THRESHOLD=0.5                # Minimum profit in %
MIN_SPREAD_THRESHOLD=0.001              # Minimum spread

# Transaction limits
MAX_TRANSACTION_AMOUNT=10000            # Maximum amount in transaction
MIN_TRANSACTION_AMOUNT=1                # Minimum amount in transaction

# API parameters
API_WORKERS_MARKET=6                    # Number of threads for data fetching
API_WORKERS_ANALYSIS=4                  # Number of threads for analysis
API_RATE_LIMIT_DELAY=1.0               # Delay between API calls

# Analysis parameters
MAX_OPPORTUNITIES_TO_ANALYZE=1000      # Maximum number of opportunities
CONFIDENCE_THRESHOLD=0.3               # Minimum confidence level
RISK_THRESHOLD=0.5                     # Maximum risk level

# Reporting parameters
REPORT_TOP_OPPORTUNITIES=20             # Number of best opportunities in report
EXPORT_FORMATS=txt,csv                  # Report export format

# Cache parameters
CACHE_DURATION_MINUTES=5                # Cache validity time
USE_CACHE=true                          # Enable/disable cache

# Optimization parameters
OPTIMIZE_FOR_VOLUME=true                # Optimize for volume
OPTIMIZE_FOR_SPREAD=true                # Optimize for spread
OPTIMIZE_FOR_RISK=false                 # Optimize for risk

# Monitoring parameters
MONITORING_INTERVAL_SECONDS=300         # Monitoring interval
ENABLE_REAL_TIME_MONITORING=false       # Real-time monitoring
```

## File Structure

```
├── currency_arbitrage.py           # Basic arbitrage application
├── advanced_currency_arbitrage.py  # Advanced application with risk analysis
├── arbitrage_config.py             # Application configuration
├── README_ARBITRAGE.md             # This file
├── requirements.txt                 # Python dependencies
└── .env                           # Environment variables (to create)
```

## Usage Examples

### Basic analysis
```python
from currency_arbitrage import CurrencyArbitrageAnalyzer

analyzer = CurrencyArbitrageAnalyzer(
    ticket_cost_gold=0.1,
    min_profit_threshold=0.5
)

analyzer.run_analysis()
```

### Advanced analysis
```python
from advanced_currency_arbitrage import AdvancedCurrencyArbitrageAnalyzer
from arbitrage_config import get_config

config = get_config()
config['portfolio_optimization_enabled'] = True
config['risk_analysis_enabled'] = True

analyzer = AdvancedCurrencyArbitrageAnalyzer(config)
analyzer.run_advanced_analysis()
```

### Custom configuration
```python
custom_config = {
    'ticket_cost_gold': 0.15,
    'min_profit_threshold': 1.0,
    'api_workers_market': 10,
    'optimize_for_risk': True,
    'enable_notifications': True
}

analyzer = AdvancedCurrencyArbitrageAnalyzer(custom_config)
analyzer.run_advanced_analysis()
```

## Results Interpretation

### Text report
- **TOP OPPORTUNITIES**: List of best arbitrage opportunities
- **RISK ANALYSIS**: Risk metrics for all opportunities
- **PROFIT STRATEGIES**: Description of different strategies
- **TIPS**: Practical advice

### CSV report
- **from_currency**: Source currency
- **to_currency**: Target currency
- **profit_percentage**: Profit in percentage
- **risk_score**: Risk score (0-1)
- **confidence**: Confidence level (0-1)
- **volume_score**: Volume score (0-1)
- **liquidity_score**: Liquidity score (0-1)

## Practical Tips

### 1. Getting Started
- Start with simple arbitrage (Gold ↔ Currency)
- Set low profit threshold (0.5-1.0%)
- Monitor risk (score < 0.5)

### 2. Optimization
- Use cache for API savings
- Adjust thread count to your connection
- Monitor API limits

### 3. Risk Management
- Diversify between different currencies
- Consider transaction costs
- Monitor price changes over time

### 4. Scaling
- Increase profit threshold with experience
- Experiment with different strategies
- Use backtesting for testing

## Troubleshooting

### Authorization error
```
Error: Authorization token not loaded from .env file.
```
**Solution**: Check if `.env` file exists and contains correct `AUTH_TOKEN`

### API error
```
Error fetching market data
```
**Solution**: 
- Check internet connection
- Reduce API thread count
- Increase delay between calls

### No opportunities
```
Found 0 arbitrage opportunities
```
**Solution**:
- Reduce minimum profit threshold
- Check if markets are active
- Check ticket costs

## Support

### API Documentation
- [Eclesiar API Documentation](https://api.eclesiar.com/)
- [Market Endpoint](https://api.eclesiar.com/market/coin/get)

### Logs
- Application generates detailed logs
- Check console for errors
- Use `LOG_TO_FILE=true` for file logging

### Monitoring
- Use `ENABLE_REAL_TIME_MONITORING=true` for continuous monitoring
- Set `MONITORING_INTERVAL_SECONDS` for interval

## License

This project is intended for educational and personal use. Use responsibly and in accordance with Eclesiar game rules.

## Author

Application created based on existing `orchestrator.py` code with extensions for currency arbitrage functionality.

---

**Note**: Currency arbitrage involves risk. Always analyze transactions before execution and don't invest more than you can afford to lose.

**Version**: 2.0  
**Date**: 2025-09-10  
**Features**: English translation, enhanced functionality, improved documentation