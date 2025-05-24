import streamlit as st
import pandas as pd
from firebase_admin import firestore
import pandas as pd
from datetime import datetime
import os
from chatbot import price_advice

CSV_FILE = "listing.csv"


# Initialize CSV file if it doesn't exist
def init_csv():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=[
            'id', 'title', 'description', 'category', 'type', 'condition',
            'service_type', 'pricing_mode', 'price', 'min_bid', 'current_bid',
            'visibility', 'university', 'created_at', 'seller'
        ])
        df.to_csv(CSV_FILE, index=False)

# Load listings from CSV
def load_listings():
    init_csv()
    return pd.read_csv(CSV_FILE)

# Save listings to CSV
def save_listings(df):
    df.to_csv(CSV_FILE, index=False)

# Add a new listing to the CSV
def add_listing(new_listing):
    df = load_listings()
    new_df = pd.DataFrame([new_listing])
    df = pd.concat([df, new_df], ignore_index=True)
    save_listings(df)
    return df
    
# Simulated Data
def app():
    

    db = firestore.client()

    if "users" not in st.session_state:
        st.session_state.users = {}
        users = db.collection("users").stream()
        for user_doc in users:
            user_data = user_doc.to_dict()
            st.session_state.users[user_data["username"]] = {
                "role": user_data.get("role", "student"),
                "suspended": user_data.get("suspended", False)
            }


    if "listings" not in st.session_state:
        st.session_state.listings = [
            {"id": 1, "title": "Laptop for sale", "status": "pending", "user": "alice"},
        ]

    if "reviews" not in st.session_state:
        st.session_state.reviews = []

    # Login
    st.title("Campus Trade ")
    #username = st.sidebar.text_input("Enter your username:")
    username = st.session_state.get("username", None)
    if username not in st.session_state.users:
        st.error("User not found.")
        st.stop()

    
    role = st.session_state.get("role", None)
    st.sidebar.write(f"Logged in as: **{username}** ({role})")

    if st.session_state.users[username]["suspended"]:
        st.warning("You are currently suspended.")
        st.stop()

    # Students see listing submission + review form
    if role == "student":
        st.header("Student Panel")
        # ----------- University Marketplace Listing Section -----------
        with st.expander("Marketplace"):
            st.title("University Marketplace")
            st.header("Create a Listing")

            with st.form("create_listing_form"):
                listing_type = st.selectbox("Listing Type", ["Tangible Item", "Service"])

                subcategory = None
                condition = None
                service_type = None

                if listing_type == "Tangible Item":
                    subcategory = st.selectbox("Choose a category", ["Textbook", "Gadgets", "Furniture"])
                    condition = st.selectbox("Condition", ["New", "Like New", "Good", "Fair", "Poor"])
                else:
                    subcategory = st.selectbox("Choose a service type", ["Tutoring", "Skill Exchange", "Other Services"])
                    service_type = subcategory

                title = st.text_input("Item*")
                description = st.text_area("Description")

                st.header("Flexible Pricing Options")
                if st.form_submit_button("Ask Ai For Price Recommendations"):
                    recommended_price = price_advice(title)  # Make sure this function exists
                    st.write(f"The price of {title} should be around {recommended_price} dollars")

                pricing_mode = st.selectbox("Choose a Pricing Model", ["Fixed Price", "Bidding", "Hourly Rate"])
                price = min_bid = current_bid = None

                if pricing_mode == "Fixed Price":
                    price = st.number_input("Enter the fixed price ($)", min_value=0.0, format="%.2f")
                elif pricing_mode == "Hourly Rate":
                    price = st.number_input("Enter hourly rate ($/hr)", min_value=0.0, format="%.2f")
                else:
                    min_bid = st.number_input("Set minimum bid price ($)", min_value=0.0, format="%.2f")
                    current_bid = min_bid

                visibility = st.selectbox("Who can view this listing?", [
                    "Only students from my university",
                    "All registered students"
                ])
                university = st.selectbox("University", [
                    "Islamic University of Technology", "BUET", "DU", "Other"
                ])

                submitted = st.form_submit_button("Publish Listing")
                if submitted:
                    if not title:
                        st.error("Title is required!")
                    else:
                        new_listing = {
                            "id": len(load_listings()) + 1,
                            "title": title,
                            "description": description,
                            "category": subcategory,
                            "type": listing_type,
                            "condition": condition if listing_type == "Tangible Item" else None,
                            "service_type": service_type if listing_type == "Service" else None,
                            "pricing_mode": pricing_mode,
                            "price": price if pricing_mode in ["Fixed Price", "Hourly Rate"] else None,
                            "min_bid": min_bid if pricing_mode == "Bidding" else None,
                            "current_bid": current_bid if pricing_mode == "Bidding" else None,
                            "visibility": visibility,
                            "university": university,
                            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "seller": username
                        }
                        add_listing(new_listing)
                        st.success("Listing published successfully!")
                        st.balloons()

        # ----------- User Review Section -----------
        with st.expander("Rate a User"):
            st.header("Rate a User")
            review_user = st.selectbox("Who did you transact with?", list(st.session_state.users.keys()))
            rating = st.slider("Rating (1-5)", 1, 5)
            comment = st.text_area("Leave a comment")

            if st.button("Submit Review"):
                st.session_state.reviews.append({
                    "from": username,
                    "to": review_user,
                    "rating": rating,
                    "comment": comment
                })
                st.success("Review submitted.")

    # Admin Panel
    if role == "admin":
        st.header("Admin Panel")

        with st.expander("Monitor marketplace"):
            st.subheader("Approve or Reject Listings")
            for listing in st.session_state.listings:
                if listing["status"] == "pending":
                    st.write(f"Listing #{listing['id']}: {listing['title']} by {listing['user']}")
                    col1, col2 = st.columns(2)
                    if col1.button(f"Approve {listing['id']}"):
                        listing["status"] = "approved"
                    if col2.button(f"Reject {listing['id']}"):
                        listing["status"] = "rejected"

        with st.expander("Monitor Reviews"):
            st.subheader("Monitor Reviews")
            flagged_users = {}
            for review in st.session_state.reviews:
                if review["rating"] <= 2:
                    flagged_users[review["to"]] = flagged_users.get(review["to"], 0) + 1
                st.write(f"{review['from']} → {review['to']} | Rating: {review['rating']} | {review['comment']}")

        with st.expander("Users with Poor Reviews"):
            st.subheader("Users with Poor Reviews")
            for user, count in flagged_users.items():
                if count >= 2:  # Flag users with 2 or more poor reviews
                    st.write(f"{user} has received {count} low ratings.")
                    if st.button(f"Suspend {user}"):
                        st.session_state.users[user]["suspended"] = True
                        st.success(f"{user} has been suspended.")

        with st.expander("User informations:"):
            def get_all_usernames():
                users_ref = db.collection("users")
                docs = users_ref.stream()
                user_data = {}
                for doc in docs:
                    data = doc.to_dict()
                    username = data.get("username")
                    if username:
                        user_data[username] = {
                            "dob": data.get("dob", "N/A"),
                            "phone": data.get("phone", "N/A")
                        }
                return user_data

            # Main Streamlit app
            st.title("User Info Viewer")

            users = get_all_usernames()

            if users:
                usernames = list(users.keys())
                selected_user = st.selectbox("Select a username", usernames)

                if selected_user:
                    st.write("### User Details")
                    st.write(f"**DOB**: {users[selected_user]['dob']}")
                    st.write(f"**Phone**: {users[selected_user]['phone']}")
            else:
                st.warning("No users found in Firestore.")

