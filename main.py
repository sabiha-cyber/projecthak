import streamlit as st
st.set_page_config(
        page_title="TRADE-IN",
)
from streamlit_option_menu import option_menu
import os
from dotenv import load_dotenv
load_dotenv()

#import home, trending, sign, your, about, buy_me_a_coffee
import admin,chatbot,market,messenger,sign,profile,map



st.markdown(
    """
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src=f"https://www.googletagmanager.com/gtag/js?id={os.getenv('analytics_tag')}"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', os.getenv('analytics_tag'));
        </script>
    """, unsafe_allow_html=True)

print(os.getenv('analytics_tag'))


class MultiApp:

    def __init__(self):
        self.apps = []

    def add_app(self, title, func):

        self.apps.append({
            "title": title,
            "function": func
        })

    def run():
        # app = st.sidebar(
        with st.sidebar:        
            app = option_menu(
                menu_title='TRADE-IN ',
                options=['Profile','Account','Market','Student-Admin panel','Chatbot','Chatapp', 'Map'],
                icons=['info-circle','person-circle','shop','bookmark-fill','robot','chat', 'geo-alt'],
                menu_icon='chat-text-fill',
                default_index=1,
                styles={
                    "container": {"padding": "5!important","background-color":'black'},
        "icon": {"color": "white", "font-size": "23px"}, 
        "nav-link": {"color":"white","font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "blue"},
        "nav-link-selected": {"background-color": "#02ab21"},}
                
                )

        
        
        if app == "Account":
            sign.app()
        if app == 'Student-Admin panel':
            admin.app()
        if app == "Chatbot":
            chatbot.app()
        if app == "Market":
            market.app()
        if app == "Chatapp":
            messenger.app()
        if app == "Profile":
            profile.app()
        if app == "Map":
            map.app()
             
          
             
    run()