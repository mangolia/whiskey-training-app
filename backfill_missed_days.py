"""
Backfill Missed Days Script
============================

Standalone script for manually backfilling missed days when the scraper didn't run.

Usage:
    python backfill_missed_days.py --auto-detect
    python backfill_missed_days.py --start-date 2026-01-01 --end-date 2026-01-05
    python backfill_missed_days.py --days 7
    python backfill_missed_days.py --auto-detect --dry-run
"""

import sys
import argparse
import yaml
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from database import (
    get_connection,
    create_database,
    detect_missed_days
)
from scrapers.breaking_bourbon import BreakingBourbonScraper
from automated_daily_check import check_reviews_for_specific_date, load_config


def setup_logging_for_backfill():
    """Set up logging for backfill script."""
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"backfill-{datetime.now().strftime('%Y-%m-%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


def backfill_date_range(start_date: datetime, end_date: datetime, dry_run: bool = False) -> Dict:
    """
    Backfill a specific date range.
    
    Args:
        start_date: Start date (inclusive)
        end_date: End date (inclusive)
        dry_run: If True, don't actually scrape, just show what would be done
    
    Returns:
        Summary dictionary
    """
    logger = logging.getLogger(__name__)
    
    # Ensure database exists
    create_database()
    
    # Initialize scraper
    scraper = BreakingBourbonScraper()
    
    # Generate list of dates to backfill
    current_date = start_date
    dates_to_backfill = []
    
    while current_date <= end_date:
        dates_to_backfill.append(current_date)
        current_date += timedelta(days=1)
    
    logger.info(f"Backfilling date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    logger.info(f"Total dates to process: {len(dates_to_backfill)}")
    
    if dry_run:
        logger.info("DRY RUN MODE - No actual scraping will be performed")
        for date in dates_to_backfill:
            logger.info(f"  Would backfill: {date.strftime('%Y-%m-%d')}")
        return {
            'status': 'dry_run',
            'dates_processed': len(dates_to_backfill),
            'dates_with_reviews': 0,
            'dates_with_zero_reviews': 0,
            'total_reviews_added': 0
        }
    
    # Process each date
    dates_with_reviews = 0
    dates_with_zero_reviews = 0
    total_reviews_added = 0
    errors = []
    
    for target_date in dates_to_backfill:
        try:
            date_str = target_date.strftime('%Y-%m-%d')
            logger.info(f"Backfilling {date_str}...")
            
            result = check_reviews_for_specific_date(scraper, target_date, logger, is_backfill=True)
            
            if result['reviews_found'] > 0:
                dates_with_reviews += 1
                total_reviews_added += result['reviews_added']
            else:
                dates_with_zero_reviews += 1
            
            if result['status'] == 'error':
                errors.append(f"{date_str}: {result.get('errors', ['Unknown error'])}")
                
        except Exception as e:
            error_msg = f"Error backfilling {target_date.strftime('%Y-%m-%d')}: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
            continue
    
    return {
        'status': 'success' if not errors else 'partial',
        'dates_processed': len(dates_to_backfill),
        'dates_with_reviews': dates_with_reviews,
        'dates_with_zero_reviews': dates_with_zero_reviews,
        'total_reviews_added': total_reviews_added,
        'errors': errors
    }


def backfill_auto_detect(config: Dict, dry_run: bool = False) -> Dict:
    """
    Auto-detect and backfill missed days.
    
    Args:
        config: Configuration dictionary
        dry_run: If True, don't actually scrape, just show what would be done
    
    Returns:
        Summary dictionary
    """
    logger = logging.getLogger(__name__)
    
    backfill_config = config.get('backfill', {})
    lookback_days = backfill_config.get('lookback_window_days', 30)
    max_days_to_backfill = backfill_config.get('max_days_to_backfill', 7)
    
    # Get database connection
    conn = get_connection()
    
    # Detect missed days
    missed_dates = detect_missed_days(conn, lookback_days=lookback_days)
    conn.close()
    
    if not missed_dates:
        logger.info("No missed days detected")
        return {
            'status': 'success',
            'dates_processed': 0,
            'dates_with_reviews': 0,
            'dates_with_zero_reviews': 0,
            'total_reviews_added': 0
        }
    
    # Limit to max_days_to_backfill
    missed_dates = missed_dates[:max_days_to_backfill]
    
    logger.info(f"Found {len(missed_dates)} missed day(s): {', '.join(missed_dates)}")
    
    if dry_run:
        logger.info("DRY RUN MODE - No actual scraping will be performed")
        for date_str in missed_dates:
            logger.info(f"  Would backfill: {date_str}")
        return {
            'status': 'dry_run',
            'dates_processed': len(missed_dates),
            'dates_with_reviews': 0,
            'dates_with_zero_reviews': 0,
            'total_reviews_added': 0
        }
    
    # Initialize scraper
    scraper = BreakingBourbonScraper()
    
    # Backfill each missed date
    dates_with_reviews = 0
    dates_with_zero_reviews = 0
    total_reviews_added = 0
    errors = []
    
    for date_str in missed_dates:
        try:
            # Parse the date
            target_date = datetime.strptime(date_str, '%Y-%m-%d')
            
            logger.info(f"Backfilling {date_str}...")
            
            # Check reviews for this date
            result = check_reviews_for_specific_date(scraper, target_date, logger, is_backfill=True)
            
            if result['reviews_found'] > 0:
                dates_with_reviews += 1
                total_reviews_added += result['reviews_added']
            else:
                dates_with_zero_reviews += 1
            
            if result['status'] == 'error':
                errors.append(f"{date_str}: {result.get('errors', ['Unknown error'])}")
            
        except Exception as e:
            error_msg = f"Error backfilling {date_str}: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
            continue
    
    return {
        'status': 'success' if not errors else 'partial',
        'dates_processed': len(missed_dates),
        'dates_with_reviews': dates_with_reviews,
        'dates_with_zero_reviews': dates_with_zero_reviews,
        'total_reviews_added': total_reviews_added,
        'errors': errors
    }


def main():
    """Main entry point for backfill script."""
    parser = argparse.ArgumentParser(
        description='Backfill missed days for whiskey scraper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect and backfill missed days
  python backfill_missed_days.py --auto-detect
  
  # Backfill specific date range
  python backfill_missed_days.py --start-date 2026-01-01 --end-date 2026-01-05
  
  # Backfill last 7 days
  python backfill_missed_days.py --days 7
  
  # Dry run to see what would be scraped
  python backfill_missed_days.py --auto-detect --dry-run
        """
    )
    
    # Mutually exclusive group for backfill mode
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--auto-detect', action='store_true',
                           help='Auto-detect missed days and backfill them')
    mode_group.add_argument('--start-date', type=str, metavar='YYYY-MM-DD',
                           help='Start date for date range (requires --end-date)')
    mode_group.add_argument('--days', type=int, metavar='N',
                           help='Backfill last N days')
    
    parser.add_argument('--end-date', type=str, metavar='YYYY-MM-DD',
                       help='End date for date range (defaults to today)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be scraped without actually scraping')
    
    args = parser.parse_args()
    
    # Set up logging
    logger = setup_logging_for_backfill()
    
    # Load configuration
    config = load_config()
    
    # Parse dates if provided
    start_date = None
    end_date = None
    
    if args.start_date:
        try:
            start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
        except ValueError:
            logger.error(f"Invalid start date format: {args.start_date}. Use YYYY-MM-DD")
            sys.exit(1)
        
        if args.end_date:
            try:
                end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
            except ValueError:
                logger.error(f"Invalid end date format: {args.end_date}. Use YYYY-MM-DD")
                sys.exit(1)
        else:
            end_date = datetime.now()
        
        if start_date > end_date:
            logger.error("Start date must be before or equal to end date")
            sys.exit(1)
    
    # Execute backfill based on mode
    if args.auto_detect:
        logger.info("Auto-detecting missed days...")
        result = backfill_auto_detect(config, dry_run=args.dry_run)
    elif args.start_date:
        logger.info(f"Backfilling date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        result = backfill_date_range(start_date, end_date, dry_run=args.dry_run)
    elif args.days:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=args.days - 1)  # -1 to include today
        logger.info(f"Backfilling last {args.days} days")
        result = backfill_date_range(start_date, end_date, dry_run=args.dry_run)
    else:
        logger.error("Must specify --auto-detect, --start-date, or --days")
        sys.exit(1)
    
    # Print summary
    logger.info("=" * 60)
    logger.info("Backfill Summary")
    logger.info("=" * 60)
    logger.info(f"Status: {result['status']}")
    logger.info(f"Dates processed: {result['dates_processed']}")
    logger.info(f"Dates with reviews: {result['dates_with_reviews']}")
    logger.info(f"Dates with zero reviews: {result['dates_with_zero_reviews']}")
    logger.info(f"Total reviews added: {result['total_reviews_added']}")
    
    if result.get('errors'):
        logger.warning(f"Errors encountered: {len(result['errors'])}")
        for error in result['errors']:
            logger.warning(f"  - {error}")
    
    # Exit with appropriate code
    if result['status'] == 'error':
        sys.exit(1)
    elif result['status'] == 'partial':
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
