elif chart_type == 'grouped bar':
    # Identify numeric columns for y-axis
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    
    # Use all non-numeric columns as grouping columns
    group_columns = [col for col in df.columns if col not in numeric_cols]
    
    if len(group_columns) == 0 or len(numeric_cols) == 0:
        st.write("Not enough appropriate columns for a grouped bar chart. Displaying data in table format:")
        st.table(df)
        return None
    
    # Perform grouping operation
    grouped_df = df.groupby(group_columns)[numeric_cols].sum().reset_index()
    
    # Create the grouped bar chart
    fig = px.bar(grouped_df, 
                 x=group_columns[0],  # First grouping column on x-axis
                 y=numeric_cols[0],   # First numeric column for bar height
                 color=group_columns[1] if len(group_columns) > 1 else None,  # Second grouping column for color
                 barmode='group',
                 title=f"Grouped Bar Chart: {numeric_cols[0]} by {', '.join(group_columns)}",
                 template="plotly_white")
    
    # Add facets if there are more than 2 grouping columns
    if len(group_columns) > 2:
        fig.update_layout(
            facet_col=group_columns[2],
            facet_col_wrap=min(3, len(set(grouped_df[group_columns[2]])))  # Wrap after 3 columns
        )
    
    fig.update_layout(
        xaxis_title=group_columns[0],
        yaxis_title=numeric_cols[0],
        legend_title=group_columns[1] if len(group_columns) > 1 else None
    )
