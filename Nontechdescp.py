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
            insights.append(f"We've organized the data by {', '.join(grouped_cols)}.")
        
        if 'ORDER BY' in sql_query.upper():
            order_cols = re.findall(r'ORDER BY\s+(.*?)(?:\s+LIMIT|\s*$)', sql_query, re.IGNORECASE)[0].split(',')
            order_cols = [col.strip() for col in order_cols]
            insights.append(f"We've arranged the results based on {', '.join(order_cols)}.")
        
        if 'LIMIT' in sql_query.upper():
            limit = re.findall(r'LIMIT\s+(\d+)', sql_query, re.IGNORECASE)[0]
            insights.append(f"We're looking at the top {limit} results.")
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
            
            # Calculate changes over time or across groups
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
                        insights.append(f"On average, {col} changes by about {abs(avg_change):.1f}% each {time_unit}.")
                        
                        # Identify significant changes
                        significant_changes = pct_change[abs(pct_change) > 10]
                        if not significant_changes.empty:
                            max_change = significant_changes.abs().idxmax()
                            direction = "increase" if significant_changes[max_change] > 0 else "decrease"
                            insights.append(f"The biggest change in {col} was a {direction} of {abs(significant_changes[max_change]):.1f}% between {grouped.iloc[max_change-1][grouped.columns[0]]} and {grouped.iloc[max_change][grouped.columns[0]]}. This might be worth looking into.")
            
            else:
                # Non-time-based grouping
                grouped = df.groupby(grouping_column).sum().reset_index()
                for col in grouped.columns[1:]:
                    if pd.api.types.is_numeric_dtype(grouped[col]):
                        max_value = grouped[col].max()
                        min_value = grouped[col].min()
                        pct_diff = (max_value - min_value) / min_value * 100
                        insights.append(f"The difference between the highest and lowest {col} across {grouping_column}s is {pct_diff:.1f}%. This shows how much variation there is.")
                        
                        # Identify top and bottom performers
                        top_performer = grouped.loc[grouped[col].idxmax(), grouping_column]
                        bottom_performer = grouped.loc[grouped[col].idxmin(), grouping_column]
                        insights.append(f"'{top_performer}' has the highest {col}, while '{bottom_performer}' has the lowest. It might be useful to understand why there's such a big difference.")
    except Exception as e:
        print(f"Error in grouping analysis: {e}")

    # Time-based analysis
    try:
        time_cols = df.select_dtypes(include=['datetime64']).columns
        if len(time_cols) > 0:
            time_col = time_cols[0]
            time_range = df[time_col].max() - df[time_col].min()
            insights.append(f"Our data covers a period of {time_range.days} days.")
            
            # Trend analysis
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                correlation = df[time_col].corr(df[col])
                if abs(correlation) > 0.7:
                    trend = "increasing" if correlation > 0 else "decreasing"
                    insights.append(f"We're seeing a clear pattern of {col} {trend} over time. This trend might continue, so it's worth planning for.")
            
            # Seasonality check
            if len(df) >= 12:
                df['month'] = df[time_col].dt.month
                for col in numeric_cols:
                    monthly_avg = df.groupby('month')[col].mean()
                    if monthly_avg.max() / monthly_avg.min() > 1.5:
                        peak_month = monthly_avg.idxmax()
                        insights.append(f"We noticed that {col} tends to be highest in {peak_month:%B}. This seasonal pattern could help with planning and forecasting.")
    except Exception as e:
        print(f"Error in time-based analysis: {e}")

    # Distribution analysis
    try:
        for col in df.select_dtypes(include=[np.number]).columns:
            if df[col].nunique() > 5:
                skewness = df[col].skew()
                if abs(skewness) > 1:
                    if skewness > 0:
                        insights.append(f"For {col}, most values are on the lower end, but there are a few much higher values that pull the average up. This might mean there are some exceptional cases worth looking into.")
                    else:
                        insights.append(f"For {col}, most values are on the higher end, but there are a few much lower values that pull the average down. It might be worth investigating these lower-than-usual cases.")
                
                # Outlier detection
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                outliers = df[(df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)]
                if len(outliers) > 0:
                    insights.append(f"There are {len(outliers)} unusual values for {col} that are very different from the rest. These could be special cases or possibly errors that need checking.")
    except Exception as e:
        print(f"Error in distribution analysis: {e}")

    # Correlation analysis
    try:
        if len(df.select_dtypes(include=[np.number]).columns) > 1:
            corr_matrix = df.select_dtypes(include=[np.number]).corr()
            high_corr = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)).stack()
            high_corr = high_corr[abs(high_corr) > 0.7]
            for (col1, col2), corr in high_corr.items():
                if corr > 0:
                    insights.append(f"We noticed that when {col1} goes up, {col2} tends to go up too. This could be useful for predicting or understanding changes in these areas.")
                else:
                    insights.append(f"We noticed that when {col1} goes up, {col2} tends to go down. This relationship might be important for balancing these two factors.")
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
                insights.append(f"{top_category[x_col]} is leading in {y_col} with {top_category[y_col]:.2f}, while {bottom_category[x_col]} is at the bottom with {bottom_category[y_col]:.2f}. Understanding why could help improve overall performance.")
            
            if len(df) > 5:
                top_5_sum = df.nlargest(5, y_cols[0])[y_cols[0]].sum()
                total_sum = df[y_cols[0]].sum()
                insights.append(f"The top 5 {x_col}s make up {(top_5_sum/total_sum)*100:.1f}% of total {y_cols[0]}. This shows where most of our results are coming from.")
            
            # Pareto analysis
            if len(df) > 1:
                df_sorted = df.sort_values(y_cols[0], ascending=False)
                cumulative_sum = df_sorted[y_cols[0]].cumsum()
                pareto_index = (cumulative_sum / total_sum >= 0.8).idxmax()
                insights.append(f"Just {pareto_index + 1} out of all the {x_col}s account for 80% of the total {y_cols[0]}. This means a small number of {x_col}s have a big impact, and focusing on these could lead to significant improvements.")
            
            # Variance analysis
            if len(df) > 2:
                variance = df[y_cols[0]].var()
                cv = df[y_cols[0]].std() / df[y_cols[0]].mean()
                if cv > 1:
                    insights.append(f"There's a lot of variation in {y_cols[0]} across different {x_col}s. This suggests there might be opportunities to improve consistency or learn from the top performers.")
                elif cv > 0.5:
                    insights.append(f"There's some variation in {y_cols[0]} across different {x_col}s, but it's not extreme. It might be worth looking into what causes these differences.")
                else:
                    insights.append(f"The {y_cols[0]} is fairly consistent across different {x_col}s. This suggests our processes are quite standardized.")
            
            if chart_type == 'grouped bar':
                category_col = df.columns[0]
                group_col = df.columns[1]
                value_col = df.columns[2]
                
                # Identify top performer in each category
                top_performers = df.loc[df.groupby(category_col)[value_col].idxmax()]
                insights.append(f"Top performers in each {category_col}: " + ", ".join([f"{row[category_col]}: {row[group_col]}" for _, row in top_performers.iterrows()]) + ". These might have best practices we can learn from.")
                
                # Identify most consistent performer across categories
                group_ranks = df.groupby([category_col, group_col])[value_col].mean().unstack().rank(ascending=False)
                most_consistent = group_ranks.mean().idxmin()
                insights.append(f"{most_consistent} shows the most consistent performance across all {category_col}s. Their approach might be worth studying.")
        
        elif chart_type == 'line':
            for col in df.columns[1:]:
                start_value = df[col].iloc[0]
                end_value = df[col].iloc[-1]
                change_pct = ((end_value - start_value) / start_value) * 100
                direction = "increased" if change_pct > 0 else "decreased"
                insights.append(f"{col} has {direction} by {abs(change_pct):.1f}% from {start_value:.2f} to {end_value:.2f}. This shows the overall trend over the period we're looking at.")
                
                peak = df[col].max()
                trough = df[col].min()
                insights.append(f"{col} reached its highest point at {peak:.2f} and its lowest at {trough:.2f}. Understanding what caused these peaks and troughs could be valuable.")
                
                # Volatility analysis
                rolling_std = df[col].rolling(window=min(len(df)//4, 30)).std()
                avg_volatility = rolling_std.mean()
                insights.append(f"On average, {col} tends to change by about {avg_volatility:.2f} from one period to the next. This gives us an idea of how stable or unpredictable it is.")
                
                # Trend strength
                x = np.arange(len(df))
                slope, _, r_value, _, _ = stats.linregress(x, df[col])
                trend_strength = r_value ** 2
                trend_direction = "upward" if slope > 0 else "downward"
                insights.append(f"{col} has a {trend_direction} trend. The strength of this trend is {trend_strength:.2f} out of 1, where 1 would be a perfect straight line. This gives us an idea of how consistent the trend is.")
                
                # Acceleration/Deceleration
                pct_changes = df[col].pct_change()
                acceleration = pct_changes.diff()
                if acceleration.mean() > 0:
                    insights.append(f"{col} seems to be growing faster over time. This accelerating growth could be important for future planning.")
                elif acceleration.mean() < 0:
                    insights.append(f"The growth rate of {col} seems to be slowing down over time. We might want to look into why this is happening.")
        
        elif chart_type == 'pie':
            values_col = df.columns[1]
            total = df[values_col].sum()
            top_category = df.nlargest(1, values_col).iloc[0]
            insights.append(f"'{top_category.iloc[0]}' is the largest slice of the pie, making up {(top_category[values_col]/total)*100:.1f}% of the total {values_col}. This shows where most of our attention might need to be focused.")
            
            if len(df) > 3:
                other_pct = (df.nsmallest(len(df)-3, values_col)[values_col].sum() / total) * 100
                insights.append(f"The smaller categories together make up {other_pct:.1f}% of the total. While individually small, together they could be significant.")
            
            # Concentration analysis
            herfindahl_index = ((df[values_col] / total) ** 2).sum()
            if herfindahl_index < 0.15:
                concentration = "very spread out"
            elif herfindahl_index < 0.25:
                concentration = "somewhat concentrated"
            else:
                concentration = "highly concentrated"
            insights.append(f"The distribution is {concentration}. This tells us how evenly or unevenly things are spread across categories.")
            
            # Relative comparisons
            if len(df) > 1:
                second_largest = df.nlargest(2, values_col).iloc[1]
                ratio = top_category[values_col] / second_largest[values_col]
                insights.append(f"The leading category '{top_category.iloc[0]}' is {ratio:.1f} times larger than the second-largest category '{second_largest.iloc[0]}'. This shows how dominant the leader is.")
            
            # Identify underperformers
            average = total / len(df)
            underperformers = df[df[values_col] < average]
            if not underperformers.empty:
                insights.append(f"{len(underperformers)} categories are below the average of {average:.2f}. These might be areas where we could look for improvements.")
    except Exception as e:
        print(f"Error in chart-specific analysis: {e}")

    # Question-specific insights
    try:
        if 'top' in question.lower() and len(df) > 1:
            top_item = df.iloc[0]
            insights.append(f"'{top_item.iloc[0]}' is at the top of the list, with a {df.columns[1]} of {top_item.iloc[1]}. Understanding what makes it successful could be valuable.")
            
            if len(df) >= 3:
                total = df.iloc[:, 1].sum()
                top_three_share = df.iloc[:3, 1].sum() / total * 100
                insights.append(f"The top three items account for {top_three_share:.1f}% of the total. This shows how much impact the leaders have.")

        elif 'average' in question.lower() or 'mean' in question.lower():
            for col in df.select_dtypes(include=[np.number]).columns:
                mean_val = df[col].mean()
                insights.append(f"The average {col} is {mean_val:.2f}. This gives us a general idea of what's typical.")
                
                # Compare to overall average if there's a grouping
                if len(df) > 1:
                    above_average = df[df[col] > mean_val]
                    insights.append(f"{len(above_average)} items are above the average {col}. Looking at what these high performers have in common could be insightful.")
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
            trend = "upward" if overall_change > 0 else "downward"
            insights.append(f"Looking at the big picture, we're seeing an overall {trend} trend in {numeric_cols[0]}, with a {abs(overall_change):.1f}% change from start to finish. This overall direction is important to keep in mind when planning for the future.")
    except Exception as e:
        print(f"Error in overall trend analysis: {e}")

    return " ".join(insights)

def determine_chart_type(df):
    # This is a placeholder function. In practice, you would implement logic here
    # to determine the best chart type based on the data characteristics.
    return "bar"
