import os
import random
from datetime import datetime, timedelta

def generate_large_log_file(filename="data/large_sample_app.log", num_lines=150):
    """
    Generates a sample log file for batch analysis testing.
    Includes normal INFO logs and plants specific ERROR/WARN anomalies.
    """
    # Ensure the target directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    start_time = datetime(2026, 3, 10, 8, 0, 0)
    
    with open(filename, 'w') as f:
        for i in range(1, num_lines + 1):
            # Increment time by 5 seconds for each log line
            current_time = start_time + timedelta(seconds=i * 5)
            timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Plant anomalies at specific lines to test different chunks
            if i == 45:
                f.write(f"{timestamp_str} ERROR Database connection timeout on port 5432\n")
            elif i == 82:
                f.write(f"{timestamp_str} WARN Memory usage spiked to 95%\n")
            elif i == 115:
                f.write(f"{timestamp_str} ERROR Failed to authenticate user 'admin'\n")
            else:
                # Generate normal logs matching the golden baseline
                if i % 10 == 0:
                    mem = random.randint(35, 45)
                    f.write(f"{timestamp_str} INFO System baseline is stable. Memory at {mem}%\n")
                else:
                    f.write(f"{timestamp_str} INFO Log line {i} - System operation normal\n")

    print(f"✅ Generated {num_lines} log lines in '{filename}'.")
    print("Anomalies planted at lines: 45, 82, and 115.")

if __name__ == "__main__":
    generate_large_log_file()