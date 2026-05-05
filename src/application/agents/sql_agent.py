import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from src.domain.services.security_auditor import SQLSecurityAuditor
from src.infrastructure.config import settings
from src.infrastructure.database.session import AsyncSessionFactory

# Inject LangSmith settings into OS environment so LangChain automatically traces
os.environ["LANGCHAIN_TRACING_V2"] = settings.LANGCHAIN_TRACING_V2
os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGCHAIN_ENDPOINT
os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
if settings.LANGCHAIN_API_KEY:
    os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY


class AgentState(TypedDict):
    user_query: str
    schema_context: str
    generated_sql: str
    is_safe: bool
    error_message: str
    auditor_retries: int
    data: list

llm = ChatGroq(
    temperature=0, 
    model_name="llama-3.3-70b-versatile",
    api_key=settings.GROQ_API_KEY
)
auditor = SQLSecurityAuditor()

@traceable(name="context_retriever")
def context_retriever_node(state: AgentState):
    print("🧠 [Planner]: Retrieving Semantic Schema...")
    mock_cube_schema = """
    Tables: 
    1. sales (sale_id, customer_id, product_id, quantity, sale_date)
    2. customers (customer_id, company_name, industry, region)
    3. products (product_id, product_name, category, price)
    
    Relationships:
    - sales.customer_id joins to customers.customer_id
    - sales.product_id joins to products.product_id
    """
    return {"schema_context": mock_cube_schema}

@traceable(name="sql_coder")
def sql_coder_node(state: AgentState):
    print(f"💻 [Coder]: Asking Llama-3 to write SQL for -> '{state['user_query']}'")
    
    system_prompt = (
        "You are a senior PostgreSQL data analyst. Use the provided schema to write a SQL query. "
        "Return ONLY the raw SQL code. Do not use any markdown formatting. No explanations.\n\n"
        "Schema:\n{schema}"
    )
    
    if state.get("error_message") and state.get("generated_sql"):
        system_prompt += (
            "\n\nThe previous SQL query you generated:\n{generated_sql}\n\n"
            "Failed with this error:\n{error_message}\n\nPlease fix the query."
        )
        
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{query}")
    ])
    
    response = llm.invoke(prompt.format(
        schema=state['schema_context'], 
        query=state['user_query'],
        generated_sql=state.get("generated_sql", ""),
        error_message=state.get("error_message", "")
    ))
    
    # Cleaning the SQL response safely
    clean_sql = response.content.replace("```", "").replace("sql", "").strip()
    
    return {"generated_sql": clean_sql}

@traceable(name="security_auditor")
def security_auditor_node(state: AgentState):
    print("🛡️ [Auditor]: Scanning generated SQL for vulnerabilities...")
    sql = state.get("generated_sql", "")
    is_safe = auditor.validate_query(sql)
    
    retries = state.get("auditor_retries", 0)
    
    if not is_safe:
        print("🚨 [Auditor]: MALICIOUS QUERY DETECTED! Blocking execution.")
        # Added extra context so the LLM knows WHY it failed, helping it self-heal
        return {
            "is_safe": False, 
            "error_message": "SQL Injection attempt detected and blocked. Note: You are an Analyst. You must only use SELECT statements. DO NOT use INSERT, UPDATE, DELETE, DROP, etc.", 
            "auditor_retries": retries + 1
        }
    
    print("✅ [Auditor]: Query is safe.")
    return {"is_safe": True, "error_message": "", "auditor_retries": retries}

@traceable(name="database_executor")
async def execute_sql_node(state: AgentState):
    print("🚀 [Executor]: Running SQL against database...")
    sql = state["generated_sql"]
    try:
        async with AsyncSessionFactory() as session:
            result = await session.execute(text(sql))
            rows = result.mappings().all()
            data = [dict(row) for row in rows]
            return {"data": data, "error_message": ""}
    except SQLAlchemyError as e:
        print(f"⚠️ [Executor]: SQL execution failed: {e}")
        return {"error_message": str(e)}


workflow = StateGraph(AgentState)

workflow.add_node("retriever", context_retriever_node)
workflow.add_node("coder", sql_coder_node)
workflow.add_node("auditor", security_auditor_node)
workflow.add_node("executor", execute_sql_node)

workflow.set_entry_point("retriever")
workflow.add_edge("retriever", "coder")
workflow.add_edge("coder", "auditor")

def auditor_router(state: AgentState):
    # If the query is UNSAFE (malicious), DO NOT self-heal. Hard stop!
    if not state["is_safe"] and "SQL Injection" in state["error_message"]:
        return END
        
    # If the query is safe, route to the Database Executor!
    if state["is_safe"]:
        return "executor"
        
    return END

def executor_router(state: AgentState):
    # If there is a syntax error from the database, route back to the coder!
    if state.get("error_message"):
        return "coder"
    # Otherwise, we have our data, finish the graph!
    return END

workflow.add_conditional_edges("auditor", auditor_router)
workflow.add_conditional_edges("executor", executor_router)

sql_agent_graph = workflow.compile()