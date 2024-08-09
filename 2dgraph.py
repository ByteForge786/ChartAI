import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

        x_column = df.columns[0]
        y_columns = df.columns[1:]

        # Add support for multiple grouping columns
        group_columns = df.columns[:-1] if len(df.columns) > 2 else [x_column]

        if chart_type == 'grouped bar':
            fig = px.bar(df, x=group_columns, y=y_columns, 
                         title=f"{', '.join(y_columns)} by {', '.join(group_columns)}",
                         template="plotly_white", barmode='group')
            fig.update_layout(xaxis_title=', '.join(group_columns), yaxis_title="Values")

        elif chart_type == 'bar':
            fig = px.bar(df, x=group_columns, y=y_columns[0],
                         title=f"{y_columns[0]} by {', '.join(group_columns)}",
                         template="plotly_white")
            fig.update_layout(xaxis_title=', '.join(group_columns), yaxis_title=y_columns[0])

        elif chart_type == 'line':
            fig = px.line(df, x=x_column, y=y_columns,
                          color=group_columns[-1] if len(group_columns) > 1 else None,
                          title=f"{', '.join(y_columns)} over {', '.join(group_columns)}",
                          template="plotly_white", markers=True)
            fig.update_layout(xaxis_title=x_column, yaxis_title="Values")

        elif chart_type == 'pie':
            if len(group_columns) > 1:
                fig = px.sunburst(df, path=group_columns, values=y_columns[0],
                                  title=f"Distribution of {y_columns[0]} by {', '.join(group_columns)}",
                                  template="plotly_white")
            else:
                fig = px.pie(df, names=x_column, values=y_columns[0],
                             title=f"Distribution of {y_columns[0]} by {x_column}",
                             template="plotly_white")

        elif chart_type == 'scatter':
            fig = px.scatter(df, x=x_column, y=y_columns[0],
                             color=group_columns[-1] if len(group_columns) > 1 else None,
                             title=f"{y_columns[0]} vs {x_column}",
                             template="plotly_white")
            fig.update_layout(xaxis_title=x_column, yaxis_title=y_columns[0])

        elif chart_type == 'histogram':
            fig = px.histogram(df, x=x_column,
                               color=group_columns[-1] if len(group_columns) > 1 else None,
                               title=f"Distribution of {x_column}",
                               template="plotly_white")
            fig.update_layout(xaxis_title=x_column, yaxis_title="Count")

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
