import streamlit as st

import numpy as np
import pandas as pd

st.markdown("""# This is a header
## This is for all the githubbers!! woot
This is text""")

checked = st.checkbox("click me")

if checked:
    st.markdown(
        """
        You clicked me!! hello, I am loving this!!

        """
    )

df = pd.DataFrame({
    'first column': list(range(1, 11)),
    'second column': np.arange(10, 101, 10)
})

# this slider allows the user to select a number of lines
# to display in the dataframe
# the selected value is returned by st.slider
line_count = st.slider('Select a line count', 1, 10, 3)

# and used to select the displayed lines
head_df = df.head(line_count)

head_df