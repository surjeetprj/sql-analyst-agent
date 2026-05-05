# tests/run_evals.py

import asyncio
import sys
import os

# Ensure Python can find our src folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.application.agents.sql_agent import sql_agent_graph
from tests.golden_dataset import GOLDEN_DATASET

async def evaluate_agent():
    print("🚀 Starting AI Agent Evaluation Pipeline...\n")
    
    passed_tests = 0
    total_tests = len(GOLDEN_DATASET)

    for i, test in enumerate(GOLDEN_DATASET):
        print(f"Test {i+1}/{total_tests} [{test['difficulty']}]: {test['question']}")
        
        initial_state = {
            "user_query": test["question"],
            "schema_context": "",
            "generated_sql": "",
            "is_safe": True,
            "error_message": ""
        }
        
        # Run the Agent
        final_state = await sql_agent_graph.ainvoke(initial_state)
        
        # 1. Check Security Routing
        if final_state["is_safe"] != test["should_be_safe"]:
            print("❌ FAILED: Security Auditor made the wrong call.\n")
            continue
            
        # 2. Check SQL Quality (If it was supposed to be safe)
        if test["should_be_safe"]:
            generated_sql = final_state["generated_sql"].upper()
            missing_keywords = [kw.upper() for kw in test["expected_keywords"] if kw.upper() not in generated_sql]
            
            if missing_keywords:
                print(f"❌ FAILED: Missing required SQL logic: {missing_keywords}")
                print(f"   Generated SQL: {final_state['generated_sql']}\n")
                continue
                
        print("✅ PASSED\n")
        passed_tests += 1

    # Calculate Final Score
    accuracy = (passed_tests / total_tests) * 100
    print("==========================================")
    print(f"🏆 Final Agent Accuracy: {accuracy:.1f}% ({passed_tests}/{total_tests})")
    print("==========================================")

if __name__ == "__main__":
    asyncio.run(evaluate_agent())
