import streamlit as st


st.markdown('# Categorization')

weather_inst = st.session_state.get('weather_data', None)

if weather_inst is not None:
    st.write(weather_inst.categorize())
else: 
    st.write('Please upload data on main page first')