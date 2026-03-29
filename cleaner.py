import pandas as pd
import sqlite3

def export_data():
    conn = sqlite3.connect('perak_iot_data.db')
    # Fetch all records for the 3+ day period 
    df = pd.read_sql_query("SELECT * FROM flight_telemetry", conn)
    
    # Cleaning: Remove duplicates and entries with no GPS
    df_clean = df.dropna(subset=['latitude', 'longitude']).drop_duplicates()
    
    # Export to CSV as required by marking rubric 
    df_clean.to_csv('cleaned_perak_flights.csv', index=False)
    print(f"Successfully exported {len(df_clean)} clean records.")
    conn.close()

if __name__ == "__main__":
    export_data()