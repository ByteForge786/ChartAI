import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re

def analyze_dataframe(df):
    return {
        'date_cols': df.select_dtypes(include=['datetime64']).columns.tolist(),
        'numeric_cols': df.select_dtypes(include=['int64', 'float64']).columns.tolist(),
        'categorical_cols': df.select_dtypes(include=['object', 'category']).columns.tolist(),
        'total_cols': len(df.columns),
        'total_rows': len(df)
    }

def analyze_sql_query(sql_query):
    sql_lower = sql_query.lower()
    return {
        'has_group_by': 'group by' in sql_lower,
        'group_by_cols': re.findall(r'group by\s+(.*?)(?:\s+order by|\s+limit|\s*$)', sql_lower, re.IGNORECASE),
        'has_aggregation': any(func in sql_lower for func in ['count(', 'sum(', 'avg(', 'max(', 'min(']),
        'order_by': 'order by' in sql_lower
    }

def generate_chart(df, sql_query, chart_recommendation=None):
    df_analysis = analyze_dataframe(df)
    sql_analysis = analyze_sql_query(sql_query)

    def create_pie_chart(df, analysis):
        if len(analysis['numeric_cols']) == 1 and len(analysis['categorical_cols']) == 1:
            return px.pie(df, values=analysis['numeric_cols'][0], names=analysis['categorical_cols'][0],
                          title=f"Distribution of {analysis['numeric_cols'][0]}")
        elif len(analysis['numeric_cols']) >= 2 and analysis['total_rows'] == 1:
            return go.Figure(data=[go.Pie(labels=analysis['numeric_cols'], values=df.iloc[0][analysis['numeric_cols']])],
                             layout=dict(title="Distribution of Values"))
        return None

    def create_bar_chart(df, analysis, sql_analysis):
        if len(analysis['categorical_cols']) >= 1 and len(analysis['numeric_cols']) >= 1:
            x = analysis['categorical_cols'][0]
            y = analysis['numeric_cols']
            if len(analysis['categorical_cols']) == 1:
                return px.bar(df, x=x, y=y, title=f"{', '.join(y)} by {x}", 
                              barmode='group' if len(y) > 1 else None)
            elif len(analysis['categorical_cols']) == 2:
                color = analysis['categorical_cols'][1]
                return px.bar(df, x=x, y=y[0], color=color, 
                              title=f"{y[0]} by {x} and {color}", barmode='group')
            else:  # 3 or more categorical columns
                color = analysis['categorical_cols'][1]
                facet_col = analysis['categorical_cols'][2]
                fig = px.bar(df, x=x, y=y[0], color=color, facet_col=facet_col,
                             title=f"{y[0]} by {x}, {color}, and {facet_col}", barmode='group')
                for annotation in fig.layout.annotations:
                    annotation.text = annotation.text.split("=")[-1]
                return fig
        return None

    def create_line_chart(df, analysis):
        if len(analysis['date_cols']) == 1 and len(analysis['numeric_cols']) >= 1:
            return px.line(df, x=analysis['date_cols'][0], y=analysis['numeric_cols'], markers=True,
                           title=f"Trend of {', '.join(analysis['numeric_cols'])}")
        elif len(analysis['numeric_cols']) >= 2:
            return px.line(df, x=analysis['numeric_cols'][0], y=analysis['numeric_cols'][1:], markers=True,
                           title=f"Trend of {', '.join(analysis['numeric_cols'][1:])}")
        return None

    def create_scatter_chart(df, analysis):
        if len(analysis['numeric_cols']) >= 2:
            x, y = analysis['numeric_cols'][:2]
            color = analysis['categorical_cols'][0] if analysis['categorical_cols'] else None
            size = analysis['numeric_cols'][2] if len(analysis['numeric_cols']) > 2 else None
            return px.scatter(df, x=x, y=y, color=color, size=size,
                              title=f"{y} vs {x}")
        return None

    def create_heatmap(df, analysis):
        if len(analysis['numeric_cols']) == 1 and len(analysis['categorical_cols']) >= 2:
            pivot = df.pivot(index=analysis['categorical_cols'][0], columns=analysis['categorical_cols'][1], 
                             values=analysis['numeric_cols'][0])
            return px.imshow(pivot, title=f"Heatmap of {analysis['numeric_cols'][0]}")
        elif len(analysis['numeric_cols']) >= 3:
            corr = df[analysis['numeric_cols']].corr()
            return px.imshow(corr, title="Correlation Heatmap")
        return None

    def create_box_plot(df, analysis):
        if len(analysis['categorical_cols']) >= 1 and len(analysis['numeric_cols']) >= 1:
            return px.box(df, x=analysis['categorical_cols'][0], y=analysis['numeric_cols'][0],
                          title=f"Distribution of {analysis['numeric_cols'][0]} by {analysis['categorical_cols'][0]}")
        return None

    def create_histogram(df, analysis):
        if len(analysis['numeric_cols']) >= 1:
            return px.histogram(df, x=analysis['numeric_cols'][0], 
                                title=f"Distribution of {analysis['numeric_cols'][0]}")
        return None

    chart_functions = {
        'pie': create_pie_chart,
        'bar': create_bar_chart,
        'line': create_line_chart,
        'scatter': create_scatter_chart,
        'heatmap': create_heatmap,
        'box': create_box_plot,
        'histogram': create_histogram
    }

    fig = None
    error_flag = False

    # Try recommended chart first
    if chart_recommendation:
        try:
            chart_type = chart_recommendation.lower()
            if chart_type in chart_functions:
                if chart_type == 'bar':
                    fig = chart_functions[chart_type](df, df_analysis, sql_analysis)
                else:
                    fig = chart_functions[chart_type](df, df_analysis)
        except Exception as e:
            print(f"Error creating recommended chart: {str(e)}")
            error_flag = True

    # If recommended chart failed or wasn't specified, try other charts
    if fig is None and not error_flag:
        for func_name, func in chart_functions.items():
            try:
                if func_name == 'bar':
                    fig = func(df, df_analysis, sql_analysis)
                else:
                    fig = func(df, df_analysis)
                if fig:
                    break
            except Exception as e:
                print(f"Error creating {func_name} chart: {str(e)}")
                error_flag = True

    # Update layout if figure was created
    if fig:
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    
    return fig, error_flag

# Example usage
# sql_query = "SELECT category1, category2, category3, SUM(value) as total FROM table GROUP BY category1, category2, category3"
# df = pd.DataFrame(...)  # Your dataframe from SQL query result
# fig, error_flag = generate_chart(df, sql_query, "Bar")
# if fig:
#     fig.show()
# elif error_flag:
#     print("An error occurred while creating the chart.")
# else:
#     print("No suitable chart could be created for this data.")
