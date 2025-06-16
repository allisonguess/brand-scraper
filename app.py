import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Brand Scraper", layout="wide")

st.title("🛍️ Brand Page Scraper")

url = st.text_input("Enter a brand website URL:")

if url:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for bad responses

        soup = BeautifulSoup(response.text, "html.parser")

        # Example extractions
        title = soup.title.string if soup.title else "No title found"
        headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2"])]

        st.subheader("📄 Page Title")
        st.write(title)

        st.subheader("🔍 Headings Found")
        st.write(headings if headings else "No headings found.")

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching the URL: {e}")
