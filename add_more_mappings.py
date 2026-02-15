#!/usr/bin/env python3
"""
Add comprehensive distillery mappings for all major duplicates
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "databases" / "whiskey_production.db"

def add_comprehensive_mappings():
    """Add mappings for all identified duplicates"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Comprehensive list of mappings
    # Format: (variant_name, canonical_name)
    mappings = [
        # A. Smith Bowman
        ('a. smith bowman', 'A. Smith Bowman Distillery'),
        ('a. smith bowman distillery', 'A. Smith Bowman Distillery'),

        # Balcones
        ('balcones', 'Balcones Distilling'),
        ('balcones distillery', 'Balcones Distilling'),
        ('balcones distilling', 'Balcones Distilling'),

        # Barton 1792
        ('barton 1792', 'Barton 1792 Distillery'),
        ('barton 1792 distillery', 'Barton 1792 Distillery'),

        # Bernheim
        ('bernheim', 'Bernheim Distillery'),
        ('bernheim distillery', 'Bernheim Distillery'),

        # Brown-Forman Shively (separate from regular Brown-Forman)
        ('brown-forman shively', 'Brown-Forman Shively Distillery'),
        ('brown-forman shively distiller', 'Brown-Forman Shively Distillery'),
        ('brown-forman shively distillery', 'Brown-Forman Shively Distillery'),

        # Buffalo Trace variants (including edge cases)
        ('buffalo trace distillery‍', 'Buffalo Trace Distillery'),  # Has invisible character

        # Castle & Key
        ('castle & key', 'Castle & Key Distillery'),
        ('castle & key distillery', 'Castle & Key Distillery'),

        # Charbay
        ('charbay', 'Charbay Distillery'),
        ('charbay distillery', 'Charbay Distillery'),

        # Chattanooga Riverfront
        ('chattanooga riverfront', 'Chattanooga Riverfront Distillery'),
        ('chattanooga riverfront distillery', 'Chattanooga Riverfront Distillery'),

        # Clear Creek
        ('clear creek', 'Clear Creek Distillery'),
        ('clear creek distillery', 'Clear Creek Distillery'),

        # Corsair Artisan
        ('corsair artisan', 'Corsair Artisan Distillery'),
        ('corsair artisan distillery', 'Corsair Artisan Distillery'),

        # Elijah Craig (Heaven Hill)
        ('elijah craig co. (heaven hill)', 'Elijah Craig Distillery Co. (Heaven Hill)'),
        ('elijah craig distillery co. (heaven hill)', 'Elijah Craig Distillery Co. (Heaven Hill)'),

        # Filibuster
        ('filibuster', 'Filibuster Distillery'),
        ('filibuster distillery', 'Filibuster Distillery'),

        # Frey Ranch
        ('frey ranch', 'Frey Ranch Distillery'),
        ('frey ranch distillery', 'Frey Ranch Distillery'),

        # Garrison Brothers
        ('garrison brothers', 'Garrison Brothers Distillery'),
        ('garrison brothers distillery', 'Garrison Brothers Distillery'),

        # Green River
        ('green river distillery', 'Green River Distilling Co.'),
        ('green river distilling', 'Green River Distilling Co.'),
        ('green river distilling co.', 'Green River Distilling Co.'),

        # Hard Truth
        ('hard truth distilling', 'Hard Truth Distilling Co.'),
        ('hard truth distilling co.', 'Hard Truth Distilling Co.'),

        # Heaven Hill
        ('heaven hill', 'Heaven Hill Distillery'),
        ('heaven hill distillery', 'Heaven Hill Distillery'),

        # Hotaling & Co.
        ('hotaling & co.', 'Hotaling & Co. Distillery'),
        ('hotaling & co. distillery', 'Hotaling & Co. Distillery'),

        # Jack Daniel (note: separate from Jack Daniel's)
        ('jack daniel', 'Jack Daniel Distillery'),
        ('jack daniel distillery', 'Jack Daniel Distillery'),

        # Jack Daniel's
        ("jack daniel's", "Jack Daniel's Distillery"),
        ("jack daniel's distillery", "Jack Daniel's Distillery"),

        # Jeptha Creed
        ('jeptha creed', 'Jeptha Creed Distillery'),
        ('jeptha creed distillery', 'Jeptha Creed Distillery'),

        # Jim Beam
        ('jim beam', 'Jim Beam Distillery'),
        ('jim beam distillery', 'Jim Beam Distillery'),

        # Kings County
        ('kings county', 'Kings County Distillery'),
        ('kings county distillery', 'Kings County Distillery'),

        # Nearest Green
        ('nearest green', 'Nearest Green Distillery'),
        ('nearest green distillery', 'Nearest Green Distillery'),

        # Neeley Family
        ('neeley family', 'Neeley Family Distillery'),
        ('neeley family distillery', 'Neeley Family Distillery'),

        # New World Whisky
        ('new world whisky', 'New World Whisky Distillery'),
        ('new world whisky distillery', 'New World Whisky Distillery'),

        # O.Z. Tyler
        ('o.z. tyler', 'O.Z. Tyler Distillery'),
        ('o.z. tyler distillery', 'O.Z. Tyler Distillery'),

        # Old 55
        ('old 55', 'Old 55 Distillery'),
        ('old 55 distillery', 'Old 55 Distillery'),

        # Old Dominick
        ('old dominick', 'Old Dominick Distillery'),
        ('old dominick distillery', 'Old Dominick Distillery'),

        # Ross & Squibb (MGP)
        ('ross & squibb (mgp)', 'Ross & Squibb Distillery (MGP)'),
        ('ross & squibb distillery (mgp)', 'Ross & Squibb Distillery (MGP)'),

        # Starlight
        ('starlight', 'Starlight Distillery'),
        ('starlight distillery', 'Starlight Distillery'),

        # Still Austin
        ('still austin', 'Still Austin Distillery'),
        ('still austin co.', 'Still Austin Distillery'),

        # Talnua
        ('talnua', 'Talnua Distillery'),
        ('talnua distillery', 'Talnua Distillery'),

        # The Willett
        ('the willett', 'The Willett Distillery'),
        ('the willett distillery', 'The Willett Distillery'),

        # Tuthilltown Spirits
        ('tuthilltown spirits', 'Tuthilltown Spirits Distillery'),
        ('tuthilltown spirits distillery', 'Tuthilltown Spirits Distillery'),

        # Watershed
        ('watershed', 'Watershed Distillery'),
        ('watershed distillery', 'Watershed Distillery'),

        # Wild Turkey
        ('wild turkey', 'Wild Turkey Distillery'),
        ('wild turkey distillery', 'Wild Turkey Distillery'),

        # Willett
        ('willett', 'Willett Distillery'),
        ('willett distillery', 'Willett Distillery'),

        # Woodford Reserve / Brown-Forman variants
        ('woodford reserve / brown-forman', 'Woodford Reserve Distillery'),
        ('woodford reserve / brown-forman distillery', 'Woodford Reserve Distillery'),
        ('woodford reserve /brown-forman', 'Woodford Reserve Distillery'),
        ('woodford reserve disrtillery / brown-forman', 'Woodford Reserve Distillery'),
        ('woodford reserve distillery / brown-forman distillery', 'Woodford Reserve Distillery'),
        ('woodford reserve distillery/brown-forman distillery', 'Woodford Reserve Distillery'),
        ('the brown-forman distillery', 'Woodford Reserve Distillery'),
    ]

    inserted = 0
    skipped = 0
    for variant_name, canonical_name in mappings:
        try:
            cursor.execute('''
                INSERT INTO distillery_mappings (variant_name, canonical_name)
                VALUES (?, ?)
            ''', (variant_name, canonical_name))
            inserted += 1
        except sqlite3.IntegrityError:
            skipped += 1

    conn.commit()
    conn.close()

    print(f"✅ Inserted {inserted} new mappings")
    print(f"⏭️  Skipped {skipped} existing mappings")

    return inserted

if __name__ == '__main__':
    print("=" * 80)
    print("ADDING COMPREHENSIVE DISTILLERY MAPPINGS")
    print("=" * 80)

    count = add_comprehensive_mappings()

    print("\n" + "=" * 80)
    print(f"✅ Added {count} new mappings!")
    print("=" * 80)
