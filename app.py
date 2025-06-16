import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# Normalize helper
def normalize(text):
    text = str(text).lower().strip()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text

# UI
st.title("🔎 Retailer Brand Matcher")

st.markdown("Upload your Faire brand list and enter a retailer website URL to see which brands are carried by the retailer and also available on Faire.")

# File and URL inputs
brand_file = st.file_uploader("📤 Upload your Faire brand list (CSV)", type=["csv"])
retailer_url = st.text_input("🌐 Retailer Website URL (e.g. https://example.com/brands)")

if brand_file and retailer_url:
    if st.button("🔍 Match Brands"):
        # Load Faire brand list
        brand_df = pd.read_csv(brand_file)
        if "Account Name" not in brand_df.columns:
            st.error("CSV must contain 'Account Name' column.")
            st.stop()

        faire_data = {}
        for _, row in brand_df.iterrows():
            name = row["Account Name"]
            key = normalize(name)
            faire_data[key] = {
                "Brand Name": name,
                "Token": row.get("Token", ""),
                "C1 Category": row.get("C1 Brand Category", ""),
                "C2 Category": row.get("C2 Brand Subcategory", "")
            }

        faire_keys = set(faire_data.keys())
        st.success(f"✅ Loaded {len(faire_keys)} Faire brands")

        # Scrape retailer website
        try:
            st.info("Scraping retailer site...")
            response = requests.get(retailer_url, timeout=15)
            soup = BeautifulSoup(response.text, "lxml")
            visible_text = [t.strip() for t in soup.stripped_strings if t.strip()]
            retailer_text = set(normalize(t) for t in visible_text)

            st.success(f"🔍 Extracted {len(retailer_text)} text elements from the page.")
        except Exception as e:
            st.error(f"Failed to load or parse the retailer site: {e}")
            st.stop()

        # Exact match
        matches = sorted(faire_keys.intersection(retailer_text))

        if matches:
            match_data = []
            for match in matches:
                data = faire_data[match]
                match_data.append(data)

            results_df = pd.DataFrame(match_data)
            st.success(f"✅ Found {len(results_df)} brand matches!")
            st.dataframe(results_df)

            csv = results_df.to_csv(index=False)
            st.download_button("📥 Download Matches as CSV", csv, file_name="matched_brands_from_retailer.csv", mime="text/csv")
        else:
            st.warning("❌ No matches found on the page.")
