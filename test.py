"""
Sample class
Specimen class
FailureEnvelope class
"""

import numpy as np
from statistics import linear_regression


class TriaxialSampleSet:
    def __init__(self, sample_id, test_type, stress_units):
        self.id = sample_id
        self.type = test_type
        self.units = stress_units
        self.specimens = []

    def add_specimen(self, specimen):
        self.specimens.append(specimen)

    def get_failure_envelope(self):
        # if len(self.specimens) <= 1:
        #     print("At least two specimens are required.")
        #     return None
        # else:
        #     sigma1s = [s.sigma1 for s in self.specimens]
        #     sigma3s = [s.sigma3 for s in self.specimens]

        #     circle_centers = [
        #         (sigma1s[i] + sigma3s[i]) / 2 for i in range(len(sigma1s))
        #     ]

        #     circle_radii = [(sigma1s[i] - sigma3s[i]) / 2 for i in range(len(sigma1s))]

        #     theta_range = np.linspace(0, 90, 900)
        #     average_delta = []
        #     storehouse = {}
        #     for theta in theta_range:
        #         x = [
        #             circle_centers[i] - circle_radii[i] * np.cos(np.deg2rad(theta))
        #             for i in range(len(circle_centers))
        #         ]
        #         y = [
        #             circle_radii[i] * np.sin(np.deg2rad(theta))
        #             for i in range(len(circle_centers))
        #         ]

        #         if linear_regression(x, y)[1] < 0:
        #             slope, y_intercept = linear_regression(x, y, proportional=True)
        #         else:
        #             slope, y_intercept = linear_regression(x, y, proportional=False)

        #         # Calculate difference between radius and distance to the drawn line
        #         def delta(circle_radius, circle_center, slope, y_intercept):
        #             return (
        #                 circle_radius - np.absolute(slope * circle_center + y_intercept)
        #             ) / np.sqrt(slope**2 + 1)

        #         average_delta.append(
        #             np.mean(
        #                 [
        #                     delta(
        #                         circle_radii[i], circle_centers[i], slope, y_intercept
        #                     )
        #                     for i in range(len(circle_radii))
        #                 ]
        #             )
        #         )
        #         storehouse[theta] = (slope, y_intercept)

        #     theta_select = theta_range[average_delta.index((min(average_delta)))]
        #     friction_angle = round(90 - theta_select, 1)
        #     cohesion = round(storehouse[theta_select][1], 0)

        #     # return cohesion, friction_angle
        #     return average_delta
        return 0, 30

        # def

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
        self.circle = {
            "x0": self.sigma3,
            "y0": (self.sigma3 - self.sigma1) / 2,
            "x1": self.sigma1,
            "y1": -(self.sigma3 - self.sigma1) / 2,
        }

    def as_dict(self):
        return {"id": self.id, "sigma1": self.sigma1, "sigma3": self.sigma3}


class MohrPlot:
    def __init__(self, units="kPa", x_max=1000, y_max=500):
        self.units = units
        self.x_max = x_max
        self.y_max = y_max
        self.plot = (
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
                xaxis=dict(title=f"Normal Stress, {self.units}"),
                yaxis=dict(title=f"Shear Stress, {self.units}"),
            )
        )

    def add_circle(self, specimen):
        coordinates = specimen.circle
        self.plot.add_shape(
            coordinates,
            type="circle",
            xref="x",
            yref="y",
            line=dict(color="black", width=2),
            fillcolor="rgba(0,0,0,0)",
            opacity=1,
        )

    def add_failure_envelope(self, cohesion, friction_angle):
        x = np.linspace(0, self.x_max)
        slope = np.tan(np.deg2rad(friction_angle))
        y_int = cohesion
        y = slope * x + y_int
        self.plot.add_trace(go.Scatter(x=x, y=y, mode="lines"))

    def show(self):
        self.plot.show()


# sampleset = TriaxialSampleSet("one", "CU", "kPa")

# sampleset.add_specimen(Specimen("a", 300, 400))
# sampleset.add_specimen(Specimen("b", 500, 700))
# sampleset.specimens[0].as_dict()
# sampleset.get_failure_envelope()

# fig = MohrPlot()

# # fig.add_shape(
# #     sampleset.specimens[0].circle,
# #     type="circle",
# # )
# fig.add_circle(sampleset.specimens[0].circle)
# fig.add_circle(sampleset.specimens[1].circle)
# fig.add_failure_envelope(0, 10)
# fig.plot

samples = {"A": (150, 550), "B": (300, 712), "C": (600, 1793)}

sample_set = TriaxialSampleSet("MDS", "CU", "kPa")


for k, v in samples.items():
    sample_set.add_specimen(Specimen(k, v[0], v[1]))

sample_set.as_dict()

plot = MohrPlot()
for specimen in sample_set.specimens:
    plot.add_circle(specimen)

plot.show()
