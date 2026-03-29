print("Checking the database...")
import sqlite3

conn = sqlite3.connect('perak_iot_data.db')
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM flight_telemetry")
total_pings = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(DISTINCT icao24) FROM flight_telemetry")
unique_planes = cursor.fetchone()[0]

print(f"📊 Total pings collected: {total_pings}")
print(f"✈️ Total unique aircraft spotted: {unique_planes}")

conn.close()