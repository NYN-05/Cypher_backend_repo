import argparse
import requests
import sys
import random
import os
import json
try:
    import genai
except Exception:
    genai = None

# Our lightweight HTTP-based Gemini client (avoids genai/endpoint usage)
try:
    from gemini_client import generate_text as gemini_generate_text
except Exception:
    gemini_generate_text = None


def get_genai_client(api_key=None):
    """Return a genai.Client initialized with API key from env or provided value."""
    if genai is None:
        raise SystemExit("The 'genai' package is not installed. Install it with 'pip install genai'.")

    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        return None

    # genai client reads key from env var by default; set it explicitly for clarity
    os.environ.setdefault("GEMINI_API_KEY", key)
    client = genai.Client()
    return client


def get_gemini_reverse_ideas(problem, api_key, model, n=5, timeout=12):
    """Use the genai client to get reverse-brainstorm ideas from Gemini."""
    # Prefer genai client if available; otherwise use HTTP helper in gemini_client.
    prompt = (
        f"Perform reverse brainstorming for the problem: \"{problem}\".\n"
        f"List {n} concise ways to make the problem worse (reverse brainstorm).\n"
        "Return the items as plain lines only, no numbering, no extra commentary."
    )

    # Try genai library first if present
    if genai is not None:
        try:
            client = get_genai_client(api_key)
            if client is not None and model:
                response = client.models.generate_content(model=model, contents=prompt)
                text = getattr(response, "text", None) or str(response)
                items = [line.strip() for line in text.splitlines() if line.strip()]
                return items[:n]
        except Exception as e:
            print(f"Warning: genai client error when generating reverse ideas: {e}", file=sys.stderr)

    # Fallback to HTTP-based generator (no genai / no endpoint object)
    if gemini_generate_text is not None and api_key and model:
        try:
            text = gemini_generate_text(api_key, model, prompt, temperature=0.2, max_output_tokens=256, timeout=timeout)
            items = [line.strip() for line in str(text).splitlines() if line.strip()]
            return items[:n]
        except Exception as e:
            print(f"Warning: HTTP Gemini client error when generating reverse ideas: {e}", file=sys.stderr)

    return None


def clarify_problem_with_gemini(problem, api_key, model, timeout=8):
    """Use the genai client to restate or clarify the problem. Return string or None on failure."""
    prompt = (
        f"You are an assistant that clarifies problem statements.\n"
        f"Original problem: \"{problem}\"\n"
        "Return a concise, clearer restatement of the problem in one sentence."
    )

    if genai is not None:
        try:
            client = get_genai_client(api_key)
            if client is not None and model:
                response = client.models.generate_content(model=model, contents=prompt)
                text = getattr(response, "text", None) or str(response)
                return text.strip()
        except Exception:
            pass

    if gemini_generate_text is not None and api_key and model:
        try:
            text = gemini_generate_text(api_key, model, prompt, temperature=0.2, max_output_tokens=128, timeout=timeout)
            return str(text).strip()
        except Exception:
            return None

    return None


# Templates removed: this script requires Gemini to generate negatives. No
# template files or hardcoded lists are used.


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


def generate_reverse_brainstorm(problem, api_key=None, model=None, n=5, solutions_per=2):
    # Generate the full five-step reverse-brainstorm flow using Gemini only.
    api_key_env = api_key or os.environ.get("GEMINI_API_KEY")
    model_env = model or os.environ.get("GEMINI_MODEL")

    if not api_key_env or not model_env:
        raise SystemExit("Gemini is required for generate_reverse_brainstorm. Set GEMINI_API_KEY and GEMINI_MODEL or pass --api-key and --model.")

    # Step 1: define
    step1 = define_problem(problem)
    # Step 2: reverse
    step2 = reverse_problem(step1)
    # Step 3: brainstorm negatives via Gemini
    step3 = brainstorm_negative_ideas(step1, api_key=api_key_env, model=model_env, n=n)
    # Step 4: analyze and flip into multiple solutions
    step4 = analyze_and_flip(step3, api_key=api_key_env, model=model_env, solutions_per_idea=solutions_per)
    # Step 5: evaluate using the first solution per idea
    flattened = [sols[0] if isinstance(sols, list) and sols else str(sols) for sols in step4]
    step5 = evaluate_and_develop(flattened, top_k=min(3, n))

    result = {
        "step_1_define_problem": step1,
        "step_2_reversed_problem": step2,
        "step_3_negative_ideas": step3,
        "step_4_flipped_solutions": step4,
        "step_5_evaluation_and_actions": step5,
    }

    return result


def define_problem(problem):
    """Step 1: Clearly state the original problem."""
    return problem.strip()


def reverse_problem(problem):
    """Step 2: Produce a reversed/negative phrasing of the problem."""
    # Simple reversal template
    return f"How could we make the following worse: {problem.strip()}?"


def brainstorm_negative_ideas(problem, api_key=None, model=None, n=5):
    """Step 3: Brainstorm negative ideas using Gemini only.

    This script requires a genai model name (no templates or interactive fallbacks).
    """
    if not api_key or not model:
        raise SystemExit("Gemini is required for generating negative ideas. Set GEMINI_API_KEY and GEMINI_MODEL (or pass --api-key and --model).")

    items = get_gemini_reverse_ideas(problem, api_key, model, n=n)
    if not items:
        raise SystemExit("Gemini failed to generate negative ideas. Check GEMINI_MODEL and GEMINI_API_KEY.")

    return items


def analyze_and_flip(negative_ideas, api_key=None, model=None, solutions_per_idea=2):
    """Step 4: Flip each negative idea into multiple constructive positive solutions.

    If Gemini is available (api_key and endpoint) try to produce multiple
    distinct solutions per negative idea. If Gemini is unavailable or fails,
    fall back to lightweight heuristic variations.
    """
    all_solutions = []
    for neg in negative_ideas:
        candidates = []
        # Attempt Gemini to produce multiple solutions using genai or HTTP helper
        if api_key and model:
            prompt = (
                f"Given this negative idea which makes a problem worse:\n\"{neg}\"\n"
                f"Provide {solutions_per_idea} concise, distinct constructive solutions that would address the original problem."
            )

            # Try genai first
            if genai is not None:
                try:
                    client = get_genai_client(api_key)
                    if client is not None:
                        resp = client.models.generate_content(model=model, contents=prompt)
                        text = getattr(resp, "text", None) or str(resp)
                        lines = [l.strip() for l in text.splitlines() if l.strip()]
                        for line in lines:
                            if len(candidates) < solutions_per_idea:
                                candidates.append(line)
                except Exception:
                    # ignore and try HTTP fallback
                    pass

            # If still missing, try our HTTP-based client
            if len(candidates) < solutions_per_idea and gemini_generate_text is not None:
                try:
                    text = gemini_generate_text(api_key, model, prompt, temperature=0.2, max_output_tokens=240)
                    lines = [l.strip() for l in str(text).splitlines() if l.strip()]
                    for line in lines:
                        if len(candidates) < solutions_per_idea:
                            candidates.append(line)
                except Exception:
                    # fall back to heuristics below
                    pass

        # Heuristic fallback: generate simple inversions and slight variants
        i = 0
        while len(candidates) < solutions_per_idea:
            if i == 0:
                cand = invert_reverse_to_solution(neg)
            else:
                # produce a lightweight variation
                cand = invert_reverse_to_solution(neg) + f" (variation {i})"
            candidates.append(cand)
            i += 1

        all_solutions.append(candidates)

    return all_solutions


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
    parser.add_argument("--solutions-per", dest="solutions_per", type=int, default=2,
                        help="Number of positive solutions to generate per negative idea")
    parser.add_argument("--model", dest="model", default=None,
                        help="Gemini model name to use (e.g. gemini-2.5-flash or text-bison-001). Can also be set via GEMINI_MODEL env var.")
    parser.add_argument("--invert", dest="invert", action="store_true",
                        help="Also produce inverted solution ideas for each reverse idea")
    args = parser.parse_args()

    # Problem is required (avoid hardcoding a default)
    problem = args.problem[0].strip()

    # API key and model come from CLI or environment (no hardcoded values)
    api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
    model = args.model or os.environ.get("GEMINI_MODEL")

    # Run the full Gemini-only flow (script will exit with clear message if Gemini is not configured)
    result = generate_reverse_brainstorm(problem, api_key=api_key, model=model, n=args.n, solutions_per=args.solutions_per)

    # Pretty-print JSON result
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
