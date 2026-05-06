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

---

## 💻 Local Development

### Step 1: Prerequisites

You need two tools installed on your machine:

*   **Python 3.11+** — [Download here](https://www.python.org/downloads/)
*   **`uv` (Fast Package Manager)** — Install with one command:
    ```bash
    # On macOS / Linux
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # On Windows (PowerShell)
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

---

### Step 2: Get Your API Keys (Free)

This project requires accounts on **two free services**:

| Service | What it's for | Sign Up Link |
|---|---|---|
| **Groq** | Free LLM API (Llama-3) | [console.groq.com](https://console.groq.com) |
| **Neon** | Free Serverless PostgreSQL | [console.neon.tech](https://console.neon.tech) |
| **LangSmith** *(optional)* | AI observability tracing | [smith.langchain.com](https://smith.langchain.com) |

After signing up:
1. On **Groq**: Go to **API Keys** → Create a new key → copy it.
2. On **Neon**: Create a project → go to **Dashboard** → copy the **Connection String** (starts with `postgresql://...`).

---

### Step 3: Initialize the Database

Your Neon database starts empty. Run the provided seed script to create tables and load sample data:

1. Open your [Neon Console](https://console.neon.tech/).
2. Click on your project → go to the **SQL Editor** tab.
3. Copy the entire contents of [`database/init_db.sql`](./database/init_db.sql) from this repo.
4. Paste it into the SQL Editor and click **Run**.

✅ This creates the `customers`, `products`, and `sales` tables with realistic sample data.

---

### Step 4: Configure Environment

Clone the repository, then create a `.env` file in the root directory:

```bash
git clone https://github.com/surjeetprj/sql-analyst-agent.git
cd sql-analyst-agent
uv pip install -e .
```

Create `.env` in the project root:

```env
# Core Application Settings
PROJECT_NAME="Enterprise SQL Analyst Agent"

# Database Connection (from your Neon Dashboard)
POSTGRES_USER="your_neon_user"
POSTGRES_PASSWORD="your_neon_password"
POSTGRES_DB="your_neon_db_name"
POSTGRES_HOST="your-neon-host.neon.tech"
POSTGRES_PORT=5432
DATABASE_URL="postgresql://user:pass@host/dbname?sslmode=require"

# AI Key (from Groq Console)
GROQ_API_KEY="gsk_your_llama3_key_here"

# Backend API Authentication (choose any username & password)
JWT_SECRET_KEY="any-random-secret-string"
API_USERNAME="admin"
API_PASSWORD="your_chosen_password"

# Cube.js (only needed if running docker-compose locally)
CUBEJS_DEV_MODE="true"

# (Optional) LangSmith Tracing
LANGCHAIN_TRACING_V2="false"
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY="your_langsmith_key"
LANGCHAIN_PROJECT="sql-analyst-agent-prod"
```

---

### Step 5: Run the Application

You need **two terminals** open simultaneously:

**Terminal 1 — Backend API:**
```bash
uv run fastapi dev src/interface/api/main.py
```

**Terminal 2 — Frontend UI:**
```bash
uv run streamlit run src/interface/ui/app.py
```

Open your browser at **http://localhost:8501** and start asking questions!

---

## 🐳 Local Docker (Cube — Optional)

Docker is **only needed** if you want to run the Cube.js semantic layer locally for development/exploration. The application works perfectly without it, as the AI reads the schema directly from the `cube/model/sales.yml` YAML file.

If you want to explore Cube's visual dashboard anyway:
```bash
docker-compose up
```
This starts the Cube playground at `http://localhost:4000`, connected to your Neon instance.

---

## 🗄️ Database Schema Reference

The sample database contains 3 tables:

| Table | Key Columns | Description |
|---|---|---|
| `customers` | `customer_id`, `company_name`, `industry`, `region` | 7 companies across different sectors |
| `products` | `product_id`, `product_name`, `category`, `price` | 7 products across 4 categories |
| `sales` | `sale_id`, `customer_id`, `product_id`, `quantity`, `sale_date` | 14 transactions across Jan-Feb 2024 |

**Semantic Layer (AI-aware metrics):**
- **Revenue** = `sales.quantity × products.price` (auto-calculated by Cube.js)

---

## 🌐 Deployment

The project is configured for continuous deployment using GitHub Actions.
To manually deploy the backend to Modal:
```bash
uv run modal deploy deploy.py
```
