"""
Simple API Server for CrowdCount Dashboard
Run this file to start the web server
"""
import sys
import os

# Setup paths
backend_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(backend_dir, 'services'))
sys.path.insert(0, os.path.join(backend_dir, 'models'))
sys.path.insert(0, os.path.join(backend_dir, 'auth'))

print("=" * 60)
print("🔧 Loading modules...")
print("=" * 60)

try:
    # Import API
    print("📦 Importing API server...")
    from _archive.api_server_old import app
    print("✅ API server imported successfully")
    
    print("📦 Importing uvicorn...")
    import uvicorn
    print("✅ Uvicorn imported successfully")
    
    print("=" * 60)
    print("🚀 Starting CrowdCount API Server...")
    print("=" * 60)
    print("📊 Dashboard: http://localhost:8000/static/login.html")
    print("📖 API Docs: http://localhost:8000/docs")
    print("🔐 Login Credentials:")
    print("   Admin: admin / admin123")
    print("   User:  user / user123")
    print("=" * 60)
    print("")
    
    # Start server
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )
    
except Exception as e:
    print("=" * 60)
    print("❌ ERROR STARTING SERVER:")
    print("=" * 60)
    print(f"Error: {e}")
    print("")
    import traceback
    traceback.print_exc()
    print("=" * 60)
    print("💡 Troubleshooting:")
    print("   1. Make sure you're in the 'backend' directory")
    print("   2. Check that all folders exist (services, models, auth, _archive)")
    print("   3. Try: pip install fastapi uvicorn")
    print("=" * 60)
    input("Press Enter to exit...")
