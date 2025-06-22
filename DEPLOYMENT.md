# Deploying to Vercel

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI**: Install with `npm i -g vercel`
3. **Git Repository**: Your code should be in a Git repository

## Files Created for Vercel Deployment

- `vercel.json`: Vercel configuration
- `wsgi.py`: WSGI entry point for the Flask app
- `.gitignore`: Excludes sensitive files from version control

## Step-by-Step Deployment

### 1. Install Vercel CLI
```bash
npm install -g vercel
```

### 2. Login to Vercel
```bash
vercel login
```

### 3. Set Environment Variables
You need to set your `GOOGLE_API_KEY` in Vercel:

**Option A: Via Vercel Dashboard**
1. Go to your project in the Vercel dashboard
2. Navigate to Settings → Environment Variables
3. Add `GOOGLE_API_KEY` with your Google API key value

**Option B: Via CLI**
```bash
vercel env add GOOGLE_API_KEY
```

### 4. Deploy
```bash
vercel
```

Or to deploy to production:
```bash
vercel --prod
```

### 5. Verify Deployment
- Your API will be available at the URL provided by Vercel
- Test the `/health` endpoint to ensure it's working
- Test the `/search` endpoint with a POST request

## API Endpoints

- `GET /` - Serves the force graph HTML
- `POST /search` - Semantic search endpoint
- `POST /explain_match` - Explain why a professor matches a query
- `GET /health` - Health check endpoint

## Important Notes

1. **Environment Variables**: Make sure `GOOGLE_API_KEY` is set in Vercel dashboard
2. **File Size**: The `vectorbig.json` file (29MB) will be included in your deployment
3. **Cold Starts**: Vercel functions may have cold starts, so the first request might be slower
4. **Timeout**: Vercel has a 10-second timeout for serverless functions

## Troubleshooting

- If you get environment variable errors, double-check that `GOOGLE_API_KEY` is set in Vercel
- If the vector database fails to load, ensure `static/vectorbig.json` is committed to your repository
- Check Vercel function logs in the dashboard for detailed error messages

## Local Development

To test locally before deploying:
```bash
python search_api.py
```

The API will be available at `http://localhost:5000` 