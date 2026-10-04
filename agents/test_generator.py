from llm_client import LLMClient

class TestGeneratorAgent:
    """Agent responsible for generating unit tests satisfying coverage criteria."""
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def generate_tests(self, prompt: str, generated_code: str, coverage_goal: str = "statement and branch coverage") -> str:
        """Generates a unittest test suite targeting coverage criteria for the provided code."""
        system_prompt = (
            "You are an expert Software Test Engineer. "
            "Your task is to write unit tests using Python's standard `unittest` framework. "
            f"Testing Objective: Maximize {coverage_goal}. "
            "Ensure you cover normal execution paths, edge cases, boundaries, and exceptional values. "
            "Write standard test methods inside a class named `TestSolution(unittest.TestCase)`. "
            "Do NOT import from solution files; assume the function is already available in the global scope or imported. "
            "Return ONLY the executable Python unit test code inside a ```python ``` block."
        )

        user_prompt = (
            f"Problem Description:\n{prompt}\n\n"
            f"Implementation Under Test:\n```python\n{generated_code}\n```\n\n"
            "Generate 4 to 8 distinct unit test methods in `TestSolution(unittest.TestCase)` "
            f"to thoroughly test this function and achieve 100% {coverage_goal}."
        )

        raw_response = self.llm.query(system_prompt, user_prompt, temperature=0.4)
        test_code = self.llm.extract_code(raw_response)
        return test_code
