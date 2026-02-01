"""
Fix Encoding Issues in Database
================================

This script fixes corrupted character encoding in existing database records.
It normalizes smart quotes and fixes UTF-8 encoding issues.
"""

import sys
from pathlib import Path
from database import get_connection

sys.path.insert(0, str(Path(__file__).parent))


def normalize_text(text):
    """Normalize text to fix encoding issues."""
    if not text:
        return text
    
    # Try to fix double-encoded UTF-8 by attempting to decode as Latin-1 then re-encode
    # This handles cases where UTF-8 bytes were stored as if they were Latin-1
    try:
        # If text contains bytes that look like double-encoded UTF-8, try to fix it
        if isinstance(text, str) and any(ord(c) > 127 for c in text):
            # Try decoding as if it was incorrectly encoded
            # First, encode to bytes if it's a string with problematic characters
            text_bytes = text.encode('latin-1', errors='ignore')
            # Then try to decode as UTF-8
            try:
                text = text_bytes.decode('utf-8', errors='ignore')
            except (UnicodeDecodeError, UnicodeError):
                pass
    except Exception:
        pass
    
    # Fix common encoding issues (smart quotes, dashes, etc.)
    replacements = {
        '\u2018': "'",  # Left single quotation mark
        '\u2019': "'",  # Right single quotation mark (apostrophe)
        '\u201C': '"',  # Left double quotation mark
        '\u201D': '"',  # Right double quotation mark
        '\u2013': '-',  # En dash
        '\u2014': '--', # Em dash
        '\u2026': '...', # Ellipsis
        '\u00A0': ' ',  # Non-breaking space
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Fix double-encoded UTF-8 patterns (like â\x80\x99)
    # These patterns occur when UTF-8 bytes are interpreted as Latin-1
    text = text.replace('â\x80\x99', "'")   # Right single quotation mark
    text = text.replace('â\x80\x9c', '"')   # Left double quotation mark  
    text = text.replace('â\x80\x9d', '"')   # Right double quotation mark
    text = text.replace('â\x80\x93', '-')    # En dash
    text = text.replace('â\x80\x94', '--')  # Em dash
    text = text.replace('â\x80¦', '...')     # Ellipsis (if present)
    
    # Fix common patterns where 'â' appears (often from encoding issues)
    # Pattern: "â" followed by something that should be an apostrophe
    import re
    # Fix "â's" -> "'s" (apostrophe-s)
    text = re.sub(r"â's", "'s", text)
    # Fix "â'N" -> "'N" (apostrophe-N)
    text = re.sub(r"â'N", "'N", text)
    # Fix "â" followed by common patterns
    text = re.sub(r"â([A-Z])", r"'\1", text)  # "âA" -> "'A"
    
    # Ensure proper UTF-8 encoding
    try:
        # Remove any remaining problematic characters
        text = text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
    except Exception:
        pass
    
    return text


def fix_whiskey_names(conn):
    """Fix encoding in whiskey names and distillery."""
    cursor = conn.cursor()
    
    # Get all whiskeys
    cursor.execute("SELECT whiskey_id, name, distillery FROM whiskeys")
    whiskeys = cursor.fetchall()
    
    fixed_count = 0
    for whiskey_id, name, distillery in whiskeys:
        normalized_name = normalize_text(name)
        normalized_distillery = normalize_text(distillery) if distillery else None
        
        if normalized_name != name or normalized_distillery != distillery:
            cursor.execute("UPDATE whiskeys SET name = ?, distillery = ? WHERE whiskey_id = ?", 
                         (normalized_name, normalized_distillery, whiskey_id))
            changes = []
            if normalized_name != name:
                changes.append(f"name: '{name}' -> '{normalized_name}'")
            if normalized_distillery != distillery:
                changes.append(f"distillery: '{distillery}' -> '{normalized_distillery}'")
            print(f"  Fixed whiskey #{whiskey_id}: {', '.join(changes)}")
            fixed_count += 1
    
    conn.commit()
    return fixed_count


def fix_review_fields(conn):
    """Fix encoding in review text fields."""
    cursor = conn.cursor()
    
    # Fields that might have text encoding issues
    text_fields = [
        'classification', 'company', 'proof', 'age', 
        'mashbill', 'color', 'price', 'nose', 'palate', 'finish', 
        'overall_notes', 'additional_data'
    ]
    
    fixed_count = 0
    
    for field in text_fields:
        cursor.execute(f"SELECT review_id, {field} FROM reviews WHERE {field} IS NOT NULL")
        reviews = cursor.fetchall()
        
        for review_id, value in reviews:
            normalized = normalize_text(value)
            if normalized != value:
                cursor.execute(f"UPDATE reviews SET {field} = ? WHERE review_id = ?",
                             (normalized, review_id))
                print(f"  Fixed review #{review_id}, field '{field}'")
                fixed_count += 1
    
    conn.commit()
    return fixed_count


def main():
    """Main function to fix encoding issues."""
    print("="*70)
    print("Fixing Character Encoding Issues")
    print("="*70)
    print()
    
    conn = get_connection()
    
    print("Fixing whiskey names...")
    whiskey_count = fix_whiskey_names(conn)
    print(f"  Fixed {whiskey_count} whiskey name(s)")
    print()
    
    print("Fixing review fields...")
    review_count = fix_review_fields(conn)
    print(f"  Fixed {review_count} review field(s)")
    print()
    
    conn.close()
    
    print("="*70)
    print(f"✓ Encoding fix complete!")
    print(f"  Total fixes: {whiskey_count + review_count}")
    print("="*70)


if __name__ == "__main__":
    main()

