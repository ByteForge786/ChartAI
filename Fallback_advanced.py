import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# In your main.py file

# Create a single placeholder for all charts
chart_placeholder = st.empty()

# ... (your existing code to get df and chart_recommendation)

figs = generate_chart(df, chart_recommendation)

if figs:
    # Create a container for all charts
    with chart_placeholder.container():
        for i, fig in enumerate(figs, 1):
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"**Chart {i}**")  # Add a numbered label for each chart
else:
    chart_placeholder.write("No charts could be generated.")

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

def create_multiple_plots(df, chart_type):
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    
    if len(categorical_cols) == 0 or len(numeric_cols) == 0:
        return fallback_chart(df)

    figs = []
    
    if len(categorical_cols) >= 3 and chart_type in ['bar', 'grouped bar']:
        # Handle multiple categories for bar and grouped bar
        main_cat = categorical_cols[0]
        secondary_cats = categorical_cols[1:]
        for num_col in numeric_cols:
            if chart_type == 'bar':
                fig = px.bar(df, x=main_cat, y=num_col, 
                             color=secondary_cats[0],
                             facet_col=secondary_cats[1] if len(secondary_cats) > 1 else None,
                             facet_row=secondary_cats[2] if len(secondary_cats) > 2 else None,
                             title=f"{num_col} by {', '.join(categorical_cols)}")
            else:  # grouped bar
                fig = px.bar(df, x=main_cat, y=num_col,
                             color=secondary_cats[0],
                             barmode='group',
                             facet_col=secondary_cats[1] if len(secondary_cats) > 1 else None,
                             facet_row=secondary_cats[2] if len(secondary_cats) > 2 else None,
                             title=f"{num_col} by {', '.join(categorical_cols)}")
            
            fig.update_layout(xaxis_title=main_cat, yaxis_title=num_col)
            figs.append(fig)
    else:
        # Original logic for other chart types or simpler category structures
        for cat_col in categorical_cols:
            for num_col in numeric_cols:
                if chart_type == 'bar':
                    fig = px.bar(df, x=cat_col, y=num_col, title=f"{num_col} by {cat_col}")
                elif chart_type == 'grouped bar':
                    fig = px.bar(df, x=cat_col, y=num_col, color=categorical_cols[0] if len(categorical_cols) > 1 else None,
                                 title=f"{num_col} by {cat_col}", barmode='group')
                elif chart_type == 'line':
                    fig = px.line(df, x=cat_col, y=num_col, color=categorical_cols[0] if len(categorical_cols) > 1 else None,
                                  title=f"{num_col} over {cat_col}", markers=True)
                elif chart_type == 'scatter':
                    fig = px.scatter(df, x=cat_col, y=num_col, color=categorical_cols[0] if len(categorical_cols) > 1 else None,
                                     title=f"{num_col} vs {cat_col}")
                else:
                    fig = px.bar(df, x=cat_col, y=num_col, title=f"{num_col} by {cat_col}")
                
                fig.update_layout(xaxis_title=cat_col, yaxis_title=num_col)
                figs.append(fig)
    
    return figs

    try:
        if chart_recommendation is None:
            chart_type = determine_chart_type(df)
        else:
            chart_type = chart_recommendation.split('(')[0].strip().lower()

        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns

        if len(categorical_cols) > 1 or len(numeric_cols) > 1:
            figs = create_multiple_plots(df, chart_type)
        else:
            x_column = df.columns[0]
            y_columns = df.columns[1:]

            if chart_type == 'grouped bar':
                fig = px.bar(df, x=x_column, y=y_columns, 
                             title=f"{', '.join(y_columns)} by {x_column}",
                             template="plotly_white", barmode='group')
                fig.update_layout(xaxis_title=x_column, yaxis_title="Values")

            elif chart_type == 'bar':
                fig = px.bar(df, x=x_column, y=y_columns[0],
                             title=f"{y_columns[0]} by {x_column}",
                             template="plotly_white")
                fig.update_layout(xaxis_title=x_column, yaxis_title=y_columns[0])

            elif chart_type == 'line':
                fig = px.line(df, x=x_column, y=y_columns,
                              title=f"{', '.join(y_columns)} over {x_column}",
                              template="plotly_white", markers=True)
                fig.update_layout(xaxis_title=x_column, yaxis_title="Values")

            elif chart_type == 'pie':
                fig = px.pie(df, names=x_column, values=y_columns[0],
                             title=f"Distribution of {y_columns[0]} by {x_column}",
                             template="plotly_white")

            elif chart_type == 'scatter':
                fig = px.scatter(df, x=x_column, y=y_columns[0],
                                 title=f"{y_columns[0]} vs {x_column}",
                                 template="plotly_white")
                fig.update_layout(xaxis_title=x_column, yaxis_title=y_columns[0])

            elif chart_type == 'histogram':
                fig = px.histogram(df, x=x_column,
                                   title=f"Distribution of {x_column}",
                                   template="plotly_white")
                fig.update_layout(xaxis_title=x_column, yaxis_title="Count")

            else:
                fig = fallback_chart(df)

            figs = [fig]

        if isinstance(figs, list):
            for fig in figs:
                fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")
            return figs
        elif figs:
            figs.update_layout(plot_bgcolor="rgba(0,0,0,0)")
            return [figs]
        
    except Exception as e:
        st.write(f"Error occurred while generating the recommended chart: {str(e)}")
        st.write("Falling back to alternative visualization...")
        fig = fallback_chart(df)
        if fig:
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")
            return [fig]

    return None

# This function is not provided in the original code, so we'll add a placeholder
def determine_chart_type(df):
    # Add logic to determine chart type based on DataFrame structure
    # For now, we'll return a default chart type
    return 'bar'
