import streamlit as st
import pandas as pd
import pyodbc

# ---------------------------
# Database Connection
# ---------------------------
def create_connection():
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=AALIYA_PC;"  # ✅ your server name
            "DATABASE=FoodWastageDB;"
            "Trusted_Connection=yes;"
        )
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

# ---------------------------
# Fetch Data Helper
# ---------------------------
def run_query(conn, query):
    try:
        return pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return pd.DataFrame()

# ---------------------------
# Streamlit App
# ---------------------------
def main():
    st.set_page_config(page_title="Food Waste Management App", layout="wide")
    st.title("🍽️ Food Waste Management App")

    conn = create_connection()
    if not conn:
        st.stop()

    # Sidebar Menu
    menu = [
        "📋 Explore Tables",
        "👀 Explore Views",
        "📝 SQL Playground",
        "📊 Insights",
    ]
    choice = st.sidebar.radio("Navigate", menu)

    # ---------------------------
    # Explore Tables
    # ---------------------------
    if choice == "📋 Explore Tables":
        st.subheader("Tables in FoodWastageDB")

        tables = ["CLAIMS", "FOOD_LISTING", "PROVIDER", "RECIEVER"]
        selected = st.selectbox("Select a table", tables)

        if selected:
            df = run_query(conn, f"SELECT TOP 50 * FROM {selected}")
            st.write(f"Showing top 50 rows of **{selected}**")
            st.dataframe(df)

    # ---------------------------
    # Explore Views
    # ---------------------------
    elif choice == "👀 Explore Views":
        st.subheader("Database Views")

        views = [
            "Available_Food",
            "Food_Claims",
            "Food_Movement",
            "Food_With_Provider",
            "NonExpired_Food_With_Provider"
        ]
        selected = st.selectbox("Select a view", views)

        if selected:
            df = run_query(conn, f"SELECT TOP 50 * FROM {selected}")
            if df.empty:
                st.warning(f"No data found in view: {selected}")
            else:
                st.write(f"Showing top 50 rows of **{selected}**")
                st.dataframe(df)

    # ---------------------------
    # SQL Playground
    # ---------------------------
    elif choice == "📝 SQL Playground":
        st.subheader("Write and Run Custom SQL Queries")
        query = st.text_area("Enter your SQL query here", height=150)

        if st.button("Execute Query"):
            if query.strip() == "":
                st.warning("Please enter a SQL query!")
            else:
                df = run_query(conn, query)
                if not df.empty:
                    st.success("✅ Query executed successfully")
                    st.dataframe(df)
                else:
                    st.warning("No results returned for this query.")

    # ---------------------------
    # Insights
    # ---------------------------
    elif choice == "📊 Insights":
        st.subheader("Analytics & Insights")

        # Most frequent providers
        st.markdown("### 🏆 Top Food Providers")
        df1 = run_query(conn, """
            SELECT P.NAME, COUNT(F.FOOD_ID) AS Total_Foods
            FROM PROVIDER P
            JOIN FOOD_LISTING F ON P.PROVIDER_ID = F.PROVIDER_ID
            GROUP BY P.NAME
            ORDER BY Total_Foods DESC
        """)
        st.dataframe(df1)

        # Highest demand locations
        st.markdown("### 📌 Highest Demand Locations")
        df2 = run_query(conn, """
            SELECT R.CITY, COUNT(C.CLAIM_ID) AS Total_Claims
            FROM RECIEVER R
            JOIN CLAIMS C ON R.RECEIVER_ID = C.RECEIVER_ID
            GROUP BY R.CITY
            ORDER BY Total_Claims DESC
        """)
        st.dataframe(df2)

        # Food wastage trends
        st.markdown("### 📉 Food Wastage Trends (Expired Items)")
        df3 = run_query(conn, """
            SELECT FOOD_TYPE, COUNT(*) AS Expired_Count
            FROM FOOD_LISTING
            WHERE EXPIRY_DATE < GETDATE()
            GROUP BY FOOD_TYPE
            ORDER BY Expired_Count DESC
        """)
        st.dataframe(df3)

    conn.close()

if __name__ == "__main__":
    main()
