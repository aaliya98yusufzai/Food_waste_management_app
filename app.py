import streamlit as st
import pandas as pd
import pyodbc

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Local Food Wastage Management", layout="wide")

# --------------------------------------------------
# SQL SERVER CONNECTION
# --------------------------------------------------
CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=FoodWastageDB;"
    "Trusted_Connection=yes;"
)

def run_query(query: str) -> pd.DataFrame:
    """Run any SQL query and return DataFrame (for SQL Playground)."""
    try:
        with pyodbc.connect(CONN_STR) as conn:
            return pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Query failed: {e}")
        return pd.DataFrame()

def read_view(view_name: str) -> pd.DataFrame:
    """Read a SQL Server view into a DataFrame."""
    try:
        with pyodbc.connect(CONN_STR) as conn:
            return pd.read_sql(f"SELECT * FROM {view_name}", conn)
    except Exception as e:
        st.error(f"Failed to read view `{view_name}`: {e}")
        return pd.DataFrame()

# --------------------------------------------------
# SIDEBAR NAV
# --------------------------------------------------
st.sidebar.title("Food Donation Analytics")
page = st.sidebar.radio(
    "Go to Page:",
    ["Provider Overview", "Claims Overview", "Available Food", "Food Movement Tracking", "SQL Playground"]
)

# --------------------------------------------------
# PROVIDER OVERVIEW
# --------------------------------------------------
if page == "Provider Overview":
    st.title("📊 Provider Overview")
    df = read_view("Food_With_Provider")

    if df.empty:
        st.warning("`Food_With_Provider` returned no rows.")
    else:
        unique_providers = (
            df["Provider_ID"].nunique()
            if "Provider_ID" in df.columns
            else df["Provider_Name"].nunique()
        )
        total_items = df["Food_ID"].nunique() if "Food_ID" in df.columns else len(df)
        total_qty = int(df["Quantity"].sum()) if "Quantity" in df.columns else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Unique Providers", int(unique_providers))
        c2.metric("Food Items Listed", int(total_items))
        c3.metric("Total Quantity", total_qty)

        st.write("### Listings")
        st.dataframe(df, use_container_width=True)

# --------------------------------------------------
# CLAIMS OVERVIEW
# --------------------------------------------------
elif page == "Claims Overview":
    st.title("📥 Claims Overview")
    df = read_view("Food_Claims")

    if df.empty:
        st.warning("`Food_Claims` returned no rows.")
    else:
        total_claims = len(df)
        unique_receivers = (
            df["Receiver_ID"].nunique()
            if "Receiver_ID" in df.columns
            else df["Receiver_Name"].nunique()
        )
        completed = (
            df["Status"].str.lower().eq("completed").sum()
            if "Status" in df.columns and df["Status"].dtype == "object"
            else 0
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Claims", int(total_claims))
        c2.metric("Unique Receivers", int(unique_receivers))
        c3.metric("Completed Claims", int(completed))

        st.write("### Claim Details")
        st.dataframe(df, use_container_width=True)

# --------------------------------------------------
# AVAILABLE FOOD
# --------------------------------------------------
elif page == "Available Food":
    st.title("🥗 Available Food")
    df = read_view("Available_Food")

    if df.empty:
        st.warning("`Available_Food` returned no rows.")
    else:
        total_items = df["Food_ID"].nunique() if "Food_ID" in df.columns else len(df)
        total_qty = int(df["Quantity"].sum()) if "Quantity" in df.columns else 0

        c1, c2 = st.columns(2)
        c1.metric("Available Items", int(total_items))
        c2.metric("Total Available Quantity", total_qty)

        filter_col = None
        for candidate in ["Location", "Provider_City", "City"]:
            if candidate in df.columns:
                filter_col = candidate
                break

        if filter_col:
            cities = ["(All)"] + sorted([x for x in df[filter_col].dropna().unique()])
            chosen = st.selectbox(f"Filter by {filter_col}", options=cities, index=0)
            if chosen != "(All)":
                df = df[df[filter_col] == chosen]

        st.write("### Available Listings")
        st.dataframe(df, use_container_width=True)

# --------------------------------------------------
# FOOD MOVEMENT
# --------------------------------------------------
elif page == "Food Movement Tracking":
    st.title("🚚 Food Movement Tracking")
    df = read_view("Food_Movement")

    if df.empty:
        st.warning("`Food_Movement` returned no rows.")
    else:
        total_rows = len(df)
        unique_pairs = (
            df[["Provider_Name", "Receiver_Name"]].dropna().drop_duplicates().shape[0]
            if {"Provider_Name", "Receiver_Name"}.issubset(df.columns)
            else total_rows
        )
        c1, c2 = st.columns(2)
        c1.metric("Movements Logged", int(total_rows))
        c2.metric("Unique Provider → Receiver Pairs", int(unique_pairs))

        st.write("### Movement Log")
        st.dataframe(df, use_container_width=True)

# --------------------------------------------------
# SQL PLAYGROUND
# --------------------------------------------------
elif page == "SQL Playground":
    st.title("📝 SQL Playground")

    st.write("Run custom SQL queries against `FoodWastageDB`")

    query = st.text_area("Enter SQL query:", "SELECT TOP 10 * FROM Food_With_Provider")
    run = st.button("Run Query")

    if run:
        df = run_query(query)
        if df.empty:
            st.warning("No rows returned or query failed.")
        else:
            st.success(f"Returned {len(df)} rows.")
            st.dataframe(df, use_container_width=True)
