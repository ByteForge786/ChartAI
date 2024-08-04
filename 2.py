import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import streamlit as st

# Load the sentence transformer model
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

def create_faiss_index(embeddings):
    """Create a FAISS index for the given embeddings."""
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype('float32'))
    return index

def search_faiss_index(index, query_embedding, k=5):
    """Search the FAISS index for the k most similar embeddings."""
    distances, indices = index.search(query_embedding.astype('float32'), k)
    return indices[0]

def process_categorical_schema(schema):
    """Process the categorical columns in the schema and create FAISS indices."""
    column_names = []
    column_values = []
    value_to_column = {}
    
    for column, values in schema.items():
        column_names.append(column)
        for value in values:
            column_values.append(value)
            value_to_column[value] = column
    
    # Create embeddings
    column_name_embeddings = model.encode(column_names)
    column_value_embeddings = model.encode(column_values)
    
    # Create FAISS indices
    column_name_index = create_faiss_index(column_name_embeddings)
    column_value_index = create_faiss_index(column_value_embeddings)
    
    return column_name_index, column_value_index, column_names, column_values, value_to_column

def answer_question(question, schema):
    """Answer the question based on the categorical schema."""
    # Process schema and create indices
    column_name_index, column_value_index, column_names, column_values, value_to_column = process_categorical_schema(schema)
    
    # Encode the question
    question_embedding = model.encode([question])
    
    # Search for similar column names
    column_indices = search_faiss_index(column_name_index, question_embedding)
    relevant_columns = [column_names[i] for i in column_indices]
    
    # Search for similar values
    value_indices = search_faiss_index(column_value_index, question_embedding)
    relevant_values = [column_values[i] for i in value_indices]
    
    # Combine results
    result = {}
    for value in relevant_values:
        column = value_to_column[value]
        if column in relevant_columns and column not in result:
            result[column] = value
    
    return result

# Streamlit app
def main():
    st.title("Categorical Data Query Assistant")

    # Define your schema with categorical columns
    schema = {
        "product_category": ["electronics", "clothing", "food", "books", "toys"],
        "customer_segment": ["young adult", "middle-aged", "senior", "teen"],
        "region": ["north", "south", "east", "west"],
        "payment_method": ["credit card", "debit card", "cash", "digital wallet"]
    }

    # User input
    question = st.text_input("Enter your question:")

    if st.button("Submit"):
        if question:
            with st.spinner("Processing your question..."):
                answer = answer_question(question, schema)
                
                st.subheader("Relevant Categorical Columns and Values:")
                if answer:
                    for column, value in answer.items():
                        st.write(f"{column}: {value}")
                else:
                    st.write("No relevant categorical information found.")
        else:
            st.warning("Please enter a question.")

if __name__ == "__main__":
    main()
