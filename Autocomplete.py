import streamlit as st
import pandas as pd
import plotly.express as px
import re
import logging
import ctranslate2
import transformers
from huggingface_hub import snapshot_download
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache the models
@st.cache_resource
def load_models():
    try:
        model_id = "ByteForge/Defog_llama-3-sqlcoder-8b-ct2-int8_float16"
        model_path = snapshot_download(model_id)
        llm = ctranslate2.Generator(model_path)
        tokenizer = transformers.AutoTokenizer.from_pretrained(model_id)
        encoder = SentenceTransformer('all-MiniLM-L6-v2')
        return llm, tokenizer, encoder
    except Exception as e:
        logger.error(f"Failed to load models: {str(e)}")
        st.error("Failed to load models. Please check the logs for details.")
        return None, None, None

# Initialize FAISS index
def init_faiss_index(encoder, column_info):
    embeddings = encoder.encode(column_info)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings.astype('float32'))
    return index

# Retrieve relevant column information
def retrieve_column_info(query, index, encoder, column_info, k=5):
    query_vector = encoder.encode([query])
    _, I = index.search(query_vector.astype('float32'), k)
    return [column_info[i] for i in I[0]]

# Reformulate question using retrieved column info
def reformulate_question(question, column_info, llm, tokenizer):
    prompt = f"""
    Given the following column information:
    {column_info}
    
    Reformulate the following question using the proper column names and sample values:
    {question}
    
    Reformulated question:
    """
    
    input_tokens = tokenizer.convert_ids_to_tokens(tokenizer.encode(prompt))
    results = llm.generate_batch([input_tokens], max_length=1024, sampling_topk=1)
    reformulated_question = tokenizer.decode(results[0].sequences_ids[0])
    
    return reformulated_question.strip()

# Your existing functions here (get_model_response, get_sql_query_from_response, etc.)

# Streamlit app
def main():
    st.set_page_config(page_title="Data Query and Visualization App", layout="wide")

    st.title("Data Query and Visualization App")

    # Load cached models
    llm, tokenizer, encoder = load_models()

    if llm is None or tokenizer is None or encoder is None:
        st.stop()

    # Initialize FAISS index (you would do this with your actual database schema)
    column_info = [
        "date (YYYY-MM-DD): sample value 2023-08-04",
        "product_category (string): sample values Electronics, Clothing, Food",
        "sales_amount (float): sample values 1250.50, 750.25, 500.00",
        "customer_age (integer): sample values 25, 35, 45",
        # Add more column information as needed
    ]
    index = init_faiss_index(encoder, column_info)

    # User input
    question = st.text_input("Enter your question:")

    if st.button("Submit"):
        if question:
            with st.spinner("Processing your question..."):
                # Retrieve relevant column info
                relevant_info = retrieve_column_info(question, index, encoder, column_info)
                
                # Reformulate question
                reformulated_question = reformulate_question(question, relevant_info, llm, tokenizer)
                
                st.subheader("Reformulated Question:")
                st.write(reformulated_question)

                # Generate SQL query (using your existing function)
                sql_query = get_sql_query_from_response(reformulated_question)
                
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
                            generate_chart(result_df, get_chart_recommendation_from_response(reformulated_question))
                    else:
                        st.warning("No results found for the given query.")
                else:
                    st.error("Could not generate a valid SQL query.")
        else:
            st.warning("Please enter a question.")

if __name__ == "__main__":
    main()
