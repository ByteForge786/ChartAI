import ctranslate2
import transformers
from huggingface_hub import snapshot_download

model_id = "ByteForge/Defog_llama-3-sqlcoder-8b-ct2-int8_float16"
model_path = snapshot_download(model_id)
model = ctranslate2.Generator(model_path)
tokenizer = transformers.AutoTokenizer.from_pretrained(model_id)

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
-- What is the maximum, the average, and the minimum capacity of stadiums ? (Generate 1 Sql query. No explanation needed)
answer:
"""

# Encode the prompt to get token IDs
input_ids = tokenizer.encode(prompt, return_tensors='pt')
# Count the number of tokens
num_tokens = input_ids.size(-1)

print(f"Number of tokens: {num_tokens}")
