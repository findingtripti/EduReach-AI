"""EduReach AI - interactive village map (folium).

Markers use [latitude, longitude] order. Distances shown in popups are
straight-line (haversine) proxies between village-level coordinates, not
road distance or travel time.
"""
from html import escape

import folium
import pandas as pd

STATUS_COLORS = {
    "Potential Gap": "red",
    "Moderate": "orange",
    "Higher": "green",
}


def _popup_html(row) -> str:
    distance = row["Nearest_School_Distance_km"]
    distance_text = f"{distance:.2f} km" if pd.notna(distance) else "N/A"
    school = "Yes" if row["Has_School"] == 1 else "No"
    return (
        '<div style="font-family:Arial,sans-serif;font-size:13px;min-width:220px;">'
        f'<div style="font-size:15px;font-weight:700;">{escape(str(row["Village"]))}</div><hr>'
        f'<b>Accessibility Index:</b> {float(row["Accessibility_Index"]):.2f}<br>'
        f'<b>Status:</b> {escape(str(row["Dashboard_Status"]))}<br>'
        f'<b>Nearest School Distance:</b> {distance_text}<br>'
        f'<b>Local School Record:</b> {school}<br>'
        f'<b>School Count:</b> {int(row["School_Count"])}<br>'
        f'<b>ML Pattern:</b> {escape(str(row["ML_Pattern"]))}<br><br>'
        '<span style="color:#64748b;font-size:11px;">Distance is a straight-line '
        "proxy between village-level coordinates.</span></div>"
    )


def _legend_html(statuses) -> str:
    items = {
        "Potential Gap": ("#dc2626", "Potential Gap (index &lt; 40)"),
        "Moderate": ("#f59e0b", "Moderate (40 to &lt; 70)"),
        "Higher": ("#16a34a", "Higher (index &ge; 70)"),
    }
    rows = "".join(
        f'<div><span style="display:inline-block;width:10px;height:10px;border-radius:50%;'
        f'background:{items[s][0]};margin-right:6px;"></span>{items[s][1]}</div>'
        for s in ["Potential Gap", "Moderate", "Higher"] if s in statuses
    )
    return (
        '<div style="position:fixed;bottom:25px;left:25px;z-index:9999;background:#fff;'
        'padding:10px 14px;border:1px solid #cbd5e1;border-radius:10px;font-size:12px;'
        'font-family:Arial,sans-serif;color:#0f172a;box-shadow:0 2px 8px rgba(0,0,0,.15);">'
        '<div style="font-weight:700;margin-bottom:4px;">Accessibility</div>'
        f"{rows}</div>"
    )


def build_village_map(df: pd.DataFrame, dark: bool = False) -> folium.Map:
    """Build a map with one circle marker per village in df.

    A light (OpenStreetMap) and a dark (darkened OpenStreetMap) base map are both
    offered through a layer control; `dark` only chooses which one starts visible.
    """
    if df.empty:
        raise ValueError("Cannot build a map from an empty selection.")
    min_lat, max_lat = df["Latitude"].min(), df["Latitude"].max()
    min_lon, max_lon = df["Longitude"].min(), df["Longitude"].max()
    m = folium.Map(
        location=[(min_lat + max_lat) / 2, (min_lon + max_lon) / 2],
        zoom_start=10, tiles=None, control_scale=True,
    )
    folium.TileLayer("OpenStreetMap", name="Light map", show=not dark).add_to(m)
    # Dark base map: the same OpenStreetMap tiles, darkened with a CSS filter.
    # (No third-party tile provider or API key is needed.)
    folium.TileLayer(
        tiles="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr="&copy; OpenStreetMap contributors",
        name="Dark map", show=dark, className="er-dark-tiles", max_zoom=19,
    ).add_to(m)
    m.get_root().header.add_child(folium.Element(
        "<style>.er-dark-tiles{filter:invert(1) hue-rotate(180deg) brightness(0.92) contrast(0.88);}</style>"
    ))
    for _, row in df.iterrows():
        color = STATUS_COLORS.get(row["Dashboard_Status"], "gray")
        folium.CircleMarker(
            location=[float(row["Latitude"]), float(row["Longitude"])],
            radius=6,
            popup=folium.Popup(_popup_html(row), max_width=320),
            tooltip=f"{row['Village']} - Accessibility: {float(row['Accessibility_Index']):.1f}",
            color=color, fill=True, fill_color=color, fill_opacity=0.78, weight=1.5,
        ).add_to(m)
    m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])
    folium.LayerControl(collapsed=True, position="topright").add_to(m)
    m.get_root().html.add_child(folium.Element(_legend_html(set(df["Dashboard_Status"]))))
    return m
