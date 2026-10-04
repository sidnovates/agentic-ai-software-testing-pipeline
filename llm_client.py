import os
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class LLMClient:
    """Lightweight wrapper for NVIDIA Nemotron / OpenAI-compatible endpoints."""
    def __init__(self):
        self.api_key = os.getenv("NVIDIA_API_KEY", "")
        self.base_url = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
        self.model_name = os.getenv("MODEL_NAME", "nvidia/llama-3.1-nemotron-70b-instruct")

        if not self.api_key:
            print("[Warning] NVIDIA_API_KEY is not set. Please set it in your .env file.")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def query(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        """Sends a query to the model and returns the text response."""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature
        )
        return response.choices[0].message.content

    @staticmethod
    def extract_code(text: str) -> str:
        """Extracts Python code from markdown blocks (```python ... ```) or returns raw text."""
        pattern = r"```(?:python)?\s*(.*?)\s*```"
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            return matches[-1].strip()
        return text.strip()
