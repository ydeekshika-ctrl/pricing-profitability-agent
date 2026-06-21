
# Adapted for CRIP_Unclean_Validation_Dataset.xlsx

import pandas as pd
import numpy as np
import streamlit as st


st.set_page_config(page_title="Pricing & Profitability Agent", layout="wide")

st.title("Agent 2 — Pricing & Profitability Agent")

uploaded_file = st.file_uploader("Upload CRIP Dataset", type=["xlsx", "csv"])

if uploaded_file:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # ---------------------------
    # Basic Cleaning
    # ---------------------------
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    numeric_cols = [
        "Written_Premium",
        "Claim_Amount",
        "Total_Expense"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Written_Premium"])

    # ---------------------------
    # Core Pricing Metrics
    # ---------------------------
    premium = df["Written_Premium"].replace(0, np.nan)

    df["Loss_Ratio_Calc"] = df["Claim_Amount"] / premium
    df["Expense_Ratio"] = df["Total_Expense"] / premium
    df["Combined_Ratio"] = df["Loss_Ratio_Calc"] + df["Expense_Ratio"]

    df["Underwriting_Profit"] = (
        df["Written_Premium"]
        - df["Claim_Amount"]
        - df["Total_Expense"]
    )

    # ---------------------------
    # Profitability Tiers
    # ---------------------------
    def classify_ratio(x):

        if pd.isna(x):
            return "Unknown"

        if x < 0.80:
            return "Excellent"
        elif x < 0.95:
            return "Good"
        elif x <= 1.00:
            return "Marginal"
        else:
            return "Loss-Making"

    df["Profitability_Tier"] = df["Combined_Ratio"].apply(classify_ratio)

    # ---------------------------
    # KPI Dashboard
    # ---------------------------
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Premium", f"₹{df['Written_Premium'].sum():,.0f}")
    c2.metric("Claims", f"₹{df['Claim_Amount'].sum():,.0f}")
    c3.metric("Expenses", f"₹{df['Total_Expense'].sum():,.0f}")
    c4.metric("Profit", f"₹{df['Underwriting_Profit'].sum():,.0f}")

    st.divider()

    # 1 Loss Ratio
    st.subheader("Loss Ratio by Product")

    loss_ratio_product = (
        df.groupby("Product_Type", as_index=False)["Loss_Ratio_Calc"]
        .mean()
        .sort_values("Loss_Ratio_Calc", ascending=False)
    )

    st.subheader("Loss Ratio by Product")

    loss_ratio_product = (
        df.groupby("Product_Type")["Loss_Ratio_Calc"]
        .mean()
        .sort_values(ascending=False)
)

st.bar_chart(loss_ratio_product)

    # 2 Profit by Product
    st.subheader("Profit by Product")

    product_profit = (
        df.groupby("Product_Type", as_index=False)["Underwriting_Profit"]
        .sum()
        .sort_values("Underwriting_Profit", ascending=False)
    )

    st.subheader("Profit by Product")

    product_profit = (
        df.groupby("Product_Type")["Underwriting_Profit"]
        .sum()
        .sort_values(ascending=False)
)

st.bar_chart(product_profit)

    # 3 Profitability Tier Classification
    st.subheader("Profitability Tiers")

    tier_df = (
        df.groupby("Profitability_Tier")
        .size()
        .reset_index(name="Count")
    )

    st.dataframe(tier_df, use_container_width=True)

    # 4 Customer Segment Profitability
    st.subheader("Customer Segment Profitability")

    segment_df = (
        df.groupby("Customer_Segment", as_index=False)
        ["Underwriting_Profit"]
        .sum()
    )

    st.dataframe(segment_df, use_container_width=True)

    # 5 Distribution Channel Profitability
    st.subheader("Distribution Channel Profitability")

    channel_df = (
        df.groupby("Distribution_Channel", as_index=False)
        ["Underwriting_Profit"]
        .sum()
    )

    st.dataframe(channel_df, use_container_width=True)

    # 6 Region-wise Profitability
    # Dataset has State instead of Region

    st.subheader("State-wise Profitability")

    state_df = (
        df.groupby("State", as_index=False)
        ["Underwriting_Profit"]
        .sum()
        .sort_values("Underwriting_Profit", ascending=False)
    )

    st.subheader("State-wise Profitability")

    state_df = (
        df.groupby("State")["Underwriting_Profit"]
        .sum()
        .sort_values(ascending=False)
)

st.bar_chart(state_df)

    # 7 Monthly Trend (36 months)
    st.subheader("Monthly Profit Trend")

    monthly_df = (
        df.groupby(pd.Grouper(key="Date", freq="M"))
        ["Underwriting_Profit"]
        .sum()
        .reset_index()
        .tail(36)
    )

    st.subheader("Monthly Profit Trend")

    monthly_df = (
        df.groupby(pd.Grouper(key="Date", freq="ME"))
        ["Underwriting_Profit"]
        .sum()
        .tail(36)
)

st.line_chart(monthly_df)

    # 8 AI Pricing Insights
    st.subheader("AI Pricing Insights")

    insights = []

    ratio_table = (
        df.groupby("Product_Type")["Combined_Ratio"]
        .mean()
        .reset_index()
    )

    for _, row in ratio_table.iterrows():

        product = row["Product_Type"]
        ratio = row["Combined_Ratio"]

        if ratio > 1:
            insights.append(
                f"🔴 {product}: Combined Ratio {ratio:.2f} → Underpriced and loss-making."
            )

        elif ratio < 0.80:
            insights.append(
                f"🟢 {product}: Combined Ratio {ratio:.2f} → Highly profitable."
            )

        else:
            insights.append(
                f"🟡 {product}: Combined Ratio {ratio:.2f} → Monitor pricing."
            )

    for item in insights:
        st.write(item)

    # Detailed outputs
    st.subheader("Detailed Metrics")

    st.dataframe(
        df[[
            "Policy_ID",
            "Product_Type",
            "Customer_Segment",
            "Distribution_Channel",
            "State",
            "Written_Premium",
            "Claim_Amount",
            "Total_Expense",
            "Loss_Ratio_Calc",
            "Expense_Ratio",
            "Combined_Ratio",
            "Underwriting_Profit",
            "Profitability_Tier"
        ]],
        use_container_width=True
    )
