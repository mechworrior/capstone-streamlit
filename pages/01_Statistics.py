import streamlit as st


st.markdown('# Statistics')

weather_inst = st.session_state.get('weather_data', None)

if weather_inst is not None:
    st.write('35℃を超えた日が何日（何％）あったか？')
    st.write(weather_inst.simple_statistics(35))
else: 
    st.write('Please upload data on main page first')