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


def default_mohr_circle(units):
    x_max = 1000
    y_max = (x_max / 2) * 1.1
    fig = go.Figure()

    fig.update_xaxes(range=[0, x_max], constrain="domain")
    fig.update_yaxes(
        range=[0, y_max],
        scaleanchor="x",
        scaleratio=1,
        constrain="domain",
    )
    fig.update_layout(
        margin=dict(t=40, b=20, l=20, r=20),
        xaxis=dict(title=f"Normal Stress, {units}"),
        yaxis=dict(title=f"Shear Stress, {units}"),
    )
    return fig


def make_circles(minor, major):
    circles = []
    for i in zip(minor, major):
        circles.append(
            {
                "type": "circle",
                "xref": "x",
                "yref": "y",
                "x0": i[0],
                "y0": (i[0] - i[1]) / 2,
                "x1": i[1],
                "y1": -(i[0] - i[1]) / 2,
                "line": {"color": "black", "width": 2},
                "fillcolor": "rgba(0,0,0,0)",
                "opacity": 1,
            }
        )
    return circles


def draw_circles(minor_principal_stress, major_principal_stress):
    x_max = max(major) * 1.1
    y_max = (max(major) - minor[major.index(max(major))]) / 1.5

    # def sp_points(minor, major):
    #     minor = np.array(minor)
    #     major = np.array(major)
    #     q = (major - minor) / 2
    #     p = (major + minor) / 2
    #     return list(q), list(p)

    # fig = go.Figure(
    #     go.Scatter(
    #         x=sp_points(minor, major)[1], y=sp_points(minor, major)[0], mode="markers"
    #     )
    # )
    fig = default_mohr_circle()

    for c in make_circles(minor, major):
        fig.add_shape(c)

    # fig.update_xaxes(
    #     title=dict(text="Normal Stress or p', kPa", font_color="black", standoff=0),
    #     range=[0, x_max],
    #     constrain="domain",
    #     showgrid=True,
    #     linecolor="black",
    #     gridcolor="lightgray",
    #     mirror=True,
    #     minor=dict(gridcolor="lightgray", showgrid=True),
    # ).update_yaxes(
    #     title=dict(text="Shear Stress or q, kPa", font_color="black", standoff=0),
    #     range=[0, y_max],
    #     mirror=True,
    #     linecolor="black",
    #     gridcolor="lightgray",
    #     minor=dict(gridcolor="lightgray", showgrid=True),
    #     scaleanchor="x",
    #     scaleratio=1,
    #     constrain="domain",
    # ).update_layout(
    #     plot_bgcolor="white"
    # )
    return fig


def get_shear_strength_mohr_circle(
    minor_principal_stress: list, major_principal_stress: list
):
    """
    Parameters
    ----------

    Returns
    -------

    Notes
    -----

    Reference
    ---------

    """
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
