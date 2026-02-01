#!/bin/bash
# Setup script for automated daily scraper
# This script installs the launchd plist and sets up the automation

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLIST_NAME="com.whiskey-scraper.daily"
PLIST_FILE="$SCRIPT_DIR/$PLIST_NAME.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
TARGET_PLIST="$LAUNCH_AGENTS_DIR/$PLIST_NAME.plist"

echo "=========================================="
echo "Whiskey Scraper Automation Setup"
echo "=========================================="
echo ""

# Check if plist file exists
if [ ! -f "$PLIST_FILE" ]; then
    echo "❌ Error: Plist file not found at $PLIST_FILE"
    exit 1
fi

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$LAUNCH_AGENTS_DIR"

# Copy plist to LaunchAgents
echo "📋 Copying plist file to LaunchAgents..."
cp "$PLIST_FILE" "$TARGET_PLIST"

# Unload existing job if it exists
if launchctl list | grep -q "$PLIST_NAME"; then
    echo "🔄 Unloading existing job..."
    launchctl unload "$TARGET_PLIST" 2>/dev/null || true
fi

# Load the job
echo "✅ Loading launchd job..."
launchctl load "$TARGET_PLIST"

# Check if it loaded successfully
if launchctl list | grep -q "$PLIST_NAME"; then
    echo ""
    echo "✅ Automation setup complete!"
    echo ""
    echo "The scraper will run daily at 11pm Eastern Time."
    echo ""
    echo "To check status:"
    echo "  launchctl list | grep $PLIST_NAME"
    echo ""
    echo "To unload (disable):"
    echo "  launchctl unload $TARGET_PLIST"
    echo ""
    echo "To reload (after changes):"
    echo "  launchctl unload $TARGET_PLIST"
    echo "  launchctl load $TARGET_PLIST"
    echo ""
else
    echo "⚠️  Warning: Job may not have loaded correctly"
    echo "Check logs at: $SCRIPT_DIR/logs/launchd.err"
fi

