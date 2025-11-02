"""
LLM Client wrapper for both OpenAI and Anthropic
"""

import json
from typing import Dict, Any, Optional
from config import Config


class LLMClient:
    """Unified client for OpenAI and Anthropic LLMs"""

    def __init__(self, config: Config):
        self.config = config
        self.provider = config.llm_provider

        if self.provider == "openai":
            import openai
            self.client = openai.OpenAI(api_key=config.get_api_key())
        elif self.provider == "azure_openai":
            import openai
            self.client = openai.AzureOpenAI(
                api_key=config.get_api_key(),
                api_version=config.azure_openai_api_version,
                azure_endpoint=config.azure_openai_endpoint
            )
        elif self.provider == "anthropic":
            import anthropic
            self.client = anthropic.Anthropic(api_key=config.get_api_key())
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate a response from the LLM

        Args:
            system_prompt: System instructions
            user_prompt: User message
            response_format: Optional JSON schema for structured output
            temperature: Optional temperature override

        Returns:
            String response from the LLM
        """
        temp = temperature if temperature is not None else self.config.temperature

        if self.provider == "openai" or self.provider == "azure_openai":
            return self._generate_openai(system_prompt, user_prompt, response_format, temp)
        elif self.provider == "anthropic":
            return self._generate_anthropic(system_prompt, user_prompt, response_format, temp)

    def _generate_openai(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: Optional[str],
        temperature: float
    ) -> str:
        """Generate using OpenAI API"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        kwargs = {
            "model": self.config.get_model(),
            "messages": messages,
            "temperature": temperature,
            "max_tokens": self.config.max_tokens
        }

        # Add JSON mode if requested
        if response_format == "json":
            kwargs["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

    def _generate_anthropic(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: Optional[str],
        temperature: float
    ) -> str:
        """Generate using Anthropic API"""

        # Add JSON instruction if needed
        if response_format == "json":
            user_prompt = user_prompt + "\n\nPlease respond with valid JSON only."

        response = self.client.messages.create(
            model=self.config.get_model(),
            max_tokens=self.config.max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )

        return response.content[0].text

    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON response from LLM, handling markdown code blocks

        Args:
            response: Raw response string

        Returns:
            Parsed JSON dictionary
        """
        # Remove markdown code blocks if present
        response = response.strip()

        if response.startswith("```json"):
            response = response[7:]  # Remove ```json
        elif response.startswith("```"):
            response = response[3:]  # Remove ```

        if response.endswith("```"):
            response = response[:-3]  # Remove trailing ```

        response = response.strip()

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {e}")
            print(f"Raw response: {response[:500]}...")
            raise ValueError(f"Invalid JSON response from LLM: {e}")