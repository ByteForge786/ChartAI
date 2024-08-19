import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st



def generate_chart(df, chart_recommendation, chart_placeholder):
    # ... (previous code remains the same)

    try:
        # ... (previous code remains the same)

        if fig:
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")
            chart_placeholder.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        chart_placeholder.write(f"Error occurred while generating the recommended chart: {str(e)}")
        chart_placeholder.write("Falling back to alternative visualizations...")
        charts = create_multiple_charts(df)
        for fig in charts:
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")
            chart_placeholder.plotly_chart(fig, use_container_width=True)
            chart_placeholder.markdown("---")  # Add a separator between charts

def generate_chart(df, chart_recommendation):
    def analyze_df(df):
        date_cols = df.select_dtypes(include=['datetime64']).columns
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        return date_cols, numeric_cols, categorical_cols

    def multi_category_bar_chart(df, cat_cols, num_cols):
        if len(cat_cols) <= 2:
            fig = px.bar(df, x=cat_cols[0], y=num_cols[0], 
                         color=cat_cols[1] if len(cat_cols) > 1 else None,
                         title=f"{num_cols[0]} by {', '.join(cat_cols)}",
                         template="plotly_white")
        else:
            # For 3 or more categories, use a heatmap-like representation
            pivot_df = df.pivot_table(values=num_cols[0], 
                                      index=[cat_cols[0], cat_cols[1]], 
                                      columns=cat_cols[2], 
                                      fill_value=0)
            fig = px.imshow(pivot_df, 
                            labels=dict(x=cat_cols[2], y=f"{cat_cols[0]}, {cat_cols[1]}", color=num_cols[0]),
                            title=f"{num_cols[0]} by {', '.join(cat_cols)}",
                            template="plotly_white")
            fig.update_xaxes(side="top")
        return fig

    def multi_numeric_chart(df, num_cols):
        fig = make_subplots(rows=len(num_cols), cols=1, shared_xaxes=True, vertical_spacing=0.05)
        for i, col in enumerate(num_cols, 1):
            fig.add_trace(go.Histogram(x=df[col], name=col), row=i, col=1)
            fig.update_yaxes(title_text=col, row=i, col=1)
        fig.update_layout(title_text="Distribution of Numeric Columns", height=300*len(num_cols))
        return fig

    def create_multiple_charts(df):
        date_cols, numeric_cols, categorical_cols = analyze_df(df)
        charts = []

        if len(date_cols) > 0 and len(numeric_cols) > 0:
            for num_col in numeric_cols:
                fig = px.line(df, x=date_cols[0], y=num_col, title=f"{num_col} over time")
                charts.append(fig)

        if len(numeric_cols) >= 2:
            fig = px.scatter_matrix(df[numeric_cols], title="Scatter Matrix Plot")
            charts.append(fig)

        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            fig = multi_category_bar_chart(df, categorical_cols, numeric_cols)
            charts.append(fig)

        if len(numeric_cols) > 0:
            fig = multi_numeric_chart(df, numeric_cols)
            charts.append(fig)

        if len(categorical_cols) > 0:
            for cat_col in categorical_cols:
                fig = px.bar(df[cat_col].value_counts().reset_index(), x='index', y=cat_col, title=f"Distribution of {cat_col}")
                charts.append(fig)

        return charts

    def fallback_chart(df):
        charts = create_multiple_charts(df)
        if charts:
            for fig in charts:
                fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("Couldn't determine appropriate chart type. Displaying data in table format:")
            st.table(df)

    if df is None or df.empty:
        st.write("Chart for this data couldn't be determined. The dataframe is empty or None.")
        return

    try:
        date_cols, numeric_cols, categorical_cols = analyze_df(df)

        if chart_recommendation is None:
            chart_type = determine_chart_type(df)
        else:
            chart_type = chart_recommendation.split('(')[0].strip().lower()

        if chart_type in ['grouped bar', 'bar']:
            if len(categorical_cols) > 0 and len(numeric_cols) > 0:
                fig = multi_category_bar_chart(df, categorical_cols, numeric_cols)
            elif len(numeric_cols) >= 2:
                fig = px.bar(df, x=numeric_cols[0], y=numeric_cols[1:], 
                             title=f"{', '.join(numeric_cols[1:])} by {numeric_cols[0]}",
                             template="plotly_white", barmode='group' if chart_type == 'grouped bar' else None)
            else:
                raise ValueError(f"Not enough columns for a {chart_type} chart")

        elif chart_type == 'line':
            if len(date_cols) > 0 and len(numeric_cols) > 0:
                fig = px.line(df, x=date_cols[0], y=numeric_cols,
                              title=f"{', '.join(numeric_cols)} over {date_cols[0]}",
                              template="plotly_white", markers=True)
            elif len(numeric_cols) >= 2:
                fig = px.line(df, x=numeric_cols[0], y=numeric_cols[1:],
                              title=f"{', '.join(numeric_cols[1:])} over {numeric_cols[0]}",
                              template="plotly_white", markers=True)
            else:
                raise ValueError("Not enough columns for a line chart")

        elif chart_type == 'pie':
            if len(categorical_cols) == 1 and len(numeric_cols) >= 1:
                fig = px.pie(df, names=categorical_cols[0], values=numeric_cols[0],
                             title=f"Distribution of {numeric_cols[0]} by {categorical_cols[0]}",
                             template="plotly_white")
                if len(numeric_cols) > 1:
                    fig = make_subplots(rows=1, cols=len(numeric_cols), specs=[[{'type':'domain'}]*len(numeric_cols)])
                    for i, num_col in enumerate(numeric_cols, 1):
                        fig.add_trace(go.Pie(labels=df[categorical_cols[0]], values=df[num_col], name=num_col), 1, i)
                    fig.update_layout(title_text=f"Distribution of numeric columns by {categorical_cols[0]}")
            elif len(categorical_cols) > 1 and len(numeric_cols) >= 1:
                fig = px.sunburst(df, path=categorical_cols, values=numeric_cols[0],
                                  title=f"Distribution of {numeric_cols[0]} by {', '.join(categorical_cols)}",
                                  template="plotly_white")
            else:
                raise ValueError("Not enough columns for a pie chart")

        elif chart_type == 'scatter':
            if len(numeric_cols) >= 2:
                fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1],
                                 color=categorical_cols[0] if len(categorical_cols) > 0 else None,
                                 size=numeric_cols[2] if len(numeric_cols) > 2 else None,
                                 title=f"{numeric_cols[1]} vs {numeric_cols[0]}",
                                 template="plotly_white")
            else:
                raise ValueError("Not enough numeric columns for a scatter plot")

        elif chart_type == 'histogram':
            if len(numeric_cols) > 0:
                fig = px.histogram(df, x=numeric_cols, title=f"Distribution of Numeric Columns",
                                   template="plotly_white")
            elif len(categorical_cols) > 0:
                fig = px.histogram(df, x=categorical_cols[0],
                                   title=f"Distribution of {categorical_cols[0]}",
                                   template="plotly_white")
            else:
                raise ValueError("No suitable columns for a histogram")

        else:
            raise ValueError("Unsupported chart type")

        if fig:
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.write(f"Error occurred while generating the recommended chart: {str(e)}")
        st.write("Falling back to alternative visualizations...")
        fallback_chart(df)
