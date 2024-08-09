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

# ... [Previous imports, constants, and functions remain the same]

# Modify the init_app function
def init_app():
    init_csv()
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    if 'session_id' not in st.session_state:
        st.session_state['session_id'] = generate_session_id()
    if 'last_question' not in st.session_state:
        st.session_state['last_question'] = None
    if 'show_chart' not in st.session_state:
        st.session_state['show_chart'] = False
    if 'current_result_df' not in st.session_state:
        st.session_state['current_result_df'] = None

# Main app
def main():
    init_app()

    # ... [Previous code for date selection and logo remains the same]

    # Display chat history
    for entry in st.session_state['chat_history']:
        with st.chat_message(name="user", avatar="user"):
            st.markdown(entry['question'])
        with st.chat_message(name="assistant", avatar="assistant"):
            st.code(entry['sql_query'], language="sql")
            st.dataframe(entry['result'])
            if entry.get('chart'):
                st.plotly_chart(entry['chart'], use_container_width=True)

    with st.chat_message(name="user", avatar="user"):
        user_input_placeholder = st.empty()
    with st.chat_message(name="assistant", avatar="assistant"):
        bot_response_1_placeholder = st.empty()
        bot_response_2_placeholder = st.empty()
        chart_placeholder = st.empty()

    user_input = st.text_area("Enter your question about the data:")

    button_column = st.columns(3)
    button_info = st.empty()

    with button_column[2]:
        if st.button("🚀 Generate SQL", key="generate_sql", use_container_width=True):
            st.session_state['show_chart'] = False  # Reset chart state
            if user_input:
                user_input_placeholder.markdown(user_input)
                try:
                    with st.spinner("Generating SQL..."):
                        sql_response = generate_sql(user_input)
                    bot_response_1_placeholder.code(sql_response, language="sql")
                    result_df = execute_query(sql_response)
                    st.session_state['current_result_df'] = result_df  # Store the result
                    bot_response_2_placeholder.dataframe(result_df)
                    
                    handle_interaction(user_input, sql_response)
                    add_to_chat_history(user_input, sql_response, result_df)
                except Exception as e:
                    logging.error(f"Error processing query: {str(e)}")
                    st.error("An error occurred while processing your query. Please try again.")

    # Add a button to show/hide the chart
    if st.session_state['current_result_df'] is not None:
        if st.button("📊 Toggle Chart", key="toggle_chart"):
            st.session_state['show_chart'] = not st.session_state['show_chart']
        
        if st.session_state['show_chart']:
            with st.spinner("Generating chart..."):
                chart = generate_chart(st.session_state['current_result_df'], None)  # You may want to add chart recommendation logic
            chart_placeholder.plotly_chart(chart, use_container_width=True)
            
            # Update the last entry in chat history to include the chart
            if st.session_state['chat_history']:
                st.session_state['chat_history'][-1]['chart'] = chart

    # ... [The rest of the code for upvote, downvote, and sample questions remains the same]

if __name__ == "__main__":
    main()
