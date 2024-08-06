import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats

# Import the function to be tested
from your_module import analyze_query_results  # Replace 'your_module' with the actual module name

# Sample dataframes for testing

# Bar Chart
df_bar = pd.DataFrame({
    'Category': ['A', 'B', 'C', 'D', 'E'],
    'Value': [100, 80, 60, 40, 20]
})

# Grouped Bar Chart
df_grouped_bar = pd.DataFrame({
    'Category': ['X', 'X', 'Y', 'Y', 'Z', 'Z'],
    'Group': ['P', 'Q', 'P', 'Q', 'P', 'Q'],
    'Value': [30, 40, 50, 45, 60, 55]
})

# Line Chart
dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='M')
df_line = pd.DataFrame({
    'Date': dates,
    'Metric1': np.random.randint(100, 200, size=len(dates)),
    'Metric2': np.random.randint(50, 150, size=len(dates))
})

# Pie Chart
df_pie = pd.DataFrame({
    'Category': ['A', 'B', 'C', 'D', 'E'],
    'Value': [35, 25, 20, 15, 5]
})

# Time Series
df_time_series = pd.DataFrame({
    'Date': pd.date_range(start='2023-01-01', end='2023-12-31', freq='D'),
    'Value': np.cumsum(np.random.randn(365))
})

# Test cases
test_cases = [
    (df_bar, "What are the top categories by value?", "bar"),
    (df_grouped_bar, "How do different groups perform across categories?", "grouped bar"),
    (df_line, "How have the metrics changed over time?", "line"),
    (df_pie, "What is the distribution of values across categories?", "pie"),
    (df_bar, "What is the average value across categories?", "bar"),
    (df_time_series, "What is the overall trend in the time series?", "line")
]

# Run tests
for df, question, chart_type in test_cases:
    print(f"\nTesting {chart_type} chart:")
    print("DataFrame:")
    print(df)
    print("\nQuestion:", question)
    insights = analyze_query_results(df, question, chart_type)
    print("\nInsights:")
    print(insights)
    print("-" * 50)

# Additional test for Pareto principle
df_pareto = pd.DataFrame({
    'Category': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'],
    'Value': [100, 80, 60, 40, 20, 10, 5, 3, 2, 1]
})
print("\nTesting Pareto principle:")
print("DataFrame:")
print(df_pareto)
print("\nQuestion: What is the Pareto distribution?")
insights = analyze_query_results(df_pareto, "What is the Pareto distribution?", "bar")
print("\nInsights:")
print(insights)
print("-" * 50)

# Test for variance analysis
df_variance = pd.DataFrame({
    'Category': ['A', 'B', 'C', 'D', 'E'],
    'Value': [100, 90, 50, 30, 10]
})
print("\nTesting variance analysis:")
print("DataFrame:")
print(df_variance)
print("\nQuestion: What is the variance in values?")
insights = analyze_query_results(df_variance, "What is the variance in values?", "bar")
print("\nInsights:")
print(insights)
print("-" * 50)
