import streamlit as st
import pandas as pd
st.write("Hello World")
x = st.text_input("Favorite color?")
st.write(f"Your favorite color is {x}")
is_clicked = st.button("Click if you are awesome")
st.write("## Don't ask questions you can't answer")

data = pd.read_csv("sample_people_colors.csv")
st.write(data)

st.bar_chart(data, x="Name", y="Favorite Color")
st.line_chart(data, x="Name", y="Favorite Color")   