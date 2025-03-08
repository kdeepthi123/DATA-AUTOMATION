import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px

# 🔹 Google Sheets Authentication
SERVICE_ACCOUNT_FILE = "credentials.json"  # Replace with your service account JSON file
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
#credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
#client = gspread.authorize(credentials)

# Load Google Credentials from Streamlit Secrets
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["google_drive"]
)

client = gspread.authorize(credentials)

# 🔹 Streamlit App Title
st.title("📊 Swiggy Data Visualization Dashboard")

# 🔹 User Input: Google Sheet URL or File Upload
data_source = st.radio("📌 Select Data Source:", ["Upload Excel File", "Paste Google Sheets URL"])

uploaded_file = None  # ✅ Initialize to avoid NameError

if data_source == "Upload Excel File":
    uploaded_file = st.file_uploader("📂 Upload your Excel file:", type=["xlsx"])
    if uploaded_file:
        xls = pd.ExcelFile(uploaded_file)
        sheet_names = xls.sheet_names
elif data_source == "Paste Google Sheets URL":
    GOOGLE_SHEET_URL = st.text_input("🔗 Paste Google Sheets URL:")
    if GOOGLE_SHEET_URL:
        sheet = client.open_by_url(GOOGLE_SHEET_URL)
        worksheet_list = sheet.worksheets()
        sheet_names = [ws.title for ws in worksheet_list]

# 🔹 Ensure user selects a valid source
if (uploaded_file or GOOGLE_SHEET_URL) and "sheet_names" in locals():
    selected_sheet = st.selectbox("📌 Select a Tab (Sheet):", sheet_names)

    # 🔹 Load Data Function
    @st.cache_data
    def load_data(sheet_name):
        if uploaded_file:
            return pd.read_excel(uploaded_file, sheet_name=sheet_name)
        elif GOOGLE_SHEET_URL:
            worksheet = sheet.worksheet(sheet_name)
            data = worksheet.get_all_records()
            return pd.DataFrame(data)

    # 🔹 Load Data from Selected Source
    df = load_data(selected_sheet)

    # 🔹 Display Data
    st.write("📜 **Data Preview:**", df.head())

    # ✅ **Data Cleaning**
    for col in ["Rating", "Total Ratings", "Price (₹)"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")  # Convert to Numeric

    # 🔹 **Highest & Lowest Rated Dishes**
    st.subheader("⭐ Top & Lowest Rated Dishes")
    if "Rating" in df.columns:
        highest_rated = df.nlargest(10, "Rating")[["Dish Name", "Rating", "Restaurant Name", "Total Ratings"]]
        lowest_rated = df.nsmallest(10, "Rating")[["Dish Name", "Rating", "Restaurant Name", "Total Ratings"]]

        col1, col2 = st.columns(2)
        with col1:
            st.write("✅ **Top 10 Highest Rated Dishes**")
            st.write(highest_rated)
        with col2:
            st.write("⚠️ **Top 10 Lowest Rated Dishes**")
            st.write(lowest_rated)

    # 🔹 **Price Distribution**
    if "Price (₹)" in df.columns:
        st.subheader("💰 Price Distribution of Dishes")
        fig = px.histogram(df, x="Price (₹)", nbins=20, title="Distribution of Dish Prices")
        st.plotly_chart(fig)

    # 🔹 **Price vs. Rating Scatter Plot**
    if "Price (₹)" in df.columns and "Rating" in df.columns:
        st.subheader("💵 Price vs Rating Analysis")
        fig = px.scatter(df, x="Price (₹)", y="Rating", hover_data=["Dish Name", "Restaurant Name"], title="Price vs Rating")
        st.plotly_chart(fig)

    # 🔹 **Top Cuisines**
    if "Cuisine" in df.columns:
        st.subheader("🍽️ Top Cuisines Available")
        cuisine_counts = df["Cuisine"].value_counts()
        st.bar_chart(cuisine_counts)

    # 🔹 **Restaurants with Most Dishes**
    if "Restaurant Name" in df.columns:
        st.subheader("🏪 Restaurants Offering the Most Dishes")
        restaurant_counts = df["Restaurant Name"].value_counts()
        st.bar_chart(restaurant_counts)

    # 🔹 Locality-Based Price Trends with Min, Max, and Margin Prices
    if "Locality" in df.columns and "Price (₹)" in df.columns:
        st.subheader("📍 Average, Minimum, and Maximum Price per Locality")

        # Group by 'Locality' and calculate avg, min, max, and price margin
        locality_price_stats = df.groupby("Locality")["Price (₹)"].agg(["mean", "min", "max"])
        locality_price_stats["Margin"] = locality_price_stats["max"] - locality_price_stats["min"]
        
        # Convert index to column for visualization
        locality_price_stats = locality_price_stats.reset_index()

        # Create an interactive bar chart with hover details
        fig = px.bar(
            locality_price_stats,
            x="Locality",
            y="mean",
            hover_data={"Locality": True, "mean": ":.2f", "min": ":.2f", "max": ":.2f", "Margin": ":.2f"},
            title="Average, Minimum & Maximum Price per Locality",
            labels={"mean": "Avg Price (₹)", "min": "Min Price (₹)", "max": "Max Price (₹)", "Margin": "Price Difference (₹)"},
        )

        st.plotly_chart(fig)

    # 🔹 **Discount Comparison**
    if "Discount" in df.columns:
        st.subheader("🎉 Discount Comparison Across Restaurants")
        discount_counts = df["Discount"].value_counts()
        st.bar_chart(discount_counts)

    # 🔹 **Discount vs Price Analysis**
    if "Discount" in df.columns and "Price (₹)" in df.columns:
        st.subheader("📉 Discount Impact on Price")
        fig = px.box(df, x="Discount", y="Price (₹)", title="Price Distribution Across Discount Categories")
        st.plotly_chart(fig)

    st.write("✅ **Data Visualization & Decision-Making Insights Completed!**")
