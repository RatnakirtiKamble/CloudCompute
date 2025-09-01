from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn 

# Router imports
from routers import auth_router, compute_router, status_router, upload_router

# Middleware imports
from middleware import JWTMiddleware, setup_cors, StaticAccessLogger

# Database imports
from db.db_connection import engine, Base

# ===== Server Configuration =====
app = FastAPI(
    title="MiniCloud Backend",
    description="Backend APIs for authentication, compute, status tracking, and uploads",
    version="1.0.0"
)

# ===== Startup Event =====
@app.on_event("startup")
async def startup_event():
    print("Initializing database...")

    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized successfully!")

# ===== Middleware =====
setup_cors(app)  
app.add_middleware(JWTMiddleware) 
app.add_middleware(StaticAccessLogger)

# ===== Routers =====
app.include_router(auth_router.router, tags=["Authentication"])
app.include_router(compute_router.router, tags=["Compute Engine"])
app.include_router(status_router.router, tags=["Status & Logs"])  
app.include_router(upload_router.router, tags=["Page/Container Upload"])

app.mount("/static", StaticFiles(directory="workspaces"), name="static")


@app.get("/")
def root():
    return {"message": "Welcome to MiniCloud"}

# ===== Entrypoint =====
if __name__ == "__main__":
    uvicorn.run(
        "server:app",        
        host="0.0.0.0",      
        port=8000,           
        reload=True          
    )
