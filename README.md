SignalForge - Advanced Swing Trading System

SignalForge is a swing-trading automation system that scans the market for technical setups, backtests them against historical data, and (optionally) places live orders through Webull's OpenAPI, with a chart review and manual confirmation before every trade.

The system is split into two pieces:

SIGNALFORGE.py - Signal engine. Handles indicators, scanning, backtesting, and candidate ranking.

SIGNALBOT.py - Trading bot. Runs the scan, shows charts and portfolio info, and executes confirmed trades via Webull.


SETUP

1. Install dependencies

pip install pandas requests yfinance beautifulsoup4 matplotlib numpy lxml webull-openapi-python-sdk

2. Configure Webull credentials

Set the following environment variables (get your App Key and App Secret from developer.webull.com):

Windows (PowerShell):
WEBULL_APP_KEY = your_app_key_here
WEBULL_APP_SECRET = your_app_secret_here
WEBULL_ACCOUNT_ID = your_account_id_here (optional, auto-detected if not set)

Linux/macOS (Bash):
export WEBULL_APP_KEY=your_app_key_here
export WEBULL_APP_SECRET=your_app_secret_here
export WEBULL_ACCOUNT_ID=your_account_id_here

If WEBULL_ACCOUNT_ID is not set, the bot automatically selects your Individual Margin account, or the first account returned if no margin account exists.


SIGNALBOT.PY - TRADING BOT

What it does:

1. Scans the configured stock universe for technical setups
2. Filters results down to a short list of high-conviction candidates
3. Logs into Webull and shows your current portfolio
4. For each candidate, displays a chart and asks whether to buy
5. Sizes and places any confirmed orders as market orders
6. Shows the updated portfolio when finished

Trading filters

A stock must meet all of the following to be considered a candidate:

Signal must be BUY (bullish trend, pullback, healthy RSI, outperforming SPY, in a bullish market)
Target upside must be at least 15 percent above entry (Target is greater than or equal to Entry times 1.15)
Backtested win rate must be between 80 and 100 percent
Backtested return must be at least 5R

Candidates that pass are sorted by win rate, then backtest return, and the top 7 are passed along for review.

Position sizing

Sizing is based on a fixed number of portfolio "slots" rather than just splitting your current cash, so the portfolio stays balanced as positions come and go.

Per-slot size equals Total Account Value divided by MAX_POSITIONS.

The bot checks how many positions you currently hold, calculates how many slots are still open, and recommends the per-slot size for each new candidate, capped at your available cash. You can accept the recommendation or type a different dollar amount for any individual trade.

Chart review

Before confirming each trade, a chart window opens showing:

6 months of daily candlesticks
20, 50, and 200 period EMAs
Volume
Horizontal lines for Entry, Stop Loss, and Target

Close the chart window to continue to the confirmation prompt.

Order execution

All orders are submitted as market orders. For each confirmed candidate you are asked for a dollar amount (the recommended size is pre-filled, press Enter to accept it), and the bot converts that into a share quantity before submitting the order.

Note: This system does not sell or manage exits automatically. Stops and targets shown on the chart are for your reference only. Closing positions is entirely manual.

Running it

python SIGNALBOT.py

Example session

ADVANCED SWING TRADING SYSTEM - SCAN
MARKET STATUS: BULLISH

[scanning stock universe...]

TOP CANDIDATES SELECTED FOR REVIEW
Stock  Entry   Stop Loss  Target  Win Rate  Backtest Return
PUBM   11.35   10.46      13.14   100.0     8

POSITION SIZING (max 7 positions):
Total Assets:      $6,894.46
Cash (buying power): $6,894.46
Open positions:    3 of 7
Slots available:   4
Per-slot size:     $984.92
Recommended per stock: $984.92

CANDIDATE: PUBM
Entry:             $11.35
Stop Loss:         $10.46
Target:            $13.14 (plus 15.8 percent)
Win Rate:          100.0 percent
Backtest Return:   8R
Recommended Size:  $984.92 (about 86 shares)

[Chart window opens, close to continue]

Do you want to buy PUBM? (y/n): y
Dollar amount for PUBM (recommended: $984.92, press Enter to accept):

Submitting -> BUY 86 shares of PUBM at market (about $976.10 total)

Configuration

Inside SIGNALBOT.py and SIGNALFORGE.py you can adjust:

MAX_POSITIONS - maximum number of open positions used for slot sizing (default is 7)
stocks - the list of tickers to scan
Filter thresholds - target upside multiplier, win rate range, and minimum backtest return


SIGNALFORGE.PY - SIGNAL ENGINE

The signal engine contains the underlying analysis logic and can be reused independently of the trading bot.

Key functions:

calculate_rsi(data, period=14)
Computes the Relative Strength Index for a price series. Above 70 means overbought, below 30 means oversold, 40 to 60 is neutral.

get_trend(hist)
Fits a linear regression line over the last 50 closes. A positive slope means an uptrend, a negative slope means a downtrend.

relative_strength(stock_hist, spy_hist)
Compares a stock's 20-day return against SPY's 20-day return to gauge whether it's outperforming the broader market.

backtest(hist)
Walks through a stock's history applying the same entry rules used live, then checks whether a 1.5 times ATR stop or 3 times ATR target was hit first within 10 bars. Returns win and loss counts, win rate, and total return in R-multiples.

run_scan(stocks)
Runs the full pipeline (indicators, signal, backtest) across the stock universe and returns a results table, also saved to advanced_swing_trades.xlsx.

pick_top_candidates(df, max_picks=7)
Applies the trading filters described above and returns the top-ranked candidates, also saved to top_candidates.xlsx.

Stock universe

The scan covers a broad list of tickers spanning large-cap, mid-cap, and small-cap stocks across all sectors. Delisted or renamed tickers are skipped automatically, since yfinance errors are caught and logged rather than treated as fatal.


FULL WORKFLOW

1. Setup - install dependencies, set Webull credentials
2. Scan - SIGNALFORGE.py logic scans the stock universe and runs backtests (this is the slowest step, expect several minutes for a large universe)
3. Filter - top 7 candidates are selected
4. Login - SIGNALBOT.py connects to Webull and pulls account balance and positions
5. Review - for each candidate, view chart, confirm yes or no, confirm or override dollar amount
6. Execute - confirmed trades are submitted as market orders
7. Wrap-up - updated portfolio is displayed


RISK MANAGEMENT AND LIMITATIONS

Manual confirmation only - nothing is bought without an explicit yes from you
No automatic exits - you manage stops and targets yourself
Market orders only - fills happen at the current market price, not a specified limit
Slot-based sizing - position size is capped by total assets divided by MAX_POSITIONS and your available cash, but you can override it per trade
End-of-day data - signals are based on daily historical data, not real-time ticks
API rate limits - Webull's API enforces request limits, so avoid running the scan back-to-back rapidly

Best practices

Test with a Webull paper trading account before going live
Stay at your computer while the bot runs, since it will pause for input
Always review the chart before confirming a trade
Don't risk more of your account on a single position than you're comfortable with, regardless of the recommended size
Keep a separate log of trades you take for your own performance review


TECHNICAL INDICATORS REFERENCE

RSI - 0 to 100 momentum oscillator. Above 70 is overbought, below 30 is oversold.
20 EMA - short-term trend
50 EMA - medium-term trend
200 EMA - long-term trend
ATR (Average True Range) - used to size stops (1.5 times ATR) and targets (3 times ATR)
Relative Strength - stock's 20-day return minus SPY's 20-day return
Market Filter - SPY and QQQ must be trading above their 50 and 200 EMA for new long signals to be considered


SECURITY NOTES

Store Webull credentials in environment variables, never hard-code them
If WEBULL_ACCOUNT_ID is not set, the bot auto-selects your Individual Margin account
Rotate your Webull API keys periodically from developer.webull.com


TROUBLESHOOTING

"Could not fetch account list"
Check that WEBULL_APP_KEY and WEBULL_APP_SECRET are set correctly and that your Webull account has API access enabled.

"No chart data for SYMBOL"
The ticker has insufficient history on Yahoo Finance. The chart is skipped and the confirmation prompt still appears.

"$XYZ: possibly delisted; no price data found"
Printed by yfinance for tickers that no longer exist. These are skipped automatically and don't stop the scan.

"Order failed"
Check buying power, confirm the market is open, and try a smaller dollar amount.

Chart window doesn't open, or backend error
Try changing matplotlib.use("TkAgg") near the top of the script to "Qt5Agg", or remove that line entirely to use your system default.


POSSIBLE FUTURE ENHANCEMENTS

Automated stop-loss and take-profit exits
Alternative position-sizing models, such as Kelly criterion or ATR-based risk sizing
Multi-timeframe confirmation
Real-time price alerts
Performance analytics dashboard
Configurable via YAML or JSON instead of editing source
Trade logging to a database
Email or SMS notifications


DISCLAIMER

This software is provided for educational and research purposes only and is not financial advice. Trading involves substantial risk of loss, and past performance does not guarantee future results. Use at your own risk. Never trade with money you cannot afford to lose, and test thoroughly with a paper trading account before using real capital.


Last Updated: June 2026
