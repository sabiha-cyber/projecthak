import streamlit as st
import json
import os
import folium
from streamlit_folium import st_folium
import pandas as pd

DATA_FILE = "meetup_points.json"

    # Initialize session state from file
if 'meetup_points' not in st.session_state:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        st.session_state['meetup_points'] = data.get("meetup_points", [])
    else:
        st.session_state['meetup_points'] = []
# Save to JSON file
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({"meetup_points": st.session_state.get('meetup_points', [])}, f, indent=4)

# Approve/disapprove functions
def approve_meetup_point(index):
    point = st.session_state['meetup_points'][index]
    point['status'] = 'approved'
    point['safe'] = True
    save_data()

def disapprove_meetup_point(index):
    point = st.session_state['meetup_points'][index]
    point['status'] = 'disapproved'
    point['safe'] = False
    save_data()

# Add new meetup point
def add_meetup_point(lat, lon, suggested_by, purpose, intended_for=None, initially_safe=True):
    st.session_state['meetup_points'].append({
        "lat": lat,
        "lon": lon,
        "status": "pending",
        "suggested_by": suggested_by,
        "purpose": purpose,
        "intended_for": intended_for,
        "safe": initially_safe
    })
    save_data()

# Show markers on map
def show_meetup_points_on_map(m):
    for point in st.session_state.get('meetup_points', []):
        color = "blue" if point["status"] == "pending" else "green" if point["status"] == "approved" else "red"
        popup_text = (
            f"Suggested by: {point['suggested_by']}\n"
            f"Status: {point['status']}\n"
            f"Purpose: {point['purpose']}"
        )
        if point['purpose'] == "Private" and point['intended_for']:
            popup_text += f"\nIntended for: {point['intended_for']}"
        popup_text += f"\nSafe: {'✅' if point['safe'] else '❌'}"

        folium.Marker(
            location=[point['lat'], point['lon']],
            popup=popup_text,
            icon=folium.Icon(color=color, icon='star')
        ).add_to(m)

# Streamlit UI starts
def app():
    # File to store meetup points
    
    #st.set_page_config(layout="wide")
    st.title("📍 Safe Meetups with Campus Maps")

    lat = st.number_input("Enter campus latitude:", value=23.9494, key="lat_input")
    lon = st.number_input("Enter campus longitude:", value=90.3775, key="lon_input")

    map_center = [lat, lon]

    @st.cache_data(show_spinner=False)
    def create_base_map(center):
        return folium.Map(location=center, zoom_start=15)

    m = create_base_map(map_center)
    show_meetup_points_on_map(m)
    m.add_child(folium.LatLngPopup())

    st.markdown("\U0001F5B1️ Click on the map to suggest a meetup spot.")
    map_data = st_folium(m, width=700, height=500)

    # Handle map click and input form
    if map_data and map_data.get("last_clicked"):
        click_lat = map_data["last_clicked"]["lat"]
        click_lon = map_data["last_clicked"]["lng"]
        st.success(f"Clicked: ({click_lat:.5f}, {click_lon:.5f})")

        meetup_type = st.radio("Is this meetup Public or to meet a friend (Private)?", ["Public", "Private"])
        intended_for = None
        if meetup_type == "Private":
            intended_for = st.text_input("Who will you meet?")
        initially_safe = st.checkbox("Do you consider this spot safe?", value=True)

        if st.button("\u2705 Save this point"):
            if meetup_type == "Private" and not intended_for:
                st.error("Please enter who you want to meet.")
            else:
                add_meetup_point(click_lat, click_lon, suggested_by="Me", purpose=meetup_type,
                                intended_for=intended_for, initially_safe=initially_safe)
                st.success("Meetup point added! Waiting for approval.")
                st.rerun()

    # Approval Section
    st.subheader("\u270D Approve or Disapprove Suggested Points")
    pending_points = [p for p in st.session_state.get('meetup_points', []) if p['status'] == 'pending']
    for idx, point in enumerate(pending_points):
        st.write(f"Point #{idx + 1}: ({point['lat']:.5f}, {point['lon']:.5f}) suggested by {point['suggested_by']}")
        st.write(f"Purpose: {point['purpose']} | Safe: {point['safe']}")
        if point['purpose'] == "Private" and point['intended_for']:
            st.write(f"Intended for: {point['intended_for']}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"✅ Approve Point #{idx + 1}", key=f"approve_{idx}"):
                main_index = st.session_state['meetup_points'].index(point)
                approve_meetup_point(main_index)
                st.success(f"You approved point #{idx + 1}.")
                st.rerun()
        with col2:
            if st.button(f"❌ Disapprove Point #{idx + 1}", key=f"disapprove_{idx}"):
                main_index = st.session_state['meetup_points'].index(point)
                disapprove_meetup_point(main_index)
                st.warning(f"You disapproved point #{idx + 1}.")
                st.rerun()

    # Display Data Table
    meetup_points = st.session_state.get('meetup_points', [])
    if meetup_points:
        st.subheader("📌 All Suggested Points:")
        df_points = pd.DataFrame(meetup_points)
        st.dataframe(df_points[['lat', 'lon', 'status', 'suggested_by', 'purpose', 'intended_for', 'safe']])

        if st.button("🗑️ Clear All Points"):
            st.session_state['meetup_points'].clear()
            save_data()
            st.rerun()

