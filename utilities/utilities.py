from statistics import linear_regression

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# Set plotting template
pio.templates["simple_white"]["layout"]["xaxis"]["mirror"] = True
pio.templates["simple_white"]["layout"]["yaxis"]["mirror"] = True
pio.templates["simple_white"]["layout"]["xaxis"]["showgrid"] = True
pio.templates["simple_white"]["layout"]["yaxis"]["showgrid"] = True
pio.templates["simple_white"]["layout"]["xaxis"]["minor"]["showgrid"] = True
pio.templates["simple_white"]["layout"]["yaxis"]["minor"]["showgrid"] = True
pio.templates["simple_white"]["layout"]["xaxis"]["title"]["standoff"] = 0
pio.templates["simple_white"]["layout"]["yaxis"]["title"]["standoff"] = 0
pio.templates["simple_white"]["layout"]["font"]["family"] = "Arial"
pio.templates.default = "simple_white"


def get_mc_failure_envelope(minor_principal_stress: list, major_principal_stress: list):
    center = [
        (major_principal_stress[i] + minor_principal_stress[i]) / 2
        for i in range(len(major_principal_stress))
    ]
    radius = [
        (major_principal_stress[i] - minor_principal_stress[i]) / 2
        for i in range(len(major_principal_stress))
    ]
    theta_range = np.linspace(0, 90, 900)
    average_delta = []
    storehouse = {}
    for theta in theta_range:
        x = [
            center[i] - radius[i] * np.cos(np.deg2rad(theta))
            for i in range(len(center))
        ]
        y = [radius[i] * np.sin(np.deg2rad(theta)) for i in range(len(center))]
        if linear_regression(x, y)[1] < 0:
            slope, y_intercept = linear_regression(x, y, proportional=True)
        else:
            slope, y_intercept = linear_regression(x, y, proportional=False)
        average_delta.append(
            np.mean(
                [
                    radius[i]
                    - np.absolute(slope * center[i] + y_intercept)
                    / np.sqrt(slope**2 + 1)
                    for i in range(len(radius))
                ]
            )
        )
        storehouse[theta] = (slope, y_intercept)

    theta_select = theta_range[average_delta.index((min(average_delta)))]
    friction_angle = round(90 - theta_select, 1)
    cohesion = round(storehouse[theta_select][1], 0)

    return cohesion, friction_angle


def default_triaxial_plot(units="kPa", x_max=1000, y_max=500):
    return (
        go.Figure()
        .update_xaxes(range=[0, x_max], constrain="domain")
        .update_yaxes(
            range=[0, y_max],
            scaleanchor="x",
            scaleratio=1,
            constrain="domain",
        )
        .update_layout(
            margin=dict(t=40, b=20, l=20, r=20),
            xaxis=dict(title=f"Normal Stress, {units}"),
            yaxis=dict(title=f"Shear Stress, {units}"),
        )
    )


def mohr_circle_plot(sigma1s, sigma3s, units="kPa"):
    x_max = max(sigma1s) * 1.1
    y_max = x_max / 2
    print(sigma3s)
    fig = default_triaxial_plot(units=units, x_max=x_max, y_max=y_max)
    for i in zip(sigma3s, sigma1s):
        x0 = i[0]
        x1 = i[1]
        y0 = (x0 - x1) / 2
        y1 = -y0
        fig.add_shape(
            type="circle",
            xref="x",
            yref="y",
            x0=x0,
            y0=y0,
            x1=x1,
            y1=y1,
            fillcolor="rgba(0,0,0,0)",
            opacity=1,
            line=dict(
                color="black",
                width=2,
            ),
        )
    return fig


def mc_failure_envelope(c, phi, x_max):
    x = np.linspace(0, x_max)
    m = np.tan(np.deg2rad(phi))
    y = m * x + c
    return x, y


class TriaxialSampleSet:
    def __init__(self, sample_id, test_type, stress_units):
        self.id = sample_id
        self.type = test_type
        self.units = stress_units
        self.specimens = []

    def add_specimen(self, specimen):
        self.specimens.append(specimen)
        self.sigma1s = [specimen.sigma1 for specimen in self.specimens]
        self.sigma3s = [specimen.sigma3 for specimen in self.specimens]

    def plot_mc_failure_envelope(self):
        fig = mohr_circle_plot(
            sigma1s=self.sigma1s, sigma3s=self.sigma3s, units=self.units
        )
        failure_envelope = mc_failure_envelope(
            get_mc_failure_envelope(self.sigma3s, self.sigma1s)[0],
            get_mc_failure_envelope(self.sigma3s, self.sigma1s)[1],
            max([specimen.sigma1 for specimen in self.specimens]) * 1.1,
        )

        return fig.add_trace(go.Scatter(x=failure_envelope[0], y=failure_envelope[1]))

    def as_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "specimens": [s.as_dict() for s in self.specimens],
        }


class Specimen:
    def __init__(self, specimen_id, sigma1, sigma3):
        self.id = specimen_id
        self.sigma1 = sigma1
        self.sigma3 = sigma3

    def as_dict(self):
        return {"id": self.id, "sigma1": self.sigma1, "sigma3": self.sigma3}
