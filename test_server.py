"""Test server imports"""
import sys
print("Testing imports...")

try:
    print("1. Importing FastAPI...")
    from fastapi import FastAPI
    print("✅ FastAPI imported")
    
    print("2. Creating app...")
    app = FastAPI()
    print("✅ App created")
    
    print("3. Importing auth router...")
    from src.api.auth.routers import router as auth_router
    print("✅ Auth router imported")
    
    print("4. Importing documents router...")
    from src.api.documents.routers import router as documents_router
    print("✅ Documents router imported")
    
    print("5. Importing workflows router...")
    from src.api.workflows.routers import router as workflows_router
    print("✅ Workflows router imported")
    
    print("6. Importing batch router...")
    from src.api.batch_routes import router as batch_router
    print("✅ Batch router imported")
    
    print("7. Including routers...")
    app.include_router(auth_router, prefix="/api/auth")
    app.include_router(documents_router, prefix="/api")
    app.include_router(workflows_router, prefix="/api")
    app.include_router(batch_router, prefix="/api")
    print("✅ All routers included")
    
    print("\n✅ All tests passed! Server should work.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
