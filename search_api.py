from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
import numpy as np
import json
import os
from dotenv import load_dotenv

# Load environment variables from config.env
load_dotenv('config.env')

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure Gemini API from environment
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in config.env")

genai.configure(api_key=GOOGLE_API_KEY)
EMBEDDING_MODEL = 'embedding-001'

# Load vector database
def load_vector_database():
    try:
        with open('static/vector_database.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading vector database: {e}")
        return []

vector_database = load_vector_database()
print(f"Loaded {len(vector_database)} entries from vector database")

def get_embedding(text):
    """Generate embedding for text using Gemini API"""
    try:
        result = genai.embed_content(
            model=f"models/{EMBEDDING_MODEL}",
            content=text,
            task_type="RETRIEVAL_QUERY"
        )
        return result['embedding']
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return None

def cosine_similarity(vec_a, vec_b):
    """Calculate cosine similarity between two vectors"""
    vec_a = np.array(vec_a)
    vec_b = np.array(vec_b)
    
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
        
    return dot_product / (norm_a * norm_b)

@app.route('/search', methods=['POST'])
def search():
    """Search endpoint that performs semantic search"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        print(f"Searching for: {query}")
        
        # Generate embedding for the query
        query_embedding = get_embedding(query)
        if not query_embedding:
            return jsonify({'error': 'Failed to generate query embedding'}), 500
        
        # Calculate similarities with all database entries
        results = []
        for item in vector_database:
            similarity = cosine_similarity(query_embedding, item['vector'])
            if similarity > 0.1:  # Only include results with similarity > 0.1
                for author_id in item['author_ids']:
                    results.append({
                        'author_id': author_id,
                        'similarity': similarity,
                        'text': item['text'][:200] + '...' if len(item['text']) > 200 else item['text']
                    })
        
        # Group by author_id and take the highest similarity for each author
        author_results = {}
        for result in results:
            author_id = result['author_id']
            if author_id not in author_results or result['similarity'] > author_results[author_id]['similarity']:
                author_results[author_id] = result
        
        # Convert back to list and sort by similarity
        final_results = list(author_results.values())
        final_results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Take top 20 results
        final_results = final_results[:20]
        
        print(f"Found {len(final_results)} results")
        
        return jsonify({
            'query': query,
            'results': final_results,
            'total_found': len(final_results)
        })
        
    except Exception as e:
        print(f"Error in search: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'database_entries': len(vector_database)
    })

@app.route('/')
def serve_force_graph():
    return send_from_directory('static', 'force_graph.html')

if __name__ == '__main__':
    print("Starting search API server...")
    print(f"Vector database loaded with {len(vector_database)} entries")
    app.run(host='0.0.0.0', port=5000, debug=True) 