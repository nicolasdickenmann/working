#!/usr/bin/env python3
"""
Script to regenerate embeddings with the new gemini-embedding-001 model
and populate Supabase with the correct 3072-dimensional vectors.
"""

import json
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import google.generativeai as genai

# Load environment variables
load_dotenv('config.env')

# Configure APIs
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials not found in environment variables")

genai.configure(api_key=GOOGLE_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Use the new embedding model
EMBEDDING_MODEL = 'gemini-embedding-001'

def get_embedding(text):
    """Generate embedding for text using the new Gemini model"""
    try:
        result = genai.embed_content(
            model=f"models/{EMBEDDING_MODEL}",
            content=text,
            task_type="RETRIEVAL_DOCUMENT"
        )
        return result['embedding']
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return None

def regenerate_from_source_data():
    """Regenerate embeddings from your source data files"""

    # Try to find your source data file
    source_files = [
        'nicolasdata/author_abstracts_5.json',
        'datascripts/merged_author_abstracts.json',
        'datascripts/converted_author_data.json'
    ]

    source_file = None
    for file_path in source_files:
        if os.path.exists(file_path):
            source_file = file_path
            break

    if not source_file:
        print("Error: No source data file found!")
        print("Looked for:", source_files)
        return

    print(f"Loading source data from {source_file}...")

    with open(source_file, 'r') as f:
        data = json.load(f)

    # Handle different data formats
    if 'author_abstracts' in data:
        author_abstracts = data['author_abstracts']
    else:
        print("Error: Expected 'author_abstracts' key in JSON data")
        return

    print(f"Found {len(author_abstracts)} authors")

    total_papers = sum(len(papers) for papers in author_abstracts.values())
    print(f"Total papers to process: {total_papers}")

    processed = 0
    batch_data = []
    batch_size = 10  # Small batches to handle rate limits

    for author_id, papers in author_abstracts.items():
        print(f"\nProcessing author {author_id} ({len(papers)} papers)...")

        for paper in papers:
            # Combine title and abstract like in your original code
            title = paper.get('title', '')
            abstract = paper.get('abstract', '')
            combined_text = f"Title: {title}\nAbstract: {abstract}"

            print(f"  Getting embedding for: {title[:50]}...")
            embedding = get_embedding(combined_text)

            if embedding:
                batch_data.append({
                    'text': combined_text,
                    'embedding': embedding,
                    'author_ids': [author_id]
                })
                processed += 1

                # Insert in batches
                if len(batch_data) >= batch_size:
                    insert_batch(batch_data)
                    batch_data = []

                if processed % 50 == 0:
                    print(f"Progress: {processed}/{total_papers} papers processed")
            else:
                print(f"  Failed to get embedding for: {title[:50]}")

    # Insert remaining data
    if batch_data:
        insert_batch(batch_data)

    print(f"\nCompleted! Processed {processed}/{total_papers} papers")

def insert_batch(batch_data):
    """Insert a batch of embeddings into Supabase"""
    try:
        response = supabase.table('embeddings').insert(batch_data).execute()
        print(f"    Inserted batch of {len(batch_data)} items")
    except Exception as e:
        print(f"    Error inserting batch: {e}")
        # Try one by one
        for item in batch_data:
            try:
                supabase.table('embeddings').insert(item).execute()
            except Exception as e2:
                print(f"    Failed individual insert: {e2}")

def check_database_status():
    """Check current database status"""
    try:
        response = supabase.table('embeddings').select('id', count='exact').execute()
        count = response.count if response.count is not None else 0
        print(f"Current database contains {count} entries")

        if count > 0:
            # Get a sample to check dimensions
            sample = supabase.table('embeddings').select('embedding').limit(1).execute()
            if sample.data:
                embedding_dim = len(sample.data[0]['embedding'])
                print(f"Sample embedding dimension: {embedding_dim}")

        return count
    except Exception as e:
        print(f"Error checking database: {e}")
        return 0

if __name__ == "__main__":
    print("Embedding Regeneration Tool")
    print("==========================")
    print(f"Using model: {EMBEDDING_MODEL}")

    current_count = check_database_status()

    if current_count > 0:
        response = input(f"\nDatabase contains {current_count} entries. Clear and regenerate? (y/n): ")
        if response.lower() == 'y':
            print("Clearing existing data...")
            try:
                supabase.table('embeddings').delete().neq('id', 0).execute()
                print("Data cleared successfully")
            except Exception as e:
                print(f"Error clearing data: {e}")
                exit(1)

    regenerate_from_source_data()

    # Final verification
    print("\nFinal verification...")
    check_database_status()