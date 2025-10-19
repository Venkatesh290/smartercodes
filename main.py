from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import weaviate
from weaviate.embedded import EmbeddedOptions
import uuid

app = FastAPI()

# Initialize Weaviate client (embedded for simplicity)
client = weaviate.Client(embedded_options=EmbeddedOptions())

# Initialize sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

class SearchRequest(BaseModel):
    url: str
    query: str

def clean_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Remove scripts and styles
    for script in soup(["script", "style"]):
        script.extract()
    # Get text
    text = soup.get_text()
    # Clean up whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    return text

def chunk_text(text, max_tokens=500):
    words = text.split()
    chunks = []
    current_chunk = []
    current_tokens = 0

    for word in words:
        # Approximate token count by word length (rough estimate)
        word_tokens = len(word) // 4 + 1  # Simple heuristic
        if current_tokens + word_tokens > max_tokens:
            if current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_tokens = 0
        current_chunk.append(word)
        current_tokens += word_tokens

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

@app.post("/search")
async def search(request: SearchRequest):
    try:
        # Fetch HTML content
        response = requests.get(request.url)
        response.raise_for_status()
        html_content = response.text

        # Clean HTML
        cleaned_text = clean_html(html_content)

        # Chunk the text
        chunks = chunk_text(cleaned_text)

        # Create class if not exists
        class_name = "HtmlChunk"
        if not client.schema.exists(class_name):
            class_obj = {
                "class": class_name,
                "properties": [
                    {"name": "content", "dataType": ["text"]},
                    {"name": "url", "dataType": ["string"]}
                ]
            }
            client.schema.create_class(class_obj)

        # Clear existing data for this URL (simple implementation)
        client.batch.delete_objects(class_name, where={"path": ["url"], "operator": "Equal", "valueString": request.url})

        # Embed and store chunks
        embeddings = model.encode(chunks)
        with client.batch as batch:
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                properties = {
                    "content": chunk,
                    "url": request.url
                }
                batch.add_data_object(properties, class_name, vector=embedding.tolist())

        # Perform semantic search
        query_embedding = model.encode([request.query])[0]
        result = client.query.get(class_name, ["content"]).with_near_vector({
            "vector": query_embedding.tolist(),
            "certainty": 0.7
        }).with_limit(10).do()

        matches = [item['content'] for item in result['data']['Get'][class_name]]

        return {"matches": matches}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
