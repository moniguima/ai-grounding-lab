"""
Configuration Module for ECLSS Q&A System

Constants:
    DEFAULT_MODEL: The default LLM model to use
    DEFAULT_TEMPERATURE: Temperature setting for deterministic outputs

Functions:
 
Date: 2025-11-11
"""

import os
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI


# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

# LLM configuration
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0  # Deterministic for factual questions


# ============================================================================
# ENVIRONMENT SETUP (SOLID: Single Responsibility - each helper has one purpose)
# ============================================================================

def _load_environment_variables() -> None:
    """Load environment variables from .env file."""
    load_dotenv(dotenv_path=find_dotenv())


def _configure_langsmith_tracing() -> None:
    """Configure LangSmith tracing programmatically."""
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_PROJECT"] = "AI-GL"


def _get_openai_api_key() -> str:
    """
    Get and validate OpenAI API key from environment.

    Returns:
        OpenAI API key

    Raises:
        ValueError: If API key is not found
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found. Please create a .env file with your API key."
        )
    return api_key


def _check_langsmith_status() -> None:
    """Check and print LangSmith tracing status."""
    langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
    if langsmith_api_key:
        print("   ℹ️  LangSmith tracing enabled - view traces at https://smith.langchain.com")
    else:
        print("   ℹ️  LangSmith tracing disabled (LANGSMITH_API_KEY not found)")


def setup_environment() -> ChatOpenAI:
    """
    Set up the environment and initialize the LLM.

    Returns:
        ChatOpenAI: Configured LLM instance

    LangSmith Tracing:
    LangSmith automatically traces all LLM calls. This is incredibly useful for:
    - Debugging prompts (see exactly what's sent to the LLM)
    - Monitoring performance (latency, token usage)
    - Iterating on prompts (compare different versions)

    To enable LangSmith:
    1. Sign up at https://smith.langchain.com (free tier available)
    2. Get your API key from the settings
    3. Add to .env file:
       LANGSMITH_API_KEY=your_key_here
       LANGSMITH_ENDPOINT='https://api.smith.langchain.com'
    4. Run your code - traces appear automatically in the dashboard!

    Note: LANGSMITH_TRACING and LANGSMITH_PROJECT are configured
    programmatically in this function.
    """
    _load_environment_variables()
    _configure_langsmith_tracing()
    _check_langsmith_status()
    api_key = _get_openai_api_key()

    llm = ChatOpenAI(
        model=DEFAULT_MODEL,
        temperature=DEFAULT_TEMPERATURE,
        api_key=api_key
    )

    return llm


