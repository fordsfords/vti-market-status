#!/usr/bin/env python3
"""
VTI Market Status Generator for GitHub Actions
Creates an HTML page showing whether VTI is in a "down" market
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, timezone
import sys

def check_market_status(rolling_days=20):
    """
    Check if VTI is currently in a down market.

    Args:
        rolling_days: Number of days for rolling average (default 20)

    Returns:
        dict with market status and key metrics, or error info if failed
    """
    try:
        # Fetch 5 years of daily data plus the prior rolling_days data.
        # Set to yesterday's date to get the most-recent close.
        # Assumes the tool is run after midnight ET and before market open.
        end_date = datetime.now() - timedelta(days=1)
        start_date = end_date - timedelta(days=5*365 + rolling_days)

        print(f"Fetching VTI data from {start_date.date()} to {end_date.date()}...")
        vti = yf.Ticker("VTI")
        hist = vti.history(start=start_date, end=end_date)

        if hist.empty:
            raise ValueError("Failed to fetch VTI data")

        # Calculate rolling average
        hist['Rolling_Avg'] = hist['Close'].rolling(window=rolling_days).mean()

        # Drop rows where rolling average hasn't been calculated yet
        hist = hist.dropna(subset=['Rolling_Avg'])

        # Convert index to timezone-naive for easier date math
        hist.index = hist.index.tz_localize(None)

        # Get exactly 5 years of data
        five_years_ago = (end_date - timedelta(days=5*365)).replace(hour=0, minute=0, second=0, microsecond=0)
        hist_5yr = hist[hist.index >= five_years_ago]

        if hist_5yr.empty:
            raise ValueError("No data available in 5-year window")

        # Find the peak rolling average in the 5-year period
        peak_rolling_avg = hist_5yr['Rolling_Avg'].max()
        peak_date = hist_5yr['Rolling_Avg'].idxmax()

        # Get date of most recent data
        current_date = hist_5yr.index[-1]

        # Get latest actual closing price (for sell decision)
        latest_close = hist['Close'].iloc[-1]

        # Calculate threshold (95% of peak)
        threshold_95pct = peak_rolling_avg * 0.95

        # Determine if market is down
        is_down = latest_close < threshold_95pct

        return {
            'error': False,
            'is_down': is_down,
            'current_date': current_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'peak_rolling_avg': round(peak_rolling_avg, 2),
            'peak_date': peak_date.strftime('%Y-%m-%d'),
            'threshold_95pct': round(threshold_95pct, 2),
            'rolling_days': rolling_days,
            'latest_close': round(hist['Close'].iloc[-1], 2)
        }
    except Exception as e:
        error_msg = str(e)
        print(f"Error checking market status: {error_msg}")
        return {
            'error': True,
            'error_message': error_msg,
            'error_type': type(e).__name__,
            'rolling_days': rolling_days
        }

def generate_html(status, output_file='index.html'):
    """
    Generate an HTML page showing the market status.

    Args:
        status: dict from check_market_status()
        output_file: name of HTML file to create
    """
    # Get current timestamp
    generated_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

    # Check if there was an error
    if status.get('error', False):
        # Generate error page
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VTI Market Status - Error</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .container {{
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 800px;
            width: 100%;
            padding: 40px;
        }}

        h1 {{
            font-size: 2rem;
            margin-bottom: 10px;
            color: #2c3e50;
        }}

        .timestamp {{
            color: #7f8c8d;
            font-size: 0.9rem;
            margin-bottom: 30px;
        }}

        .error-box {{
            background: #dc3545;
            color: white;
            padding: 30px;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .error-icon {{
            font-size: 3rem;
            margin-bottom: 10px;
        }}

        .error-message {{
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 10px;
        }}

        .error-details {{
            background: #f8d7da;
            color: #721c24;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #dc3545;
            margin-bottom: 20px;
            text-align: left;
        }}

        .error-details h2 {{
            font-size: 1rem;
            margin-bottom: 10px;
        }}

        .error-details p {{
            font-size: 0.9rem;
            line-height: 1.8;
            margin-bottom: 10px;
        }}

        .error-details code {{
            background: #fff;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}

        .info-section {{
            background: #e8f4f8;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
            margin-bottom: 20px;
        }}

        .info-section h2 {{
            font-size: 1rem;
            color: #2c3e50;
            margin-bottom: 10px;
        }}

        .info-section p {{
            font-size: 0.9rem;
            color: #555;
            line-height: 1.8;
        }}

        .footer {{
            text-align: center;
            color: #95a5a6;
            font-size: 0.85rem;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
        }}

        @media (max-width: 600px) {{
            .container {{
                padding: 20px;
            }}

            h1 {{
                font-size: 1.5rem;
            }}

            .error-message {{
                font-size: 1.5rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>VTI Market Status</h1>
        <div class="timestamp">Last update attempted: {generated_time}</div>

        <div class="error-box">
            <div class="error-icon">❌</div>
            <div class="error-message">ERROR OCCURRED</div>
        </div>

        <div class="error-details">
            <h2>Error Details</h2>
            <p><strong>Type:</strong> <code>{status.get('error_type', 'Unknown')}</code></p>
            <p><strong>Message:</strong> {status.get('error_message', 'Unknown error')}</p>
        </div>

        <div class="info-section">
            <h2>What This Means</h2>
            <p>
                The VTI market status could not be retrieved. This might be due to network issues,
                Yahoo Finance API problems, or other technical difficulties. The page will attempt
                to update again during the next scheduled run.
            </p>
        </div>

        <div class="info-section" style="border-left-color: #e74c3c; background: #fdeaea;">
            <h2>⚠️ Action Required</h2>
            <p>
                Until this issue is resolved, <strong>do not sell</strong> without manually
                checking current market conditions.
            </p>
        </div>

        <div class="footer">
            Generated automatically via GitHub Actions<br>
            Check the Actions log for more details
        </div>
    </div>
</body>
</html>
"""
        with open(output_file, 'w') as f:
            f.write(html)
        print(f"Error page generated: {output_file}")
        return

    # Normal status page - determine status color and message
    if status['is_down']:
        status_color = '#dc3545'  # Red
        status_message = 'MARKET IS DOWN'
        status_icon = '⚠️'
    else:
        status_color = '#28a745'  # Green
        status_message = 'MARKET IS OK'
        status_icon = '✓'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VTI Market Status</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .container {{
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 800px;
            width: 100%;
            padding: 40px;
        }}

        h1 {{
            font-size: 2rem;
            margin-bottom: 10px;
            color: #2c3e50;
        }}

        .timestamp {{
            color: #7f8c8d;
            font-size: 0.9rem;
            margin-bottom: 30px;
        }}

        .status-box {{
            background: {status_color};
            color: white;
            padding: 30px;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .status-icon {{
            font-size: 3rem;
            margin-bottom: 10px;
        }}

        .status-message {{
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 10px;
        }}

        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .metric {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}

        .metric-label {{
            font-size: 0.85rem;
            color: #7f8c8d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 5px;
        }}

        .metric-value {{
            font-size: 1.5rem;
            font-weight: bold;
            color: #2c3e50;
        }}

        .metric-subtext {{
            font-size: 0.85rem;
            color: #95a5a6;
            margin-top: 5px;
        }}

        .info-section {{
            background: #e8f4f8;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
            margin-bottom: 20px;
        }}

        .info-section h2 {{
            font-size: 1rem;
            color: #2c3e50;
            margin-bottom: 10px;
        }}

        .info-section p {{
            font-size: 0.9rem;
            color: #555;
            line-height: 1.8;
        }}

        .footer {{
            text-align: center;
            color: #95a5a6;
            font-size: 0.85rem;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
        }}

        @media (max-width: 600px) {{
            .container {{
                padding: 20px;
            }}

            h1 {{
                font-size: 1.5rem;
            }}

            .status-message {{
                font-size: 1.5rem;
            }}

            .metric-value {{
                font-size: 1.2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>VTI Market Status</h1>
        <div class="timestamp">Last updated: {generated_time}</div>

        <div class="status-box">
            <div class="status-icon">{status_icon}</div>
            <div class="status-message">{status_message}</div>
        </div>

        <div class="metrics">
            <div class="metric">
                <div class="metric-label">5-Year Peak, Smoothed</div>
                <div class="metric-value">${status['peak_rolling_avg']}</div>
                <div class="metric-subtext">Peak on {status['peak_date']}</div>
            </div>

            <div class="metric">
                <div class="metric-label">95% of Peak</div>
                <div class="metric-value">${status['threshold_95pct']}</div>
                <div class="metric-subtext">Threshold for Down Market</div>
            </div>

            <div class="metric">
                <div class="metric-label">Last Closing Price</div>
                <div class="metric-value">${status['latest_close']}</div>
                <div class="metric-subtext">Close on {status['end_date']}</div>
            </div>
        </div>

        <div class="info-section">
            <h2>How This Works</h2>
            <p>
                This page finds the peak {status['rolling_days']}-day rolling average of VTI over the past 5 years
                (smoothing eliminates false peaks from volatility), then compares the most recent closing price
                against 95% of that peak. When the current price falls more than 5% below the peak, the market is
                considered "down".
            </p>
        </div>

        <div class="info-section" style="border-left-color: #e74c3c; background: #fdeaea;">
            <h2>⚠️ Important Reminder</h2>
            <p>
                Always use a <strong>limit order</strong> when selling. Even if this page shows
                "MARKET IS OK", you can get sudden market drops.
            </p>
        </div>

        <div class="footer">
            Generated automatically via GitHub Actions<br>
            Data updates daily at approximately 06:00 UTC
        </div>
    </div>
</body>
</html>
"""

    with open(output_file, 'w') as f:
        f.write(html)

    print(f"HTML file generated: {output_file}")

def main():
    """Main function to check market status and generate HTML."""
    # Check market status
    rolling_days = 20  # Must be less than 100.
    print("Checking VTI market status...")
    status = check_market_status(rolling_days=rolling_days)

    # Print to console for GitHub Actions logs
    print("\n" + "="*60)
    print("VTI MARKET STATUS")
    print("="*60)

    if status.get('error', False):
        # Error case - print error details
        print(f"ERROR: {status['error_type']}")
        print(f"Message: {status['error_message']}")

        # Generate error HTML page
        generate_html(status)
        print("⚠ Generated error page: index.html")
    else:
        # Success case - print status details
        print(f"Date: {status['current_date']}")
        print(f"5-year peak, smoothed: ${status['peak_rolling_avg']} (on {status['peak_date']})")
        print(f"95% threshold: ${status['threshold_95pct']}")
        print(f"Latest close: ${status['latest_close']}")

        if status['is_down']:
            print("STATUS: MARKET IS DOWN - Maybe don't sell")
        else:
            print("STATUS: MARKET IS OK - Can sell")

        print("="*60 + "\n")

        # Generate HTML
        generate_html(status)
        print("✓ Successfully generated index.html")

if __name__ == "__main__":
    main()
