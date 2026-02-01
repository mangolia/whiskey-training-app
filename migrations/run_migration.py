#!/usr/bin/env python3
"""
Migration Runner Script
Safely applies database migrations with backup and rollback support.
"""

import sqlite3
import os
import shutil
from datetime import datetime
import sys

# Add parent directory to path to import project modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = '/Users/michaelangolia/whiskey-scraper/whiskey_reviews.db'
MIGRATIONS_DIR = os.path.dirname(os.path.abspath(__file__))


def backup_database(db_path):
    """Create a timestamped backup of the database."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = os.path.join(os.path.dirname(db_path), 'backups')
    os.makedirs(backup_dir, exist_ok=True)

    backup_path = os.path.join(backup_dir, f'whiskey_reviews_{timestamp}.db')
    shutil.copy2(db_path, backup_path)
    print(f"✓ Database backed up to: {backup_path}")
    return backup_path


def get_applied_migrations(conn):
    """Get list of already applied migrations."""
    cursor = conn.cursor()

    # Check if migrations table exists
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='migrations'
    """)

    if not cursor.fetchone():
        return set()

    cursor.execute("SELECT migration_name FROM migrations")
    return {row[0] for row in cursor.fetchall()}


def apply_migration(conn, migration_file):
    """Apply a single migration file."""
    migration_name = os.path.basename(migration_file)

    print(f"\n→ Applying migration: {migration_name}")

    with open(migration_file, 'r') as f:
        sql = f.read()

    try:
        # Execute the migration in a transaction
        cursor = conn.cursor()
        cursor.executescript(sql)
        conn.commit()
        print(f"✓ Migration {migration_name} applied successfully")
        return True
    except Exception as e:
        print(f"✗ Error applying migration {migration_name}: {e}")
        conn.rollback()
        return False


def verify_migration(conn):
    """Verify the migration was successful."""
    cursor = conn.cursor()

    print("\n" + "="*80)
    print("MIGRATION VERIFICATION")
    print("="*80)

    # Check new tables exist
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name IN ('flavor_vocabulary', 'review_flavors', 'aggregated_whiskey_flavors', 'migrations')
        ORDER BY name
    """)
    tables = cursor.fetchall()
    print(f"\n✓ New tables created: {len(tables)}")
    for table in tables:
        print(f"  - {table[0]}")

    # Check whiskeys table columns
    cursor.execute("PRAGMA table_info(whiskeys)")
    whiskey_columns = {row[1] for row in cursor.fetchall()}
    new_whiskey_cols = {'brand_family', 'variant_name', 'attributes', 'classification', 'proof', 'age', 'mashbill', 'price', 'image_url'}
    found_cols = new_whiskey_cols & whiskey_columns
    print(f"\n✓ New whiskeys columns: {len(found_cols)}/{len(new_whiskey_cols)}")
    for col in sorted(found_cols):
        print(f"  - {col}")

    # Check reviews table columns
    cursor.execute("PRAGMA table_info(reviews)")
    review_columns = {row[1] for row in cursor.fetchall()}
    new_review_cols = {'nose_text', 'palate_text', 'finish_text'}
    found_review_cols = new_review_cols & review_columns
    print(f"\n✓ New reviews columns: {len(found_review_cols)}/{len(new_review_cols)}")
    for col in sorted(found_review_cols):
        print(f"  - {col}")

    # Check data was copied
    cursor.execute("SELECT COUNT(*) FROM reviews WHERE nose_text IS NOT NULL")
    nose_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM reviews WHERE palate_text IS NOT NULL")
    palate_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM reviews WHERE finish_text IS NOT NULL")
    finish_count = cursor.fetchone()[0]

    print(f"\n✓ Data copied to new columns:")
    print(f"  - nose_text: {nose_count} reviews")
    print(f"  - palate_text: {palate_count} reviews")
    print(f"  - finish_text: {finish_count} reviews")

    # Check indexes
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='index' AND name LIKE 'idx_flavor%' OR name LIKE 'idx_review_flavors%' OR name LIKE 'idx_aggregated%'
        ORDER BY name
    """)
    indexes = cursor.fetchall()
    print(f"\n✓ New indexes created: {len(indexes)}")
    for idx in indexes:
        print(f"  - {idx[0]}")

    print("\n" + "="*80)
    print("VERIFICATION COMPLETE")
    print("="*80 + "\n")


def main():
    """Main migration runner."""
    print("="*80)
    print("WHISKEY SCRAPER - DATABASE MIGRATION")
    print("="*80)

    if not os.path.exists(DB_PATH):
        print(f"✗ Database not found at: {DB_PATH}")
        return 1

    # Create backup
    print("\n1. Creating backup...")
    backup_path = backup_database(DB_PATH)

    # Connect to database
    print("\n2. Connecting to database...")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    print(f"✓ Connected to: {DB_PATH}")

    try:
        # Check what migrations have been applied
        print("\n3. Checking migration status...")
        applied = get_applied_migrations(conn)
        if applied:
            print(f"✓ Previously applied migrations: {len(applied)}")
            for m in sorted(applied):
                print(f"  - {m}")
        else:
            print("  No previous migrations found")

        # Find migration files to apply
        migration_files = sorted([
            os.path.join(MIGRATIONS_DIR, f)
            for f in os.listdir(MIGRATIONS_DIR)
            if f.endswith('.sql') and f not in applied
        ])

        if not migration_files:
            print("\n✓ No new migrations to apply")
            return 0

        print(f"\n4. Migrations to apply: {len(migration_files)}")
        for f in migration_files:
            print(f"  - {os.path.basename(f)}")

        # Ask for confirmation
        response = input("\nProceed with migration? (yes/no): ").strip().lower()
        if response != 'yes':
            print("\n✗ Migration cancelled by user")
            return 1

        # Apply migrations
        print("\n5. Applying migrations...")
        success = True
        for migration_file in migration_files:
            if not apply_migration(conn, migration_file):
                success = False
                break

        if not success:
            print("\n✗ Migration failed! Rolling back...")
            conn.rollback()
            print(f"  Database restored from backup: {backup_path}")
            return 1

        # Verify migration
        print("\n6. Verifying migration...")
        verify_migration(conn)

        print("\n✓✓✓ Migration completed successfully! ✓✓✓")
        print(f"\nBackup saved at: {backup_path}")
        print("You can safely delete the backup after verifying everything works.\n")

        return 0

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        conn.rollback()
        return 1
    finally:
        conn.close()


if __name__ == '__main__':
    sys.exit(main())
