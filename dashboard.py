import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Perak Flight IoT Dashboard", layout="wide")
st.title("✈️ Perak Aircraft Monitoring System")

try:
    df = pd.read_csv('cleaned_perak_flights.csv')

    # --- TOP METRICS BAR ---
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Records", len(df))
    # Filter out empty callsigns before counting unique ones
    m2.metric("Unique Aircraft", df['callsign'].dropna().nunique())
    m3.metric("Latest Altitude", f"{df['altitude'].iloc[-1]}m" if not df.empty else "N/A")
    st.divider()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Geospatial Visualization")
        
        # FIX: Drop empty callsigns, convert to string, then sort
        valid_callsigns = df['callsign'].dropna().astype(str).unique().tolist()
        all_callsigns = ["All Flights"] + sorted(valid_callsigns)
        
        selected_flight = st.selectbox("Select a flight to track:", all_callsigns)

        if selected_flight == "All Flights":
            plot_df = df.dropna(subset=['latitude', 'longitude']).tail(200)
        else:
            plot_df = df[df['callsign'] == selected_flight]

        m = folium.Map(location=[4.8, 101.0], zoom_start=8)
        for _, row in plot_df.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=4,
                popup=f"Callsign: {row['callsign']} | Alt: {row['altitude']}m",
                color="crimson" if selected_flight == "All Flights" else "blue",
                fill=True
            ).add_to(m)
        st_folium(m, width=700)

    with col2:
        st.subheader("Flight Record Analysis")
        
        # NEW: A toggle to let you see the full history or just the latest
        show_full_history = st.checkbox("Show Entire Database History")

        if selected_flight == "All Flights":
            if show_full_history:
                # This shows EVERY row in your CSV
                display_df = df[['callsign', 'altitude', 'timestamp']].reset_index(drop=False)
                st.write(f"Showing ALL {len(df)} records in database:")
            else:
                # Default view: Latest 100 to match the map
                display_df = df[['callsign', 'altitude', 'timestamp']].tail(100).reset_index(drop=False)
                st.write("Showing Latest 100 records (Global):")
        else:
            # If a specific flight is picked, always show its entire history
            display_df = df[df['callsign'] == selected_flight][['callsign', 'altitude', 'timestamp']].reset_index(drop=False)
            st.write(f"Showing ENTIRE history for {selected_flight}:")
            
        st.dataframe(display_df, width='stretch')
        
        # Chart: Only show the last 100 on the chart so it doesn't get too squashed
        st.line_chart(display_df['altitude'].tail(100))

        # BONUS: Download Button
        st.download_button(
            label="Download Full Dataset (CSV)",
            data=df.to_csv(index=False),
            file_name="perak_flight_data_full.csv",
            mime="text/csv"
        )

except FileNotFoundError:
    st.error("⚠️ Data file not found. Ensure collector.py is running.")
except Exception as e:
    st.error(f"⚠️ Error: {e}")