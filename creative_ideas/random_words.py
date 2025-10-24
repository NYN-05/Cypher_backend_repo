import re
import argparse
import requests
import sys


def get_random_word_from_gemini(api_key, count=1, timeout=10):
    """Try to get a single random noun from Gemini using the provided API key.

    This function is defensive: it will return None if Gemini responds with an
    error or an unexpected schema so callers can fall back to other sources.
    """
    if not api_key:
        return None

    # Ask Gemini to return `count` nouns, comma-separated, no explanation
    prompt = f"Generate {count} random, concrete nouns in English (just the words, no explanation). Separate the words with commas."
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
        # sometimes Gemini may return plain text; try to parse text body
        text_body = resp.text if hasattr(resp, 'text') else None
        if text_body:
            # split by commas/newlines and return up to count
            parts = [p.strip() for p in re.split('[,\n]', text_body) if p.strip()]
            return parts[:count] if count > 1 else (parts[0] if parts else None)
        print("Warning: Gemini response was not valid JSON", file=sys.stderr)
        return None

    # Helpful debug output (don't print the API key)
    if resp.status_code != 200:
        print(f"Gemini API returned status {resp.status_code}: {response_json}", file=sys.stderr)
        return None

    # Defensive extraction: different Gemini responses may use different keys
    # Attempt known shapes. If not found, try to extract text and split into words.
    if isinstance(response_json, dict):
        # Try candidates -> content parts path
        if "candidates" in response_json:
            try:
                text = response_json["candidates"][0]["content"]["parts"][0]["text"].strip()
            except Exception:
                text = None
        elif "output" in response_json and isinstance(response_json["output"], list):
            try:
                text = response_json["output"][0]["content"][0]["text"].strip()
            except Exception:
                text = None
        else:
            # try to find any text field
            text = None

        if text:
            parts = [p.strip() for p in re.split('[,\n]', text) if p.strip()]
            return parts[:count] if count > 1 else (parts[0] if parts else None)

    # Unknown schema -> try to stringify and split
    try:
        text_body = resp.text
        parts = [p.strip() for p in re.split('[,\n]', text_body) if p.strip()]
        if parts:
            return parts[:count] if count > 1 else parts[0]
    except Exception:
        pass
    print("Warning: Gemini response did not contain expected keys; falling back.", file=sys.stderr)
    print("Gemini response sample:", response_json, file=sys.stderr)
    return None


def get_random_word_fallback(count=1, timeout=5):
    """Fetch a random word from a public free API as a fallback.

    This avoids failing when Gemini isn't available or the requested model
    isn't supported for the caller's API version.
    """
    # Use a simple public API that returns an array with one word.
    # The public API supports a 'number' parameter
    url = f"https://random-word-api.herokuapp.com/word?number={count}"
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and data:
            return data if count > 1 else data[0]
    except requests.RequestException as e:
        print(f"Fallback random-word API failed: {e}", file=sys.stderr)
    except ValueError:
        print("Fallback random-word API returned invalid JSON", file=sys.stderr)

    # Ultimate fallback: small local list
    local = ["bridge", "bicycle", "lamp", "ticket", "garden", "bench", "sensor", "clock", "mirror", "candle", "book", "key"]
    import random

    if count > 1:
        return random.sample(local, min(count, len(local)))
    return random.choice(local)


def random_word_association(problem_statement, api_key=None, count=4):
    """Return `count` random words and association prompts.

    Backwards compatible: if count==1 returns the original shape with
    'random_word' and 'association_prompt'. If count>1 returns
    'random_words' (list) and 'association_prompts' (list).
    """
    words = None
    if api_key:
        try:
            words = get_random_word_from_gemini(api_key, count=count)
        except Exception:
            words = None

    if not words:
        words = get_random_word_fallback(count=count)

    # Normalize to list
    if isinstance(words, str):
        words = [words]

    words = words or []

    prompts = [
        f"Connect the random word '{w}' to your problem. How could '{w}' help solve or inspire new solutions for: '{problem_statement}'?"
        for w in words
    ]

    if count == 1:
        w = words[0] if words else None
        return {
            "problem_statement": problem_statement,
            "random_word": w,
            "association_prompt": prompts[0] if prompts else None,
        }

    return {
        "problem_statement": problem_statement,
        "random_words": words,
        "association_prompts": prompts,
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
