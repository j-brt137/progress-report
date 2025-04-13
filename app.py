import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
import seaborn as sns
from io import BytesIO

# Set page configuration
st.set_page_config(page_title="User Rating App", layout="wide")

# Initialize session state variables if they don't exist
if 'page' not in st.session_state:
    st.session_state.page = "Input"

# Function to load data from CSV
def load_data():
    file_path = "user_ratings.csv"
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return pd.DataFrame(columns=["Name", "Date", "Scale", "Note"])

# Function to save data to CSV
def save_data(df):
    df.to_csv("user_ratings.csv", index=False)

# Function to create navigation
def create_navigation():
    col1, col2 = st.columns([1, 9])
    with col1:
        if st.button("Input Data"):
            st.session_state.page = "Input"
            st.rerun()
    with col2:
        if st.button("View Analytics"):
            st.session_state.page = "Analytics"
            st.rerun()

# Input Page
def input_page():
    st.title("User Rating Input Form")
    
    with st.form(key="rating_form"):
        # User name input
        user_name = st.text_input("Name")
        
        # Date selection
        rating_date = st.date_input("Date", value=datetime.now())
        
        # Self-rating scale
        rating_scale = st.slider("Rate yourself (1-10)", min_value=1, max_value=10, value=5)
        
        # Notes
        notes = st.text_area("Notes (Optional)")
        
        # Submit button
        submit_button = st.form_submit_button(label="Submit Rating")
        
        if submit_button:
            if not user_name:
                st.error("Please enter your name.")
            else:
                # Load existing data
                df = load_data()
                
                # Create new entry
                new_entry = pd.DataFrame({
                    "Name": [user_name],
                    "Date": [rating_date.strftime("%Y-%m-%d")],
                    "Scale": [rating_scale],
                    "Note": [notes]
                })
                
                # Append new entry to existing data
                df = pd.concat([df, new_entry], ignore_index=True)
                
                # Save updated data
                save_data(df)
                
                st.success("Your rating has been recorded successfully!")

# Analytics Page
def analytics_page():
    st.title("User Rating Analytics")
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.warning("No data available. Please add ratings on the input page.")
        return
    
    # Convert date to datetime for proper sorting
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    
    # Get unique user names
    user_names = df['Name'].unique().tolist()
    
    # User selection sidebar
    st.sidebar.header("Filter Options")
    
    # Option to view all users or select specific ones
    view_option = st.sidebar.radio("View", ["All Users", "Select User"])
    
    selected_users = []
    if view_option == "All Users":
        selected_users = user_names
    else:
        selected_user = st.sidebar.selectbox("Select User", user_names)
        selected_users = [selected_user]
    
    # Filter data based on selection
    filtered_df = df[df['Name'].isin(selected_users)]
    
    # Download button
    if st.sidebar.button("Download Data CSV"):
        csv = df.to_csv(index=False)
        b64 = BytesIO()
        b64.write(csv.encode())
        b64.seek(0)
        st.sidebar.download_button(
            label="Click to Download",
            data=b64,
            file_name="user_ratings.csv",
            mime="text/csv"
        )
    
    # Line chart visualization
    st.subheader("Rating Trends Over Time")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot line chart by user
    for user in selected_users:
        user_data = filtered_df[filtered_df['Name'] == user]
        ax.plot(user_data['Date'], user_data['Scale'], marker='o', label=user)
    
    ax.set_xlabel('Date')
    ax.set_ylabel('Rating Scale')
    ax.set_title('User Self-Rating Over Time')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Format x-axis dates to be more readable
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    st.pyplot(fig)
    
    # Show data table
    st.subheader("Data Table")
    st.dataframe(filtered_df[["Name", "Date", "Scale", "Note"]], use_container_width=True)
    
    # Show statistics if data exists
    if not filtered_df.empty:
        st.subheader("Statistics")
        
        stats_col1, stats_col2 = st.columns(2)
        
        with stats_col1:
            avg_rating = filtered_df.groupby('Name')['Scale'].mean().reset_index()
            avg_rating.columns = ['User', 'Average Rating']
            st.dataframe(avg_rating, use_container_width=True)
        
        with stats_col2:
            max_rating = filtered_df.groupby('Name')['Scale'].max().reset_index()
            max_rating.columns = ['User', 'Highest Rating']
            st.dataframe(max_rating, use_container_width=True)

# Main app logic
def main():
    create_navigation()
    
    if st.session_state.page == "Input":
        input_page()
    else:
        analytics_page()

if __name__ == "__main__":
    main()