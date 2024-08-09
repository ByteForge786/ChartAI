import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def generate_chart(df, chart_recommendation):
    def fallback_chart(df):
        # ... (keep the existing fallback_chart function as is)
        pass

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
            # ... (keep existing code for grouped bar chart)
            pass

        elif chart_type == 'bar':
            # ... (keep existing code for bar chart)
            pass

        elif chart_type == 'line':
            # ... (keep existing code for line chart)
            pass

        elif chart_type == 'pie':
            # ... (keep existing code for pie chart)
            pass

        elif chart_type == 'scatter':
            # ... (keep existing code for scatter chart)
            pass

        elif chart_type == 'histogram':
            # ... (keep existing code for histogram)
            pass

        elif chart_type == 'heatmap':
            if len(group_columns) < 2 or len(y_columns) < 1:
                st.write("Heatmap requires at least two grouping columns and one numeric column.")
                return None

            heatmap_data = df.pivot(index=group_columns[0], columns=group_columns[1], values=y_columns[0])
            
            fig = px.imshow(heatmap_data,
                            labels=dict(x=group_columns[1], y=group_columns[0], color=y_columns[0]),
                            title=f"Heatmap of {y_columns[0]} by {group_columns[0]} and {group_columns[1]}",
                            template="plotly_white")
            
            fig.update_xaxes(side="top")
            fig.update_layout(
                xaxis_title=group_columns[1],
                yaxis_title=group_columns[0],
                coloraxis_colorbar_title=y_columns[0]
            )

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
