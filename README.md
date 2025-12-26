# VTI Market Status - GitHub Actions Setup

Automatically generate a web page showing whether VTI is in a "down" market, updated daily via GitHub Actions.
The idea is to avoid "selling low".

Thanks to Claude.ai for initially writing most of the content of this repo.
Note that I, Steven Ford, have reviewed all of the content, have made changes,
and am ultimately responsible for it.

To see the market status as of the previous close: https://www.geeky-boy.com/vti-market-status/

## Down Market

This tool fetches 10 years worth of price data for the VTI stock (an ETF) and does a 20-day
rolling average and finds the peak value. This is the peak VTI price over the past 10 years.
The rolling average is done to eliminate spikes of volatility.
95% of that peak is the down market threshold.
If the previous trading day's close price is below that threshold, the market is "down".

Why do I care?
My retirement strategy watches for a "down market".
A central concept of my strategy is to never "sell stocks low".
I want an objective and quantatative way to define when the market is "down" before
I sell stocks.

Here is my installation of this tool: https://www.geeky-boy.com/vti-market-status/

Here is a recent history of VTI price data: https://finance.yahoo.com/quote/VTI/history/

**Warning:** Do not make trading decisions based solely on this tool.
For one thing, there might be bugs in this code;
it has not been extensively vetted by trusted entities.
For another, it bases its decision on the most-recent closing price.
But market declines frequently happen immediately after the open since overnight bad news can
affect the markets.
So a Tuesday close at an all-time high can be erased within seconds after Wednesday's open.

A better approach: when selling VTI, use a limit order with the threshold value 
(5% below the 10-year peak) as the minimum price.
This prevents selling into a sudden drop that occurs after you place your order.

## Notes to myself on how to deploy this tool on GitHub.

### 1. Create the GitHub Repository

1. Go to https://github.com and create a new repository
2. Name it something like `vti-market-status`
3. Make it **public** (required for free GitHub Pages)
4. Initialize with a README

### 2. Upload Files

Upload these files to your repository:
- `vti_market_status.py` - The Python script
- `requirements.txt` - Python dependencies
- `.github/workflows/update-vti-status.yml` - GitHub Actions workflow

### 3. Enable GitHub Actions

1. Go to your repository on GitHub
2. Click the "Actions" tab
3. If prompted, click "I understand my workflows, go ahead and enable them"
4. You should see the "Update VTI Market Status" workflow listed

### 4. Set Workflow Permissions

**Important:** This step is required or the workflow will fail with a 403 permission error.

1. Go to Settings → Actions → General (left sidebar)
2. Scroll down to "Workflow permissions"
3. Select "Read and write permissions"
4. Click "Save"

### 5. Run the Workflow Manually (First Time)

1. Go to Actions tab
2. Click "Update VTI Market Status" workflow
3. Click "Run workflow" → "Run workflow"
4. Wait ~30 seconds for it to complete
5. A new `gh-pages` branch will be created with just `index.html`

**Note:** The workflow only touches the `gh-pages` branch. Your `main` branch stays clean with just source code - no daily commits cluttering your history.

### 6. Enable GitHub Pages

Now that the `gh-pages` branch exists, you can enable GitHub Pages:

1. Go to Settings → Pages (left sidebar)
2. Under "Source", select "Deploy from a branch"
3. Under "Branch", select `gh-pages` and folder `/` (root)
4. Click "Save"
5. Wait a few minutes, then refresh - you'll see your site URL
6. Visit your GitHub Pages URL to see the status page

### 7. Verify Automatic Updates

The workflow runs automatically daily at 06:00 UTC (1am EST / 2am EDT). You can verify by:
- Checking the Actions tab for scheduled runs
- Switching to the `gh-pages` branch - you'll see the timestamp in the commit message
- Visiting your live site to see the updated timestamp

## URLs

After setup, you can bookmark:
- **Live page**: `https://YOUR-USERNAME.github.io/vti-market-status/`

## Logs

* Go to your repo on GitHub
* Click the "Actions" tab
* You'll see a list of workflow runs (each with a date/commit message)
* Click any run to see the details
* Click the job name (like "update-status") to see logs
* Each step shows expandable logs

Each workflow run gets its own separate log which is retained for 90 days.
 
## Customization

### Change Update Time

Edit `.github/workflows/update-vti-status.yml`:
```yaml
schedule:
  - cron: '0 6 * * *'  # 06:00 UTC (1am EST / 2am EDT)
```

NOTE: the tool assumes that it is run after midnight eastern time and before
market open. If you run it while the market is open, you won't get the
previous day's close.

### Change Rolling Average Period

Edit `vti_market_status.py`:
```python
rolling_days = 20  # Change to 10, 30, 50, etc.
```

## Troubleshooting

**Workflow fails with "permission denied"**:
- This means workflow permissions weren't set correctly
- See step 4 in the setup instructions above
- Go to Settings → Actions → General, select "Read and write permissions", then Save

**GitHub Pages not working**:
- Ensure repository is public
- Check Settings → Pages shows the site URL
- Wait 5 minutes after first enabling Pages

**Data looks old**:
- Remember: Market data is from previous trading day
- Check Actions tab to see when workflow last ran
- Manually trigger workflow if needed

## Running Locally

To test changes locally before pushing:
```bash
pip install -r requirements.txt
python vti_market_status.py
open index.html  # macOS
# or
start index.html  # Windows
```

## Technical Details

### Dependencies

This tool uses **yfinance**, an unofficial open-source Python library that scrapes data from Yahoo Finance's website. Key points for maintainers:

- **Not official**: Yahoo discontinued their official Finance API in 2017. yfinance is a third-party library maintained by Ran Aroussi.
- **Documentation**: https://ranaroussi.github.io/yfinance/
- **PyPI page**: https://pypi.org/project/yfinance/
- **Could break**: Since yfinance scrapes Yahoo Finance's website, changes to the website structure could break the library. This is the main risk of this tool.
- **Free and no API keys**: No account or authentication required.

The tool also uses **pandas** for data manipulation, particularly for calculating rolling averages.

### Data Behavior

Understanding when data is available and what "current price" means:

**Trading Days vs Calendar Days**:
- Stock markets are closed on weekends and holidays
- If the workflow runs on Saturday/Sunday, the "current price" will be Friday's closing price
- If the workflow runs on a market holiday, the "current price" will be from the last trading day
- The `current_date` shown on the page reflects the date of the most recent trading data, not necessarily today's date

**Data Timing**:
- The workflow is scheduled to run at 06:00 UTC (1am EST / 2am EDT)
- Market closes at 4pm ET, but Yahoo Finance data may not be immediately available
- There can be a delay of minutes to hours before end-of-day data appears
- Weekend runs will always show Friday's data

**Example**: If you check the page on Sunday December 22, 2024, you'll see data from Friday December 20, 2024.

### Rolling Average Calculation

The code fetches more than 10 years of data to properly calculate the rolling average:

```python
start_date = end_date - timedelta(days=5*365 + rolling_days)
```

This expansion by `rolling_days` (default 20) is necessary because:
- A 20-day rolling average needs 20 days of prior data to calculate
- Without this expansion, the first ~20 days of the 10-year window wouldn't have a rolling average
- After calculating the rolling average for all data, the code filters to exactly 10 years

For example, with `rolling_days=20`, the code:
1. Fetches 10 years + 20 days of data
2. Calculates 20-day rolling average for all data
3. Filters to exactly 10 years of data (where rolling average is defined)
4. Finds the peak rolling average in that 10-year window

#### Comparing Averaged Data to Non-Averaged Data

The peak is calculated using a smoothed 20-day rolling average (to avoid false peaks from
volatility spikes), but the current price check uses today's actual closing price. This asymmetry is
intentional - we want to detect market crashes immediately, not after they've been smoothed over 20 days.
If a crash happens today, we need to know NOW to avoid selling into it.

### Timezone Handling

Yahoo Finance returns data with timezone information (typically US/Eastern for US stocks). The code strips this timezone info on line 41:

```python
hist.index = hist.index.tz_localize(None)
```

This is done to simplify date comparisons and avoid timezone-related edge cases. Since we only care about daily closing prices (not intraday times), the timezone doesn't affect the results.

### Maintenance

**If yfinance breaks** (returns errors, empty data, or wrong data):

1. **Check GitHub Issues**: Visit https://github.com/ranaroussi/yfinance/issues to see if it's a known problem
2. **Update yfinance**: Try updating to the latest version:
   ```bash
   pip install --upgrade yfinance
   ```
   Then update `requirements.txt` with the new version number
3. **Check Yahoo Finance**: Visit https://finance.yahoo.com/quote/VTI to verify the website is working
4. **Alternative data sources**: If yfinance is permanently broken, consider:
   - **polygon.io** - Paid service with free tier, official exchange data
   - **IEX Cloud** - Paid service with free tier, lower latency
   - **Alpha Vantage** - Free API with rate limits
   - **Tiingo** - Free for end-of-day data

**Breaking changes to watch for**:
- Yahoo Finance website structure changes (would break yfinance)
- yfinance API changes (check release notes when updating)
- Changes to VTI ticker symbol (unlikely but possible)
- GitHub Actions workflow changes (Actions occasionally deprecate old action versions)

## Security Note

This setup requires no API keys or secrets. All data comes from Yahoo Finance via the yfinance library (see Technical Details above for important notes about this unofficial library).
