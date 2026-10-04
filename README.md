# Agentic AI Software Testing Pipeline

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Testing: unittest](https://img.shields.io/badge/testing-unittest-green.svg)](https://docs.python.org/3/library/unittest.html)
[![Coverage: branch--coverage](https://img.shields.io/badge/coverage-branch--guided-blueviolet.svg)](https://coverage.readthedocs.io/)

A modular, first-principles **Agentic AI Unit Testing Pipeline** built for automated test generation, isolated execution, statement/branch coverage measurement, and token-optimised root-cause failure diagnosis.

Designed and implemented for **CSE731: Software Testing** (Term I, 2026–27) at **IIIT Bangalore**.

---

## 🌟 Core Highlights

- **Built from First Principles:** No heavy or opaque orchestration frameworks (e.g. LangChain, CrewAI). Pure standard Python architecture.
- **Three-Agent Workflow:**
  1. **Agent 1 (`CodeGeneratorAgent`):** Generates clean, idiomatic Python solutions from natural language problem descriptions.
  2. **Agent 2 (`TestGeneratorAgent`):** Generates comprehensive, coverage-driven `unittest.TestCase` suites with boundary and edge cases.
  3. **Agent 3 (`TestExecutorAgent`):** Performs offline execution inside a temporary `subprocess` sandbox and runs a token-optimised diagnostic triage engine on failures.
- **Safe Sandboxed Execution:** Untrusted LLM-generated code executes exclusively in an isolated `tempfile.TemporaryDirectory` subprocess with a 5-second infinite-loop timeout guard.
- **Two-Dimensional Quality Assessment:**
  - **Pass Rate & Branch Coverage:** Evaluated on the generated code using `coverage.py --branch`.
  - **Test Validity %:** Evaluated against the human-written canonical benchmark solution.
- **Token-Optimised Diagnostic Triage:** 
  - **0 LLM tokens** consumed when all tests pass cleanly.
  - Minimal targeted payloads (failed test snippet + relevant code only) sent only when failures occur.

---

## 🏗 Pipeline Architecture

```
                  MBPP Problem Specification
                              │
                              ▼
                 [Agent 1: Code Generator]
                     (LLM Call, T = 0.2)
                              │
                              ▼
                   Generated Python Function
                              │
                              ▼
                 [Agent 2: Test Generator]
                     (LLM Call, T = 0.4)
                              │
                              ▼
                  Generated unittest Suite
                              │
                              ▼
                 [Agent 3: Test Executor]
                   (Subprocess Sandbox)
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
     Run on Generated Code           Run on Canonical Code
    (+ coverage.py --branch)        (Ground-Truth Reference)
              │                               │
              ▼                               ▼
    Statement Coverage %               Test Validity %
    Generated Pass Rate %                     │
              │                               │
              └───────────────┬───────────────┘
                              ▼
                       Verdict Engine
            (PASSED / PARTIAL_PASS / FAILED /
             LOW_TEST_VALIDITY / TIMEOUT)
                              │
                     Triage Gate (Failures?)
                      /               \
             No Failures             Failures Exist
                 │                          │
                 ▼                          ▼
            [0 Tokens]               [Phase 2: LLM Call]
        (Offline Complete)          Targeted Failure Triage
                                            │
                                            ▼
                               Root-Cause Diagnostic Report
```

---

## 🔍 Failure Triage Matrix

When a test failure occurs, the pipeline inspects *which* implementation failed and sends only the relevant context to the LLM:

| Failure Pattern | Context Sent to LLM | Root-Cause Diagnosis |
| :--- | :--- | :--- |
| **Both solutions fail the same test** | Problem statement + failing test + traceback | **Invalid / Hallucinated Test Case** (test violates specification or Python semantics) |
| **Canonical fails, Generated passes** | Problem statement + canonical code + failing test + traceback | **Canonical Benchmark Limitation** (reference code missed an edge case) |
| **Generated fails, Canonical passes** | Problem statement + generated code + failing test + traceback | **Defect in Generated Code** (missing logic or algorithmic flaw) |
| **All tests pass** | *Nothing (0 tokens)* | **No diagnosis needed** (offline completion) |

---

## 📁 Repository Structure

```
├── agents/
│   ├── __init__.py
│   ├── code_generator.py      # Agent 1: LLM-based function synthesis
│   ├── test_generator.py      # Agent 2: Coverage-driven unit test generation
│   └── test_executor.py       # Agent 3: Subprocess sandbox, coverage & diagnostic triage
├── data/
│   ├── download_mbpp.py       # Automatic downloader for sanitized MBPP dataset
│   └── sanitized-mbpp.json    # MBPP benchmark dataset (ignored by git; auto-downloaded)
├── report/
│   ├── report.tex             # Comprehensive LaTeX technical report
│   └── *.png                  # Result screenshots and system diagrams
├── llm_client.py              # OpenAI-compatible API client wrapper
├── main.py                    # CLI entry point to run pipeline tasks
├── requirements.txt           # Minimal Python dependencies
└── .gitignore                 # Excludes cache, environments, secrets, and datasets
```

---

## 🚀 Quickstart Guide

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

### 2. Set Up Virtual Environment
```bash
# On Linux / macOS:
python3 -m venv .venv
source .venv/bin/activate

# On Windows (PowerShell):
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and provide your API key:
```bash
cp .env.example .env
```
Edit `.env`:
```env
NVIDIA_API_KEY=your_api_key_here
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
MODEL_NAME=nvidia/llama-3.1-nemotron-70b-instruct
```
*(Supports any OpenAI-compatible API endpoint such as NVIDIA NIM, OpenRouter, or OpenAI).*

### 5. Download the Benchmark Dataset
```bash
python data/download_mbpp.py
```

---

## 💻 Running the Pipeline

Run the pipeline on any task from the MBPP benchmark by specifying `--task <id>`:

```bash
# Run Task #2
python main.py --task 2

# Run Task #3
python main.py --task 3

# Run Task #12
python main.py --task 12
```

### Sample Output:
```text
==================================================
 EXECUTION RESULTS & TESTING METRICS
==================================================
Test Validity (Pass on Canonical) : 87.5%
Statement Coverage (on Gen Code)  : 100.0%
Generated Code Test Pass Rate     : 87.5%
Python Execution Verdict          : PARTIAL_PASS
Failed Tests (Generated Code)     : #1 (test_mixed_types)
Failed Tests (Canonical Code)     : #1 (test_mixed_types)

--------------------------------------------------
Agent 3 (Phase 2): Diagnostic Evaluation (LLM Triage)...

--- Diagnostic Verdict ---
[Category: BUGGY / INVALID TEST CASE]
The test case is invalid because Python treats True/1 and False/0 as equal values with identical hashes, causing sets and Counter to deduplicate them. The test incorrectly expects [True, 1] as two distinct elements in the intersection.
==================================================
```

---

## ⚙️ Hyperparameters

| Agent | Role | Temperature | Rationale |
| :--- | :--- | :---: | :--- |
| **Agent 1: Code Generator** | Function Synthesis | `0.2` | Prioritizes deterministic, standard, syntax-exact code |
| **Agent 2: Test Generator** | Test Suite Synthesis | `0.4` | Encourages diverse input exploration and tricky edge-case generation |
| **Agent 3: Diagnostic Engine** | Failure Root-Cause Analysis | `0.2` | Ensures factual, hallucination-free explanation of assertion tracebacks |

---

## 👥 Authors & Team Contributions

* **Pranay Kelotra (IMT2023563)** — MBPP dataset integration, `LLMClient` and API design, `CodeGeneratorAgent`, prompt engineering, and pipeline integration.
* **Siddharth Anil (IMT2023503)** — `TestGeneratorAgent`, `TestExecutorAgent` (subprocess isolation, branch coverage via `coverage.py`, verdict logic), diagnostic failure triage engine, and debugging.
* **Both Members** — System architecture, hyperparameter selection, experimental evaluation, and technical report writing.

---

## 📜 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
