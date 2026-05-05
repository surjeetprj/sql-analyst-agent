import modal

# 1. Define the Cloud Environment
# We now add your local 'src' directory directly into the cloud image definition!
app_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "fastapi[standard]",
        "pydantic-settings",
        "sqlalchemy",
        "asyncpg",
        "langchain-groq",
        "langchain-core",
        "langgraph",
        "PyJWT"
    )
    .add_local_dir("src", remote_path="/root/src")  # <--- The 1.0 Fix
    .add_local_dir("cube/model", remote_path="/root/cube/model") # <--- Inject real schema
)

# 2. Initialize the Modal App
app = modal.App("enterprise-sql-agent")

# 3. Teleport the FastAPI app into the Cloud
@app.function(
    image=app_image,
    # Securely pulls your encrypted secrets directly from Modal's Cloud Dashboard
    secrets=[modal.Secret.from_name("enterprise-sql-secrets")] 
)
@modal.asgi_app()
def serve():
    import sys
    sys.path.append("/root") # Ensure Python can find your 'src' module
    
    # Import your actual FastAPI application!
    from src.interface.api.main import app as fastapi_app
    return fastapi_app