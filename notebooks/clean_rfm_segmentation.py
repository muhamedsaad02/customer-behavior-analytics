"""
Customer Behavior Analytics — Cleaning, RFM & Segmentation
=============================================================
This script takes the raw simulated e-commerce session data
(generate_data.py output), cleans it, computes RFM metrics per
customer, and applies K-Means clustering to segment customers
into behavioral groups (VIP, Active/Loyal, Regular/Casual, At Risk).

Output: final_dashboard_data.csv — ready to load into Power BI.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# ============================================================
# 1. Load raw data
# ============================================================
df = pd.read_csv("customer_behavior_funnel_data.csv")
print(f"Loaded {df.shape[0]:,} rows, {df.shape[1]} columns")

# ============================================================
# 2. Data Cleaning
# ============================================================

# --- 2.1 Missing values: logical gaps get a contextual label ---
df["campaign_type"] = df["campaign_type"].fillna("No Campaign")
df["product_category"] = df["product_category"].fillna("No View")

# --- 2.2 Missing values: random/unexplained gaps ---
df["channel"] = df["channel"].fillna("Unknown")
df["device"] = df["device"].fillna("Unknown")

# --- 2.3 Duplicate rows: drop fully duplicated sessions ---
before = len(df)
df = df.drop_duplicates()
print(f"Removed {before - len(df):,} duplicate rows")

# --- 2.4 Inconsistent text casing ---
df["device"] = df["device"].str.strip().str.title()
df["channel"] = df["channel"].str.strip().str.title()

# --- 2.5 Outlier values in session duration ---
median_duration = df["session_duration_min"].median()
mask = (df["session_duration_min"] > 60) | (df["session_duration_min"] <= 0)
df.loc[mask, "session_duration_min"] = median_duration

# --- 2.6 Parse date column ---
df["date"] = pd.to_datetime(df["date"])

print("Cleaning complete ✅")
print(df.isnull().sum().sum(), "missing values remaining")

# ============================================================
# 3. RFM Calculation (per customer)
# ============================================================
latest_date = df["date"].max()

recency_df = df.groupby("user_id")["date"].max().reset_index()
recency_df["Recency"] = (latest_date - recency_df["date"]).dt.days

frequency_df = df.groupby("user_id")["session_id"].nunique().reset_index()
frequency_df.columns = ["user_id", "Frequency"]

monetary_df = df.groupby("user_id")["revenue"].sum().reset_index()
monetary_df.columns = ["user_id", "Monetary"]

rfm_df = recency_df[["user_id", "Recency"]].merge(frequency_df, on="user_id")
rfm_df = rfm_df.merge(monetary_df, on="user_id")

print(f"RFM table built for {len(rfm_df):,} unique customers")

# ============================================================
# 4. K-Means Segmentation
# ============================================================
features = rfm_df[["Recency", "Frequency", "Monetary"]]

scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(features)

kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
rfm_df["Segment"] = kmeans.fit_predict(rfm_scaled)

# --- Name segments based on their RFM averages ---
segment_summary = rfm_df.groupby("Segment")[["Recency", "Frequency", "Monetary"]].mean()
print("\nSegment averages:\n", segment_summary)

# NOTE: mapping below is based on THIS run's cluster order.
# Always inspect segment_summary above before trusting these labels —
# K-Means cluster numbers (0,1,2,3) are arbitrary and can shift between runs.
segment_names = {
    0: "Regular/Casual",
    1: "Active/Loyal",
    2: "VIP",
    3: "At Risk",
}
rfm_df["Segment_Name"] = rfm_df["Segment"].map(segment_names)

print("\nSegment distribution:\n", rfm_df["Segment_Name"].value_counts())

# ============================================================
# 5. Merge segments back into the full session-level dataset
# ============================================================
final_df = df.merge(
    rfm_df[["user_id", "Recency", "Frequency", "Monetary", "Segment_Name"]],
    on="user_id",
    how="left",
)

print(f"\nFinal dataset: {final_df.shape[0]:,} rows, {final_df.shape[1]} columns")

# ============================================================
# 6. Export for Power BI
# ============================================================
final_df.to_csv("final_dashboard_data.csv", index=False)
print("Saved final_dashboard_data.csv ✅")
