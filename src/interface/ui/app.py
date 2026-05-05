import sys
import os

# Add project root to path to resolve 'src' module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

import streamlit as st
import requests
import pandas as pd
from src.infrastructure.config import get_frontend_settings
settings = get_frontend_settings()
st.set_page_config(
    page_title="Enterprise SQL Analyst",
    page_icon="📊",
    layout="wide"
)

# ... inside the chat loop ...
# (The code down below relies on these loaded settings)

st.title("📊 Enterprise SQL Analyst Agent")
st.markdown("Ask natural language questions about your database. I'll translate them to safe SQL and give you the data!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "data" in message:
            df = message["data"]
            st.dataframe(df, use_container_width=True)
            
            # Simple heuristic: if there's a numeric column and a non-numeric column, try a chart
            if len(df.columns) >= 2:
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                categorical_cols = df.select_dtypes(exclude=['number']).columns.tolist()
                
                if numeric_cols and categorical_cols:
                    try:
                        st.bar_chart(df, x=categorical_cols[0], y=numeric_cols[0])
                    except Exception:
                        pass
        
        if "sql" in message:
            with st.expander("Show Generated SQL"):
                st.code(message["sql"], language="sql")

# Accept user input
if prompt := st.chat_input("E.g., What are the total sales by region?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🤔 *Thinking and writing SQL...*")
        
        try:
            # Dynamically fetch the API URL from our centralized Settings
            API_BASE_URL = settings.API_BASE_URL
            
            # 1. Fetch JWT Token first
            token_response = requests.post(
                f"{API_BASE_URL}/api/v1/token", 
                data={"username": settings.API_USERNAME, "password": settings.API_PASSWORD}
            )
            
            if token_response.status_code != 200:
                st.error("Authentication failed. Check backend credentials.")
                st.stop()
                
            access_token = token_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # 2. Hit the FastAPI endpoint with JWT
            response = requests.post(
                f"{API_BASE_URL}/api/v1/ask", 
                json={"query": prompt},
                headers=headers
            )
            response_data = response.json()
            
            if response.status_code == 200 and "error" not in response_data:
                sql_query = response_data.get("generated_sql", "")
                data_rows = response_data.get("data", [])
                
                if data_rows:
                    df = pd.DataFrame(data_rows)
                    message_placeholder.markdown(f"Here is the data for: **{prompt}**")
                    st.dataframe(df, use_container_width=True)
                    
                    # Auto-charting heuristic
                    if len(df.columns) >= 2:
                        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                        categorical_cols = df.select_dtypes(exclude=['number']).columns.tolist()
                        if numeric_cols and categorical_cols:
                            st.bar_chart(df, x=categorical_cols[0], y=numeric_cols[0])
                    
                    with st.expander("Show Generated SQL"):
                        st.code(sql_query, language="sql")
                        
                    # Save to state
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": f"Here is the data for: **{prompt}**",
                        "data": df,
                        "sql": sql_query
                    })
                else:
                    message_placeholder.markdown("No data returned for that query.")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "No data returned for that query.",
                        "sql": sql_query
                    })
            else:
                error_msg = response_data.get("error", "Unknown Error")
                details = response_data.get("details", "")
                sql = response_data.get("generated_sql", "")
                
                full_error = f"❌ **Error:** {error_msg}\n\n*Details:* {details}"
                message_placeholder.markdown(full_error)
                if sql:
                    with st.expander("Show Failing SQL"):
                        st.code(sql, language="sql")
                        
                st.session_state.messages.append({"role": "assistant", "content": full_error})
                
        except requests.exceptions.ConnectionError:
            error_msg = "❌ Failed to connect to the backend server. Is FastAPI running on port 8000?"
            message_placeholder.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
        except Exception as e:
            error_msg = f"❌ An unexpected error occurred: {str(e)}"
            message_placeholder.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
