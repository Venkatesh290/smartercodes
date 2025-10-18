# Web Search SPA

A single-page application that allows users to input a website URL and a search query to retrieve the top 10 matches of HTML DOM content chunks based on semantic search.

## Features

- Frontend: Next.js with TypeScript and Tailwind CSS
- Backend: FastAPI with HTML parsing, tokenization, and vector search
- Vector Database: Weaviate (embedded for simplicity)
- Semantic search using sentence transformers

## Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- Docker (for Weaviate, optional if using embedded)

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd web-search-spa/backend
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd web-search-spa/frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

## Running the Application

1. Start the backend server:
   ```
   cd web-search-spa/backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. In a new terminal, start the frontend:
   ```
   cd web-search-spa/frontend
   npm run dev
   ```

3. Open your browser and go to `http://localhost:3000`

## Usage

1. Enter a website URL (e.g., https://example.com)
2. Enter a search query (e.g., "about us")
3. Click "Search"
4. View the top 10 matching HTML content chunks

## API Endpoint

- POST `/search`: Accepts JSON with `url` and `query` fields, returns top 10 matches

## Technologies Used

- Frontend: Next.js, TypeScript, Tailwind CSS
- Backend: FastAPI, BeautifulSoup, tiktoken, sentence-transformers, Weaviate
- Vector Search: Weaviate with embedded option
