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
    m2.metric("Unique Aircraft", df['callsign'].dropna().nunique())
    m3.metric("Latest Altitude", f"{df['altitude'].iloc[-1]}m" if not df.empty else "N/A")
    st.divider()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Geospatial Visualization")
        
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
        
        show_full_history = st.checkbox("Show Entire Database History")

        if selected_flight == "All Flights":
            if show_full_history:
                display_df = df[['callsign', 'altitude', 'timestamp']].reset_index(drop=False)
                st.write(f"Showing ALL {len(df)} records in database:")
            else:
                display_df = df[['callsign', 'altitude', 'timestamp']].tail(100).reset_index(drop=False)
                st.write("Showing Latest 100 records (Global):")
        else:
            display_df = df[df['callsign'] == selected_flight][['callsign', 'altitude', 'timestamp']].reset_index(drop=False)
            st.write(f"Showing ENTIRE history for {selected_flight}:")
            
        st.dataframe(display_df, width='stretch')
        st.line_chart(display_df['altitude'].tail(100))

        # --- RESTORED: AIRPORT INFERENCE (BONUS) ---
        st.divider()
        st.subheader("📍 Airport Inference (Bonus)")
        # We search the ENTIRE dataframe for planes under 1000 meters
        # This highlights planes that are landing or taking off
        low_alt_df = df[df['altitude'] < 1000].sort_values(by='altitude').head(10).reset_index(drop=False)
        
        if not low_alt_df.empty:
            st.write("Low Altitude Clusters (Potential Runways):")
            st.dataframe(low_alt_df[['callsign', 'latitude', 'longitude', 'altitude']], width='stretch')
        else:
            st.info("No low-altitude flights detected yet. Waiting for landing data...")

        # --- DOWNLOAD SECTION ---
        st.divider()
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
