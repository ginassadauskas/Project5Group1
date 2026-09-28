import streamlit as st
st.write("This is the dashboard page.")

st.download_button(label="Download Data", data="sample_people_colors.csv", file_name="data.csv", mime="text/csv")