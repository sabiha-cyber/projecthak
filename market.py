import streamlit as st
import pandas as pd
import os

def load_listings():
    
    return pd.read_csv("listing.csv")

def app():
  
 # Browse listings section
    st.header("Browse Listings")
    
    # Load listings from CSV
    try:
        df = load_listings()
        all_listings = df.to_dict(orient="records")
    except FileNotFoundError:
        st.error("Listings data not found!")
        all_listings = []
        return
    
    # Current user's university (would come from session in real app)
    current_user_university = "Islamic University of Technology"
    
    def is_visible(listing):
        if listing["visibility"] == "All registered students":
            return True
        return listing["university"] == current_user_university
    
    visible_listings = [l for l in all_listings if is_visible(l)]
    
    # Filters
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
        # Handle price filtering differently based on pricing mode
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
        # Create display table
        display_data = []
        for listing in filtered_listings:
            if listing['pricing_mode'] == 'Bidding':
                price_display = f"Bidding (Current: ${listing.get('current_bid', listing.get('min_bid', 0)):.2f})"
            elif listing['pricing_mode'] == 'Hourly Rate':
                price_display = f"${listing['price']:.2f}/hr"
            else:
                price_display = f"${listing['price']:.2f}"
            
            display_data.append({
                "Title": listing['title'],
                "Category": listing['category'],
                "Type": listing['type'],
                "Price": price_display,
                "Condition": listing.get('condition', 'N/A'),
                "University": listing['university'],
                "Visibility": listing['visibility']
            })
        
        # Convert to DataFrame for nice display
        display_df = pd.DataFrame(display_data)
        
        # Display the table
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Title": st.column_config.TextColumn(width="large"),
                "Price": st.column_config.TextColumn(width="medium"),
                "Condition": st.column_config.TextColumn(width="medium")
            }
        )
    else:
        st.info("No listings match your filters. Try adjusting them!")
        
        
