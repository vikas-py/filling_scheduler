"""
Chart Generation Module

Generates chart images using Plotly for embedding in PDF reports.
"""

import base64
from typing import Any

import plotly.graph_objects as go
from plotly.io import to_image


def generate_gantt_chart_image(
    activities: list[dict[str, Any]],
    num_fillers: int,
    makespan: float,
    width: int = 1200,
    height: int = 600,
) -> str:
    """
    Generate a Gantt chart as a base64-encoded PNG image.

    Args:
        activities: List of activity dictionaries with keys:
            - filler_id: int
            - lot_id: str
            - start_time: float
            - end_time: float
            - duration: float
            - kind: str (optional) - 'FILL', 'CLEAN', 'CHANGEOVER'
        num_fillers: Number of fillers
        makespan: Total schedule time
        width: Image width in pixels
        height: Image height in pixels

    Returns:
        Base64-encoded PNG image string
    """
    # Color scheme for activity types
    color_map = {
        "FILL": "#1976d2",  # Blue
        "CLEAN": "#ff9800",  # Orange
        "CHANGEOVER": "#f44336",  # Red
    }

    fig = go.Figure()

    # Group activities by filler
    for filler_id in range(1, num_fillers + 1):
        filler_activities = [a for a in activities if a["filler_id"] == filler_id]

        for activity in filler_activities:
            activity_kind = activity.get("kind", "FILL")
            color = color_map.get(activity_kind, "#757575")

            fig.add_trace(
                go.Bar(
                    name=f"Filler {filler_id}",
                    y=[f"Filler {filler_id}"],
                    x=[activity["duration"]],
                    base=[activity["start_time"]],
                    orientation="h",
                    marker={"color": color, "line": {"color": "#333", "width": 1}},
                    hovertemplate=(
                        f"<b>{activity['lot_id']}</b><br>"
                        f"Type: {activity_kind}<br>"
                        f"Start: {activity['start_time']:.1f}h<br>"
                        f"End: {activity['end_time']:.1f}h<br>"
                        f"Duration: {activity['duration']:.1f}h<br>"
                        "<extra></extra>"
                    ),
                    showlegend=False,
                )
            )

    # Update layout
    fig.update_layout(
        title={
            "text": "Schedule Timeline",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 20, "family": "Arial, sans-serif"},
        },
        xaxis={
            "title": "Time (hours)",
            "range": [0, makespan * 1.05],  # Add 5% padding
            "showgrid": True,
            "gridcolor": "#e0e0e0",
            "gridwidth": 1,
        },
        yaxis={
            "title": "Resources",
            "autorange": "reversed",
            "showgrid": True,
            "gridcolor": "#e0e0e0",
            "gridwidth": 1,
        },
        barmode="overlay",
        height=height,
        width=width,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin={"l": 100, "r": 50, "t": 80, "b": 80},
    )

    # Export to PNG and encode as base64
    try:
        img_bytes = to_image(fig, format="png", width=width, height=height, scale=2)
        return base64.b64encode(img_bytes).decode("utf-8")
    except Exception as e:
        print(f"Warning: Failed to generate Gantt chart image: {e}")
        return ""


def generate_utilization_chart_image(
    activities: list[dict[str, Any]],
    num_fillers: int,
    makespan: float,
    width: int = 1000,
    height: int = 400,
) -> str:
    """
    Generate a resource utilization chart showing filler usage over time.

    Args:
        activities: List of activity dictionaries
        num_fillers: Number of fillers
        makespan: Total schedule time
        width: Image width in pixels
        height: Image height in pixels

    Returns:
        Base64-encoded PNG image string
    """
    # Calculate utilization by hour
    hours = int(makespan) + 1
    utilization_by_hour = {
        "hour": list(range(hours)),
        "filling": [0] * hours,
        "cleaning": [0] * hours,
        "changeover": [0] * hours,
    }

    for activity in activities:
        start_hour = int(activity["start_time"])
        end_hour = min(int(activity["end_time"]) + 1, hours)
        activity_kind = activity.get("kind", "FILL").lower()

        for hour in range(start_hour, end_hour):
            if activity_kind == "fill":
                utilization_by_hour["filling"][hour] += 1
            elif activity_kind == "clean":
                utilization_by_hour["cleaning"][hour] += 1
            elif activity_kind == "changeover":
                utilization_by_hour["changeover"][hour] += 1

    fig = go.Figure()

    # Add stacked area traces
    fig.add_trace(
        go.Scatter(
            x=utilization_by_hour["hour"],
            y=utilization_by_hour["filling"],
            mode="lines",
            name="Filling",
            fill="tozeroy",
            line={"color": "#1976d2", "width": 0},
            fillcolor="rgba(25, 118, 210, 0.7)",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=utilization_by_hour["hour"],
            y=[
                f + c
                for f, c in zip(
                    utilization_by_hour["filling"], utilization_by_hour["cleaning"], strict=False
                )
            ],
            mode="lines",
            name="Cleaning",
            fill="tonexty",
            line={"color": "#ff9800", "width": 0},
            fillcolor="rgba(255, 152, 0, 0.7)",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=utilization_by_hour["hour"],
            y=[
                f + c + ch
                for f, c, ch in zip(
                    utilization_by_hour["filling"],
                    utilization_by_hour["cleaning"],
                    utilization_by_hour["changeover"],
                    strict=False,
                )
            ],
            mode="lines",
            name="Changeover",
            fill="tonexty",
            line={"color": "#f44336", "width": 0},
            fillcolor="rgba(244, 67, 54, 0.7)",
        )
    )

    fig.update_layout(
        title={
            "text": "Resource Utilization Over Time",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 18, "family": "Arial, sans-serif"},
        },
        xaxis={
            "title": "Time (hours)",
            "showgrid": True,
            "gridcolor": "#e0e0e0",
        },
        yaxis={
            "title": "Active Fillers",
            "showgrid": True,
            "gridcolor": "#e0e0e0",
            "rangemode": "tozero",
        },
        hovermode="x unified",
        height=height,
        width=width,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin={"l": 80, "r": 50, "t": 80, "b": 80},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
    )

    # Export to PNG and encode as base64
    try:
        img_bytes = to_image(fig, format="png", width=width, height=height, scale=2)
        return base64.b64encode(img_bytes).decode("utf-8")
    except Exception as e:
        print(f"Warning: Failed to generate utilization chart image: {e}")
        return ""


def generate_activity_distribution_chart(
    activities: list[dict[str, Any]],
    width: int = 600,
    height: int = 400,
) -> str:
    """
    Generate a pie chart showing the distribution of activity types.

    Args:
        activities: List of activity dictionaries
        width: Image width in pixels
        height: Image height in pixels

    Returns:
        Base64-encoded PNG image string
    """
    # Count activities by type
    activity_counts = {"FILL": 0, "CLEAN": 0, "CHANGEOVER": 0}

    for activity in activities:
        activity_kind = activity.get("kind", "FILL")
        if activity_kind in activity_counts:
            activity_counts[activity_kind] += 1

    # Filter out zero counts
    labels = [k for k, v in activity_counts.items() if v > 0]
    values = [v for v in activity_counts.values() if v > 0]
    colors = ["#1976d2", "#ff9800", "#f44336"][: len(labels)]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                marker={"colors": colors, "line": {"color": "#fff", "width": 2}},
                textinfo="label+percent",
                textfont={"size": 14, "family": "Arial, sans-serif"},
                hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title={
            "text": "Activity Distribution",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 18, "family": "Arial, sans-serif"},
        },
        height=height,
        width=width,
        paper_bgcolor="white",
        margin={"l": 20, "r": 20, "t": 80, "b": 20},
        showlegend=True,
        legend={"orientation": "v", "yanchor": "middle", "y": 0.5, "xanchor": "left", "x": 1.05},
    )

    # Export to PNG and encode as base64
    try:
        img_bytes = to_image(fig, format="png", width=width, height=height, scale=2)
        return base64.b64encode(img_bytes).decode("utf-8")
    except Exception as e:
        print(f"Warning: Failed to generate activity distribution chart: {e}")
        return ""


def generate_filler_breakdown_data(
    activities: list[dict[str, Any]], num_fillers: int
) -> list[dict[str, Any]]:
    """
    Calculate per-filler statistics for reporting.

    Args:
        activities: List of activity dictionaries
        num_fillers: Number of fillers

    Returns:
        List of filler statistics dictionaries
    """
    filler_stats = []

    for filler_id in range(1, num_fillers + 1):
        filler_activities = [a for a in activities if a["filler_id"] == filler_id]

        if not filler_activities:
            continue

        total_time = sum(a["duration"] for a in filler_activities)
        fill_count = sum(1 for a in filler_activities if a.get("kind") == "FILL")
        clean_count = sum(1 for a in filler_activities if a.get("kind") == "CLEAN")
        changeover_count = sum(1 for a in filler_activities if a.get("kind") == "CHANGEOVER")

        filler_stats.append(
            {
                "filler_id": filler_id,
                "total_activities": len(filler_activities),
                "total_time": total_time,
                "fill_count": fill_count,
                "clean_count": clean_count,
                "changeover_count": changeover_count,
                "lots_processed": len(
                    {a["lot_id"] for a in filler_activities if a.get("kind") == "FILL"}
                ),
            }
        )

    return filler_stats
