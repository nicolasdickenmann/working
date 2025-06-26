from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS, cross_origin
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from config.env (for local development)
# For Vercel, environment variables will be set in the Vercel dashboard
if os.path.exists('config.env'):
    load_dotenv('config.env')

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure Gemini API from environment
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

genai.configure(api_key=GOOGLE_API_KEY)
EMBEDDING_MODEL = 'embedding-001'

# Configure Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials not found in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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
    import math
    # Ensure vectors are lists of floats
    vec_a = list(vec_a)
    vec_b = list(vec_b)
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)

# Add this helper function to collect all texts for an author
def get_author_texts(author_id):
    """Get all texts for an author from Supabase"""
    try:
        response = supabase.table('embeddings').select('text').contains('author_ids', [author_id]).execute()
        return [item['text'] for item in response.data]
    except Exception as e:
        print(f"Error getting author texts: {e}")
        return []

@app.route('/search', methods=['POST'])
def search():
    """Search endpoint that performs semantic search using Supabase"""
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
        
        # Search in Supabase using vector similarity
        try:
            response = supabase.rpc(
                'match_embeddings',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': 0.1,
                    'match_count': 200
                }
            ).execute()
            
            results = []
            for item in response.data:
                for author_id in item['author_ids']:
                    results.append({
                        'author_id': author_id,
                        'similarity': item['similarity'],
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
            
            print(f"Found {len(final_results)} results")
            
            return jsonify({
                'query': query,
                'results': final_results,
                'total_found': len(final_results)
            })
            
        except Exception as e:
            print(f"Error searching Supabase: {e}")
            return jsonify({'error': 'Database search failed'}), 500
        
    except Exception as e:
        print(f"Error in search: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        # Check if we can connect to Supabase
        response = supabase.table('embeddings').select('id', count='exact').limit(1).execute()
        count = response.count if response.count is not None else 0
        return jsonify({
            'status': 'healthy',
            'database_entries': count,
            'database_type': 'supabase_pgvector'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'database_type': 'supabase_pgvector'
        }), 500

@app.route('/')
def serve_force_graph():
    return send_from_directory('static', 'force_graph.html')

@app.route('/explain_match', methods=['POST', 'OPTIONS'])
@cross_origin(origins="*")
def explain_match():
    if request.method == 'OPTIONS':
        return '', 200
    data = request.json
    query = data.get('query')
    author_id = data.get('author_id')

    # Gather all research texts for this author
    author_texts = get_author_texts(author_id)
    if not author_texts:
        return jsonify({'explanation': "No research texts found for this professor."})

    # Compose a prompt for Gemini
    prompt = (
        "You are an expert academic assistant. Your output will be shown on a card for a specific professor. "
        "Always make an effort to connect the user's search query to the professor's research interests, even if the connection is not obvious. "
        "Be creative and imaginative in finding possible links between the search and the research. "
        "Do NOT simply say there is no similarity; instead, try to find any plausible or tangential connection. "
        "Only explain why THIS professor matches the user's search, quoting or paraphrasing relevant research below. "
        "Do NOT suggest searching for other professors or topics. "
        "Be friendly, helpful, and use first or second person (e.g., 'You might be interested in this professor's work...'). "
        f"\n\nUser's search: '{query}'\n"
        f"Professor's research abstracts:\n"
        + "\n---\n".join(author_texts[:5]) +
        "\n\nIn 2-3 sentences, explain to the user why this professor matches their search, quoting or paraphrasing relevant research."
    )

    # Call Gemini
    try:
        model = genai.GenerativeModel('models/gemini-1.5-pro')
        response = model.generate_content(prompt)
        explanation = response.text
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        explanation = "Could not generate explanation at this time."

    return jsonify({'explanation': explanation}) 