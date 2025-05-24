import streamlit as st
import json
import os

DB_FILE = "student_profile.json"

# Load profile data from file
def load_profile():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

# Save profile to file
def save_profile(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)
def app():

    if "useremail" not in st.session_state or not st.session_state.useremail:
        st.warning("🚫 You must be logged in to access your academic profile.")
        st.info("Please go to the login/signup page to sign in.")
        return
    # Initialize session state
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False

    if "profile_data" not in st.session_state:
        st.session_state.profile_data = load_profile()

    st.title("🎓 Student Academic Profile")

    # -----------------------------
    # 👁️ VIEW MODE
    # -----------------------------
    if not st.session_state.edit_mode:
        if st.session_state.profile_data:
            profile = st.session_state.profile_data
            st.subheader("👤 Your Academic Info")

            if profile.get("public", False):
                st.markdown(f"**University:** {profile['university']}")
                st.markdown(f"**Department:** {profile['department']}")
                st.markdown(f"**Program:** {profile['program']}")
                st.markdown(f"**Year of Study:** {profile['year_of_study']}")
            else:
                st.info("Your profile is private and not visible to others.")

            if st.button("✏️ Edit Profile"):
                st.session_state.edit_mode = True
                st.rerun()

        else:
            st.warning("No academic profile found. Click below to set it up.")
            if st.button("➕ Create Profile"):
                st.session_state.edit_mode = True
                st.rerun()

    # -----------------------------
    # ✏️ EDIT MODE
    # -----------------------------
    else:
        profile = st.session_state.profile_data
        st.subheader("🛠️ Edit Academic Info")

        with st.form("academic_profile_form"):
            university = st.text_input("University", value=profile.get("university", ""))
            department = st.text_input("Department", value=profile.get("department", ""))
            program = st.selectbox(
                "Program", ["Undergraduate", "Masters", "PhD"],
                index=["Undergraduate", "Masters", "PhD"].index(profile.get("program", "Undergraduate"))
            )
            year_of_study = st.selectbox(
                "Year of Study", [1, 2, 3, 4, 5],
                index=[1, 2, 3, 4, 5].index(profile.get("year_of_study", 1))
            )
            public = st.checkbox("Show this info publicly on your profile", value=profile.get("public", True))

            submitted = st.form_submit_button("💾 Save Profile")

            if submitted:
                new_profile = {
                    "university": university,
                    "department": department,
                    "program": program,
                    "year_of_study": year_of_study,
                    "public": public
                }
                save_profile(new_profile)  # Save to file
                st.session_state.profile_data = new_profile  # Update session memory
                st.session_state.edit_mode = False  # Switch to view mode
                st.success("✅ Profile saved successfully!")

                st.rerun() 