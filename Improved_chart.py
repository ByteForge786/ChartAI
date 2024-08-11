import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import re

def analyze_dataframe(df):
    analysis = {
        'date_cols': df.select_dtypes(include=['datetime64']).columns.tolist(),
        'numeric_cols': df.select_dtypes(include=['int64', 'float64']).columns.tolist(),
        'categorical_cols': df.select_dtypes(include=['object', 'category']).columns.tolist(),
        'total_cols': len(df.columns),
        'total_rows': len(df)
    }
    return analysis

def analyze_sql_query(sql_query):
    sql_lower = sql_query.lower()
    analysis = {
        'has_group_by': 'group by' in sql_lower,
        'group_by_cols': re.findall(r'group by\s+(.*?)(?:\s+order by|\s+limit|\s*$)', sql_lower, re.IGNORECASE),
        'has_aggregation': any(func in sql_lower for func in ['count(', 'sum(', 'avg(', 'max(', 'min(']),
        'order_by': 'order by' in sql_lower
    }
    return analysis

def create_pie_chart(df, analysis):
    if len(analysis['numeric_cols']) >= 1 and len(analysis['categorical_cols']) >= 1:
        fig = px.pie(df, values=analysis['numeric_cols'][0], names=analysis['categorical_cols'][0],
                     title=f"Distribution of {analysis['numeric_cols'][0]}")
    elif len(analysis['numeric_cols']) == 2 and analysis['total_rows'] == 1:
        fig = go.Figure(data=[go.Pie(labels=analysis['numeric_cols'], values=df.iloc[0][analysis['numeric_cols']])])
        fig.update_layout(title="Distribution of Percentages")
    elif len(analysis['numeric_cols']) >= 2:
        fig = go.Figure(data=[go.Pie(labels=analysis['numeric_cols'], values=df[analysis['numeric_cols']].sum())])
        fig.update_layout(title="Distribution of Numeric Values")
    else:
        return None
    return fig

def create_bar_chart(df, analysis, sql_analysis):
    if len(analysis['categorical_cols']) >= 1 and len(analysis['numeric_cols']) >= 1:
        x = analysis['categorical_cols'][0]
        y = analysis['numeric_cols']
        if sql_analysis['has_group_by'] and len(sql_analysis['group_by_cols']) > 1:
            color = analysis['categorical_cols'][1] if len(analysis['categorical_cols']) > 1 else None
            fig = px.bar(df, x=x, y=y[0], color=color, title=f"{y[0]} by {x}", barmode='group')
        else:
            fig = px.bar(df, x=x, y=y, title=f"{', '.join(y)} by {x}")
            if len(y) > 1:
                fig.update_layout(barmode='group')
    else:
        return None
    return fig

def create_grouped_bar_chart(df, analysis):
    if len(analysis['categorical_cols']) >= 2 and len(analysis['numeric_cols']) >= 1:
        fig = px.bar(df, x=analysis['categorical_cols'][0], y=analysis['numeric_cols'][0],
                     color=analysis['categorical_cols'][1], barmode='group',
                     title=f"Grouped Bar Chart: {analysis['numeric_cols'][0]} by {analysis['categorical_cols'][0]} and {analysis['categorical_cols'][1]}")
    else:
        return None
    return fig

def create_line_chart(df, analysis):
    if len(analysis['date_cols']) >= 1 and len(analysis['numeric_cols']) >= 1:
        fig = px.line(df, x=analysis['date_cols'][0], y=analysis['numeric_cols'], markers=True)
    elif len(analysis['numeric_cols']) >= 2:
        fig = px.line(df, x=analysis['numeric_cols'][0], y=analysis['numeric_cols'][1:], markers=True)
    else:
        return None
    fig.update_layout(title=f"Trend of {', '.join(analysis['numeric_cols'])}")
    return fig

def create_scatter_chart(df, analysis):
    if len(analysis['numeric_cols']) >= 2:
        fig = px.scatter(df, x=analysis['numeric_cols'][0], y=analysis['numeric_cols'][1],
                         color=analysis['categorical_cols'][0] if analysis['categorical_cols'] else None)
        fig.update_layout(title=f"{analysis['numeric_cols'][1]} vs {analysis['numeric_cols'][0]}")
    else:
        return None
    return fig

def create_heatmap(df, analysis):
    if len(analysis['numeric_cols']) >= 1 and len(analysis['categorical_cols']) >= 2:
        pivot = df.pivot(index=analysis['categorical_cols'][0], columns=analysis['categorical_cols'][1], 
                         values=analysis['numeric_cols'][0])
        fig = px.imshow(pivot, title=f"Heatmap of {analysis['numeric_cols'][0]}")
    else:
        return None
    return fig

def fallback_chart(df, analysis):
    if analysis['total_cols'] <= 10 and analysis['total_rows'] <= 50:
        return px.table(df, title="Data Table")
    else:
        return px.scatter_matrix(df, dimensions=analysis['numeric_cols'][:4], title="Scatter Matrix")

def generate_chart(df, sql_query, recommended_chart=None):
    df_analysis = analyze_dataframe(df)
    sql_analysis = analyze_sql_query(sql_query)
    
    chart_functions = {
        'pie': create_pie_chart,
        'bar': create_bar_chart,
        'grouped bar': create_grouped_bar_chart,
        'line': create_line_chart,
        'scatter': create_scatter_chart,
        'heatmap': create_heatmap
    }

    fig = None

    # Try recommended chart first
    if recommended_chart:
        chart_type = recommended_chart.lower()
        if chart_type in chart_functions:
            if chart_type == 'bar':
                fig = chart_functions[chart_type](df, df_analysis, sql_analysis)
            else:
                fig = chart_functions[chart_type](df, df_analysis)
            if fig:
                st.success(f"Successfully created the recommended {chart_type} chart.")
            else:
                st.warning(f"Unable to create the recommended {chart_type} chart. Trying alternatives.")

    # If recommended chart failed or wasn't specified, try other charts
    if fig is None:
        for func_name, func in chart_functions.items():
            if func_name == 'bar':
                fig = func(df, df_analysis, sql_analysis)
            else:
                fig = func(df, df_analysis)
            if fig:
                st.info(f"Created a {func_name} chart based on the data structure.")
                break

    # Fallback mechanism
    if fig is None:
        st.warning("Unable to create a standard chart. Falling back to alternative visualization.")
        try:
            if df_analysis['total_cols'] <= 10 and df_analysis['total_rows'] <= 50:
                st.table(df)
            else:
                fig = fallback_chart(df, df_analysis)
        except Exception as e:
            st.error(f"Error in fallback mechanism: {str(e)}")
            st.dataframe(df)

    # Display the chart if one was created
    if fig:
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")
        try:
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error displaying the chart: {str(e)}")
            st.dataframe(df)
    else:
        st.error("Unable to generate any suitable chart. Displaying data as a table:")
        st.dataframe(df)

# Example usage
# sql_query = "SELECT column1, COUNT(*) as count FROM table GROUP BY column1, column2"
# df = pd.DataFrame(...)  # Your dataframe from SQL query result
# generate_chart(df, sql_query, "Bar")
