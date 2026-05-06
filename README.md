# 📊 Enterprise AI SQL Analyst Agent

An enterprise-grade, fully autonomous AI agent that translates natural language into safe, executable PostgreSQL queries. Built with a decoupled architecture, semantic context injection, and native self-healing capabilities.

## 🚀 Key Features

*   **Self-Healing State Machine:** Orchestrated by **LangGraph**, the agent doesn't just guess SQL. It writes the query, executes it, and if the database throws a syntax error, the agent intercepts the error and autonomously routes back to the LLM to fix its own mistake before responding.
*   **Headless Semantic Layer:** Integrates **Cube.js** YAML configuration files to inject business logic natively into the LLM context. The AI automatically understands complex metrics (e.g., how to calculate revenue) and table JOIN relationships without hardcoded prompts.
*   **Enterprise Security Guardrails:** 
    *   **SQL Injection Auditor:** A dedicated LangGraph node scans every generated query, immediately blocking malicious intents (`DROP`, `DELETE`, `UPDATE`) and refusing to self-heal.
    *   **JWT Authentication:** The FastAPI backend is fully locked down behind OAuth2 Password Bearer token authentication.
*   **Cloud-Native & Decoupled:**
    *   **Backend:** Serverless **FastAPI** deployed on **Modal**.
    *   **Frontend:** Decoupled **Streamlit** UI deployed on **Streamlit Cloud**.
    *   **Database:** Serverless **Neon PostgreSQL**.
*   **Automated CI/CD:** A robust **GitHub Actions** pipeline tests every commit against a specialized **Golden Dataset**. If the AI accuracy falls below 100%, the build fails. If successful, the pipeline securely deploys the container to Modal using internal dashboard secrets.

## 🛠️ Technology Stack

*   **AI Orchestration:** LangGraph, LangChain, Groq API (Llama-3.3-70b-versatile)
*   **Backend:** Python 3.11, FastAPI, Pydantic, SQLAlchemy, asyncpg
*   **Frontend:** Streamlit, Pandas
*   **Semantic Layer:** Cube.dev
*   **Observability:** LangSmith
*   **Infrastructure:** Modal (Serverless Compute), Neon (Serverless DB), GitHub Actions (CI/CD)

## 🏗️ Architecture

The backend is built around a cyclic **LangGraph** workflow:
1.  **Context Retriever Node:** Dynamically loads the `sales.yml` Cube schema to give the LLM structural database context.
2.  **SQL Coder Node:** Prompts Llama-3 to generate raw Postgres SQL.
3.  **Security Auditor Node:** Validates the query to ensure it only performs `SELECT` operations. Blocks malicious injection attempts.
4.  **Database Executor Node:** Executes the query asynchronously via `asyncpg`. If an error occurs, the graph routes back to the Coder Node.

```mermaid
graph TD
    User([Streamlit User]) -->|Natural Language Query| API[FastAPI Backend]
    
    subgraph LangGraph AI Agent
        API --> Context[1. Context Retriever Node]
        Context -->|Injects Cube.js Schema| Coder[2. SQL Coder Node]
        Coder -->|Generates SQL| Auditor[3. Security Auditor Node]
        
        Auditor -->|Malicious SQL Detected| Blocked([Block Execution & Return Error])
        Auditor -->|Safe SELECT Query| Executor[4. Database Executor Node]
        
        Executor -->|Execution Failed| Coder
        Executor -->|Execution Succeeded| ReturnData([Return Data to User])
    end
```

## 💻 Local Development

### Prerequisites
*   Python 3.11+
*   `uv` (Fast Python Package Manager)

### Setup
1. Clone the repository and install dependencies:
   ```bash
   uv pip install -e .
   ```
2. Set up your local `.env` file with the required credentials. Create a file named `.env` in the root directory and add the following:
   ```env
   # Core Application Settings
   PROJECT_NAME="Enterprise SQL Analyst Agent"
   
   # Database Connections (Neon Serverless Postgres)
   POSTGRES_USER="your_database_user"
   POSTGRES_PASSWORD="your_database_password"
   POSTGRES_DB="your_database_name"
   DATABASE_URL="postgresql://user:pass@host/dbname?sslmode=require"
   
   # External API Keys
   GROQ_API_KEY="gsk_your_llama3_key_here"
   
   # Backend API Authentication (For Swagger & Streamlit Login)
   JWT_SECRET_KEY="your_custom_secret_key"
   API_USERNAME="admin"
   API_PASSWORD="your_custom_password"
   
   # (Optional) LangSmith Tracing
   LANGCHAIN_TRACING_V2="true"
   LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
   LANGCHAIN_API_KEY="your_langsmith_key"
   LANGCHAIN_PROJECT="sql-analyst-agent-prod"
   ```
3. Run the backend server:
   ```bash
   uv run fastapi dev src/interface/api/main.py
   ```
4. Run the Streamlit UI:
   ```bash
   uv run streamlit run src/interface/ui/app.py
   ```

## 🗄️ Database Initialization

This repository includes a pre-configured database schema and sample data to help you get started quickly.

### For Local (Docker) Setup
If you are using Docker, the database will be automatically initialized when you run `docker-compose up`. The initialization script is located at `database/init_db.sql`.

### For Cloud/Manual Setup
If you are using a cloud database like Neon, you can manually run the initialization script:
1. Open your database console (e.g., Neon Console).
2. Copy the contents of `database/init_db.sql`.
3. Paste and execute the SQL script in your database's SQL editor.

## 🌐 Deployment

The project is configured for continuous deployment using GitHub Actions.
To manually deploy the backend to Modal:
```bash
uv run modal deploy deploy.py
```
