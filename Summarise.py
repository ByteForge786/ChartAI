import pandas as pd
from transformers import pipeline

# Load your CSV data into a DataFrame
df = pd.read_csv("your_data.csv")

# Example DataFrame for demonstration
# df = pd.DataFrame({
#     'date': pd.date_range(start='2023-01-01', periods=10, freq='D'),
#     'exception_count': [10, 15, 12, 9, 18, 17, 25, 20, 30, 28]
# })

# Initialize the Hugging Face pipeline for text generation
text_generator = pipeline("text-generation", model="gpt-3.5-turbo")

# Convert DataFrame to a string format understandable by the LLM
def df_to_prompt(df):
    prompt = "Here is the data:\n"
    prompt += df.to_string(index=False)
    prompt += "\n\nPlease analyze this data and summarize the insights, such as identifying highs and lows, trends, and any other interesting observations."
    return prompt

# Generate the analysis and summary using the LLM
def generate_summary(df):
    prompt = df_to_prompt(df)
    response = text_generator(prompt, max_length=200)[0]['generated_text']
    return response

# Generate and print the summary
summary = generate_summary(df)
print(summary)
