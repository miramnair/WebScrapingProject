import streamlit as st
import requests
import json

st.title("Search Home Page")
st.write("Welcome to my Streamlit app")

prompt = st.text_input("Enter your keyword:")
if st.button("Search"):
    api_url = "https://s7riv05n85.execute-api.us-east-1.amazonaws.com/"
    response = requests.post(api_url, json={"prompt": prompt})

    if response.status_code == 200:
        results = response.json()
        st.write("### **Search Results**")
        for match in results:
                st.write("**Match:**", match["tour_name"])
                st.write("**Date:**", match["match_date"])
                st.write("**Status:**", match["event_status"])
                st.write("**Score:**", match["winning_margin"])
                st.write("---")
        else:
                st.write("Error in fetching results")

