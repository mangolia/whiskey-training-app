#!/usr/bin/env python3
"""
QA Script: Compare extracted descriptors against original review URLs
Outputs a report you can use to manually verify against the source websites
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("whiskey_mvp_v2.db")

def generate_qa_report(output_file="QA_REPORT.md"):
    """Generate a QA report with all whiskeys, their URLs, and extracted descriptors"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all whiskeys
    cursor.execute("""
        SELECT whiskey_id, name
        FROM whiskeys
        ORDER BY name
    """)

    whiskeys = cursor.fetchall()

    with open(output_file, 'w') as f:
        f.write("# QA REPORT: Extracted Descriptors vs Source Reviews\n\n")
        f.write(f"Total whiskeys: {len(whiskeys)}\n\n")
        f.write("---\n\n")

        for whiskey_id, whiskey_name in whiskeys:
            f.write(f"## {whiskey_name}\n\n")

            # Get reviews for this whiskey
            cursor.execute("""
                SELECT review_id, source_site, source_url, nose, palate, finish
                FROM reviews
                WHERE whiskey_id = ?
                ORDER BY review_id
            """, (whiskey_id,))

            reviews = cursor.fetchall()

            for review_id, source, url, nose_text, palate_text, finish_text in reviews:
                f.write(f"### Review #{review_id} - {source}\n\n")
                f.write(f"**URL:** {url}\n\n")

                # Get extracted descriptors for each section
                for section, original_text in [("nose", nose_text), ("palate", palate_text), ("finish", finish_text)]:

                    # Get extracted descriptors
                    cursor.execute("""
                        SELECT dv.descriptor_name
                        FROM review_descriptors rd
                        JOIN descriptor_vocabulary dv ON rd.descriptor_id = dv.descriptor_id
                        WHERE rd.review_id = ? AND rd.tasting_section = ?
                        ORDER BY dv.descriptor_name
                    """, (review_id, section))

                    descriptors = [row[0] for row in cursor.fetchall()]

                    f.write(f"**{section.upper()}:**\n")
                    f.write(f"- Original: `{original_text}`\n")
                    f.write(f"- Extracted ({len(descriptors)}): {', '.join(descriptors)}\n")
                    f.write(f"- [ ] Verified\n\n")

            # Summary: Aggregated descriptors for this whiskey
            f.write("### Aggregated Quiz Data\n\n")

            for section in ["nose", "palate", "finish"]:
                cursor.execute("""
                    SELECT dv.descriptor_name, awd.review_count
                    FROM aggregated_whiskey_descriptors awd
                    JOIN descriptor_vocabulary dv ON awd.descriptor_id = dv.descriptor_id
                    WHERE awd.whiskey_id = ? AND awd.tasting_section = ?
                    ORDER BY awd.review_count DESC, dv.descriptor_name
                """, (whiskey_id, section))

                descriptors = cursor.fetchall()

                f.write(f"**{section.upper()}** ({len(descriptors)} unique descriptors):\n")
                for desc, count in descriptors:
                    marker = "✅✅" if count == 2 else "✅"
                    f.write(f"- {marker} {desc} ({count}/{len(reviews)} reviews)\n")
                f.write("\n")

            f.write("---\n\n")

    conn.close()

    print(f"✅ QA report generated: {output_file}")
    print(f"   Total whiskeys: {len(whiskeys)}")
    print(f"\nNext steps:")
    print(f"1. Open {output_file}")
    print(f"2. For each whiskey, click the review URL")
    print(f"3. Compare extracted descriptors against the actual review")
    print(f"4. Check the [ ] box when verified")

def generate_simple_list(output_file="QA_SIMPLE.txt"):
    """Generate a simple text file for quick review"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT w.name, r.source_url, r.nose, r.palate, r.finish
        FROM reviews r
        JOIN whiskeys w ON r.whiskey_id = w.whiskey_id
        ORDER BY w.name, r.review_id
    """)

    with open(output_file, 'w') as f:
        f.write("WHISKEY | URL | NOSE | PALATE | FINISH\n")
        f.write("=" * 120 + "\n\n")

        for name, url, nose, palate, finish in cursor.fetchall():
            f.write(f"{name}\n")
            f.write(f"URL: {url}\n")
            f.write(f"NOSE:   {nose}\n")
            f.write(f"PALATE: {palate}\n")
            f.write(f"FINISH: {finish}\n")
            f.write("-" * 120 + "\n\n")

    conn.close()

    print(f"✅ Simple list generated: {output_file}")

def query_specific_whiskey(whiskey_name):
    """Query a specific whiskey and show all its data"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT whiskey_id, name
        FROM whiskeys
        WHERE name LIKE ?
    """, (f"%{whiskey_name}%",))

    result = cursor.fetchone()
    if not result:
        print(f"❌ Whiskey not found: {whiskey_name}")
        conn.close()
        return

    whiskey_id, name = result

    print("=" * 80)
    print(f"WHISKEY: {name}")
    print("=" * 80)

    # Get all reviews
    cursor.execute("""
        SELECT review_id, source_site, source_url, nose, palate, finish
        FROM reviews
        WHERE whiskey_id = ?
    """, (whiskey_id,))

    reviews = cursor.fetchall()

    for review_id, source, url, nose, palate, finish in reviews:
        print(f"\n📄 Review #{review_id} - {source}")
        print(f"🔗 {url}\n")

        for section, text in [("NOSE", nose), ("PALATE", palate), ("FINISH", finish)]:
            print(f"{section}:")
            print(f"  Original: {text}")

            # Get extracted descriptors
            cursor.execute("""
                SELECT dv.descriptor_name
                FROM review_descriptors rd
                JOIN descriptor_vocabulary dv ON rd.descriptor_id = dv.descriptor_id
                WHERE rd.review_id = ? AND rd.tasting_section = ?
                ORDER BY dv.descriptor_name
            """, (review_id, section.lower()))

            descriptors = [row[0] for row in cursor.fetchall()]
            print(f"  Extracted ({len(descriptors)}): {', '.join(descriptors)}")
            print()

    # Show aggregated data
    print("\n" + "=" * 80)
    print("AGGREGATED QUIZ DATA:")
    print("=" * 80)

    for section in ["nose", "palate", "finish"]:
        cursor.execute("""
            SELECT dv.descriptor_name, awd.review_count
            FROM aggregated_whiskey_descriptors awd
            JOIN descriptor_vocabulary dv ON awd.descriptor_id = dv.descriptor_id
            WHERE awd.whiskey_id = ? AND awd.tasting_section = ?
            ORDER BY awd.review_count DESC, dv.descriptor_name
        """, (whiskey_id, section))

        descriptors = cursor.fetchall()
        print(f"\n{section.upper()} ({len(descriptors)} descriptors):")
        for desc, count in descriptors:
            marker = "✅✅" if count == 2 else "✅"
            print(f"  {marker} {desc} ({count}/{len(reviews)} reviews)")

    conn.close()

def main():
    """Main function"""
    import sys

    if len(sys.argv) > 1:
        # Query specific whiskey
        whiskey_name = ' '.join(sys.argv[1:])
        query_specific_whiskey(whiskey_name)
    else:
        # Generate reports
        print("QA REPORT GENERATOR")
        print("=" * 80)
        print()
        print("Select option:")
        print("1. Generate full QA report (markdown with checkboxes)")
        print("2. Generate simple text list")
        print("3. Query specific whiskey")
        print("4. Generate both reports")
        print()

        choice = input("Choice (1-4): ").strip()

        if choice == "1":
            generate_qa_report()
        elif choice == "2":
            generate_simple_list()
        elif choice == "3":
            name = input("Enter whiskey name (partial match OK): ").strip()
            query_specific_whiskey(name)
        elif choice == "4":
            generate_qa_report()
            generate_simple_list()
            print("\n✅ Both reports generated!")
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
