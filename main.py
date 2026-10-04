import os
import sys
import json
import argparse
from llm_client import LLMClient
from agents.code_generator import CodeGeneratorAgent
from agents.test_generator import TestGeneratorAgent
from agents.test_executor import TestExecutorAgent

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "sanitized-mbpp.json")

def load_mbpp_task(task_id: int):
    """Loads a specific task from sanitized-mbpp.json."""
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}. Run 'python data/download_mbpp.py' first.")

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        tasks = json.load(f)

    for task in tasks:
        if task.get("task_id") == task_id:
            return task

    # Default to first task if ID not found
    return tasks[0]

def run_pipeline(task_id: int = 2, with_llm_verdict: bool = True):
    print("=" * 70)
    print(f" AGENTIC AI SOFTWARE TESTING PIPELINE - TASK #{task_id}")
    print("=" * 70)

    # 1. Load task from dataset
    task = load_mbpp_task(task_id)
    prompt = task["prompt"]
    canonical_code = task["code"]
    test_hints = task.get("test_list", [])

    print(f"\n[Problem Specification]\n{prompt}\n")

    # Initialize LLM and Agents
    llm = LLMClient()
    code_agent = CodeGeneratorAgent(llm)
    test_agent = TestGeneratorAgent(llm)
    executor_agent = TestExecutorAgent(timeout=5)

    # Agent 1: Code Generator Agent
    print("-" * 50)
    print("[1] Code Generator Agent: Generating code...")
    generated_code = code_agent.generate_code(prompt, test_hints)
    print("\n--- Generated Code ---")
    print(generated_code)

    # Agent 2: Test Generator Agent
    print("-" * 50)
    print("[2] Test Generator Agent: Generating unit tests (Goal: Statement Coverage)...")
    generated_tests = test_agent.generate_tests(prompt, generated_code)
    print("\n--- Generated Tests ---")
    print(generated_tests)

    # Agent 3: Test Executor Agent (Pure Python execution & Coverage)
    print("-" * 50)
    print("[3] Test Executor Agent: Executing in Python sandbox & calculating metrics...")
    eval_result = executor_agent.evaluate(
        canonical_code=canonical_code,
        generated_code=generated_code,
        test_code=generated_tests
    )

    print("\n" + "=" * 50)
    print(" EXECUTION RESULTS & TESTING METRICS")
    print("=" * 50)
    print(f"Test Validity (Pass on Canonical) : {eval_result['test_validity_percent']}%")
    print(f"Statement Coverage (on Gen Code)  : {eval_result['statement_coverage_percent']}%")
    print(f"Generated Code Test Pass Rate     : {eval_result['generated_pass_percent']}%")
    print(f"Python Execution Verdict          : {eval_result['verdict']}")

    gen_fails = list(eval_result["generated_execution"].get("failure_details", {}).keys())
    can_fails = list(eval_result["canonical_execution"].get("failure_details", {}).keys())
    if gen_fails:
        formatted = ", ".join([f"#{i+1} ({name})" for i, name in enumerate(gen_fails)])
        print(f"Failed Tests (Generated Code)     : {formatted}")
    else:
        print(f"Failed Tests (Generated Code)     : None (All Passed)")

    if can_fails:
        formatted = ", ".join([f"#{i+1} ({name})" for i, name in enumerate(can_fails)])
        print(f"Failed Tests (Canonical Code)     : {formatted}")

    # Agent 3 Phase 2: Diagnostic Analysis (Triage: 0 tokens on success, minimal targeted payload on failure)
    if with_llm_verdict and llm.api_key:
        print("\n" + "-" * 50)
        print("Agent 3 (Phase 2): Diagnostic Evaluation (LLM Triage)...")
        try:
            diagnosis = executor_agent.diagnose(
                llm_client=llm,
                prompt=prompt,
                canonical_code=canonical_code,
                generated_code=generated_code,
                test_code=generated_tests,
                eval_result=eval_result
            )
            print("\n--- Diagnostic Verdict ---")
            print(diagnosis)
            eval_result["diagnosis"] = diagnosis
        except Exception as e:
            print(f"Could not retrieve diagnostic verdict: {e}")

    print("=" * 70)
    return eval_result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Agentic AI Unit Testing Pipeline")
    parser.add_argument("--task", type=int, default=2, help="MBPP Task ID to execute (default: 2)")
    args = parser.parse_args()

    run_pipeline(task_id=args.task)
