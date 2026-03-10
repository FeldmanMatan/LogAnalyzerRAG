import sqlite3
import json
import os

def init_stats_db():
    # Construct paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, 'log_format.json')
    db_path = os.path.join(base_dir, 'logs_stats.db')

    # Read log_format.json
    try:
        with open(config_path, 'r') as f:
            log_formats = json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {config_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {config_path}")
        return

    # Connect to SQLite DB
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"Connected to database: {db_path}")

    # Iterate over keys and create tables
    for table_name, config in log_formats.items():
        columns = config.get("columns", [])
        
        # Build column definitions
        # id INTEGER PRIMARY KEY AUTOINCREMENT is added automatically
        # source_file TEXT is required
        # Dynamic columns are all TEXT
        column_defs = ["id INTEGER PRIMARY KEY AUTOINCREMENT", "source_file TEXT"]
        column_defs.extend([f"{col} TEXT" for col in columns])
        
        columns_sql = ", ".join(column_defs)
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql});"
        
        try:
            cursor.execute(create_table_sql)
            print(f"✅ Table '{table_name}' created successfully.")
        except sqlite3.Error as e:
            print(f"❌ Error creating table '{table_name}': {e}")

    conn.commit()
    conn.close()
    print("Database initialization complete.")

if __name__ == "__main__":
    init_stats_db()