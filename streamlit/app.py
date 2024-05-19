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
        for tournament, matches in results.items():
            st.write(f"### **{tournament}**")
            for match in matches:
                st.write("**Match:**", match["Match"])
                st.write("**Date:**", match["Date"])
                st.write("**Status:**", match["Status"])
                st.write("**Score:**", match["Score"])
                st.write("---")
            else:
                st.write("Error in fetching results")

