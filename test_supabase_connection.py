#!/usr/bin/env python3
"""
Test script to verify Supabase connection and database setup
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv('config.env')

def test_supabase_connection():
    """Test basic Supabase connection and table access"""
    
    # Get credentials
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: Supabase credentials not found in environment variables")
        print("Make sure you have SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in your config.env")
        return False
    
    try:
        # Create client
        print("🔌 Connecting to Supabase...")
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Test basic connection
        print("✅ Successfully connected to Supabase")
        
        # Test table access
        print("📊 Testing table access...")
        response = supabase.table('embeddings').select('id', count='exact').limit(1).execute()
        
        count = response.count if response.count is not None else 0
        print(f"✅ Successfully accessed embeddings table")
        print(f"📈 Table contains {count} entries")
        
        if count == 0:
            print("⚠️  Warning: Table is empty. You may need to run the migration script.")
        
        # Test function access
        print("🔍 Testing similarity search function...")
        try:
            # Test with a dummy vector (768 dimensions)
            dummy_vector = [0.1] * 768
            response = supabase.rpc(
                'match_embeddings',
                {
                    'query_embedding': dummy_vector,
                    'match_threshold': 0.1,
                    'match_count': 5
                }
            ).execute()
            print("✅ Similarity search function is working")
        except Exception as e:
            print(f"❌ Error testing similarity search function: {e}")
            print("Make sure you've run the SQL schema in Supabase")
            return False
        
        print("\n🎉 All tests passed! Your Supabase setup is ready.")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_environment_status():
    """Show the status of environment variables"""
    print("Environment Variables Status:")
    print("=" * 40)
    
    vars_to_check = [
        ('SUPABASE_URL', 'Supabase Project URL'),
        ('SUPABASE_SERVICE_ROLE_KEY', 'Supabase Service Role Key'),
        ('GOOGLE_API_KEY', 'Google API Key')
    ]
    
    for var_name, description in vars_to_check:
        value = os.getenv(var_name)
        if value:
            # Show first few characters for security
            display_value = value[:10] + "..." if len(value) > 10 else value
            print(f"✅ {description}: {display_value}")
        else:
            print(f"❌ {description}: Not set")

if __name__ == "__main__":
    print("Supabase Connection Test")
    print("=" * 30)
    
    show_environment_status()
    print()
    
    if test_supabase_connection():
        print("\n🚀 You're ready to deploy to Vercel!")
    else:
        print("\n🔧 Please fix the issues above before deploying.") 