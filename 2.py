import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import streamlit as st
import os
from datetime import datetime, date, timedelta
import hashlib
import logging
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ... (keep all the existing imports and functions)

# Add the generate_chart function here
def generate_chart(df, chart_recommendation):
    # ... (paste the entire generate_chart function here)

# Update the add_to_chat_history function
def add_to_chat_history(question, sql_query, result_df):
    chart = generate_chart(result_df, None)
    st.session_state['chat_history'].append({
        'question': question,
        'sql_query': sql_query,
        'result_df': result_df,
        'chart': chart
    })

# Update the main function
def main():
    init_app()

    # ... (keep all the existing code up to the chat history display)

    # Display chat history
    for entry in st.session_state['chat_history']:
        with st.chat_message(name="user", avatar="user"):
            st.markdown(entry['question'])
        with st.chat_message(name="assistant", avatar="assistant"):
            st.code(entry['sql_query'], language="sql")
            st.dataframe(entry['result_df'])
            if entry['chart'] is not None:
                st.plotly_chart(entry['chart'], use_container_width=True)

    with st.chat_message(name="user", avatar="user"):
        user_input_placeholder = st.empty()
    with st.chat_message(name="assistant", avatar="assistant"):
        bot_response_1_placeholder = st.empty()
        bot_response_2_placeholder = st.empty()
        bot_response_3_placeholder = st.empty()

    user_input = st.text_area("Enter your question about the data:")

    button_column = st.columns(3)
    button_info = st.empty()

    with button_column[2]:
        if st.button("🚀 Generate SQL", key="generate_sql", use_container_width=True):
            if user_input:
                user_input_placeholder.markdown(user_input)
                try:
                    with st.spinner("Generating SQL..."):
                        sql_response = generate_sql(user_input)
                    bot_response_1_placeholder.code(sql_response, language="sql")
                    result_df = execute_query(sql_response)
                    bot_response_2_placeholder.dataframe(result_df)
                    
                    # Generate and display chart
                    chart = generate_chart(result_df, None)
                    if chart is not None:
                        bot_response_3_placeholder.plotly_chart(chart, use_container_width=True)
                    
                    handle_interaction(user_input, sql_response)
                    add_to_chat_history(user_input, sql_response, result_df)
                except Exception as e:
                    logging.error(f"Error processing query: {str(e)}")
                    st.error("An error occurred while processing your query. Please try again.")

    # ... (keep the rest of the existing code)

if __name__ == "__main__":
    main()
