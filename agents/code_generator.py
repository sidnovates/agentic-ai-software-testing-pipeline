from llm_client import LLMClient

class CodeGeneratorAgent:
    """Agent responsible for generating unit-level Python functions from specifications."""
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def generate_code(self, prompt: str, test_hints: list = None) -> str:
        """Generates the Python function solving the problem."""
        system_prompt = (
            "You are an expert Python software engineer. "
            "Write a single, correct Python function that solves the given problem. "
            "Important: Match the expected function name and signature indicated in the examples. "
            "Include any required imports. Return ONLY the executable Python code inside a ```python ``` block."
        )

        user_prompt = f"Problem Description:\n{prompt}\n\n"
        if test_hints:
            user_prompt += "Example assertions:\n" + "\n".join(test_hints[:2]) + "\n\n"
        user_prompt += "Write the complete Python function implementation:"

        raw_response = self.llm.query(system_prompt, user_prompt, temperature=0.2)
        code = self.llm.extract_code(raw_response)
        return code
