import streamlit as st

st.markdown('# Visualization')


weather_inst = st.session_state.get('weather_data', None)
years = st.session_state.get('years', [])

if weather_inst is not None:
    if len(years) == 1:
        st.write('Need at least 2 years of data.')
    else:
        if years:
            st.write(f'data from {years[-1]} compared to previous {years[-1]-years[0]} year(s)')
        st.pyplot(weather_inst.visualize())
else: 
    st.write('Please upload data on main page first')