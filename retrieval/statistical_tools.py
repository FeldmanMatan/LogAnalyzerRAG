import sqlite3
import pandas as pd
import os
from langchain_core.tools import tool

STATS_DB_PATH = "logs_stats.db"

@tool
def analyze_log_statistics(log_type: str, start_time: str = None, end_time: str = None) -> str:
    """
    Use this tool to get exact counts and statistics of log events from the SQLite database.
    Input should be the log type (e.g., 'app_logs').
    Optionally, you can provide `start_time` and `end_time` (in 'YYYY-MM-DD HH:MM:SS' format) to filter the logs by a specific time window.
    """
    try:
        # Construct absolute path to the database to ensure it works from any execution context
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, STATS_DB_PATH)

        # Connect to logs_stats.db
        conn = sqlite3.connect(db_path)
        
        # Check if the table exists
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (log_type,))
        if cursor.fetchone() is None:
            conn.close()
            return f"Error: Table '{log_type}' not found in the statistics database."

        # Load data into DataFrame
        # Using f-string as requested, but validated by the existence check above
        df = pd.read_sql_query(f"SELECT * FROM {log_type}", conn)
        
        # Close the database connection
        conn.close()

        # If the DataFrame is empty before any filtering
        if df.empty:
            return f"No data found for log type: {log_type}"

        # Time-based filtering if requested
        if start_time or end_time:
            if 'log_timestamp' not in df.columns:
                return f"Error: Time filtering requires a 'log_timestamp' column in the '{log_type}' table."

            df['log_timestamp'] = pd.to_datetime(df['log_timestamp'])
            
            if start_time:
                df = df[df['log_timestamp'] >= pd.to_datetime(start_time)]
            
            if end_time:
                df = df[df['log_timestamp'] <= pd.to_datetime(end_time)]

        # If the DataFrame is empty after potential filtering
        if df.empty:
            return f"No data found for log type: {log_type} in the specified time range."

        # Calculate basic statistics
        total_rows = len(df)
        stats_output = f"📊 Statistics for '{log_type}':\n"
        stats_output += f"- Total Log Entries: {total_rows}\n"

        # Count occurrences for log_level if the column exists
        if 'log_level' in df.columns:
            level_counts = df['log_level'].value_counts()
            stats_output += f"- Log Level Breakdown:\n{level_counts.to_string()}\n"

        return stats_output

    except Exception as e:
        return f"Error analyzing statistics: {str(e)}"