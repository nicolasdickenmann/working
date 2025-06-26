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

def migrate_data():
    """Migrate data from JSON file to Supabase"""
    
    # Check if vectorbig.json exists
    json_file_path = 'static/vectorbig.json'
    if not os.path.exists(json_file_path):
        print(f"Error: {json_file_path} not found!")
        return
    
    # Load existing data
    print(f"Loading data from {json_file_path}...")
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    print(f"Found {len(data)} entries to migrate")
    
    # Check if embeddings table exists and has data
    try:
        response = supabase.table('embeddings').select('id', count='exact').limit(1).execute()
        existing_count = response.count if response.count is not None else 0
        if existing_count > 0:
            print(f"Warning: Table already contains {existing_count} entries")
            response = input("Do you want to continue and add more data? (y/n): ")
            if response.lower() != 'y':
                print("Migration cancelled")
                return
    except Exception as e:
        print(f"Error checking existing data: {e}")
        print("Make sure you've created the embeddings table in Supabase first!")
        return
    
    # Insert data in batches
    batch_size = 50  # Smaller batch size for better reliability
    successful_inserts = 0
    
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        
        # Prepare batch for insertion
        insert_data = []
        for item in batch:
            insert_data.append({
                'text': item['text'],
                'embedding': item['vector'],
                'author_ids': item['author_ids']
            })
        
        try:
            response = supabase.table('embeddings').insert(insert_data).execute()
            successful_inserts += len(batch)
            print(f"Inserted batch {i//batch_size + 1}/{(len(data) + batch_size - 1)//batch_size} ({successful_inserts}/{len(data)} total)")
        except Exception as e:
            print(f"Error inserting batch {i//batch_size + 1}: {e}")
            # Try inserting one by one to identify problematic entries
            for j, item in enumerate(batch):
                try:
                    supabase.table('embeddings').insert({
                        'text': item['text'],
                        'embedding': item['vector'],
                        'author_ids': item['author_ids']
                    }).execute()
                    successful_inserts += 1
                except Exception as e2:
                    print(f"Failed to insert item {i + j}: {e2}")
    
    print(f"\nMigration completed! Successfully inserted {successful_inserts}/{len(data)} entries")
    
    # Verify the migration
    try:
        response = supabase.table('embeddings').select('id', count='exact').execute()
        final_count = response.count if response.count is not None else 0
        print(f"Final database count: {final_count} entries")
    except Exception as e:
        print(f"Error verifying final count: {e}")

def create_table_schema():
    """Create the embeddings table schema in Supabase"""
    print("""
To create the embeddings table in Supabase, run the following SQL in your Supabase SQL editor:

-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create table for storing embeddings
CREATE TABLE IF NOT EXISTS embeddings (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    embedding vector(768), -- Adjust dimension based on your embedding model
    author_ids TEXT[] NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for similarity search
CREATE INDEX IF NOT EXISTS embeddings_embedding_idx ON embeddings USING ivfflat (embedding vector_cosine_ops);

-- Create function for similarity search
CREATE OR REPLACE FUNCTION match_embeddings(
    query_embedding vector(768),
    match_threshold float,
    match_count int
)
RETURNS TABLE (
    id bigint,
    text text,
    author_ids text[],
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        embeddings.id,
        embeddings.text,
        embeddings.author_ids,
        1 - (embeddings.embedding <=> query_embedding) as similarity
    FROM embeddings
    WHERE 1 - (embeddings.embedding <=> query_embedding) > match_threshold
    ORDER BY embeddings.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
""")

if __name__ == "__main__":
    print("Supabase Migration Tool")
    print("======================")
    
    choice = input("Choose an option:\n1. Create table schema (show SQL)\n2. Migrate data\nEnter choice (1 or 2): ")
    
    if choice == "1":
        create_table_schema()
    elif choice == "2":
        migrate_data()
    else:
        print("Invalid choice") 