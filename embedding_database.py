import google.generativeai as genai
import numpy as np
import os
import json # Using json for saving/loading the database
import math

# --- Configuration and Setup ---

# Configure the Gemini API key.
# It's best practice to use an environment variable.
# If the environment variable is not set, you can paste your key directly.
try:
    # Get the API key from an environment variable
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    genai.configure(api_key=GOOGLE_API_KEY)
except KeyError:
    print("----------------------------------------------------------------------")
    print("API Key not found in environment variables.")
    print("Please set the GOOGLE_API_KEY environment variable.")
    # Or uncomment the next line and paste your key.
    # genai.configure(api_key="YOUR_API_KEY")
    # For now, we will exit if no key is found.
    exit("Exiting: No API key configured.")
    print("----------------------------------------------------------------------")


# The embedding model to use
EMBEDDING_MODEL = 'embedding-001'
DB_FILE_PATH = 'vectorbig.json'

# --- Core Functions ---

def get_embedding(text):
    """
    Generates an embedding for the given text using the Gemini API.

    Args:
        text (str): The text to embed.

    Returns:
        list[float]: The embedding vector, or None if an error occurs.
    """
    try:
        # The API handles requests where the text is too long by chunking it.
        # Here we assume the text fits within the model's context window for simplicity.
        result = genai.embed_content(
            model=f"models/{EMBEDDING_MODEL}",
            content=text,
            task_type="RETRIEVAL_DOCUMENT" # Use 'RETRIEVAL_DOCUMENT' for items in DB
                                           # and 'RETRIEVAL_QUERY' for search queries.
        )
        return result['embedding']
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return None

def cosine_similarity(vec_a, vec_b):
    """Calculate cosine similarity between two vectors"""
    # Ensure vectors are lists of floats
    vec_a = list(vec_a)
    vec_b = list(vec_b)
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)

# --- Database Management ---

def load_database():
    """Loads the vector database from a JSON file."""
    if os.path.exists(DB_FILE_PATH):
        with open(DB_FILE_PATH, 'r') as f:
            return json.load(f)
    return [] # Return an empty list if the file doesn't exist

def save_database(db):
    """Saves the vector database to a JSON file."""
    with open(DB_FILE_PATH, 'w') as f:
        json.dump(db, f, indent=4)
    print(f"\nDatabase saved to {DB_FILE_PATH}")

def find_existing_chunk(db, text):
    """
    Finds if a chunk with the same text already exists in the database.
    
    Args:
        db (list): The database
        text (str): The text to search for
        
    Returns:
        int: Index of the existing chunk, or -1 if not found
    """
    for i, item in enumerate(db):
        if item['text'] == text:
            return i
    return -1

def add_text_to_db(db, text, author_id):
    """
    Adds text and its embedding to the database, handling duplicates.
    
    Args:
        db (list): The database
        text (str): The text to add
        author_id (str): The author ID to associate with this text
    """
    # Check if this exact text already exists
    existing_index = find_existing_chunk(db, text)
    
    if existing_index >= 0:
        # Text already exists, just add the new author_id to the existing entry
        if author_id not in db[existing_index]['author_ids']:
            db[existing_index]['author_ids'].append(author_id)
            print(f"Added author ID {author_id} to existing chunk.")
            save_database(db)
        else:
            print(f"Author ID {author_id} already associated with this chunk.")
    else:
        # New text, create embedding and add to database
        print(f"\nGetting embedding for: '{text[:100]}...'...")
        embedding = get_embedding(text)
        if embedding:
            db.append({
                'text': text, 
                'vector': embedding, 
                'author_ids': [author_id]
            })
            print("New chunk added to the database.")
            save_database(db)
        else:
            print("Failed to add text to the database.")

def load_author_abstracts_from_json(json_file_path):
    """
    Loads author abstracts from a JSON file and returns the data.
    
    Args:
        json_file_path (str): Path to the JSON file
        
    Returns:
        dict: The loaded JSON data
    """
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return None

def process_author_abstracts(json_file_path):
    """
    Processes author abstracts from JSON file and adds them to the database.
    
    Args:
        json_file_path (str): Path to the JSON file containing author abstracts
    """
    print(f"Loading author abstracts from {json_file_path}...")
    data = load_author_abstracts_from_json(json_file_path)
    
    if not data or 'author_abstracts' not in data:
        print("No author_abstracts found in the JSON file.")
        return
    
    database = load_database()
    author_abstracts = data['author_abstracts']
    
    total_papers = sum(len(papers) for papers in author_abstracts.values())
    processed = 0
    
    print(f"Found {len(author_abstracts)} authors with {total_papers} total papers.")
    
    for author_id, papers in author_abstracts.items():
        print(f"\nProcessing author {author_id} with {len(papers)} papers...")
        
        for paper in papers:
            # Combine title and abstract
            title = paper.get('title', '')
            abstract = paper.get('abstract', '')
            combined_text = f"Title: {title}\nAbstract: {abstract}"
            
            # Add to database
            add_text_to_db(database, combined_text, author_id)
            processed += 1
            
            # Progress update
            if processed % 10 == 0:
                print(f"Processed {processed}/{total_papers} papers...")
    
    print(f"\nCompleted processing {processed} papers from {len(author_abstracts)} authors.")
    print(f"Database now contains {len(database)} unique chunks.")

def search_db(db, query_text, top_n=3):
    """Searches the database for text similar to the query."""
    if not db:
        print("Database is empty. Please add some text first.")
        return

    print(f"\nGetting embedding for search query: '{query_text}'...")
    # Use 'RETRIEVAL_QUERY' for the search query embedding
    query_vector = genai.embed_content(
        model=f"models/{EMBEDDING_MODEL}",
        content=query_text,
        task_type="RETRIEVAL_QUERY"
    )['embedding']
    
    if not query_vector:
        print("Could not get embedding for the search query.")
        return

    # Calculate similarities
    results = []
    for item in db:
        similarity = cosine_similarity(query_vector, item['vector'])
        results.append({
            'text': item['text'], 
            'similarity': similarity,
            'author_ids': item['author_ids']
        })

    # Sort results by similarity in descending order
    results.sort(key=lambda x: x['similarity'], reverse=True)

    # Display top N results
    print("\n--- Search Results ---")
    for i, result in enumerate(results[:top_n]):
        print(f"\n{i+1}. Similarity: {result['similarity']:.4f}")
        print(f"   Author IDs: {', '.join(result['author_ids'])}")
        print(f"   Text: {result['text'][:200]}...")
    print("----------------------")

# --- Main Application Loop ---

def main():
    """The main function to run the interactive command-line interface."""
    database = load_database()
    print("--- Local Vector DB ---")
    print(f"Loaded {len(database)} items from {DB_FILE_PATH}")

    while True:
        print("\nWhat would you like to do?")
        print("1. Load author abstracts from JSON file")
        print("2. Add new text to the database")
        print("3. Search the database")
        print("4. View all items in the database")
        print("5. View statistics")
        print("6. Exit")
        
        choice = input("Enter your choice (1/2/3/4/5/6): ")

        if choice == '1':
            json_path = input("Enter the path to the JSON file: ")
            process_author_abstracts(json_path)
        elif choice == '2':
            text = input("Enter the text to add: ")
            author_id = input("Enter the author ID: ")
            add_text_to_db(database, text, author_id)
        elif choice == '3':
            query = input("Enter your search query: ")
            search_db(database, query)
        elif choice == '4':
            print("\n--- All Database Items ---")
            if not database:
                print("The database is empty.")
            else:
                for i, item in enumerate(database):
                    print(f"{i+1}. Author IDs: {', '.join(item['author_ids'])}")
                    print(f"   Text: {item['text'][:100]}...")
                    print()
            print("--------------------------")
        elif choice == '5':
            print("\n--- Database Statistics ---")
            if not database:
                print("The database is empty.")
            else:
                total_chunks = len(database)
                all_author_ids = set()
                for item in database:
                    all_author_ids.update(item['author_ids'])
                
                print(f"Total unique chunks: {total_chunks}")
                print(f"Total unique authors: {len(all_author_ids)}")
                print(f"Average authors per chunk: {len(all_author_ids) / total_chunks:.2f}")
                
                # Show chunks with multiple authors
                multi_author_chunks = [item for item in database if len(item['author_ids']) > 1]
                if multi_author_chunks:
                    print(f"Chunks with multiple authors: {len(multi_author_chunks)}")
                    for item in multi_author_chunks:
                        print(f"  - {len(item['author_ids'])} authors: {', '.join(item['author_ids'])}")
            print("--------------------------")
        elif choice == '6':
            print("Exiting. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
