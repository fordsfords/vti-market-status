# VTI Market Status - GitHub Actions Setup

Automatically generate a web page showing whether VTI is in a "down" market, updated daily via GitHub Actions.

Thanks to Claude.ai for initially writing most of the content of this repo.
Note that I, Steven Ford, have reviewed all of the content, have made changes,
and am ultimately responsible for it.

## Down Market

What is a "down" market?
It's a market condition that my retirement strategy watches for.
A central concept of my strategy is to never "sell low" stocks.
I want an objective and quantatative way to define when the market is "down".

This tool fetches 5 years worth of price data for the VTI stock (an ETF) and does a 20-day
rolling average and finds the peak value. This is the peak VTI price over the past 5 years.
The rolling average is done to eliminate spikes of volatility.

Given that peak value, a "down" market means that the current price of VTI is 5% or more below that peak.

## Setup Instructions

Notes to myself on how to deploy this tool on GitHub.

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

### 4. Enable GitHub Pages

1. Go to Settings → Pages (left sidebar)
2. Under "Source", select "Deploy from a branch"
3. Under "Branch", select `gh-pages` and folder `/root`
4. Click "Save"
5. **Note:** The `gh-pages` branch won't exist until you run the workflow for the first time
6. After running the workflow once, refresh the Pages settings and you'll see your site URL

### 5. Run the Workflow Manually (First Time)

1. Go to Actions tab
2. Click "Update VTI Market Status" workflow
3. Click "Run workflow" → "Run workflow"
4. Wait ~30 seconds for it to complete
5. A new `gh-pages` branch will be created with just `index.html`
6. Visit your GitHub Pages URL to see the status page

**Note:** The workflow only touches the `gh-pages` branch. Your `main` branch stays clean with just source code - no daily commits cluttering your history.

### 6. Verify Automatic Updates

The workflow runs automatically daily at 00:00 UTC (after market close). You can verify by:
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
  - cron: '0 0 * * *'  # Current: 00:00 UTC daily
  # Examples:
  # - cron: '0 12 * * *'  # 12:00 UTC (7am ET / 4am PT)
  # - cron: '0 21 * * *'  # 21:00 UTC (4pm ET / 1pm PT)
```

### Change Rolling Average Period

Edit `vti_market_status.py`:
```python
rolling_days = 20  # Change to 10, 30, 50, etc.
```

## Troubleshooting

**Workflow fails with "permission denied"**:
- Go to Settings → Actions → General
- Under "Workflow permissions", select "Read and write permissions"
- Click "Save"

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

## Security Note

This setup requires no API keys or secrets. All data comes from Yahoo Finance's public API.
