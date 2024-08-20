import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import itertools

def generate_chart(df, chart_recommendation):
    def fallback_chart(df):
        date_cols = df.select_dtypes(include=['datetime64']).columns
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns

        if len(date_cols) > 0 and len(numeric_cols) > 0:
            fig = make_subplots(rows=len(numeric_cols), cols=1, shared_xaxes=True, vertical_spacing=0.05)
            for i, col in enumerate(numeric_cols, 1):
                fig.add_trace(go.Scatter(x=df[date_cols[0]], y=df[col], mode='lines+markers', name=col), row=i, col=1)
                fig.update_yaxes(title_text=col, row=i, col=1)
            fig.update_layout(title_text="Time Series Plot", height=300*len(numeric_cols))
        elif len(numeric_cols) >= 2:
            fig = px.scatter_matrix(df[numeric_cols], title="Scatter Matrix Plot")
        elif len(categorical_cols) > 0 and len(numeric_cols) > 0:
            fig = px.bar(df, x=categorical_cols[0], y=numeric_cols[0], title=f"Bar Chart: {numeric_cols[0]} by {categorical_cols[0]}")
        else:
            st.write("Couldn't determine appropriate chart type. Displaying data in table format:")
            st.table(df)
            return None

        return fig

    def analyze_df(df):
        date_cols = df.select_dtypes(include=['datetime64']).columns
        numeric_cols = df.select_dtypes(include(['int64', 'float64'])).columns
        categorical_cols = df.select_dtypes(include(['object', 'category'])).columns

        return date_cols, numeric_cols, categorical_cols

    def create_trace_combinations(dates, categories, numerics, chart_type):
        # Generate all combinations of Date, Category, Numeric columns
        combinations = []
        if len(dates) > 0:
            for d in dates:
                for n in numerics:
                    if chart_type in ['line']:
                        combinations.append((d, n))
                    elif chart_type in ['bar', 'grouped bar']:
                        for c in categories:
                            combinations.append((d, c, n))
                    elif chart_type == 'pie':
                        combinations.append((d, n))
        else:
            for n in numerics:
                if chart_type in ['bar', 'grouped bar']:
                    for c in categories:
                        combinations.append((c, n))
                elif chart_type == 'pie':
                    for c in categories:
                        combinations.append((c, n))
        return combinations

    try:
        date_cols, numeric_cols, categorical_cols = analyze_df(df)

        if chart_recommendation is None:
            chart_type = determine_chart_type(df)
        else:
            chart_type = chart_recommendation.split('(')[0].strip().lower()

        trace_combinations = create_trace_combinations(date_cols, categorical_cols, numeric_cols, chart_type)

        fig = go.Figure()

        for combination in trace_combinations:
            if chart_type == 'grouped bar':
                x_col, color_col, y_col = combination
                fig.add_trace(go.Bar(x=df[x_col], y=df[y_col], name=f"{y_col} by {x_col} and {color_col}", 
                                     hoverinfo="x+y+name"))
            elif chart_type == 'bar':
                x_col, color_col, y_col = combination
                fig.add_trace(go.Bar(x=df[x_col], y=df[y_col], name=y_col, hoverinfo="x+y+name"))
            elif chart_type == 'line':
                x_col, y_col = combination
                fig.add_trace(go.Scatter(x=df[x_col], y=df[y_col], mode='lines+markers', name=y_col))
            elif chart_type == 'pie':
                x_col, y_col = combination
                fig.add_trace(go.Pie(labels=df[x_col], values=df[y_col], name=y_col))

        # Final layout adjustment based on chart type
        if chart_type == 'grouped bar':
            fig.update_layout(barmode='group', title="Grouped Bar Chart", xaxis_title="Categories", yaxis_title="Values")
        elif chart_type == 'bar':
            fig.update_layout(title="Bar Chart", xaxis_title="Categories", yaxis_title="Values")
        elif chart_type == 'line':
            fig.update_layout(title="Line Chart", xaxis_title="Date", yaxis_title="Values")
        elif chart_type == 'pie':
            fig.update_layout(title="Pie Chart")

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
