#!/usr/bin/env python3
import sqlite3
import csv
import os

# Set up database path
db_path = './data/data.db'
output_dir = './data'

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Connect to SQLite database
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row  # Get results as dictionaries
cursor = conn.cursor()

def export_csv(query, output_file):
    """Execute query and export results to CSV file with headers."""
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if rows:
            # Get column names
            columns = [description[0] for description in cursor.description]
            
            # Write to CSV file
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, lineterminator='\n')
                writer.writerow(columns)  # Write header
                for row in rows:
                    writer.writerow(row)
            
            print(f"✓ Exported to {output_file} ({len(rows)} rows)")
        else:
            print(f"⚠ No data found for {output_file}")
    
    except Exception as e:
        print(f"✗ Error exporting {output_file}: {e}")

# Export the three CSV files
export_csv(
    "select * from unofficial_difficulty order by song_id",
    os.path.join(output_dir, 'unofficial_difficulty.csv')
)

export_csv(
    "select * from ereternet_difficulty order by song_id",
    os.path.join(output_dir, 'ereternet_difficulty.csv')
)

export_csv(
    "select song_id, name, difficulty, unofficial_diff, ec_diff, hc_diff, exh_diff from ereternet_difficulty order by song_id",
    os.path.join(output_dir, 'ereternet_difficulty_diffonly.csv')
)

# Close connection
conn.close()
print("\n✓ All exports completed successfully!")
