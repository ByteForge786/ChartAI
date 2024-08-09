import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Add this after bot_response_2_placeholder.dataframe(result_df)
chart_placeholder = st.empty()

# Modify the execute_query function to return both the dataframe and a chart recommendation
def execute_query(sql):
    # This is a mock implementation. Replace with actual query execution.
    df = pd.DataFrame({'Column1': ['Data1', 'Data2'], 'Column2': [1, 2]})
    chart_recommendation = "bar"  # This should be determined by your SQL generation logic
    return df, chart_recommendation

# In the part where you process the query, modify it like this:
result_df, chart_recommendation = execute_query(sql_response)
bot_response_2_placeholder.dataframe(result_df)

# Generate and display the chart
with st.spinner("Generating visualization..."):
    generate_chart(result_df, chart_recommendation)
    
# Add this line to display the chart in the placeholder
chart_placeholder.plotly_chart(fig, use_container_width=True)

try:
    with st.spinner("Generating visualization..."):
        generate_chart(result_df, chart_recommendation)
        chart_placeholder.plotly_chart(fig, use_container_width=True)
except Exception as e:
    logging.error(f"Error generating chart: {str(e)}")
    st.error("An error occurred while generating the chart.")


def add_to_chat_history(question, sql_query, result, chart):
    st.session_state['chat_history'].append({
        'question': question,
        'sql_query': sql_query,
        'result': result,
        'chart': chart
    })


for entry in st.session_state['chat_history']:
    with st.chat_message(name="user", avatar="user"):
        st.markdown(entry['question'])
    with st.chat_message(name="assistant", avatar="assistant"):
        st.code(entry['sql_query'], language="sql")
        st.dataframe(entry['result'])
        if entry['chart'] is not None:
            st.plotly_chart(entry['chart'], use_container_width=True)
