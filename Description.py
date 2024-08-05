      import pandas as pd
import numpy as np
import re
from scipy import stats

def analyze_query_results(df, question, sql_query, chart_recommendation):
    insights = []
    
    try:
        chart_type = chart_recommendation.split('(')[0].strip().lower() if chart_recommendation else determine_chart_type(df)
    except Exception as e:
        print(f"Error determining chart type: {e}")
        chart_type = "unknown"

    # SQL Query Analysis
    try:
        if 'GROUP BY' in sql_query.upper():
            grouped_cols = re.findall(r'GROUP BY\s+(.*?)(?:\s+ORDER BY|\s*$)', sql_query, re.IGNORECASE)[0].split(',')
            grouped_cols = [col.strip() for col in grouped_cols]
            insights.append(f"The data is grouped by {', '.join(grouped_cols)}.")
        
        if 'ORDER BY' in sql_query.upper():
            order_cols = re.findall(r'ORDER BY\s+(.*?)(?:\s+LIMIT|\s*$)', sql_query, re.IGNORECASE)[0].split(',')
            order_cols = [col.strip() for col in order_cols]
            insights.append(f"The results are sorted by {', '.join(order_cols)}.")
        
        if 'LIMIT' in sql_query.upper():
            limit = re.findall(r'LIMIT\s+(\d+)', sql_query, re.IGNORECASE)[0]
            insights.append(f"The query returns up to {limit} rows.")
    except Exception as e:
        print(f"Error analyzing SQL query: {e}")

    # Check for time-based or other groupings in the question
    try:
        group_pattern = r'by\s+(\w+)'
        group_matches = re.findall(group_pattern, question.lower())
        
        if group_matches:
            group_by = group_matches[0]
            if group_by in ['week', 'weeks', 'day', 'days', 'month', 'months', 'year', 'years']:
                time_based_grouping = True
                time_unit = group_by
            else:
                time_based_grouping = False
                grouping_column = group_by
            
            # Calculate percentage change
            if time_based_grouping:
                if time_unit in ['week', 'weeks']:
                    df['date'] = pd.to_datetime(df.iloc[:, 0])
                    df['week'] = df['date'].dt.to_period('W')
                    grouped = df.groupby('week').sum().reset_index()
                elif time_unit in ['day', 'days']:
                    df['date'] = pd.to_datetime(df.iloc[:, 0])
                    grouped = df.groupby('date').sum().reset_index()
                elif time_unit in ['month', 'months']:
                    df['date'] = pd.to_datetime(df.iloc[:, 0])
                    df['month'] = df['date'].dt.to_period('M')
                    grouped = df.groupby('month').sum().reset_index()
                else:  # year, years
                    df['date'] = pd.to_datetime(df.iloc[:, 0])
                    df['year'] = df['date'].dt.year
                    grouped = df.groupby('year').sum().reset_index()
                
                for col in grouped.columns[1:]:
                    if pd.api.types.is_numeric_dtype(grouped[col]):
                        pct_change = grouped[col].pct_change() * 100
                        avg_change = pct_change.mean()
                        insights.append(f"On average, {col} changes by {avg_change:.2f}% per {time_unit}.")
                        
                        # Identify significant changes
                        significant_changes = pct_change[abs(pct_change) > 10]
                        if not significant_changes.empty:
                            max_change = significant_changes.abs().idxmax()
                            direction = "increase" if significant_changes[max_change] > 0 else "decrease"
                            insights.append(f"The most significant {direction} in {col} was {abs(significant_changes[max_change]):.2f}% between {grouped.iloc[max_change-1][grouped.columns[0]]} and {grouped.iloc[max_change][grouped.columns[0]]}.")
            
            else:
                # Non-time-based grouping
                grouped = df.groupby(grouping_column).sum().reset_index()
                for col in grouped.columns[1:]:
                    if pd.api.types.is_numeric_dtype(grouped[col]):
                        max_value = grouped[col].max()
                        min_value = grouped[col].min()
                        pct_diff = (max_value - min_value) / min_value * 100
                        insights.append(f"The difference between the highest and lowest {col} across {grouping_column}s is {pct_diff:.2f}%.")
                        
                        # Identify top and bottom performers
                        top_performer = grouped.loc[grouped[col].idxmax(), grouping_column]
                        bottom_performer = grouped.loc[grouped[col].idxmin(), grouping_column]
                        insights.append(f"'{top_performer}' leads in {col}, while '{bottom_performer}' has the lowest value.")
    except Exception as e:
        print(f"Error in grouping analysis: {e}")

    # Time-based analysis
    try:
        time_cols = df.select_dtypes(include=['datetime64']).columns
        if len(time_cols) > 0:
            time_col = time_cols[0]
            time_range = df[time_col].max() - df[time_col].min()
            insights.append(f"The data covers a period of {time_range.days} days.")
            
            # Trend analysis
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                correlation = df[time_col].corr(df[col])
                if abs(correlation) > 0.7:
                    trend = "upward" if correlation > 0 else "downward"
                    insights.append(f"There's a strong {trend} trend for {col} over time.")
            
            # Seasonality check
            if len(df) >= 12:
                df['month'] = df[time_col].dt.month
                for col in numeric_cols:
                    monthly_avg = df.groupby('month')[col].mean()
                    if monthly_avg.max() / monthly_avg.min() > 1.5:
                        peak_month = monthly_avg.idxmax()
                        insights.append(f"{col} shows seasonal patterns with peaks typically in {peak_month:%B}.")
    except Exception as e:
        print(f"Error in time-based analysis: {e}")

    # Distribution analysis
    try:
        for col in df.select_dtypes(include=[np.number]).columns:
            if df[col].nunique() > 5:
                skewness = df[col].skew()
                if abs(skewness) > 1:
                    skew_direction = "higher" if skewness > 0 else "lower"
                    insights.append(f"The distribution of {col} is skewed, with more {skew_direction} values than expected.")
                
                # Outlier detection
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                outliers = df[(df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)]
                if len(outliers) > 0:
                    insights.append(f"There are {len(outliers)} potential outliers in {col}, which may warrant further investigation.")
    except Exception as e:
        print(f"Error in distribution analysis: {e}")

    # Correlation analysis
    try:
        if len(df.select_dtypes(include=[np.number]).columns) > 1:
            corr_matrix = df.select_dtypes(include=[np.number]).corr()
            high_corr = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)).stack()
            high_corr = high_corr[abs(high_corr) > 0.7]
            for (col1, col2), corr in high_corr.items():
                relationship = "strong positive" if corr > 0 else "strong negative"
                insights.append(f"There's a {relationship} relationship between {col1} and {col2}.")
    except Exception as e:
        print(f"Error in correlation analysis: {e}")

    # Chart-specific insights
    try:
        if chart_type in ['bar', 'grouped bar']:
            x_col = df.columns[0]
            y_cols = df.columns[1:]
            
            for y_col in y_cols:
                top_category = df.nlargest(1, y_col).iloc[0]
                bottom_category = df.nsmallest(1, y_col).iloc[0]
                insights.append(f"{top_category[x_col]} leads in {y_col} with {top_category[y_col]:.2f}, while {bottom_category[x_col]} lags at {bottom_category[y_col]:.2f}.")
            
            if len(df) > 5:
                top_5_sum = df.nlargest(5, y_cols[0])[y_cols[0]].sum()
                total_sum = df[y_cols[0]].sum()
                insights.append(f"The top 5 {x_col}s drive {(top_5_sum/total_sum)*100:.1f}% of total {y_cols[0]}.")
            
            # Pareto analysis
            if len(df) > 1:
                df_sorted = df.sort_values(y_cols[0], ascending=False)
                cumulative_sum = df_sorted[y_cols[0]].cumsum()
                pareto_index = (cumulative_sum / total_sum >= 0.8).idxmax()
                insights.append(f"The top {pareto_index + 1} {x_col}s account for 80% of the total {y_cols[0]}, suggesting a Pareto distribution.")
            
            # Variance analysis
            if len(df) > 2:
                variance = df[y_cols[0]].var()
                cv = df[y_cols[0]].std() / df[y_cols[0]].mean()
                insights.append(f"There's a variance of {variance:.2f} in {y_cols[0]} across {x_col}s, with a coefficient of variation of {cv:.2f}, indicating {'high' if cv > 1 else 'moderate' if cv > 0.5 else 'low'} relative variability.")
            
            if chart_type == 'grouped bar':
                category_col = df.columns[0]
                group_col = df.columns[1]
                value_col = df.columns[2]
                
                # Identify top performer in each category
                top_performers = df.loc[df.groupby(category_col)[value_col].idxmax()]
                insights.append(f"Top performers in each {category_col}: " + ", ".join([f"{row[category_col]}: {row[group_col]}" for _, row in top_performers.iterrows()]))
                
                # Identify most consistent performer across categories
                group_ranks = df.groupby([category_col, group_col])[value_col].mean().unstack().rank(ascending=False)
                most_consistent = group_ranks.mean().idxmin()
                insights.append(f"{most_consistent} shows the most consistent performance across all {category_col}s.")
        
        elif chart_type == 'line':
            for col in df.columns[1:]:
                start_value = df[col].iloc[0]
                end_value = df[col].iloc[-1]
                change_pct = ((end_value - start_value) / start_value) * 100
                direction = "grew" if change_pct > 0 else "declined"
                insights.append(f"{col} {direction} by {abs(change_pct):.1f}% from {start_value:.2f} to {end_value:.2f}.")
                
                peak = df[col].max()
                trough = df[col].min()
                insights.append(f"{col} peaked at {peak:.2f} and bottomed at {trough:.2f}.")
                
                # Volatility analysis
                rolling_std = df[col].rolling(window=min(len(df)//4, 30)).std()
                avg_volatility = rolling_std.mean()
                insights.append(f"The average volatility (standard deviation) of {col} over time is {avg_volatility:.2f}.")
                
                # Trend strength
                x = np.arange(len(df))
                slope, _, r_value, _, _ = stats.linregress(x, df[col])
                trend_strength = r_value ** 2
                trend_direction = "upward" if slope > 0 else "downward"
                insights.append(f"{col} shows a {trend_direction} trend with a strength of {trend_strength:.2f} (R-squared).")
                
                # Acceleration/Deceleration
                pct_changes = df[col].pct_change()
                acceleration = pct_changes.diff()
                if acceleration.mean() > 0:
                    insights.append(f"{col} is showing signs of acceleration in its growth rate.")
                elif acceleration.mean() < 0:
                    insights.append(f"{col} is showing signs of deceleration in its growth rate.")
        
        elif chart_type == 'pie':
            values_col = df.columns[1]
            total = df[values_col].sum()
            top_category = df.nlargest(1, values_col).iloc[0]
            insights.append(f"'{top_category.iloc[0]}' dominates with {(top_category[values_col]/total)*100:.1f}% of the total {values_col}.")
            
            if len(df) > 3:
                other_pct = (df.nsmallest(len(df)-3, values_col)[values_col].sum() / total) * 100
                insights.append(f"The smaller categories collectively represent {other_pct:.1f}% of the total, indicating a long tail distribution.")
            
            # Concentration analysis
            herfindahl_index = ((df[values_col] / total) ** 2).sum()
            if herfindahl_index < 0.15:
                concentration = "highly diverse"
            elif herfindahl_index < 0.25:
                concentration = "moderately concentrated"
            else:
                concentration = "highly concentrated"
            insights.append(f"The market is {concentration} with a Herfindahl index of {herfindahl_index:.2f}.")
            
            # Relative comparisons
            if len(df) > 1:
                second_largest = df.nlargest(2, values_col).iloc[1]
                ratio = top_category[values_col] / second_largest[values_col]
                insights.append(f"The leading category '{top_category.iloc[0]}' is {ratio:.1f} times larger than the second-largest category '{second_largest.iloc[0]}'.")
            
            # Identify underperformers
            average = total / len(df)
            underperformers = df[df[values_col] < average]
if not underperformers.empty:
                insights.append(f"{len(underperformers)} categories are performing below the average of {average:.2f}, potentially indicating areas for improvement.")
    except Exception as e:
        print(f"Error in chart-specific analysis: {e}")

    # Question-specific insights
    try:
        if 'top' in question.lower() and len(df) > 1:
            top_item = df.iloc[0]
            insights.append(f"'{top_item.iloc[0]}' stands out as the leader, with a {df.columns[1]} of {top_item.iloc[1]}.")
            
            if len(df) >= 3:
                total = df.iloc[:, 1].sum()
                top_three_share = df.iloc[:3, 1].sum() / total * 100
                insights.append(f"The top three contenders command {top_three_share:.1f}% of the total, highlighting a concentration at the top.")

        elif 'average' in question.lower() or 'mean' in question.lower():
            for col in df.select_dtypes(include=[np.number]).columns:
                mean_val = df[col].mean()
                insights.append(f"On average, {col} stands at {mean_val:.2f}.")
                
                # Compare to overall average if there's a grouping
                if len(df) > 1:
                    above_average = df[df[col] > mean_val]
                    insights.append(f"{len(above_average)} items outperform the average {col}, suggesting room for improvement in others.")
    except Exception as e:
        print(f"Error in question-specific analysis: {e}")

    # Overall trend for time series
    try:
        time_cols = df.select_dtypes(include=['datetime64']).columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(time_cols) > 0 and len(numeric_cols) > 0:
            first_value = df[numeric_cols[0]].iloc[0]
            last_value = df[numeric_cols[0]].iloc[-1]
            overall_change = ((last_value - first_value) / first_value) * 100
            trend = "growth" if overall_change > 0 else "decline"
            insights.append(f"We're seeing a {trend} trend in {numeric_cols[0]}, with a {abs(overall_change):.1f}% change from start to finish.")
    except Exception as e:
        print(f"Error in overall trend analysis: {e}")

    return " ".join(insights)

def determine_chart_type(df):
    # This is a placeholder function. In practice, you would implement logic here
    # to determine the best chart type based on the data characteristics.
    return "bar"

# Example usage:
# df = pd.read_csv('your_data.csv')
# question = "What are the top 5 products by sales revenue by week?"
# sql_query = "SELECT product, week, SUM(revenue) as total_revenue FROM sales GROUP BY product, week ORDER BY total_revenue DESC LIMIT 5"
# chart_recommendation = "Bar chart (horizontal)"
# insights = analyze_query_results(df, question, sql_query, chart_recommendation)
# print(insights)






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
