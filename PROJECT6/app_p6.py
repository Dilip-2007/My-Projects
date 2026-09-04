import streamlit as st
import pandas as pd
import numpy as np


# --------------------------------
# Page configuration
# --------------------------------
st.set_page_config(
    page_title="Data Detective Agent",
    page_icon="🔎",
    layout="wide"
)


# --------------------------------
# Title
# --------------------------------
st.title("🔎 Data Detective Agent")

st.write(
    "Upload a CSV file and the agent will clean the data, "
    "calculate statistics, and generate charts."
)


# --------------------------------
# File uploader
# --------------------------------
uploaded_file = st.file_uploader(
    "Upload your CSV file",
    type=["csv"]
)


# --------------------------------
# Main application
# --------------------------------
if uploaded_file is not None:

    try:

        # --------------------------------
        # Read CSV
        # --------------------------------
        df = pd.read_csv(uploaded_file)

        st.subheader("📄 Original Data")

        st.dataframe(
            df,
            use_container_width=True
        )


        # --------------------------------
        # Clean column names
        # --------------------------------
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )


        # --------------------------------
        # Find important columns
        # --------------------------------
        category_column = None
        revenue_column = None

        for column in df.columns:

            if column in ["category", "product_category", "type"]:
                category_column = column

            if column in [
                "revenue",
                "sales",
                "amount",
                "price"
            ]:
                revenue_column = column


        # --------------------------------
        # Check required columns
        # --------------------------------
        if category_column is None:

            st.error(
                "Could not find a category column. "
                "Use a column such as 'Category'."
            )

            st.stop()


        if revenue_column is None:

            st.error(
                "Could not find a revenue column. "
                "Use a column such as 'Revenue'."
            )

            st.stop()


        # --------------------------------
        # Clean category values
        # --------------------------------
        df[category_column] = (
            df[category_column]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
        )


        # --------------------------------
        # Clean revenue values
        # --------------------------------
        df[revenue_column] = (
            df[revenue_column]
            .astype(str)
            .str.replace("₹", "", regex=False)
            .str.replace("$", "", regex=False)
            .str.replace(",", "", regex=False)
            .str.strip()
        )


        # Convert invalid values to NaN
        df[revenue_column] = pd.to_numeric(
            df[revenue_column],
            errors="coerce"
        )


        # --------------------------------
        # Handle missing revenue
        # --------------------------------
        missing_revenue = df[revenue_column].isna().sum()

        if missing_revenue > 0:

            median_revenue = df[revenue_column].median()

            df[revenue_column] = (
                df[revenue_column]
                .fillna(median_revenue)
            )


        # --------------------------------
        # Remove duplicate rows
        # --------------------------------
        duplicate_count = df.duplicated().sum()

        df = df.drop_duplicates()


        # --------------------------------
        # Cleaned data
        # --------------------------------
        st.subheader("🧹 Cleaned Data")

        st.dataframe(
            df,
            use_container_width=True
        )


        # --------------------------------
        # Data cleaning report
        # --------------------------------
        st.subheader("🧪 Cleaning Report")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Rows",
                len(df)
            )

        with col2:

            st.metric(
                "Missing Revenue Fixed",
                missing_revenue
            )

        with col3:

            st.metric(
                "Duplicates Removed",
                duplicate_count
            )


        # --------------------------------
        # Revenue statistics
        # --------------------------------
        st.subheader("📊 Revenue Statistics")

        minimum = df[revenue_column].min()

        maximum = df[revenue_column].max()

        mean = df[revenue_column].mean()

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Minimum Revenue",
                f"{minimum:,.2f}"
            )

        with col2:

            st.metric(
                "Maximum Revenue",
                f"{maximum:,.2f}"
            )

        with col3:

            st.metric(
                "Average Revenue",
                f"{mean:,.2f}"
            )


        # --------------------------------
        # Category summary
        # --------------------------------
        st.subheader("📋 Category Metrics")

        category_summary = (
            df
            .groupby(category_column)[revenue_column]
            .agg(
                Minimum="min",
                Maximum="max",
                Average="mean",
                Total="sum"
            )
            .reset_index()
        )


        # Round numbers
        category_summary[
            ["Minimum", "Maximum", "Average", "Total"]
        ] = category_summary[
            ["Minimum", "Maximum", "Average", "Total"]
        ].round(2)


        st.dataframe(
            category_summary,
            use_container_width=True
        )


        # --------------------------------
        # Revenue by category chart
        # --------------------------------
        st.subheader("📈 Revenue by Category")

        chart_data = (
            df
            .groupby(category_column)[revenue_column]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(chart_data)


        # --------------------------------
        # Revenue distribution
        # --------------------------------
        st.subheader("📊 Revenue Distribution")

        histogram, bins = np.histogram(
            df[revenue_column],
            bins=10
        )

        distribution = pd.DataFrame(
            {
                "Revenue Range": [
                    f"{bins[i]:,.0f} - {bins[i + 1]:,.0f}"
                    for i in range(len(bins) - 1)
                ],
                "Number of Records": histogram
            }
        )

        st.bar_chart(
            distribution.set_index("Revenue Range")
        )


        # --------------------------------
        # Download cleaned data
        # --------------------------------
        st.subheader("💾 Download Cleaned Data")

        csv_data = df.to_csv(index=False)

        st.download_button(
            label="Download Cleaned CSV",
            data=csv_data,
            file_name="cleaned_data.csv",
            mime="text/csv"
        )


    except Exception as e:

        st.error(
            f"Could not process the CSV file: {e}"
        )