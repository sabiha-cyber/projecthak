import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# File to store wishlists
WISHLIST_FILE = "wishlist.json"

def load_listings():
    return pd.read_csv("listing.csv")

def load_wishlist():
    if os.path.exists(WISHLIST_FILE):
        with open(WISHLIST_FILE, "r") as f:
            return json.load(f)
    return {"items": [], "matches": []}

def save_wishlist(wishlist):
    with open(WISHLIST_FILE, "w") as f:
        json.dump(wishlist, f)

def app():
    # Load data
    try:
        df = load_listings()
        all_listings = df.to_dict(orient="records")
    except FileNotFoundError:
        st.error("Listings data not found!")
        all_listings = []
        return
    
    # Load wishlist
    wishlist = load_wishlist()
    
    
    
    visible_listings = all_listings
    
    # Filters
    st.header("Browse Listings")
    st.subheader("Filters")
    col1, col2 = st.columns(2)
    
    with col1:
        search_keyword = st.text_input("Search keyword")
        selected_category = st.selectbox("Category", ["All"] + list(df['category'].unique()))
        condition_filter = st.selectbox("Condition", ["Any"] + list(df['condition'].dropna().unique()))
    
    with col2:
        price_range = st.slider("Price Range", 0, 1000, (0, 500))
        university_filter = st.selectbox("University", ["All"] + list(df['university'].unique()))
    
    def matches_filters(listing):
        if listing['pricing_mode'] == 'Bidding':
            price_to_check = listing.get('current_bid', listing.get('min_bid', 0))
        else:
            price_to_check = listing.get('price', 0)
        
        return (
            (selected_category == "All" or listing["category"] == selected_category) and
            (condition_filter == "Any" or listing["condition"] == condition_filter) and
            (university_filter == "All" or listing["university"] == university_filter) and
            (price_range[0] <= price_to_check <= price_range[1]) and
            (not search_keyword or 
             search_keyword.lower() in str(listing['title']).lower() or 
             search_keyword.lower() in str(listing.get('description', '')).lower())
        )
    
    filtered_listings = [l for l in visible_listings if matches_filters(l)]
    
    # Display results
    st.subheader(f"🔍 {len(filtered_listings)} Listings Found")
    
    if filtered_listings:
        # Create display table with checkboxes
        display_data = []
        for idx, listing in enumerate(filtered_listings):
            if listing['pricing_mode'] == 'Bidding':
                price_display = f"Bidding (Current: ${listing.get('current_bid', listing.get('min_bid', 0)):.2f})"
            elif listing['pricing_mode'] == 'Hourly Rate':
                price_display = f"${listing['price']:.2f}/hr"
            else:
                price_display = f"${listing['price']:.2f}"
            
            display_data.append({
                "Add to Wishlist": False,  # This will become a checkbox
                "Title": listing['title'],
                "Category": listing['category'],
                "Price": price_display,
                "Condition": listing.get('condition', 'N/A'),
                "University": listing['university']
            })
        
        # Create editable dataframe
        edited_df = st.data_editor(
            pd.DataFrame(display_data),
            disabled=["Title", "Category", "Price", "Condition", "University"],
            hide_index=True,
            use_container_width=True,
            column_config={
                "Add to Wishlist": st.column_config.CheckboxColumn(required=True),
                "Title": st.column_config.TextColumn(width="large"),
                "Price": st.column_config.TextColumn(width="medium")
            }
        )
        
        # Handle wishlist additions from checkboxes
        added_items = edited_df[edited_df["Add to Wishlist"]]
        if not added_items.empty:
            for _, row in added_items.iterrows():
                new_item = {
                    "title": row["Title"],
                    "category": row["Category"],
                    "condition": row["Condition"],
                    "max_price": float(row["Price"].replace("$", "").split()[0]),
                    "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "notified": False
                }
                
                # Check if already in wishlist
                if not any(item["title"] == new_item["title"] for item in wishlist["items"]):
                    wishlist["items"].append(new_item)
                    save_wishlist(wishlist)
                    st.success(f"Added '{new_item['title']}' to wishlist!")
    
    # Option to add search term to wishlist when no results found
    elif search_keyword:
        st.info("No listings match your filters. Try adjusting them!")
        
        with st.expander("Add this search to your wishlist"):
            with st.form("wishlist_form"):
                st.write(f"Item: {search_keyword}")
                category = st.selectbox("Category", list(df['category'].unique()))
                condition = st.selectbox("Condition", list(df['condition'].dropna().unique()))
                max_price = st.number_input("Maximum Price", min_value=0, value=100)
                
                if st.form_submit_button("Add to Wishlist"):
                    new_item = {
                        "title": search_keyword,
                        "category": category,
                        "condition": condition,
                        "max_price": max_price,
                        "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "notified": False
                    }
                    wishlist["items"].append(new_item)
                    save_wishlist(wishlist)
                    st.success("Added to wishlist!")
    
    # Check for wishlist matches
    new_matches = []
    for wish_item in wishlist["items"]:
        for listing in all_listings:
            if (wish_item["title"].lower() in listing["title"].lower() and
                float(listing.get('price', float('inf'))) <= wish_item["max_price"] and
                not wish_item["notified"]):
                
                new_matches.append({
                    "wish_item": wish_item["title"],
                    "listing": listing["title"],
                    "price": listing.get("price", "N/A"),
                    "date_matched": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                wish_item["notified"] = True
    
    # Save if new matches found
    if new_matches:
        wishlist["matches"].extend(new_matches)
        save_wishlist(wishlist)
    
    # Display notifications
    if new_matches:
        st.sidebar.success(f"🎉 {len(new_matches)} new wishlist matches!")
        with st.expander("🔔 New Wishlist Matches", expanded=True):
            for match in new_matches:
                st.write(f"{match['wish_item']}** is now available!")
                st.write(f"*Listing:* {match['listing']} (${match['price']})")
                st.divider()
    
    # Show wishlist in sidebar
    st.sidebar.header("My Wishlist")
    if wishlist["items"]:
        for idx, item in enumerate(wishlist["items"]):
            cols = st.sidebar.columns([4,1])
            cols[0].write(f"{item['title']}")
            cols[0].caption(f"Max ${item['max_price']} | {item['condition']}")
            if cols[1].button("×", key=f"remove_{idx}"):
                wishlist["items"].pop(idx)
                save_wishlist(wishlist)
                st.rerun()
    else:
        st.sidebar.info("Your wishlist is empty")