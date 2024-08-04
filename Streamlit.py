import streamlit as st
import pandas as pd
import plotly.express as px
import re
import logging
import ctranslate2
import transformers
from huggingface_hub import snapshot_download

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache the model
@st.cache_resource
def load_model():
    try:
        model_id = "ByteForge/Defog_llama-3-sqlcoder-8b-ct2-int8_float16"
        model_path = snapshot_download(model_id)
        model = ctranslate2.Generator(model_path)
        tokenizer = transformers.AutoTokenizer.from_pretrained(model_id)
        return model, tokenizer
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        st.error("Failed to load model. Please check the logs for details.")
        return None, None

def get_model_response(question, prompt, model, tokenizer):
    try:
        full_prompt = prompt + question
        input_tokens = tokenizer.convert_ids_to_tokens(tokenizer.encode(full_prompt))
        results = model.generate_batch([input_tokens], max_length=1024, sampling_topk=10)
        output_text = tokenizer.decode(results[0].sequences_ids[0])
        return output_text
    except Exception as e:
        logger.error(f"Error getting model response: {str(e)}")
        st.error("Failed to get a response from the model. Please check the logs for details.")
        return None

def get_sql_query_from_response(response):
    match = re.search(r'```sql\n(.*?)\n```', response, re.DOTALL)
    return match.group(1) if match else None

def get_chart_recommendation_from_response(response):
    match = re.search(r'Chart recommendation: (.*?)$', response, re.MULTILINE)
    return match.group(1) if match else None

def determine_chart_type(df):
    if len(df.columns) == 2:
        if df.dtypes[1] in ['int64', 'float64'] and len(df) > 1:
            return 'bar'
        elif df.dtypes[1] in ['int64', 'float64'] and len(df) <= 10:
            return 'pie'
    elif len(df.columns) >= 3 and df.dtypes[1] in ['int64', 'float64']:
        return 'line'
    return None

def generate_chart(df, chart_recommendation):
    if chart_recommendation is None:
        chart_type = determine_chart_type(df)
    else:
        chart_type = chart_recommendation.split('(')[0].strip().lower()

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
        st.write(f"Chart type '{chart_type}' not supported or could not be determined. Displaying data in table format:")
        st.table(df)
        return

    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

# Streamlit app
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
                        'Column1': ['A', 'B', 'C'],
                        'Column2': [10, 20, 30]
                    })

                if not result_df.empty:
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("Query Results:")
                        st.dataframe(result_df)

                    with col2:
                        st.subheader("Visualization:")
                        generate_chart(result_df, chart_recommendation)
                else:
                    st.warning("No results found for the given query.")
            else:
                st.error("Could not generate a valid SQL query.")
        else:
            st.warning("Please enter a question.")

if __name__ == "__main__":
    main()
