from fastapi import FastAPI
from src.interface.api.routes import router as agent_router

# 1. Initialize the FastAPI application
app = FastAPI(
    title="Enterprise SQL Analyst Agent",
    description="Hexagonal Architecture AI Agent for secure text-to-SQL",
    version="1.0.0"
)

# 2. Attach our agent endpoints to the app
app.include_router(agent_router, prefix="/api/v1", tags=["Agent Operations"])

# 3. Add a simple health check route
@app.get("/")
async def health_check():
    return {
        "status": "online",
        "message": "AI SQL Agent is running.",
        "docs_url": "/docs"
    }