# Supabase Setup Guide

This guide will help you migrate your vector database from the local JSON file to Supabase with pgvector, which will solve your Vercel deployment size issues.

## Prerequisites

1. **Supabase Account**: Sign up at [supabase.com](https://supabase.com)
2. **Google API Key**: You already have this for Gemini embeddings
3. **Python Environment**: Your existing setup

## Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Wait for the project to be created (this may take a few minutes)
3. Go to Settings → API to get your project credentials

## Step 2: Get Supabase Credentials

In your Supabase dashboard:

1. Go to **Settings** → **API**
2. Copy the following values:
   - **Project URL** (looks like: `https://your-project-id.supabase.co`)
   - **Service Role Key** (starts with `eyJ...`)

## Step 3: Update Environment Variables

Add these to your `config.env` file:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
GOOGLE_API_KEY=your-google-api-key
```

## Step 4: Create Database Schema

1. In your Supabase dashboard, go to **SQL Editor**
2. Copy and paste the contents of `supabase_schema.sql` into the editor
3. Click **Run** to execute the SQL

This will:
- Enable the pgvector extension
- Create the embeddings table
- Create the similarity search function
- Set up proper indexing

## Step 5: Install Dependencies

Install the new dependencies:

```bash
pip install supabase==2.3.4 psycopg2-binary==2.9.9
```

## Step 6: Migrate Your Data

Run the migration script:

```bash
python migrate_to_supabase.py
```

Choose option **2** to migrate your data. The script will:
- Load your existing `static/vectorbig.json` file
- Upload all embeddings to Supabase in batches
- Show progress and handle any errors

## Step 7: Test Locally

Test your updated API:

```bash
python search_api.py
```

Or if you're using the WSGI entry point:

```bash
python wsgi.py
```

Test the endpoints:
- `GET /health` - Should show database connection status
- `POST /search` - Should work with your search queries

## Step 8: Deploy to Vercel

1. **Set Environment Variables in Vercel**:
   - Go to your Vercel project dashboard
   - Navigate to Settings → Environment Variables
   - Add:
     - `SUPABASE_URL`
     - `SUPABASE_SERVICE_ROLE_KEY`
     - `GOOGLE_API_KEY`

2. **Deploy**:
   ```bash
   vercel --prod
   ```

## Step 9: Verify Deployment

1. Check your Vercel deployment URL
2. Test the `/health` endpoint
3. Test the `/search` endpoint with a POST request

## Troubleshooting

### Common Issues

1. **"Supabase credentials not found"**
   - Make sure you've added the environment variables to both `config.env` and Vercel

2. **"Table 'embeddings' does not exist"**
   - Run the SQL schema in Supabase SQL Editor first

3. **"pgvector extension not available"**
   - Make sure you're on a Supabase plan that supports pgvector (Pro plan or higher)

4. **Migration fails**
   - Check your Supabase project limits
   - Try smaller batch sizes in the migration script

### Performance Tips

1. **Index Optimization**: The migration creates an IVFFlat index which is good for similarity search
2. **Batch Size**: The migration uses batches of 50 entries for reliability
3. **Connection Pooling**: Supabase handles connection pooling automatically

### Cost Considerations

- **Free Tier**: 500MB database, 2GB bandwidth
- **Pro Tier**: 8GB database, 250GB bandwidth, includes pgvector
- **Team Tier**: 100GB database, 1TB bandwidth

For your 29MB vector database, the free tier should be sufficient for testing, but you'll need the Pro tier for pgvector support.

## Benefits of This Setup

1. **Reduced Deployment Size**: Your Vercel deployment will be much smaller
2. **Better Performance**: Vector similarity search in PostgreSQL is very fast
3. **Scalability**: Easy to add more data without deployment issues
4. **Reliability**: Supabase provides high availability and backups
5. **Cost Effective**: Generous free tier for development

## Next Steps

After successful migration:

1. **Remove the JSON file**: You can delete `static/vectorbig.json` to save space
2. **Update your embedding script**: Modify `embedding_database.py` to save directly to Supabase
3. **Monitor usage**: Check your Supabase dashboard for usage metrics
4. **Optimize**: Consider adding more indexes or optimizing queries based on usage patterns

## Support

If you encounter issues:

1. Check the Supabase documentation: [supabase.com/docs](https://supabase.com/docs)
2. Check the pgvector documentation: [github.com/pgvector/pgvector](https://github.com/pgvector/pgvector)
3. Review the migration logs for specific error messages 