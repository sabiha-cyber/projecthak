import streamlit as st
import firebase_admin
from firebase_admin import firestore, credentials, auth
import json
import requests
import re
from chatbot import price_advice

valid_admin_usernames = ["admin123", "muzna", "cs_head", "professor1"]
valid_admin_emails = ["admin@university.edu", "muzna@csdept.edu", "faculty@college.edu"]
valid_domains = ["@iut-dhaka.edu", "@du.ac.bd", "@buet.ac.bd"]
def is_valid_uni_email(email):
    return email.endswith(tuple(valid_domains))

# Firebase setup
if not firebase_admin._apps:
    cred = credentials.Certificate("json_code.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

def app():
    st.title('Welcome to :violet[our shop] 🛍️')

    # Session states
    for key in ['username', 'useremail', 'role', 'signedout', 'signout']:
        if key not in st.session_state:
            st.session_state[key] = ''

    def sign_up_with_email_and_password(email, password, username=None):
        try:
            url = "https://identitytoolkit.googleapis.com/v1/accounts:signUp"
            payload = json.dumps({
                "email": email,
                "password": password,
                "returnSecureToken": True,
                "displayName": username
            })
            r = requests.post(url, params={"key": "AIzaSyAXNnzMMHirvViR6qe_rED4q5yHranAQYE"}, data=payload)
            res = r.json()
            if "email" in res:
                role = "admin" if username in valid_admin_usernames or st.session_state.email_input in valid_admin_emails else "student"
                db.collection("users").document(res['email']).set({
                    "email": res['email'],
                    "username": username,
                    "role": role,
                    "suspended": False,
                    "dob": st.session_state.dob.strftime("%Y-%m-%d"),
                    "phone": st.session_state.number  # storing number here
                })
                return res['email']
            else:
                st.warning(res)
        except Exception as e:
            st.warning(f"Signup failed: {e}")

    def sign_in_with_email_and_password(email, password):
        try:
            url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
            payload = json.dumps({
                "email": email,
                "password": password,
                "returnSecureToken": True
            })
            r = requests.post(url, params={"key": "AIzaSyAXNnzMMHirvViR6qe_rED4q5yHranAQYE"}, data=payload)
            res = r.json()
            if "email" in res:
                user_ref = db.collection("users").document(res['email']).get()
                if user_ref.exists:
                    user_info = user_ref.to_dict()
                    return {
                        "email": res['email'],
                        "username": user_info.get("username", ""),
                        "role": user_info.get("role", "student"),
                        "suspended": user_info.get("suspended", False)
                    }
                else:
                    st.warning("User data not found.")
            else:
                st.warning(res)
        except Exception as e:
            st.warning(f"Signin failed: {e}")

    def reset_password(email):
        try:
            url = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"
            payload = json.dumps({
                "email": email,
                "requestType": "PASSWORD_RESET"
            })
            r = requests.post(url, params={"key": "AIzaSyAXNnzMMHirvViR6qe_rED4q5yHranAQYE"}, data=payload)
            return r.status_code == 200, "Reset email sent" if r.status_code == 200 else r.json()
        except Exception as e:
            return False, str(e)

    def handle_login():
        userinfo = sign_in_with_email_and_password(st.session_state.email_input, st.session_state.password_input)
        if userinfo:
            if userinfo['suspended']:
                st.error("Account suspended.")
                return
            st.session_state.username = userinfo['username']
            st.session_state.useremail = userinfo['email']
            st.session_state.role = userinfo['role']
            st.session_state.signedout = True
            st.session_state.signout = True

    def handle_logout():
        for key in ['username', 'useremail', 'role', 'signedout', 'signout']:
            st.session_state[key] = ''

    if not st.session_state["signedout"]:
        choice = st.selectbox('Login/Signup', ['Login', 'Sign up'])
        st.session_state.email_input = st.text_input('Email Address')
        st.session_state.password_input = st.text_input('Password', type='password')

        if choice == 'Sign up':
            st.session_state.username = st.text_input("Enter your unique username")
            st.session_state.uni = st.text_input("Enter your uni name")
            st.session_state.number = st.text_input("Enter your number")
            st.session_state.dob = st.date_input("Enter your date of birth")

            if st.button('Create my account'):
                if not is_valid_uni_email(st.session_state.email_input):
                    st.error(f"Invalid organisation")
                else:
                    result = sign_up_with_email_and_password(
                        st.session_state.email_input,
                        st.session_state.password_input,
                        st.session_state.username
                    )
                    if result:
                        st.success('Account created! Please log in.')
        else:
            st.button('Login', on_click=handle_login)
            with st.expander("Forgot password?"):
                email = st.text_input('Enter your email')
                if st.button("Send Reset Email"):
                    success, msg = reset_password(email)
                    st.success(msg) if success else st.error(msg)

    if st.session_state.signout:
        st.success(f"Welcome {st.session_state.username}!")
        st.info(f"Role: {st.session_state.role}")
        st.button('Sign out', on_click=handle_logout)

        if st.session_state.role == "admin":
            st.subheader("Admin Panel")
            users = db.collection("users").stream()
            students = [u.id for u in users if u.to_dict().get("role") == "student"]
            promote = st.selectbox("Promote a student to admin", students)
            if st.button("Promote"):
                db.collection("users").document(promote).update({"role": "admin"})
                st.success(f"{promote} promoted to admin!")
