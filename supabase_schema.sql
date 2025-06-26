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

-- Enable Row Level Security (RLS) - optional but recommended
ALTER TABLE embeddings ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (you can restrict this later)
CREATE POLICY "Allow all operations" ON embeddings FOR ALL USING (true); 