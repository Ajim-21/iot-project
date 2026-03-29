import time
import sqlite3
import requests
import subprocess
from datetime import datetime

# Bounding box for Perak, Malaysia
PERAK_BBOX = {
    'lamin': 3.6, 
    'lamax': 6.0, 
    'lomin': 100.0, 
    'lomax': 101.8
}

def init_db():
    conn = sqlite3.connect('perak_iot_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flight_telemetry (
            icao24 TEXT,
            callsign TEXT,
            latitude REAL,
            longitude REAL,
            altitude REAL,
            timestamp DATETIME
        )
    ''')
    conn.commit()
    return conn

def start_collection():
    conn = init_db()
    cursor = conn.cursor()
    url = "https://opensky-network.org/api/states/all"
    
    # NEW: Counter for the cleaner
    loop_count = 0
    
    print("🚀 IoT System Online: Monitoring Perak...")
    print("📊 Data collection: every 60 seconds")
    print("🧹 CSV Auto-clean: every 5 minutes")
    
    while True:
        try:
            response = requests.get(url, params=PERAK_BBOX, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                states = data.get('states')
                malaysia_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                if states:
                    for s in states:
                        cursor.execute('''
                            INSERT INTO flight_telemetry (icao24, callsign, longitude, latitude, altitude, timestamp)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (s[0], s[1].strip() if s[1] else "N/A", s[5], s[6], s[7], malaysia_time))
                    conn.commit()
                    print(f"✅ Recorded {len(states)} aircraft at {malaysia_time}")
                else:
                    print(f"☁️ No aircraft currently over Perak at {malaysia_time}")

                # --- 5-MINUTE CLEANER LOGIC ---
                loop_count += 1
                if loop_count >= 5:
                    print("🧹 5 minutes passed. Updating cleaned_perak_flights.csv...")
                    subprocess.run(["python", "cleaner.py"])
                    loop_count = 0 # Reset the counter
                # ------------------------------
                
                time.sleep(60)

            elif response.status_code == 429:
                print(f"⚠️ Rate limit hit. Cooling down for 5 minutes...")
                time.sleep(300) 
            
            else:
                print(f"⚠️ API issue (Status {response.status_code}). Retrying in 60s...")
                time.sleep(60)

        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(60) 

if __name__ == "__main__":
    start_collection()