"""
Large Language Model service using various providers
"""

import logging
from typing import Optional, Dict, Any
from config import Config

logger = logging.getLogger(__name__)


class LLMService:
    """LLM service with multiple provider support"""

    def __init__(self, config: Config):
        self.config = config
        self.provider = None
        self.client = None
        self._available = False

    async def initialize(self):
        """Initialize LLM service with configured provider"""
        provider_name = self.config.get("llm.provider", "openai")

        try:
            if provider_name == "openai":
                await self._init_openai()
            elif provider_name == "anthropic":
                await self._init_anthropic()
            elif provider_name == "ollama":
                await self._init_ollama()
            else:
                logger.error(f"Unknown LLM provider: {provider_name}")
                return

            self.provider = provider_name
            self._available = True
            logger.info(f"LLM service initialized with provider: {provider_name}")

        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {e}")
            self._available = False

    async def _init_openai(self):
        """Initialize OpenAI LLM"""
        try:
            import openai

            api_key = self.config.get("llm.openai_api_key")
            if not api_key:
                raise ValueError("OpenAI API key not configured")

            openai.api_key = api_key
            self.client = openai

        except ImportError:
            logger.error("OpenAI library not installed")
            raise

    async def _init_anthropic(self):
        """Initialize Anthropic Claude"""
        try:
            import anthropic

            api_key = self.config.get("llm.anthropic_api_key")
            if not api_key:
                raise ValueError("Anthropic API key not configured")

            self.client = anthropic.Anthropic(api_key=api_key)

        except ImportError:
            logger.error("Anthropic library not installed")
            raise

    async def _init_ollama(self):
        """Initialize Ollama local LLM"""
        try:
            import ollama

            self.client = ollama

        except ImportError:
            logger.error("Ollama library not installed")
            raise

    async def cleanup(self):
        """Cleanup LLM service"""
        self.client = None
        self._available = False
        logger.info("LLM service cleaned up")

    def is_available(self) -> bool:
        """Check if LLM service is available"""
        return self._available

    async def generate_response(
        self, user_input: str, context: Dict[str, Any] = None
    ) -> Optional[str]:
        """
        Generate response using LLM

        Args:
            user_input: User's input text
            context: Additional context for the conversation

        Returns:
            Generated response or None if failed
        """
        if not self._available or not self.client:
            logger.error("LLM service not available")
            return None

        try:
            if self.provider == "openai":
                return await self._generate_openai(user_input, context)
            elif self.provider == "anthropic":
                return await self._generate_anthropic(user_input, context)
            elif self.provider == "ollama":
                return await self._generate_ollama(user_input, context)
            else:
                logger.error(f"Unknown provider: {self.provider}")
                return None

        except Exception as e:
            logger.error(f"Error in LLM generation: {e}")
            return None

    async def _generate_openai(
        self, user_input: str, context: Dict[str, Any] = None
    ) -> Optional[str]:
        """Generate response using OpenAI"""
        try:
            system_prompt = self.config.get(
                "llm.system_prompt", "You are a helpful personal assistant robot."
            )

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ]

            # Add context if provided
            if context:
                context_str = f"Context: {context}"
                messages.insert(1, {"role": "system", "content": context_str})

            from openai import OpenAI
# client = OpenAI()
            client: OpenAI = self.client
            response = await client.responses.create(
                model=self.config.get("llm.model", "gpt-4.1-mini"),
                # reasoning={"effort": "low"},
                input=[
                    {
                        "role": "developer",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_input,
                    }
                ]
            )

            # response = self.client.ChatCompletion.create(
            #     model=self.config.get("llm.model", "gpt-3.5-turbo"),
            #     messages=messages,
            #     max_tokens=self.config.get("llm.max_tokens", 150),
            #     temperature=self.config.get("llm.temperature", 0.7),
            # )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"OpenAI LLM error: {e}")
            return None

    async def _generate_anthropic(
        self, user_input: str, context: Dict[str, Any] = None
    ) -> Optional[str]:
        """Generate response using Anthropic Claude"""
        try:
            system_prompt = self.config.get(
                "llm.system_prompt", "You are a helpful personal assistant robot."
            )

            prompt = f"{system_prompt}\n\nUser: {user_input}\n\nAssistant:"

            if context:
                prompt = f"{system_prompt}\n\nContext: {context}\n\nUser: {user_input}\n\nAssistant:"

            response = self.client.completions.create(
                model=self.config.get("llm.model", "claude-3-sonnet-20240229"),
                prompt=prompt,
                max_tokens_to_sample=self.config.get("llm.max_tokens", 150),
                temperature=self.config.get("llm.temperature", 0.7),
            )

            return response.completion.strip()

        except Exception as e:
            logger.error(f"Anthropic LLM error: {e}")
            return None

    async def _generate_ollama(
        self, user_input: str, context: Dict[str, Any] = None
    ) -> Optional[str]:
        """Generate response using Ollama"""
        try:
            system_prompt = self.config.get(
                "llm.system_prompt", "You are a helpful personal assistant robot."
            )

            prompt = f"{system_prompt}\n\nUser: {user_input}"

            if context:
                prompt = f"{system_prompt}\n\nContext: {context}\n\nUser: {user_input}"

            response = self.client.generate(
                model=self.config.get("llm.model", "llama2"),
                prompt=prompt,
                options={
                    "temperature": self.config.get("llm.temperature", 0.7),
                    "max_tokens": self.config.get("llm.max_tokens", 150),
                },
            )

            return response["response"].strip()

        except Exception as e:
            logger.error(f"Ollama LLM error: {e}")
            return None
