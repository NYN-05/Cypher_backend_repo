import argparse
import requests
import sys
import random
import os
import json


def get_gemini_reverse_ideas(problem, api_key, endpoint, n=5, timeout=12):
    """Attempt to get reverse-brainstorm ideas from Gemini. Return list or None on failure."""
    if not api_key or not endpoint:
        return None

    prompt = (
        f"Perform reverse brainstorming for the problem: \"{problem}\".\n"
        f"List {n} concise ways to make the problem worse (reverse brainstorm).\n"
        "Return the items as plain lines only, no numbering, no extra commentary."
    )

    url = endpoint
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    params = {"key": api_key}

    try:
        resp = requests.post(url, headers=headers, params=params, json=data, timeout=timeout)
    except requests.RequestException as e:
        print(f"Warning: network error calling Gemini: {e}", file=sys.stderr)
        return None

    try:
        json_resp = resp.json()
    except ValueError:
        print("Warning: Gemini response not valid JSON", file=sys.stderr)
        return None

    if resp.status_code != 200:
        print(f"Gemini API status {resp.status_code}: {json_resp}", file=sys.stderr)
        return None

    # Try common response shapes
    if isinstance(json_resp, dict):
        # shape used earlier
        if "candidates" in json_resp:
            try:
                text = json_resp["candidates"][0]["content"]["parts"][0]["text"].strip()
                items = [line.strip() for line in text.splitlines() if line.strip()]
                return items[:n]
            except Exception:
                return None
        # alternative shape
        if "output" in json_resp and isinstance(json_resp["output"], list):
            try:
                text = json_resp["output"][0]["content"][0]["text"].strip()
                items = [line.strip() for line in text.splitlines() if line.strip()]
                return items[:n]
            except Exception:
                return None

    print("Warning: Gemini response schema unexpected; falling back.", file=sys.stderr)
    return None


def load_templates_from_env_or_file():
    """Load reverse-brainstorm templates from an external source.

    Priority:
      1. File path from env var REVERSE_TEMPLATES_FILE (JSON array)
      2. JSON array string in env var REVERSE_TEMPLATES

    Raises ValueError if no templates found or parsing fails.
    """
    # 1) file
    fp = os.environ.get("REVERSE_TEMPLATES_FILE")
    if fp:
        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list) and data:
                return data
            raise ValueError("Templates file does not contain a non-empty JSON array")
        except Exception as e:
            raise ValueError(f"Failed to load templates from file '{fp}': {e}")

    # 2) env var JSON
    env_json = os.environ.get("REVERSE_TEMPLATES")
    if env_json:
        try:
            data = json.loads(env_json)
            if isinstance(data, list) and data:
                return data
            raise ValueError("REVERSE_TEMPLATES must be a JSON array of strings")
        except Exception as e:
            raise ValueError(f"Failed to parse REVERSE_TEMPLATES: {e}")

    raise ValueError("No reverse-brainstorm templates found. Set REVERSE_TEMPLATES_FILE or REVERSE_TEMPLATES environment variable.")


def fallback_reverse_ideas(problem, templates, n=5):
    """Generate reverse-brainstorm (bad/worsening) ideas locally as a fallback.

    Templates must be provided by `load_templates_from_env_or_file` to avoid
    hardcoding list contents in the source code.
    """
    if not templates or not isinstance(templates, list):
        raise ValueError("Templates must be a non-empty list")

    random.shuffle(templates)
    # If requested n > templates, create variations
    results = []
    i = 0
    while len(results) < n:
        base = templates[i % len(templates)]
        if i >= len(templates):
            # vary slightly
            base = base + f" (variation {i})"
        results.append(base)
        i += 1

    return results[:n]


def invert_reverse_to_solution(reverse_idea):
    """Simple heuristic to invert a reverse (bad) idea into a solution idea.

    This is intentionally lightweight: it attempts to flip verbs/nouns or
    produces a short 'Do the opposite' suggestion.
    """
    opposites = {
        "allow": "restrict",
        "remove": "add",
        "ban": "permit",
        "widen": "narrow or redesign for multi-modal use",
        "close": "open or repurpose for shared use",
        "free": "priced appropriately to manage demand",
        "cheap": "priced to manage demand and encourage turnover",
        "reduce": "increase/improve",
        "increase": "decrease or optimize",
    }

    # Lowercase for simple matching
    low = reverse_idea.lower()
    for k, v in opposites.items():
        if k in low:
            return low.replace(k, v).capitalize()

    # fallback
    return "Do the opposite: " + reverse_idea


def generate_reverse_brainstorm(problem, api_key=None, n=5, invert=False):
    # Deprecated: use the structured five-step flow functions below. Keep for
    # backward compatibility by delegating to the new flow when templates are
    # available via environment or file.
    templates = None
    try:
        templates = load_templates_from_env_or_file()
    except Exception:
        # If templates can't be loaded, we can't run without hardcoded values.
        templates = None

    endpoint = os.environ.get("GEMINI_ENDPOINT")
    api_key_env = api_key or os.environ.get("GEMINI_API_KEY")

    if templates:
        negatives = brainstorm_negative_ideas(problem, templates, api_key=api_key_env, endpoint=endpoint, n=n)
    else:
        # Last-resort: generate a minimal list using the heuristic (no hardcoded list)
        negatives = [f"No templates provided - placeholder negative idea {i+1}" for i in range(n)]

    result = {
        "problem_statement": problem,
        "reverse_ideas": negatives,
    }

    if invert:
        inverted = [invert_reverse_to_solution(i) for i in negatives]
        result["inverted_solutions"] = inverted

    return result


def define_problem(problem):
    """Step 1: Clearly state the original problem."""
    return problem.strip()


def reverse_problem(problem):
    """Step 2: Produce a reversed/negative phrasing of the problem."""
    # Simple reversal template
    return f"How could we make the following worse: {problem.strip()}?"


def brainstorm_negative_ideas(problem, templates, api_key=None, endpoint=None, n=5):
    """Step 3: Brainstorm negative ideas using Gemini or fallback."""
    # Try Gemini first if key provided
    items = None
    if api_key:
        items = get_gemini_reverse_ideas(problem, api_key, endpoint, n=n)

    if not items:
        items = fallback_reverse_ideas(problem, templates, n=n)

    return items


def analyze_and_flip(negative_ideas, api_key=None, endpoint=None):
    """Step 4: Flip each negative idea into a constructive positive solution.

    If an API key is provided we attempt to use Gemini to perform the flip; if
    that fails we fall back to the lightweight heuristic `invert_reverse_to_solution`.
    """
    flipped = []
    for neg in negative_ideas:
        # Try heuristic first (fast, deterministic)
        solution = invert_reverse_to_solution(neg)

        # If there is an API key, attempt a better flip via Gemini (best-effort)
        if api_key and endpoint:
            try:
                # Prompt Gemini to flip one item into a positive solution
                prompt = (
                    f"Flip this negative idea into a constructive, actionable solution:\n\"{neg}\"\n"
                    "Return a single short sentence that describes the solution with one suggested next step."
                )
                url = endpoint
                headers = {"Content-Type": "application/json"}
                data = {"contents": [{"parts": [{"text": prompt}]}]}
                params = {"key": api_key}
                resp = requests.post(url, headers=headers, params=params, json=data, timeout=12)
                jr = resp.json() if resp.status_code == 200 else None
                if jr and isinstance(jr, dict) and "candidates" in jr:
                    cand = jr["candidates"][0]["content"]["parts"][0]["text"].strip()
                    if cand:
                        solution = cand
            except Exception:
                # Ignore errors and keep heuristic solution
                pass

        flipped.append(solution)

    return flipped


def evaluate_and_develop(solutions, top_k=3):
    """Step 5: Evaluate and develop concrete action steps.

    This function selects the top_k solutions (simple heuristic: shortest
    solutions first for readability) and generates a tiny action template for
    each.
    """
    # Simple scoring: shorter solutions get higher priority (heuristic)
    ranked = sorted(solutions, key=lambda s: len(s))
    selected = ranked[:top_k]

    actions = []
    for sol in selected:
        action = {
            "solution": sol,
            "next_steps": [
                "Draft a small pilot (1-2 week) to test the idea",
                "Define one metric to measure success",
                "Assign a single owner to run the pilot",
            ],
            "suggested_metric": "% change in parking turnover or user satisfaction (choose one)",
        }
        actions.append(action)

    return {
        "selected_solutions": selected,
        "actions": actions,
    }


def main():
    parser = argparse.ArgumentParser(description="Reverse brainstorming helper")
    parser.add_argument("problem", nargs=1,
                        help="Problem statement to reverse-brainstorm (required)")
    parser.add_argument("--api-key", dest="api_key", default=None,
                        help="Optional Gemini API key. If provided, script will attempt Gemini first.")
    parser.add_argument("--num", dest="n", type=int, default=5, help="Number of reverse ideas to generate")
    parser.add_argument("--invert", dest="invert", action="store_true",
                        help="Also produce inverted solution ideas for each reverse idea")
    args = parser.parse_args()

    # Problem is required (avoid hardcoding a default)
    problem = args.problem[0].strip()

    # Load templates from file or env (required to avoid hardcoded templates)
    try:
        templates = load_templates_from_env_or_file()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        print("Provide templates via REVERSE_TEMPLATES_FILE or REVERSE_TEMPLATES environment variable.", file=sys.stderr)
        sys.exit(1)

    # API key and endpoint come from CLI or environment (no hardcoded values)
    api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
    endpoint = os.environ.get("GEMINI_ENDPOINT")

    # Step 1: Define
    step1 = define_problem(problem)

    # Step 2: Reverse
    step2 = reverse_problem(step1)

    # Step 3: Brainstorm negatives
    step3 = brainstorm_negative_ideas(step1, templates, api_key=api_key, endpoint=endpoint, n=args.n)

    # Step 4: Analyze & flip
    step4 = analyze_and_flip(step3, api_key=api_key, endpoint=endpoint)

    # Step 5: Evaluate & develop
    step5 = evaluate_and_develop(step4, top_k=min(3, args.n))

    result = {
        "step_1_define_problem": step1,
        "step_2_reversed_problem": step2,
        "step_3_negative_ideas": step3,
        "step_4_flipped_solutions": step4,
        "step_5_evaluation_and_actions": step5,
    }

    # Pretty-print JSON result
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
