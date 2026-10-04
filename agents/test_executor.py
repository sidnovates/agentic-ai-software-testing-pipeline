import os
import sys
import json
import re
import tempfile
import subprocess

class TestExecutorAgent:
    """Agent that executes unit tests in pure Python using unittest and coverage.py."""

    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        self.python_bin = sys.executable

    def _prepare_test_script(self, test_code: str) -> str:
        """Ensures solution is imported and unittest.main() is present."""
        code_lines = []
        if "from solution import" not in test_code and "import solution" not in test_code:
            code_lines.append("from solution import *\n")
        if "import unittest" not in test_code:
            code_lines.append("import unittest\n")
        code_lines.append(test_code)

        if "unittest.main" not in test_code:
            code_lines.append("\nif __name__ == '__main__':\n    unittest.main(verbosity=2)\n")

        return "\n".join(code_lines)

    def _parse_unittest_output(self, stderr: str, returncode: int) -> dict:
        """Parses unittest output to count tests run, passed, and failed."""
        ran_match = re.search(r"Ran (\d+) test", stderr)
        total = int(ran_match.group(1)) if ran_match else 0

        fail_match = re.search(r"failures=(\d+)", stderr)
        failures = int(fail_match.group(1)) if fail_match else 0

        err_match = re.search(r"errors=(\d+)", stderr)
        errors = int(err_match.group(1)) if err_match else 0

        passed = max(0, total - (failures + errors))
        success = (returncode == 0) and (total > 0)

        # Extract specific failure details per test to save tokens
        failure_details = {}
        pattern = r"={5,}\n(?:FAIL|ERROR):\s*(\w+)[^\n]*\n-{5,}\n(.*?)(?=\n-{5,}|\n={5,}|\Z)"
        for match in re.finditer(pattern, stderr, re.DOTALL):
            test_name = match.group(1)
            error_block = match.group(2).strip()
            lines = error_block.splitlines()
            failure_details[test_name] = "\n".join(lines[-3:]) if len(lines) > 3 else error_block

        if returncode != 0 and not failure_details and stderr.strip():
            failure_details["execution_error"] = "\n".join(stderr.strip().splitlines()[-4:])

        return {
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": failures,
            "error_tests": errors,
            "failure_details": failure_details,
            "success": success
        }

    def run_tests_against_code(self, code: str, test_code: str, measure_coverage: bool = False) -> dict:
        """Runs test_code against code in an isolated temporary directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            sol_path = os.path.join(temp_dir, "solution.py")
            test_path = os.path.join(temp_dir, "test_solution.py")

            with open(sol_path, "w", encoding="utf-8") as f:
                f.write(code)

            prepared_tests = self._prepare_test_script(test_code)
            with open(test_path, "w", encoding="utf-8") as f:
                f.write(prepared_tests)

            # Command to run tests
            if measure_coverage:
                cmd = [
                    self.python_bin, "-m", "coverage", "run",
                    "--source=solution", "--branch",
                    "-m", "unittest", "test_solution.py"
                ]
            else:
                cmd = [self.python_bin, "-m", "unittest", "test_solution.py", "-v"]

            try:
                result = subprocess.run(
                    cmd,
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )
                output = self._parse_unittest_output(result.stderr, result.returncode)
                output["raw_stderr"] = result.stderr
                output["raw_stdout"] = result.stdout
                output["timed_out"] = False

                # Extract coverage if requested
                if measure_coverage:
                    cov_cmd = [self.python_bin, "-m", "coverage", "json", "-o", "coverage.json"]
                    subprocess.run(cov_cmd, cwd=temp_dir, capture_output=True, text=True)
                    cov_file = os.path.join(temp_dir, "coverage.json")
                    if os.path.exists(cov_file):
                        with open(cov_file, "r", encoding="utf-8") as cf:
                            cov_data = json.load(cf)
                            totals = cov_data.get("totals", {})
                            output["statement_coverage_percent"] = round(totals.get("percent_covered", 0.0), 2)
                            output["covered_lines"] = totals.get("covered_lines", 0)
                            output["num_statements"] = totals.get("num_statements", 0)
                    else:
                        output["statement_coverage_percent"] = 0.0

            except subprocess.TimeoutExpired:
                output = {
                    "total_tests": 0,
                    "passed_tests": 0,
                    "failed_tests": 0,
                    "error_tests": 1,
                    "success": False,
                    "timed_out": True,
                    "statement_coverage_percent": 0.0,
                    "raw_stderr": "Execution timed out (potential infinite loop)"
                }

        return output

    def evaluate(self, canonical_code: str, generated_code: str, test_code: str) -> dict:
        """Executes generated tests on both Canonical Solution and Generated Code."""
        # 1. Test Validity Check on Canonical Solution
        canonical_result = self.run_tests_against_code(canonical_code, test_code, measure_coverage=False)
        can_total = canonical_result["total_tests"]
        can_passed = canonical_result["passed_tests"]
        test_validity_percent = round((can_passed / can_total) * 100, 2) if can_total > 0 else 0.0

        # 2. Execution & Coverage on Generated Code
        gen_result = self.run_tests_against_code(generated_code, test_code, measure_coverage=True)
        gen_total = gen_result["total_tests"]
        gen_passed = gen_result["passed_tests"]
        gen_pass_percent = round((gen_passed / gen_total) * 100, 2) if gen_total > 0 else 0.0

        # 3. Formulate Verdict
        if gen_result.get("timed_out"):
            verdict = "TIMEOUT"
        elif test_validity_percent < 50.0:
            verdict = "LOW_TEST_VALIDITY"
        elif gen_result["success"]:
            verdict = "PASSED"
        elif gen_passed > 0:
            verdict = "PARTIAL_PASS"
        else:
            verdict = "FAILED"

        return {
            "test_validity_percent": test_validity_percent,
            "statement_coverage_percent": gen_result.get("statement_coverage_percent", 0.0),
            "generated_pass_percent": gen_pass_percent,
            "canonical_execution": canonical_result,
            "generated_execution": gen_result,
            "verdict": verdict
        }

    @staticmethod
    def _extract_test_snippet(test_code: str, test_name: str) -> str:
        """Extracts the specific test method from test_code to save prompt tokens."""
        if not test_code or not test_name:
            return ""
        pattern = rf"(def {re.escape(test_name)}\b.*?)(?=\n    def |\nif __name__|\Z)"
        match = re.search(pattern, test_code, re.DOTALL)
        return match.group(1).strip() if match else f"# Test: {test_name}"

    def diagnose(self, llm_client, prompt: str, canonical_code: str, generated_code: str, test_code: str, eval_result: dict) -> str:
        """
        Token-optimized diagnostic engine:
        - 0 tokens if all tests pass.
        - If tests fail, sends only the minimal relevant code and failed test(s).
        """
        can_fails = eval_result.get("canonical_execution", {}).get("failure_details", {})
        gen_fails = eval_result.get("generated_execution", {}).get("failure_details", {})

        # Scenario 1: Zero failures -> No LLM tokens consumed!
        if not can_fails and not gen_fails:
            return "No failures detected. All unit tests passed cleanly on both Canonical and Generated code."

        # Triage failure sets
        both = set(can_fails.keys()) & set(gen_fails.keys())
        can_only = set(can_fails.keys()) - both
        gen_only = set(gen_fails.keys()) - both

        diagnoses = []
        sys_prompt = "You are an expert Software Testing Diagnostic Engine. Provide direct, concise 2-sentence answers."

        # Scenario 2: Fails on BOTH -> Test case itself is likely invalid or hallucinated
        if both:
            tests_info = "\n\n".join([
                f"Test: {t}\nCode:\n{self._extract_test_snippet(test_code, t)}\nError:\n{can_fails[t]}"
                for t in both
            ])
            user_msg = (
                f"[Problem Specification]\n{prompt}\n\n"
                f"[Failed Test Case(s) - Failed on BOTH independent solutions]\n{tests_info}\n\n"
                "Both the canonical reference and generated code failed this test. "
                "Is the test case itself invalid, contradictory to the specification, or hallucinated? Explain why in 2 sentences."
            )
            ans = llm_client.query(sys_prompt, user_msg, temperature=0.1)
            diagnoses.append(f"[Category: BUGGY / INVALID TEST CASE]\n{ans}")

        # Scenario 3: Fails on CANONICAL only -> Canonical benchmark limitation
        if can_only:
            tests_info = "\n\n".join([
                f"Test: {t}\nCode:\n{self._extract_test_snippet(test_code, t)}\nError on Canonical:\n{can_fails[t]}"
                for t in can_only
            ])
            user_msg = (
                f"[Problem Specification]\n{prompt}\n\n"
                f"[Canonical Benchmark Code]\n```python\n{canonical_code}\n```\n\n"
                f"[Failed Test Case(s) on Canonical]\n{tests_info}\n\n"
                "The generated code passed this test, but the canonical benchmark code failed. "
                "Explain why the canonical code failed (e.g., edge-case omission like n <= 1) and whether the test is reasonable in 2 sentences."
            )
            ans = llm_client.query(sys_prompt, user_msg, temperature=0.1)
            diagnoses.append(f"[Category: CANONICAL BENCHMARK LIMITATION]\n{ans}")

        # Scenario 4: Fails on GENERATED only -> Defect in generated code
        if gen_only:
            tests_info = "\n\n".join([
                f"Test: {t}\nCode:\n{self._extract_test_snippet(test_code, t)}\nError on Generated Code:\n{gen_fails[t]}"
                for t in gen_only
            ])
            user_msg = (
                f"[Problem Specification]\n{prompt}\n\n"
                f"[Generated Code Under Test]\n```python\n{generated_code}\n```\n\n"
                f"[Failed Test Case(s) on Generated Code]\n{tests_info}\n\n"
                "The canonical benchmark code passed this test, but the generated code failed. "
                "Explain what specific defect or missing logic in the generated code caused this failure in 2 sentences."
            )
            ans = llm_client.query(sys_prompt, user_msg, temperature=0.1)
            diagnoses.append(f"[Category: DEFECT IN GENERATED CODE]\n{ans}")

        return "\n\n".join(diagnoses)

    def generate_llm_verdict(self, llm_client, prompt: str, generated_code: str, eval_result: dict, canonical_code: str = "", test_code: str = "") -> str:
        """Backward-compatible wrapper delegating to diagnose."""
        return self.diagnose(llm_client, prompt, canonical_code, generated_code, test_code, eval_result)
