"""
View Daily Scraper Reports
==========================

Query and display daily scraper run reports from the database.

Usage:
    python view_reports.py [source_site] [days]
    
    source_site: Filter by source site (e.g., "Breaking Bourbon")
    days: Number of days to look back (default: 7)
"""

import sys
from pathlib import Path
from database import get_connection, get_daily_reports


def display_reports(source_site=None, days=7):
    """
    Display daily scraper reports.
    
    Args:
        source_site: Filter by source site name (optional)
        days: Number of days to look back
    """
    conn = get_connection()
    
    reports = get_daily_reports(conn, source_site=source_site, days=days)
    
    if not reports:
        print(f"\nNo reports found for the last {days} day(s)")
        if source_site:
            print(f"Filtered by: {source_site}")
        conn.close()
        return
    
    print("\n" + "="*80)
    print("DAILY SCRAPER REPORTS")
    print("="*80)
    if source_site:
        print(f"Source Site: {source_site}")
    print(f"Days Back: {days}")
    print(f"Total Reports: {len(reports)}")
    print("="*80 + "\n")
    
    for report in reports:
        status_icon = {
            'success': '✓',
            'error': '✗',
            'partial': '⚠'
        }.get(report['status'], '?')
        
        print(f"{status_icon} [{report['run_date']}] {report['source_site']}")
        print(f"   Status: {report['status'].upper()}")
        print(f"   Reviews Found: {report['reviews_found']}")
        print(f"   Reviews Added: {report['reviews_added']}")
        
        if report['execution_time']:
            print(f"   Execution Time: {report['execution_time']:.2f}s")
        
        if report['error_message']:
            print(f"   Errors: {report['error_message']}")
        
        print()
    
    # Summary statistics
    total_runs = len(reports)
    successful = sum(1 for r in reports if r['status'] == 'success')
    errors = sum(1 for r in reports if r['status'] == 'error')
    partial = sum(1 for r in reports if r['status'] == 'partial')
    total_found = sum(r['reviews_found'] for r in reports)
    total_added = sum(r['reviews_added'] for r in reports)
    
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total Runs:       {total_runs}")
    print(f"Successful:       {successful}")
    print(f"With Errors:      {errors}")
    print(f"Partial Success: {partial}")
    print(f"Total Found:      {total_found}")
    print(f"Total Added:      {total_added}")
    print("="*80 + "\n")
    
    conn.close()


def main():
    """Main entry point."""
    source_site = None
    days = 7
    
    if len(sys.argv) > 1:
        source_site = sys.argv[1]
    
    if len(sys.argv) > 2:
        try:
            days = int(sys.argv[2])
        except ValueError:
            print(f"Error: '{sys.argv[2]}' is not a valid number of days")
            print("Usage: python view_reports.py [source_site] [days]")
            sys.exit(1)
    
    display_reports(source_site=source_site, days=days)


if __name__ == "__main__":
    main()

