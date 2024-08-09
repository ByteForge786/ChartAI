elif chart_type == 'heatmap':
    # Ensure we have at least two numeric columns for x and y
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    if len(numeric_cols) < 2:
        st.write("Not enough numeric columns for a heatmap. Displaying data in table format:")
        st.table(df)
        return None
    
    x_column = numeric_cols[0]
    y_column = numeric_cols[1]
    
    # If we have a third numeric column, use it for color intensity
    z_column = numeric_cols[2] if len(numeric_cols) > 2 else None
    
    if z_column:
        fig = px.density_heatmap(df, x=x_column, y=y_column, z=z_column,
                                 title=f"Heatmap of {z_column} by {x_column} and {y_column}",
                                 template="plotly_white")
    else:
        fig = px.density_heatmap(df, x=x_column, y=y_column,
                                 title=f"Heatmap of {y_column} vs {x_column}",
                                 template="plotly_white")
    
    fig.update_layout(xaxis_title=x_column, yaxis_title=y_column)
