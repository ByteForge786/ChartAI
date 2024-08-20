import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def generate_chart(df, chart_recommendation):
    def fallback_chart(df):
        # Determine column types
        date_cols = df.select_dtypes(include=['datetime64']).columns
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns

        if len(date_cols) > 0 and len(numeric_cols) > 0:
            # Time series plot
            fig = make_subplots(rows=len(numeric_cols), cols=1, shared_xaxes=True, vertical_spacing=0.05)
            for i, col in enumerate(numeric_cols, 1):
                fig.add_trace(go.Scatter(x=df[date_cols[0]], y=df[col], mode='lines+markers', name=col), row=i, col=1)
                fig.update_yaxes(title_text=col, row=i, col=1)
            fig.update_layout(title_text="Time Series Plot", height=300*len(numeric_cols))
        elif len(numeric_cols) >= 2:
            # Scatter plot matrix
            fig = px.scatter_matrix(df[numeric_cols], title="Scatter Matrix Plot")
        elif len(categorical_cols) > 0 and len(numeric_cols) > 0:
            # Bar chart
            fig = px.bar(df, x=categorical_cols[0], y=numeric_cols[0], title=f"Bar Chart: {numeric_cols[0]} by {categorical_cols[0]}")
        else:
            # Fallback to table view
            st.write("Couldn't determine appropriate chart type. Displaying data in table format:")
            st.table(df)
            return None

        return fig

    try:
        if chart_recommendation is None:
            chart_type = determine_chart_type(df)
        else:
            chart_type = chart_recommendation.split('(')[0].strip().lower()

        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns

        if chart_type in ['grouped bar', 'bar']:
            if len(categorical_cols) > 0 and len(numeric_cols) > 0:
                x_column = categorical_cols[0]
                y_column = numeric_cols[0]
                
                if len(categorical_cols) > 1:
                    # Multiple categories and numeric column
                    color_column = categorical_cols[1]
                    fig = px.bar(df, x=x_column, y=y_column, 
                                 color=color_column, barmode='group',
                                 title=f"{y_column} by {x_column} and {color_column}",
                                 template="plotly_white")
                    
                    if len(categorical_cols) > 2:
                        fig.update_traces(hovertemplate='%{x}<br>%{y}<br>' + 
                                          '<br>'.join([f'{col}: %{{customdata[{i}]}}' for i, col in enumerate(categorical_cols[2:])]))
                        fig.update_traces(customdata=df[categorical_cols[2:]])
                else:
                    # Single category and numeric column
                    fig = px.bar(df, x=x_column, y=y_column,
                                 title=f"{y_column} by {x_column}",
                                 template="plotly_white")
                
                fig.update_layout(xaxis_title=x_column, yaxis_title=y_column)
            else:
                st.write("Insufficient column types for bar chart. Falling back to alternative visualization.")
                fig = fallback_chart(df)

        elif chart_type == 'line':
            if len(numeric_cols) > 0:
                if len(categorical_cols) > 0:
                    x_column = categorical_cols[0]
                else:
                    x_column = df.columns[0]
                y_columns = numeric_cols
                fig = px.line(df, x=x_column, y=y_columns,
                              title=f"{', '.join(y_columns)} over {x_column}",
                              template="plotly_white", markers=True)
                fig.update_layout(xaxis_title=x_column, yaxis_title="Values")
            else:
                st.write("No numeric columns found for line chart. Falling back to alternative visualization.")
                fig = fallback_chart(df)

        elif chart_type == 'pie':
            if len(categorical_cols) > 0 and len(numeric_cols) > 0:
                names_column = categorical_cols[0]
                values_column = numeric_cols[0]
                fig = px.pie(df, names=names_column, values=values_column,
                             title=f"Distribution of {values_column} by {names_column}",
                             template="plotly_white")
            else:
                st.write("Insufficient columns for pie chart. Falling back to alternative visualization.")
                fig = fallback_chart(df)

        elif chart_type == 'scatter':
            if len(numeric_cols) >= 2:
                x_column = numeric_cols[0]
                y_column = numeric_cols[1]
                fig = px.scatter(df, x=x_column, y=y_column,
                                 title=f"{y_column} vs {x_column}",
                                 template="plotly_white")
                fig.update_layout(xaxis_title=x_column, yaxis_title=y_column)
            else:
                st.write("Insufficient numeric columns for scatter plot. Falling back to alternative visualization.")
                fig = fallback_chart(df)

        elif chart_type == 'histogram':
            if len(numeric_cols) > 0:
                x_column = numeric_cols[0]
                fig = px.histogram(df, x=x_column,
                                   title=f"Distribution of {x_column}",
                                   template="plotly_white")
                fig.update_layout(xaxis_title=x_column, yaxis_title="Count")
            else:
                st.write("No numeric columns found for histogram. Falling back to alternative visualization.")
                fig = fallback_chart(df)

        else:
            fig = fallback_chart(df)

        if fig:
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.write(f"Error occurred while generating the recommended chart: {str(e)}")
        st.write("Falling back to alternative visualization...")
        fig = fallback_chart(df)
        if fig:
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)




elif chart_type == 'pie':
    if len(categorical_cols) > 0 and len(numeric_cols) > 0:
        names_column = categorical_cols[0]
        
        if len(numeric_cols) == 1:
            # Single numeric column
            values_column = numeric_cols[0]
            fig = px.pie(df, names=names_column, values=values_column,
                         title=f"Distribution of {values_column} by {names_column}",
                         template="plotly_white")
        else:
            # Multiple numeric columns
            fig = make_subplots(rows=len(numeric_cols), cols=1, 
                                subplot_titles=[f"Distribution of {col} by {names_column}" for col in numeric_cols])
            
            for i, values_column in enumerate(numeric_cols, start=1):
                pie_fig = px.pie(df, names=names_column, values=values_column,
                                 title=f"Distribution of {values_column} by {names_column}")
                for trace in pie_fig.traces:
                    fig.add_trace(trace, row=i, col=1)
            
            fig.update_layout(height=400*len(numeric_cols), title_text="Pie Charts for Each Numeric Column")
    else:
        st.write("Insufficient columns for pie chart. Falling back to alternative visualization.")
        fig = fallback_chart(df)




elif chart_type == 'line':
    if len(numeric_cols) > 0:
        # Identify the date column (assuming there's only one date column)
        date_cols = df.select_dtypes(include=['datetime', 'datetime64']).columns.tolist()
        
        if len(date_cols) > 0:
            x_column = date_cols[0]  # Use the date column for the x-axis
        else:
            x_column = df.columns[0]  # Fallback to the first column if no date columns are present
        
        if len(categorical_cols) > 0:
            category_column = categorical_cols[0]  # Use the categorical column for color grouping
        else:
            category_column = None  # No categorical column for grouping
        
        y_columns = numeric_cols
        
        # Create a line chart with color differentiation based on the categorical column
        if category_column:
            fig = px.line(df, x=x_column, y=y_columns, color=category_column,
                          title=f"{', '.join(y_columns)} over {x_column} grouped by {category_column}",
                          template="plotly_white", markers=True)
        else:
            fig = px.line(df, x=x_column, y=y_columns,
                          title=f"{', '.join(y_columns)} over {x_column}",
                          template="plotly_white", markers=True)
        
        # Customize layout and hover information
        fig.update_layout(
            xaxis_title=x_column,
            yaxis_title="Values",
            legend_title=category_column if category_column else "Variables",  # Legend based on category if present
            xaxis=dict(tickformat='%Y-%m-%d'),  # Custom date format for x-axis
        )
        
        # Customize each trace (line)
        for i, y_column in enumerate(y_columns):
            fig.update_traces(
                line=dict(width=2),  # Adjust line width
                marker=dict(size=8),  # Adjust marker size
                mode='lines+markers',  # Show both lines and markers
                hovertemplate=f'{x_column}: %{{x|%Y-%m-%d}}<br>{y_column}: %{{y}}<extra></extra>',
                selector=dict(name=y_column)  # Apply to the correct trace
            )
    else:
        st.write("No numeric columns found for line chart. Falling back to alternative visualization.")
        fig = fallback_chart(df)


if chart_type in ['grouped bar', 'bar']:
    if len(categorical_cols) > 0 and len(numeric_cols) > 0:
        x_column = categorical_cols[0]  # First category for x-axis
        
        if len(categorical_cols) > 1:
            # Multiple categories and numeric columns
            color_column = categorical_cols[1]  # Second category for color differentiation
            fig = go.Figure()
            
            for num_col in numeric_cols:
                fig.add_trace(go.Bar(
                    x=df[x_column],
                    y=df[num_col],
                    name=num_col,
                    customdata=df[categorical_cols[2:]] if len(categorical_cols) > 2 else None,
                    hovertemplate='%{x}<br>%{y}<br>' + 
                                  '<br>'.join([f'{col}: %{{customdata[{i}]}}' for i, col in enumerate(categorical_cols[2:])]) if len(categorical_cols) > 2 else '%{x}<br>%{y}'
                ))
            
            fig.update_layout(barmode='group',
                              title=f"Comparison of {', '.join(numeric_cols)} by {x_column} and {color_column}",
                              xaxis_title=x_column,
                              yaxis_title="Values",
                              template="plotly_white")
            
            if len(categorical_cols) > 2:
                fig.for_each_trace(lambda t: t.update(customdata=df[categorical_cols[2:]]))
        else:
            # Single category and multiple numeric columns
            fig = go.Figure()
            for num_col in numeric_cols:
                fig.add_trace(go.Bar(
                    x=df[x_column],
                    y=df[num_col],
                    name=num_col
                ))

            fig.update_layout(barmode='group',
                              title=f"Comparison of {', '.join(numeric_cols)} by {x_column}",
                              xaxis_title=x_column,
                              yaxis_title="Values",
                              template="plotly_white")
        
        fig.update_layout(xaxis_title=x_column, yaxis_title="Values")
    else:
        st.write("Insufficient column types for bar chart. Falling back to alternative visualization.")
        fig = fallback_chart(df)


