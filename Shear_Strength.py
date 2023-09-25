import streamlit as st
import pandas as pd
import numpy as np
import io

# Local Libraries
from utilities.utilities import *


st.title("Shear Strength of Soils")
st.write(
    "Input the triaxial test results in the table below. When all tests are included, click the 'Calculate and plot $c$ & $\phi$' button view see the results in the space below.\nThe plot can be downloaded as a pdf (see button below the plot)."
)
df = pd.DataFrame(
    {
        "Specimen Number": [1, 2],
        "Minor Principal Stress": [0, 0],
        "Major Principal Stress": [0, 0],
    }
)

edited_df = st.experimental_data_editor(df, num_rows="dynamic")

units = st.text_input("Input Stress Units", "kPa")

fig = default_triaxial_plot(units=units, x_max=1000, y_max=500)

if st.button("Calculate and plot $c$ & $\phi$"):
    if any(edited_df["Minor Principal Stress"] >= edited_df["Major Principal Stress"]):
        st.write(
            "Update data table above so that all minor principal stresses are smaller than their respective major principal stress"
        )
    else:
        x_max = max(edited_df["Major Principal Stress"]) * 1.1
        y_max = x_max / 2
        c, phi = get_mc_failure_envelope(
            edited_df["Minor Principal Stress"], edited_df["Major Principal Stress"]
        )
        failure_envelope = mc_failure_envelope(c, phi, x_max)
        fig = (
            mohr_circle_plot(
                edited_df["Major Principal Stress"],
                edited_df["Minor Principal Stress"],
                units="kPa",
            )
            .add_trace(go.Scatter(x=failure_envelope[0], y=failure_envelope[1]))
            .add_annotation(
                text=f"Cohesion={c}<br>Friction Angle={phi}",
                showarrow=False,
                x=x_max * 0.95,
                xanchor="right",
                y=y_max * 0.95,
                yanchor="top",
                align="right",
                font_color="black",
                bordercolor="black",
                borderpad=4,
                bgcolor="#FFFFFF",
            )
        )

st.plotly_chart(fig)

# Create an in-memory buffer
buffer = io.BytesIO()

# Save the figure as a pdf to the buffer
fig.write_image(file=buffer, format="pdf")

# Download the pdf from the buffer
st.download_button(
    label="Download PDF",
    data=buffer,
    file_name="MohrCricleWithFailureEnvelope.pdf",
    mime="application/pdf",
)
