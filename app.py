import streamlit as st
import sqlite3
import pandas as pd
import os

st.set_page_config(page_title="Food Waste Management", layout="wide")

# Load DB path from secrets
db_path = st.secrets["DB_PATH"]

# Connect to SQLite
def get_connection():
    return sqlite3.connect(db_path)

# Sample function to fetch data
def show_data():
    try:
        conn = get_connection()
        query = "SELECT * FROM Food_Listing LIMIT 5;"
        df = pd.read_sql_query(query, conn)  # ✅ Use pandas to fetch data
        st.dataframe(df)  # ✅ Proper way to display
        conn.close()
    except Exception as e:
        st.error(f"Error: {e}")

st.title("🍽️ Food Waste Management System")

menu = ["Home", "Database Playground"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Home":
    st.subheader("Welcome to the Food Waste Management App")
    st.write("This app helps track food donations and reduce waste.")
    show_data()  # ✅ Show sample table on Home page

elif choice == "Database Playground":
    st.subheader("🔍 SQL Playground (Read-Only Mode)")
    query = st.text_area("Enter your SQL query", "SELECT * FROM Food_Listing LIMIT 5;")
    
    if st.button("Run Query"):
        try:
            conn = get_connection()
            df = pd.read_sql_query(query, conn)  # ✅ Return as DataFrame
            st.dataframe(df)
            conn.close()
        except Exception as e:
            st.error(f"Query failed: {e}")
