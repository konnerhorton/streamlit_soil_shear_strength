import streamlit as st
import pandas as pd
import numpy as np

# Local Libraries
from utilities.utilities import *


st.title("Shear Strength of Soils")
df = pd.DataFrame(
    {
        "Specimen Number": [1, 2],
        "Minor Principal Stress": [0, 0],
        "Major Principal Stress": [0, 0],
    }
)

edited_df = st.experimental_data_editor(df, num_rows="dynamic")

units = st.text_input("Input Stress Units", "kPa")

fig = default_mohr_circle(units)

if st.button("Calculate and plot $c$ & $\phi$"):
    if any(edited_df["Minor Principal Stress"] >= edited_df["Major Principal Stress"]):
        st.write(
            "Update data table above so that all minor principal stresses are smaller than their respective major principal stress"
        )
    else:
        circles = make_circles(
            edited_df["Major Principal Stress"], edited_df["Minor Principal Stress"]
        )
        for c in circles:
            fig.add_shape(c)

# """If minor < major plot circles. Make a function to add a circle to a figure, instead of making a whole new figure. Might be a reasonable use case for making a class etc."""
st.plotly_chart(fig)
