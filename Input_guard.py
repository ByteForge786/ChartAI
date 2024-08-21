import streamlit as st
import ctranslate2
import transformers
from huggingface_hub import snapshot_download

@st.cache_resource
def load_model_and_tokenizer():
    model_id = "ByteForge/Defog_llama-3-sqlcoder-8b-ct2-int8_float16"
    model_path = snapshot_download(model_id)
    model = ctranslate2.Generator(model_path)
    tokenizer = transformers.AutoTokenizer.from_pretrained(model_id)
    return model, tokenizer

model, tokenizer = load_model_and_tokenizer()

# Define the prompt
prompt = """
CREATE TABLE stadium (
    stadium_id number,
    location text,
    name text,
    capacity number,
    highest number,
    lowest number,
    average number
)
CREATE TABLE singer (
    singer_id number,
    name text,
    country text,
    song_name text,
    song_release_year text,
    age number,
    is_male others
)
CREATE TABLE concert (
    concert_id number,
    concert_name text,
    theme text,
    stadium_id text,
    year text
)
CREATE TABLE singer_in_concert (
    concert_id number,
    singer_id text
)
-- Using valid SQLite, answer the following questions for the tables provided above.
-- What is the maximum, the average, and the minimum capacity of stadiums ? (Generate 1 Sql query. No explaination needed)
answer:
"""

def generate_sql_query(prompt):
    messages = [
        {"role": "system", "content": "You are SQL Expert. Given a input question and schema, answer with correct sql query"},
        {"role": "user", "content": prompt},
    ]
    input_ids = tokenizer.apply_chat_template(
        messages, 
        tokenize=False, 
        add_generation_prompt=True
    )
    terminators = [
        tokenizer.eos_token_id,
        tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]
    input_tokens = tokenizer.convert_ids_to_tokens(tokenizer.encode(input_ids))
    results = model.generate_batch([input_tokens], include_prompt_in_result=False, max_length=256, sampling_temperature=0.6, sampling_topp=0.9, end_token=terminators)
    output = tokenizer.decode(results[0].sequences_ids[0])
    return output

# Streamlit app
st.title("SQL Query Generator")

if st.button("Generate SQL Query"):
    sql_query = generate_sql_query(prompt)
    st.code(sql_query, language='sql')
