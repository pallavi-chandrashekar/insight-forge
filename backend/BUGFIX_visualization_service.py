# FIX for visualization_service.py
# The issue is that labels dict can have None values which Plotly doesn't handle well

# ORIGINAL CODE (lines 22-37):
"""
    x_col = config.get("x_column")
    y_col = config.get("y_column")
    color_col = config.get("color_column")
    title = config.get("title", "")
    x_label = config.get("x_label", x_col)
    y_label = config.get("y_label", y_col)

    if chart_type == ChartType.BAR:
        fig = px.bar(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            title=title,
            labels={x_col: x_label, y_col: y_label},
        )
"""

# FIXED CODE:
"""
    x_col = config.get("x_column")
    y_col = config.get("y_column")
    color_col = config.get("color_column")
    title = config.get("title", "")
    x_label = config.get("x_label", x_col)
    y_label = config.get("y_label", y_col)

    # Build labels dict, excluding None values
    labels = {}
    if x_col and x_label:
        labels[x_col] = x_label
    if y_col and y_label:
        labels[y_col] = y_label

    if chart_type == ChartType.BAR:
        fig = px.bar(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            title=title,
            labels=labels if labels else None,
        )
"""

print("Apply this fix to app/services/visualization_service.py")
print("Change: Build labels dict dynamically, excluding None values")
print("This prevents Plotly from trying to concatenate None with strings")
