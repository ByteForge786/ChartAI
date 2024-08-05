import pandas as pd
import numpy as np
import re

def analyze_query_results(df, question, sql_query, chart_recommendation):
    insights = []
    
    def add_insight(text):
        insights.append(text)

    chart_type = chart_recommendation.split('(')[0].strip().lower() if chart_recommendation else determine_chart_type(df)
    
    # Analyze SQL query
    aggregations = re.findall(r'(SUM|AVG|COUNT|MAX|MIN)\((\w+)\)', sql_query, re.IGNORECASE)
    grouping = re.search(r'GROUP BY\s+(\w+)', sql_query, re.IGNORECASE)
    ordering = re.search(r'ORDER BY\s+(\w+)\s+(ASC|DESC)', sql_query, re.IGNORECASE)
    
    # Time-based analysis
    time_cols = df.select_dtypes(include=['datetime64']).columns
    if len(time_cols) > 0:
        time_col = time_cols[0]
        time_range = df[time_col].max() - df[time_col].min()
        add_insight(f"The data covers a period of {time_range.days} days, from {df[time_col].min().date()} to {df[time_col].max().date()}.")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            first_value = df[col].iloc[0]
            last_value = df[col].iloc[-1]
            change = last_value - first_value
            pct_change = (change / first_value) * 100 if first_value != 0 else 0
            direction = "up" if change > 0 else "down"
            add_insight(f"{col.capitalize()} has gone {direction} from {first_value:,.0f} to {last_value:,.0f}, " 
                        f"a change of {abs(pct_change):.1f}% over the period.")

    # Chart-specific insights
    if chart_type in ['bar', 'grouped bar']:
        x_col = df.columns[0]
        y_cols = df.columns[1:]
        for y_col in y_cols:
            top_category = df.nlargest(1, y_col).iloc[0]
            bottom_category = df.nsmallest(1, y_col).iloc[0]
            add_insight(f"{top_category[x_col]} leads in {y_col} with {top_category[y_col]:,.0f}, " 
                        f"while {bottom_category[x_col]} has the lowest at {bottom_category[y_col]:,.0f}.")
        
        if len(df) > 5:
            top_5_sum = df.nlargest(5, y_cols[0])[y_cols[0]].sum()
            total_sum = df[y_cols[0]].sum()
            add_insight(f"The top 5 {x_col}s make up {(top_5_sum/total_sum)*100:.1f}% of total {y_cols[0]}.")
    
    elif chart_type == 'line':
        for col in df.columns[1:]:
            peak = df[col].max()
            peak_date = df.loc[df[col].idxmax(), time_col] if len(time_cols) > 0 else 'N/A'
            trough = df[col].min()
            trough_date = df.loc[df[col].idxmin(), time_col] if len(time_cols) > 0 else 'N/A'
            add_insight(f"{col.capitalize()} reached its highest point of {peak:,.0f} on {peak_date.date()}, " 
                        f"and its lowest of {trough:,.0f} on {trough_date.date()}.")
    
    elif chart_type == 'pie':
        values_col = df.columns[1]
        total = df[values_col].sum()
        top_category = df.nlargest(1, values_col).iloc[0]
        add_insight(f"{top_category.iloc[0]} is the largest segment, accounting for "
                    f"{(top_category[values_col]/total)*100:.1f}% of the total.")
        
        if len(df) > 3:
            other_pct = (df.nsmallest(len(df)-3, values_col)[values_col].sum() / total) * 100
            add_insight(f"The smallest segments combined represent {other_pct:.1f}% of the total.")
    
    elif chart_type == 'scatter':
        x_col, y_col = df.columns[:2]
        correlation = df[x_col].corr(df[y_col])
        if abs(correlation) > 0.7:
            strength = "strong"
        elif abs(correlation) > 0.3:
            strength = "moderate"
        else:
            strength = "weak"
        direction = "positive" if correlation > 0 else "negative"
        add_insight(f"There appears to be a {strength} {direction} relationship between {x_col} and {y_col}.")
        
    elif chart_type == 'histogram':
        col = df.columns[0]
        mean_val = df[col].mean()
        median_val = df[col].median()
        add_insight(f"The typical {col} is around {median_val:,.0f}, with an average of {mean_val:,.0f}.")
        
        skewness = df[col].skew()
        if abs(skewness) > 0.5:
            skew_direction = "higher" if skewness > 0 else "lower"
            add_insight(f"There are more {col}s with {skew_direction} values than you might expect.")
    
    # Aggregation insights
    for agg, col in aggregations:
        if agg.upper() == 'SUM':
            total = df[col].sum()
            add_insight(f"The total {col} across all entries is {total:,.0f}.")
        elif agg.upper() == 'AVG':
            avg = df[col].mean()
            add_insight(f"On average, each entry has a {col} of {avg:,.2f}.")
        elif agg.upper() == 'COUNT':
            count = len(df)
            add_insight(f"There are {count:,} entries in total.")
    
    # Grouping insights
    if grouping:
        group_col = grouping.group(1)
        add_insight(f"The data is grouped by {group_col}, allowing for comparison across different {group_col}s.")
    
    # Ordering insights
    if ordering:
        order_col, direction = ordering.groups()
        dir_word = "highest" if direction.upper() == "DESC" else "lowest"
        add_insight(f"The results are ordered by {order_col}, with the {dir_word} values first.")

    # Question-specific insights
    if 'top' in question.lower() and len(df) > 1:
        top_item = df.iloc[0]
        add_insight(f"{top_item.iloc[0]} stands out as the leader, with a value of {top_item.iloc[1]:,.0f}.")
        
        if len(df) >= 3:
            total = df.iloc[:, 1].sum()
            top_three_share = df.iloc[:3, 1].sum() / total * 100
            add_insight(f"The top three contenders together account for {top_three_share:.1f}% of the total.")

    return " ".join(insights)







def main():
    st.set_page_config(page_title="Data Query and Visualization App", layout="wide")

    st.title("Data Query and Visualization App")

    # Load cached model
    model, tokenizer = load_model()

    if model is None or tokenizer is None:
        st.stop()

    # Your prompt (to be filled)
    prompt = ["Your prompt here"]

    # User input
    question = st.text_input("Enter your question:")

    if st.button("Submit"):
        if question:
            with st.spinner("Generating SQL query..."):
                response = get_model_response(question, prompt, model, tokenizer)
                sql_query = get_sql_query_from_response(response)
                chart_recommendation = get_chart_recommendation_from_response(response)

            if sql_query:
                st.subheader("Generated SQL Query:")
                st.code(sql_query, language="sql")

                with st.spinner("Executing query..."):
                    # This is where you would run your SQL query on Snowflake
                    # and get the result_df. For now, we'll use a dummy DataFrame.
                    result_df = pd.DataFrame({
                        'date': pd.date_range(start='2023-01-01', periods=10, freq='W'),
                        'value': [100, 120, 115, 130, 125, 140, 135, 150, 145, 160]
                    })

                if not result_df.empty:
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("Query Results:")
                        st.dataframe(result_df)

                    with col2:
                        st.subheader("Visualization:")
                        generate_chart(result_df, chart_recommendation)

                    st.subheader("Key Insights:")
                    analysis = analyze_query_results(result_df, question, sql_query, chart_recommendation)
                    st.write(analysis)
                else:
                    st.warning("No results found for the given query.")
            else:
                st.error("Could not generate a valid SQL query.")
        else:
            st.warning("Please enter a question.")

if __name__ == "__main__":
    main()
