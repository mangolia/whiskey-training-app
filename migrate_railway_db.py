"""
Script to add distillery_mappings to Railway production database
Run this directly on Railway to update the production database
"""
import sqlite3
import os

DB_PATH = 'databases/whiskey_production.db'

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if table already exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='distillery_mappings'")
    if cursor.fetchone():
        print("Table already exists, skipping creation")
    else:
        # Create table
        cursor.execute('''
            CREATE TABLE distillery_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                variant_name TEXT NOT NULL UNIQUE,
                canonical_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        ''')
        cursor.execute('''
            CREATE INDEX idx_variant_name
            ON distillery_mappings(variant_name)
        ''')
        print("Created distillery_mappings table")
    
    # Add all mappings
    mappings = [
        ('a. smith bowman', 'A. Smith Bowman Distillery'),
        ('balcones', 'Balcones Distilling'),
        ('barrell craft spirits', 'Barrell Craft Spirits'),
        ('belle meade', 'Belle Meade Bourbon'),
        ('bib & tucker', 'Bib & Tucker Bourbon'),
        ('blade and bow', 'Blade and Bow'),
        ('breuckelen', 'Breuckelen Distilling'),
        ('breuckelen distilling', 'Breuckelen Distilling'),
        ('brown-forman', 'Brown-Forman Corporation'),
        ('brown-forman corporation', 'Brown-Forman Corporation'),
        ('brown-forman distillery', 'Brown-Forman Corporation'),
        ('brown forman', 'Brown-Forman Corporation'),
        ('buffalo trace', 'Buffalo Trace Distillery'),
        ('buffalo trace distillery', 'Buffalo Trace Distillery'),
        ('bulleit', 'Bulleit Distilling Co.'),
        ('castle & key', 'Castle & Key Distillery'),
        ('cooperstown', 'Cooperstown Distillery'),
        ('cooper spirits co.', 'Cooper Spirits Co.'),
        ('coopers\' craft', 'Coopers\' Craft'),
        ('copper fox', 'Copper Fox Distillery'),
        ('corsair', 'Corsair Distillery'),
        ('daddy rack', 'Daddy Rack Whiskey'),
        ('david nicholson', 'David Nicholson'),
        ('diageo', 'Diageo'),
        ('dickel', 'George Dickel'),
        ('downslope', 'Downslope Distilling'),
        ('dystillery', 'Dystillery'),
        ('eagle rare', 'Buffalo Trace Distillery'),
        ('elijah craig', 'Heaven Hill Distillery'),
        ('evan williams', 'Heaven Hill Distillery'),
        ('ezra brooks', 'Lux Row Distillers'),
        ('frey ranch', 'Frey Ranch Distillery'),
        ('garrison brothers', 'Garrison Brothers Distillery'),
        ('george dickel', 'George Dickel'),
        ('george dickel distillery', 'George Dickel'),
        ('high west', 'High West Distillery'),
        ('hillrock', 'Hillrock Estate Distillery'),
        ('hudson', 'Tuthilltown Spirits'),
        ('jackson purchase', 'Jackson Purchase Bourbon'),
        ('jefferson\'s', 'Jefferson\'s Bourbon'),
        ('jim beam', 'Jim Beam Distillery'),
        ('jim beam distillery', 'Jim Beam Distillery'),
        ('john j. bowman', 'A. Smith Bowman Distillery'),
        ('journeyman', 'Journeyman Distillery'),
        ('koval', 'Koval Distillery'),
        ('kings county', 'Kings County Distillery'),
        ('knob creek', 'Jim Beam Distillery'),
        ('laws whiskey house', 'Laws Whiskey House'),
        ('larceny', 'Heaven Hill Distillery'),
        ('legent', 'Jim Beam Distillery'),
        ('limestone branch', 'Limestone Branch Distillery'),
        ('lux row', 'Lux Row Distillers'),
        ('maker\'s mark', 'Maker\'s Mark Distillery'),
        ('mb roland', 'MB Roland Distillery'),
        ('michter\'s', 'Michter\'s Distillery'),
        ('minor case', 'Limestone Branch Distillery'),
        ('mx spirits', 'MX Spirits'),
        ('new riff', 'New Riff Distilling'),
        ('old carter', 'Old Carter Whiskey'),
        ('old elk', 'Old Elk Distillery'),
        ('old ezra', 'Lux Row Distillers'),
        ('old forester', 'Brown-Forman Corporation'),
        ('old pepper', 'Castle & Key Distillery'),
        ('orphan barrel', 'Diageo'),
        ('peerless', 'Kentucky Peerless Distilling Co.'),
        ('penelope', 'Penelope Bourbon'),
        ('pinhook', 'Pinhook Bourbon'),
        ('pursuit united', 'Bardstown Bourbon Company'),
        ('redemption', 'Bardstown Bourbon Company'),
        ('resilient', 'Resilient Bourbon'),
        ('rhetoric', 'Orphan Barrel'),
        ('rossville union', 'MGP Ingredients'),
        ('russell\'s reserve', 'Wild Turkey Distillery'),
        ('smooth ambler', 'Smooth Ambler Spirits'),
        ('sons of liberty', 'Sons of Liberty Spirits'),
        ('spirits of french lick', 'Spirits of French Lick'),
        ('stellum', 'Barrell Craft Spirits'),
        ('taconic', 'Taconic Distillery'),
        ('talnua', 'Talnua Distillery'),
        ('the prisoner', 'The Prisoner Wine Company'),
        ('town branch', 'Alltech Lexington Brewing & Distilling Co.'),
        ('traverse city', 'Traverse City Whiskey Co.'),
        ('uncle nearest', 'Uncle Nearest Premium Whiskey'),
        ('union horse', 'Union Horse Distilling Co.'),
        ('van winkle', 'Buffalo Trace Distillery'),
        ('widow jane', 'Widow Jane Distillery'),
        ('wild turkey', 'Wild Turkey Distillery'),
        ('wild turkey distillery', 'Wild Turkey Distillery'),
        ('wilderness trail', 'Wilderness Trail Distillery'),
        ('willett', 'Willett Distillery'),
        ('woodford reserve', 'Brown-Forman Corporation'),
        ('wyoming whiskey', 'Wyoming Whiskey'),
        ('heaven hill', 'Heaven Hill Distillery'),
        ('heaven hill distillery', 'Heaven Hill Distillery'),
    ]
    
    # Insert mappings
    cursor.executemany(
        "INSERT OR IGNORE INTO distillery_mappings (variant_name, canonical_name) VALUES (?, ?)",
        mappings
    )
    
    rows_inserted = cursor.rowcount
    conn.commit()
    conn.close()
    
    print(f"✓ Inserted {rows_inserted} mappings")
    print("✓ Migration complete!")

if __name__ == '__main__':
    main()
