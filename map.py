import streamlit as st
import folium
from streamlit_folium import st_folium

def app():
    st.title("Interactive Meetup Points Map")

    # Initialize meetup points list in session state if not exists
    if "meetup_points" not in st.session_state:
        st.session_state.meetup_points = []

    lat = st.number_input("Enter campus latitude:", value=23.9494, key="lat_input")
    lon = st.number_input("Enter campus longitude:", value=90.3775, key="lon_input")

    map_center = [lat, lon]

    @st.cache_data(show_spinner=False)
    def create_base_map(center):
        return folium.Map(location=center, zoom_start=18)

    # Get the cached base map
    m = create_base_map(map_center)

    # Add markers for all meetup points
    for idx, point in enumerate(st.session_state.meetup_points):
        folium.Marker(
            location=[point["lat"], point["lon"]],
            popup=f'Meetup Point {idx + 1}'
        ).add_to(m)

    # Render map and get click data
    map_data = st_folium(m, width=700, height=500)

    # Add new meetup point if user clicked on map
    if map_data and map_data.get("last_clicked"):
        clicked_lat = map_data["last_clicked"]["lat"]
        clicked_lon = map_data["last_clicked"]["lng"]

        # Check if point is already in list to avoid duplicates
        if not any(p["lat"] == clicked_lat and p["lon"] == clicked_lon for p in st.session_state.meetup_points):
            st.session_state.meetup_points.append({"lat": clicked_lat, "lon": clicked_lon})
            st.success(f"Added meetup point at ({clicked_lat:.4f}, {clicked_lon:.4f})")
        else:
            st.info("This meetup point is already added.")

    # Display all meetup points coordinates
    st.markdown("### All Meetup Points Coordinates:")
    for i, pt in enumerate(st.session_state.meetup_points):
        st.write(f"{i+1}. Latitude: {pt['lat']:.4f}, Longitude: {pt['lon']:.4f}")
