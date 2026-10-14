"""EduReach AI - small, theme-safe Altair bar charts.

Bars use one mid-blue that reads well on light and dark backgrounds. Axis text
comes from Streamlit's own chart theme, so it follows the active theme. The
value is written into each category label (for example "Baseline: 67.25")
instead of being drawn on top of the bars.
"""
import altair as alt
import pandas as pd

BAR_COLOR = "#3b82f6"


def labelled_bar_chart(labels, values, x_title, y_title, y_max,
                       value_format=".2f", height=320, horizontal=False):
    """Bar chart with a fixed 0..y_max value axis (never negative, never clipped).

    x_title names the categories and y_title names the values, in both the
    vertical and the horizontal layout.
    """
    values = [float(v) for v in values]
    data = pd.DataFrame({
        "label": [f"{lab}: {val:{value_format}}" for lab, val in zip(labels, values)],
        "name": [str(lab) for lab in labels],
        "value": values,
    })
    tooltip = [alt.Tooltip("name:N", title=x_title),
               alt.Tooltip("value:Q", title=y_title, format=value_format)]
    value_scale = alt.Scale(domain=[0, y_max], nice=False)
    if horizontal:
        chart = alt.Chart(data).mark_bar(color=BAR_COLOR, size=30).encode(
            y=alt.Y("label:N", sort=None, title=x_title, axis=alt.Axis(labelLimit=320)),
            x=alt.X("value:Q", title=y_title, scale=value_scale),
            tooltip=tooltip,
        )
        return chart.properties(height=max(110, 52 * len(data) + 60))
    chart = alt.Chart(data).mark_bar(color=BAR_COLOR, size=90).encode(
        x=alt.X("label:N", sort=None, title=x_title,
                axis=alt.Axis(labelAngle=0, labelLimit=320)),
        y=alt.Y("value:Q", title=y_title, scale=value_scale),
        tooltip=tooltip,
    )
    return chart.properties(height=height)
