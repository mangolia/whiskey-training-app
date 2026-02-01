# Installation & Setup Guide

## Prerequisites

1. Python 3.8+ installed
2. Virtual environment set up
3. Dependencies installed

## Step 1: Install Dependencies

```bash
cd ~/whiskey-scraper
source venv/bin/activate
pip install -r requirements.txt
```

## Step 2: Verify Configuration

Edit `config.yaml` if needed (defaults should work):
- Schedule time (default: 11pm Eastern)
- Log directory (default: `logs/`)
- Dashboard port (default: 5000)

## Step 3: Set Up Automation

Run the setup script to install the launchd job:

```bash
./setup_automation.sh
```

This will:
- Copy the plist file to `~/Library/LaunchAgents/`
- Load the job into launchd
- Set up daily automation at 11pm EST

## Step 4: Verify Installation

Check that the job is loaded:

```bash
launchctl list | grep com.whiskey-scraper.daily
```

You should see the job listed.

## Step 5: Start Dashboard

Start the Flask dashboard:

```bash
source venv/bin/activate
python app.py
```

Then open your browser to: `http://127.0.0.1:5000`

## Testing

### Test the Automated Script Manually

```bash
source venv/bin/activate
python automated_daily_check.py --manual
```

### Test Battery Detection

The script will automatically skip if on battery (unless `--manual` flag is used).

### View Logs

```bash
# View today's log
tail -f logs/scraper-$(date +%Y-%m-%d).log

# View error log
tail -f logs/errors.log

# View launchd output
tail -f logs/launchd.out
tail -f logs/launchd.err
```

## Managing the Automation

### Check Status
```bash
launchctl list | grep com.whiskey-scraper.daily
```

### Unload (Disable)
```bash
launchctl unload ~/Library/LaunchAgents/com.whiskey-scraper.daily.plist
```

### Reload (After Changes)
```bash
launchctl unload ~/Library/LaunchAgents/com.whiskey-scraper.daily.plist
launchctl load ~/Library/LaunchAgents/com.whiskey-scraper.daily.plist
```

### Remove Completely
```bash
launchctl unload ~/Library/LaunchAgents/com.whiskey-scraper.daily.plist
rm ~/Library/LaunchAgents/com.whiskey-scraper.daily.plist
```

## Troubleshooting

### Job Not Running
1. Check logs: `logs/launchd.err`
2. Verify plist is loaded: `launchctl list | grep whiskey`
3. Check file permissions
4. Verify Python path in plist matches your venv

### Battery Issues
- Mac must be plugged into power for wake-from-sleep
- Check Energy Saver settings
- Manual runs work on battery (use `--manual` flag)

### Dashboard Not Loading
1. Check if Flask is installed: `pip list | grep Flask`
2. Check if port 5000 is in use: `lsof -i :5000`
3. Check app.py logs for errors

### Dependencies Missing
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Next Steps

1. ✅ Automation is set up and running
2. ✅ Dashboard is available at http://127.0.0.1:5000
3. ✅ Logs are being created in `logs/` directory
4. ✅ Errors are tracked in dashboard

The system will automatically:
- Run daily at 11pm EST
- Wake Mac from sleep (if plugged in)
- Retry on failures (up to 3 times)
- Log all activity
- Track errors in dashboard

