import argparse
import requests
import sys


def get_random_word_from_gemini(api_key, timeout=10):
    """Try to get a single random noun from Gemini using the provided API key.

    This function is defensive: it will return None if Gemini responds with an
    error or an unexpected schema so callers can fall back to other sources.
    """
    if not api_key:
        return None

    prompt = "Generate one random, concrete noun in English (just the word, no explanation)."
    # NOTE: The exact Gemini endpoint and supported methods may vary by API
    # version. The original script used an endpoint that returned a 404. We
    # still attempt a request but handle errors gracefully.
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    params = {"key": api_key}

    try:
        resp = requests.post(url, headers=headers, params=params, json=data, timeout=timeout)
    except requests.RequestException as e:
        # Network error, return None to let caller fallback
        print(f"Warning: network error when calling Gemini: {e}", file=sys.stderr)
        return None

    try:
        response_json = resp.json()
    except ValueError:
        print("Warning: Gemini response was not valid JSON", file=sys.stderr)
        return None

    # Helpful debug output (don't print the API key)
    if resp.status_code != 200:
        print(f"Gemini API returned status {resp.status_code}: {response_json}", file=sys.stderr)
        return None

    # Defensive extraction: different Gemini responses may use different keys
    # Attempt known shapes. If not found, return None for fallback.
    if isinstance(response_json, dict):
        if "candidates" in response_json:
            try:
                word = response_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                return word
            except Exception:
                return None
        if "output" in response_json and isinstance(response_json["output"], list):
            # Another possible shape
            try:
                word = response_json["output"][0]["content"][0]["text"].strip()
                return word
            except Exception:
                return None

    # Unknown schema -> let caller fallback
    print("Warning: Gemini response did not contain expected keys; falling back.", file=sys.stderr)
    print("Gemini response sample:", response_json, file=sys.stderr)
    return None


def get_random_word_fallback(timeout=5):
    """Fetch a random word from a public free API as a fallback.

    This avoids failing when Gemini isn't available or the requested model
    isn't supported for the caller's API version.
    """
    # Use a simple public API that returns an array with one word.
    url = "https://random-word-api.herokuapp.com/word?number=1"
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and data:
            return data[0]
    except requests.RequestException as e:
        print(f"Fallback random-word API failed: {e}", file=sys.stderr)
    except ValueError:
        print("Fallback random-word API returned invalid JSON", file=sys.stderr)

    # Ultimate fallback: small local list
    local = ["bridge", "bicycle", "lamp", "ticket", "garden", "bench", "sensor"]
    import random

    return random.choice(local)


def random_word_association(problem_statement, api_key=None):
    word = None
    if api_key:
        word = get_random_word_from_gemini(api_key)

    if not word:
        # fallback path
        word = get_random_word_fallback()

    return {
        "problem_statement": problem_statement,
        "random_word": word,
        "association_prompt": (
            f"Connect the random word '{word}' to your problem. "
            f"How could '{word}' help solve or inspire new solutions for: '{problem_statement}'?"
        ),
    }


def main():
    parser = argparse.ArgumentParser(description="Random word association helper")
    parser.add_argument("problem", nargs="?", default="How can we improve parking in cities?",
                        help="Problem statement to associate the random word with")
    parser.add_argument("--api-key", dest="api_key", default=None,
                        help="Optional Gemini API key. If omitted, the script will use a fallback API.")
    args = parser.parse_args()

    result = random_word_association(args.problem, args.api_key)
    print(result)


if __name__ == "__main__":
    main()
