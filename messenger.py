import streamlit as st
import firebase_admin
from firebase_admin import firestore
import os
import json
from datetime import datetime

from sign import db  # Firestore client from sign2.py

def app():
    # --- Constants ---
    DATA_FILE = "chat_data.json"
    IMAGE_FOLDER = "uploaded_images"
    os.makedirs(IMAGE_FOLDER, exist_ok=True)

    # --- Check login state ---
    if not st.session_state.get("signedout", False):
        st.warning("⚠️ Please log in first from the Account page.")
        st.stop()

    username = st.session_state.get("username", "")

    # --- Reset Chat History Button ---
    if st.button("🗑️ Reset Chat History"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        st.success("Chat history deleted. The app will reload now.")
        st.rerun()

    # --- Load & Save Chat Functions ---
    def load_chat():
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                try:
                    data = json.load(f)
                    # Filter for valid message dicts
                    data = [msg for msg in data if isinstance(msg, dict) and "sender" in msg and "receiver" in msg]
                    return data
                except json.JSONDecodeError:
                    return []
        return []

    def save_chat(data):
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)

    # --- Role Input ---
    role = st.text_input("🧑‍💼 Enter your role (buyer or seller)", key="role_input")
    if role.lower() not in ["buyer", "seller"]:
        st.warning("Please enter a valid role: 'buyer' or 'seller'")
        st.stop()
    role = role.lower()

    st.markdown(f"### Hello **{username}** ({role.title()})")

    chat_data = load_chat()
    target_user = None

    # --- Helper to check if username exists in Firestore ---
    def check_username_exists(username_to_check):
        users_ref = db.collection("users")
        query = users_ref.where("username", "==", username_to_check).limit(1).get()
        return bool(query)

    # --- Buyer flow ---
    if role == "buyer":
        sellers = list({msg.get("receiver") for msg in chat_data if msg.get("sender") == username and msg.get("receiver")})
        st.subheader("🧑‍💼 Choose a Seller to chat with")
        if sellers:
            options = sellers + ["(New Seller)"]
            choice = st.selectbox("Select:", options)
            if choice == "(New Seller)":
                new_seller = st.text_input("Enter new seller name")
                if new_seller.strip():
                    if check_username_exists(new_seller.strip()):
                        target_user = new_seller.strip()
                    else:
                        st.warning("This username does not exist. Please check and try again.")
            else:
                target_user = choice
        else:
            new_seller = st.text_input("Enter seller name to start chatting")
            if new_seller.strip():
                if check_username_exists(new_seller.strip()):
                    target_user = new_seller.strip()
                else:
                    st.warning("This username does not exist. Please check and try again.")

    # --- Seller flow ---
    elif role == "seller":
        buyers = list({msg.get("sender") for msg in chat_data if msg.get("receiver") == username and msg.get("sender")})
        if buyers:
            st.subheader("💬 Buyers who contacted you:")
            target_user = st.selectbox("Select a buyer to reply to:", buyers)
        else:
            st.info("No buyers have contacted you yet.")
            st.stop()

    # --- Chat Interface ---
    if target_user:
        st.subheader(f"Chat with {target_user}")
        message = st.text_input("💬 Type your message")
        uploaded_file = st.file_uploader("📷 Upload image", type=["png", "jpg", "jpeg"])

        if st.button("Send") and (message or uploaded_file):
            image_filename = None
            if uploaded_file:
                image_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uploaded_file.name}"
                with open(os.path.join(IMAGE_FOLDER, image_filename), "wb") as f:
                    f.write(uploaded_file.getbuffer())

            chat_data.append({
                "sender": username,
                "receiver": target_user,
                "message": message,
                "image": image_filename,
                "timestamp": datetime.now().isoformat()
            })
            save_chat(chat_data)
            st.rerun()

        # --- Display Chat History ---
        st.markdown("---")
        st.subheader("📜 Chat History")

        history = [msg for msg in chat_data if
                   (msg["sender"] == username and msg["receiver"] == target_user) or
                   (msg["sender"] == target_user and msg["receiver"] == username)]

        for msg in reversed(history[-30:]):
            time_str = msg["timestamp"].split("T")[1].split(".")[0]
            is_you = msg["sender"] == username
            name = "You" if is_you else msg["sender"]

            bubble_color = "#dcf8c6" if is_you else "#f1f0f0"
            align = "right" if is_you else "left"

            message_html = f"""
            <div style='text-align: {align}; margin: 10px 0;'>
                <div style='display: inline-block; background-color: {bubble_color}; padding: 10px 15px;
                            border-radius: 15px; max-width: 70%; word-wrap: break-word;color: #120c0c;'>
                    <div style='font-weight: bold;color: #120c0c;'>{name} <span style="font-size: 0.8em; color: black;">{time_str}</span></div>
                    <div>{msg['message'] if msg['message'] else ''}</div>
                </div>
            </div>
            """
            st.markdown(message_html, unsafe_allow_html=True)

            if msg["image"]:
                image_path = os.path.join(IMAGE_FOLDER, msg["image"])
                if os.path.exists(image_path):
                    st.image(image_path, width=250, caption=f"{name}'s Image", use_container_width=False)
                else:
                    st.warning(f"Image file not found: {image_path}")