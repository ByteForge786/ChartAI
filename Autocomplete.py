import streamlit as st

# Mock data for suggestions
MOCK_COLUMNS = ['CompanyName', 'EmployeeCount', 'Revenue', 'Industry', 'FoundedYear']
MOCK_VALUES = {
    'CompanyName': ['Apple', 'Google', 'Microsoft'],
    'Industry': ['Tech', 'Finance', 'Healthcare'],
    'FoundedYear': ['1976', '1998', '1975']
}

def get_suggestions(input_text):
    suggestions = []
    input_lower = input_text.lower()
    
    # Suggest columns
    for col in MOCK_COLUMNS:
        if col.lower().startswith(input_lower):
            suggestions.append(col)
    
    # Suggest values
    for col, values in MOCK_VALUES.items():
        if col.lower().startswith(input_lower):
            suggestions.extend([f"{col}: {value}" for value in values])
        else:
            for value in values:
                if value.lower().startswith(input_lower):
                    suggestions.append(f"{col}: {value}")
    
    return suggestions

def on_input_change():
    current_input = st.session_state.question_input
    words = current_input.split()
    if words:
        last_word = words[-1]
        suggestions = get_suggestions(last_word)
        st.session_state.suggestions = suggestions
    else:
        st.session_state.suggestions = []

def main():
    st.title("Auto-completion Demo")

    # Initialize session state for suggestions
    if 'suggestions' not in st.session_state:
        st.session_state.suggestions = []

    # User input with auto-completion
    question = st.text_input("Enter your question:", key="question_input", on_change=on_input_change)

    # Display suggestions
    if st.session_state.suggestions:
        suggestion = st.selectbox("Suggestions:", [""] + st.session_state.suggestions)
        if suggestion:
            if st.button("Use Suggestion"):
                words = st.session_state.question_input.split()
                words[-1] = suggestion
                st.session_state.question_input = " ".join(words)
                st.experimental_rerun()

    # Display the current question for demonstration
    if question:
        st.write("Current question:", question)

if __name__ == "__main__":
    main()
