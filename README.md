# Trading Bot - EMA Strategy

## Introduction

This repository contains a Python-based trading bot that implements an Exponential Moving Average (EMA) strategy. The bot is designed to automate trading by executing buy and sell orders based on EMA crossover signals. The bot has been tested using historical data to evaluate its performance and robustness.

**Disclaimer:** Certain parts of the strategy are obfuscated to protect intellectual property, as this bot may be commercialized in the future.

## Features

- **EMA Crossover Strategy**: The bot uses a simple yet effective EMA crossover strategy to determine entry and exit points.
- **Backtesting Module**: A comprehensive backtesting module is included to test the strategy against historical data.
- **Configurable Parameters**: The bot allows for the customization of key parameters, such as the periods for the fast and slow EMAs, trade size, and more.
- **Real-time Trading**: Capable of executing trades in real-time using live market data (when connected to a supported API).
- **Risk Management**: Implements basic risk management strategies, including stop-loss and take-profit levels.

## Technical Indicators and Their Mathematical Formulas

### 1. Exponential Moving Average (EMA)

The EMA is a type of moving average that gives more weight to recent prices, making it more responsive to new information.

**Formula**:
$$
EMA_t = \alpha \times P_t + (1 - \alpha) \times EMA_{t-1}
$$
where:
- \(P_t\) is the price at time \(t\),
- \(\alpha = \frac{2}{N + 1}\) is the smoothing factor,
- \(N\) is the number of periods.

### 2. Average True Range (ATR)

The Average True Range (ATR) is a volatility indicator that measures the degree of price fluctuation in a given period.

**Formula**:
$$
ATR = \frac{1}{n} \sum_{i=1}^{n} TR_i
$$
where \(TR\) (True Range) is the maximum of the following:
$$
TR = \max[(H - L), |H - C_{\text{previous}}|, |L - C_{\text{previous}}|]
$$
- \(H\) is the high of the current period,
- \(L\) is the low of the current period,
- \(C_{\text{previous}}\) is the close of the previous period.

## Project Structure

- **`bot_ema_public.py`**: Contains the main logic for the EMA trading bot, including the strategy, trade execution, and risk management. 
- **`backtest_public.ipynb`**: Jupyter notebook for backtesting the strategy on historical data. This notebook demonstrates the performance and efficiency of the trading bot.

**Note:** Some key parts of the strategy logic have been intentionally obfuscated.

## Performance Summary

### ETHUSDT Performance from 2018-01-01 to 2024-08-26

- **Trading ROI**: 6560.02%
- **HODL ROI**: 203.24%

This comparison shows that the trading strategy would have achieved approximately 66 times the initial investment, compared to a 2 times return using a simple HODL strategy.

## Getting Started

### Prerequisites

- Python 3.7+
- Required Python packages can be installed via `pip`:

  ```bash
  pip install -r requirements.txt


For real-time trading, the bot needs to be connected to a supported trading API. Make sure to set up API credentials securely.

## Important Notes

- **Obfuscated Logic**: The `bot_ema.py` script contains key parts of the strategy that are obfuscated to protect proprietary information.
- **Disclaimer**: Trading involves significant risk, and this bot is provided "as-is" without any warranty. Use it at your own risk.

## Contributions

This project is provided for demonstration purposes and is not intended for modification. However, you are welcome to fork the repository for personal use. The core strategy logic is obfuscated to protect intellectual property.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
