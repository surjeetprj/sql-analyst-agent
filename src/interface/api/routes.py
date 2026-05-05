from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from src.application.agents.sql_agent import sql_agent_graph
from src.infrastructure.database.session import AsyncSessionFactory
from src.interface.api.security import verify_token, create_access_token
from src.infrastructure.config import settings

router = APIRouter()

@router.post("/token")
async def login(request: OAuth2PasswordRequestForm = Depends()):
    """Simple login endpoint to generate a JWT token."""
    if request.username == settings.API_USERNAME and request.password == settings.API_PASSWORD:
        token = create_access_token(data={"sub": request.username})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

class QueryRequest(BaseModel):
    query: str

@router.post("/ask")
async def ask_data_agent(
    request: QueryRequest, 
    current_user: dict = Depends(verify_token)   # RBAC Guardrail (JWT required)
):
    # 1. Initialize the agent's memory
    current_state = {
        "user_query": request.query,
        "schema_context": "",
        "generated_sql": "",
        "is_safe": True,
        "error_message": ""
    }
    
    # 2. Run the fully autonomous LangGraph Agent
    final_state = await sql_agent_graph.ainvoke(current_state)
    
    # 3. Handle Malicious Blocks
    if not final_state["is_safe"]:
        return {"error": final_state["error_message"]}
        
    # 4. Handle Persistent Syntax Errors (if it couldn't self-heal)
    if final_state.get("error_message"):
        return {
            "error": "The AI generated invalid SQL or the database execution failed.",
            "details": final_state["error_message"],
            "generated_sql": final_state.get("generated_sql")
        }
        
    # 5. Success! Return Data!
    return {
        "user_question": final_state["user_query"],
        "generated_sql": final_state["generated_sql"],
        "data": final_state.get("data", []),
        "status": "Success"
    }