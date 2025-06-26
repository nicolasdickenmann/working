# Deploying to Vercel with Supabase

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Supabase Account**: Sign up at [supabase.com](https://supabase.com) (Pro plan required for pgvector)
3. **Vercel CLI**: Install with `npm i -g vercel`
4. **Git Repository**: Your code should be in a Git repository

## Files Created for Vercel Deployment

- `vercel.json`: Vercel configuration
- `wsgi.py`: WSGI entry point for the Flask app
- `.gitignore`: Excludes sensitive files and large data files from version control
- `supabase_schema.sql`: Database schema for Supabase
- `migrate_to_supabase.py`: Migration script for moving data to Supabase

## Step-by-Step Deployment

### 1. Set up Supabase

1. **Create Supabase Project**:
   - Go to [supabase.com](https://supabase.com) and create a new project
   - Wait for the project to be created

2. **Get Credentials**:
   - Go to Settings → API in your Supabase dashboard
   - Copy the Project URL and Service Role Key

3. **Create Database Schema**:
   - Go to SQL Editor in Supabase
   - Copy and paste the contents of `supabase_schema.sql`
   - Click Run to execute

4. **Migrate Data**:
   ```bash
   python migrate_to_supabase.py
   ```
   Choose option 2 to migrate your existing data.

### 2. Install Vercel CLI
```bash
npm install -g vercel
```

### 3. Login to Vercel
```bash
vercel login
```

### 4. Set Environment Variables

You need to set these environment variables in Vercel:

**Option A: Via Vercel Dashboard**
1. Go to your project in the Vercel dashboard
2. Navigate to Settings → Environment Variables
3. Add the following variables:
   - `GOOGLE_API_KEY` with your Google API key value
   - `SUPABASE_URL` with your Supabase project URL
   - `SUPABASE_SERVICE_ROLE_KEY` with your Supabase service role key

**Option B: Via CLI**
```bash
vercel env add GOOGLE_API_KEY
vercel env add SUPABASE_URL
vercel env add SUPABASE_SERVICE_ROLE_KEY
```

### 5. Deploy
```bash
vercel
```

Or to deploy to production:
```bash
vercel --prod
```

### 6. Verify Deployment
- Your API will be available at the URL provided by Vercel
- Test the `/health` endpoint to ensure it's working
- Test the `/search` endpoint with a POST request

## API Endpoints

- `GET /` - Serves the force graph HTML
- `POST /search` - Semantic search endpoint (now using Supabase)
- `POST /explain_match` - Explain why a professor matches a query
- `GET /health` - Health check endpoint (now shows Supabase connection status)

## Important Notes

1. **Environment Variables**: Make sure all three environment variables are set in Vercel
2. **Supabase Plan**: You need a Pro plan or higher for pgvector support
3. **Cold Starts**: Vercel functions may have cold starts, so the first request might be slower
4. **Timeout**: Vercel has a 10-second timeout for serverless functions
5. **Database Connection**: The app now connects to Supabase instead of loading a local file

## Troubleshooting

- If you get environment variable errors, double-check that all three variables are set in Vercel
- If the database connection fails, verify your Supabase credentials and that the table exists
- Check Vercel function logs in the dashboard for detailed error messages
- If pgvector is not available, upgrade to a Pro plan in Supabase

## Local Development

To test locally before deploying:

1. **Set up environment variables** in `config.env`:
   ```env
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   GOOGLE_API_KEY=your-google-api-key
   ```

2. **Run the application**:
   ```bash
   python wsgi.py
   ```

The API will be available at `http://localhost:5000`

## Benefits of This Setup

1. **Reduced Deployment Size**: No more 29MB JSON file in your deployment
2. **Better Performance**: Vector similarity search in PostgreSQL is very fast
3. **Scalability**: Easy to add more data without deployment issues
4. **Reliability**: Supabase provides high availability and backups
5. **Cost Effective**: Generous free tier for development

## Migration from Old Setup

If you're migrating from the old JSON-based setup:

1. Follow the Supabase setup guide in `SUPABASE_SETUP.md`
2. Run the migration script to move your data
3. Update your environment variables
4. Deploy to Vercel
5. You can now safely remove `static/vectorbig.json` from your repository 