"""Small helper to call Google Generative Language (Gemini) REST API using an API key.

This avoids using the `genai` client library or an endpoint object. It uses
the public REST endpoint and an API key passed either directly or via
the GEMINI_API_KEY environment variable.

Usage:
  from gemini_client import generate_text
  text = generate_text(api_key, model, prompt)

The function is intentionally tolerant of a few response shapes returned by
different server versions.
"""
from typing import Optional
import os
import requests


def _post_generate(api_key: str, model: str, body: dict, timeout: int = 15):
    """Low-level POST to the generativelanguage REST endpoint.

    Returns parsed JSON or raises requests.HTTPError on non-2xx.
    """
    base = "https://generativelanguage.googleapis.com"
    url = f"{base}/v1beta2/models/{model}:generateText"
    # Put API key in query param; acceptable for simple API key usage.
    params = {"key": api_key}
    resp = requests.post(url, params=params, json=body, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def generate_text(api_key: Optional[str], model: str, prompt: str,
                  temperature: float = 0.2, max_output_tokens: int = 256,
                  timeout: int = 15) -> str:
    """Generate text from Gemini using an API key (no genai lib).

    Args:
      api_key: Gemini API key string (if None, read GEMINI_API_KEY env var).
      model: Model id (example: "gemini-1.5" or "text-bison-001").
      prompt: Prompt text to send.
      temperature: Sampling temperature.
      max_output_tokens: Maximum tokens to produce.
      timeout: HTTP timeout in seconds.

    Returns the generated string. On error raises an exception.
    """
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ValueError("API key required: pass api_key or set GEMINI_API_KEY")

    # Request body using common field names seen in examples.
    body = {
        "prompt": {"text": prompt},
        "temperature": temperature,
        "maxOutputTokens": max_output_tokens,
    }

    data = _post_generate(key, model, body, timeout=timeout)

    # The API can return a few shapes. Try the most common ones in order.
    # 1) {"candidates": [{"output": "..."}, ...]}
    if isinstance(data, dict):
        cands = data.get("candidates") or data.get("candidates")
        if cands and isinstance(cands, list) and len(cands) > 0:
            first = cands[0]
            for k in ("output", "content", "text", "outputText"):
                if isinstance(first, dict) and k in first:
                    return first[k]
            # If first is a string
            if isinstance(first, str):
                return first

        # 2) Some responses put the text at data['result'] or data['output']
        for keyname in ("result", "output", "text"):
            candidate = data.get(keyname)
            if isinstance(candidate, str):
                return candidate

    # Fallback: convert whole JSON to string
    return str(data)


__all__ = ["generate_text"]
