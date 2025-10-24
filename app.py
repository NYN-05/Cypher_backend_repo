# standard libs
import os
import threading
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit, join_room

# plug in cognitive-bias checker and random-word helper
try:
    from Cognitive_bias_checker.cognitive_bias_checker import CognitiveBiasChecker
except Exception:
    # fallback import path or raise later when used
    CognitiveBiasChecker = None

try:
    from creative_ideas.random_words import random_word_association
except Exception:
    random_word_association = None

app = Flask(__name__)
# use eventlet as async mode explicitly
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')  # CORS for any frontend

SESSION_IDEAS = {}   # session_id -> list of {"user": ..., "idea": ..., "diversity_score": ..., "bias_flag": ...}
SESSION_USERS = {}   # session_id -> set of usernames

# instantiate checker if available
if CognitiveBiasChecker:
    bias_checker = CognitiveBiasChecker()
else:
    bias_checker = None

# submissions persistence
SUBMISSIONS_DIR = Path("data")
SUBMISSIONS_FILE = SUBMISSIONS_DIR / "submissions.json"
_submissions_lock = threading.Lock()

def save_submission_record(record: dict):
    """Append a submission record to the JSON file in a thread-safe way.

    File contains a JSON array of submission objects. This reads the file,
    appends the record, and writes back with indentation.
    """
    try:
        with _submissions_lock:
            SUBMISSIONS_DIR.mkdir(parents=True, exist_ok=True)
            if SUBMISSIONS_FILE.exists():
                try:
                    with SUBMISSIONS_FILE.open('r', encoding='utf-8') as fh:
                        data = json.load(fh)
                        if not isinstance(data, list):
                            data = []
                except Exception:
                    data = []
            else:
                data = []

            data.append(record)

            # write atomically by writing to temp file then replacing
            tmp = SUBMISSIONS_FILE.with_suffix('.tmp')
            with tmp.open('w', encoding='utf-8') as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
            tmp.replace(SUBMISSIONS_FILE)
    except Exception as e:
        # keep server resilient - log to stderr
        import sys
        print(f"Error saving submission record: {e}", file=sys.stderr)


def dump_all_state_to_root_file(root_path: Path = Path("data.json")):
    """Collect current in-memory state and persisted submissions and write to root JSON file.

    This function reads the submissions file (if present), and combines it with
    the current SESSION_IDEAS and SESSION_USERS into a single JSON object written
    to `data.json` at the repository root (or the provided path).
    """
    try:
        out = {
            'exported_at': datetime.now().isoformat(),
            'sessions': SESSION_IDEAS,
            'users': {k: list(v) for k, v in SESSION_USERS.items()},
            'submissions': []
        }

        # load persisted submissions if available
        if SUBMISSIONS_FILE.exists():
            try:
                with SUBMISSIONS_FILE.open('r', encoding='utf-8') as fh:
                    subs = json.load(fh)
                    if isinstance(subs, list):
                        out['submissions'] = subs
            except Exception:
                out['submissions'] = []

        # write to requested root path
        with root_path.open('w', encoding='utf-8') as fh:
            json.dump(out, fh, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        import sys
        print(f"Error dumping all state: {e}", file=sys.stderr)
        return False

def score_diversity(idea, session_ideas):
    # Lightweight diversity score: fraction of words in idea not seen in session
    if not idea:
        return 0.0
    existing = " ".join([i.get('idea', '') for i in (session_ideas or [])])
    existing_words = set(existing.lower().split())
    words = [w for w in idea.lower().split() if w.isalpha()]
    if not words:
        return 0.0
    new_words = [w for w in words if w not in existing_words]
    score = len(new_words) / len(words)
    return round(score, 2)

def detect_bias(idea, session_ideas, user_id=None, session_id=None):
    # Use the CognitiveBiasChecker if available, otherwise return empty
    if bias_checker:
        result = bias_checker.detect_biases(idea, user_id=user_id, session_id=session_id)
        return result
    return {"detected_biases": {}, "overall_bias_score": 0}

@app.route('/export_session', methods=['GET'])
def export_session():
    session_id = request.args.get("session_id")
    return jsonify({"ideas": SESSION_IDEAS.get(session_id, [])})

@socketio.on('join')
def handle_join(data):
    session_id = data['session_id']
    user = data['username']
    join_room(session_id)
    SESSION_USERS.setdefault(session_id, set()).add(user)
    emit('session_state', {"ideas": SESSION_IDEAS.get(session_id, []), "users": list(SESSION_USERS[session_id])}, room=session_id)


@app.route('/session/<session_id>')
def session_page(session_id):
    # Render a simple collaboration UI using Jinja, passing initial state
    users = list(SESSION_USERS.get(session_id, []))
    ideas = SESSION_IDEAS.get(session_id, [])
    return render_template('collaboration.html', session_id=session_id, users=users, ideas=ideas)


@app.route('/')
def index():
    # Simple landing page to create/join sessions
    return render_template('index.html')


# API endpoints for frontend to call directly
@app.route('/api/analyze_bias', methods=['POST'])
def api_analyze_bias():
    data = request.get_json() or {}
    text = data.get('text', '')
    user_id = data.get('user_id')
    session_id = data.get('session_id')
    if not bias_checker:
        return jsonify({'error': 'CognitiveBiasChecker not available on server'}), 500
    try:
        res = bias_checker.detect_biases(text, user_id=user_id, session_id=session_id)
        return jsonify(res)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/random_word', methods=['GET'])
def api_random_word():
    problem = request.args.get('problem', '')
    api_key = request.args.get('api_key') or None
    if not random_word_association:
        return jsonify({'error': 'random_word_association not available on server'}), 500
    try:
        res = random_word_association(problem, api_key)
        return jsonify(res)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/save_all', methods=['POST', 'GET'])
def save_all():
    """Endpoint to force writing all state to root `data.json` file."""
    ok = dump_all_state_to_root_file(Path(__file__).parent / 'data.json')
    if ok:
        return jsonify({'status': 'saved', 'path': str(Path(__file__).parent / 'data.json')})
    return jsonify({'status': 'error'}), 500

@socketio.on('submit_idea')
def handle_submit_idea(data):
    session_id = data['session_id']
    user = data['username']
    idea_text = data['idea']

    def run_ai_logic():
        # compute diversity
        diversity = score_diversity(idea_text, SESSION_IDEAS.get(session_id, []))

        # detect biases (store via checker if available)
        bias_result = detect_bias(idea_text, SESSION_IDEAS.get(session_id, []), user_id=user, session_id=session_id)

        # try to get a random-word association if helper available
        assoc = None
        if random_word_association:
            try:
                # request 4 random words by default
                assoc = random_word_association(idea_text, None, 4)
            except Exception:
                assoc = None

        idea_data = {
            "user": user,
            "idea": idea_text,
            "diversity_score": diversity,
            "bias_summary": bias_result,
            "bias_flag": list(bias_result.get('detected_biases', {}).keys()) if isinstance(bias_result, dict) else [],
        }

        # attach random words/prompts (backwards compatible)
        if assoc:
            # multiple words
            if 'random_words' in assoc:
                idea_data['random_words'] = assoc.get('random_words')
                idea_data['association_prompts'] = assoc.get('association_prompts')
                # keep first as compatibility
                if assoc.get('random_words'):
                    idea_data['random_word'] = assoc['random_words'][0]
                if assoc.get('association_prompts'):
                    idea_data['association_prompt'] = assoc['association_prompts'][0]
            else:
                # single-word response
                idea_data['random_word'] = assoc.get('random_word')
                idea_data['association_prompt'] = assoc.get('association_prompt')

        # persist idea in memory and notify room
        SESSION_IDEAS.setdefault(session_id, []).append(idea_data)
        # emit a system message with the random-word association so front-end can show it
        try:
            if assoc:
                socketio.emit('system_message', {
                    'type': 'random_words',
                    'data': assoc,
                }, room=session_id)
        except Exception:
            pass
        # persist to disk as JSON record
        try:
            record = {
                'timestamp': datetime.now().isoformat(),
                'session_id': session_id,
                'user': user,
                'idea': idea_text,
                'diversity_score': diversity,
                'bias_flag': idea_data.get('bias_flag'),
                'bias_summary': idea_data.get('bias_summary'),
                'random_word': idea_data.get('random_word'),
                'random_words': idea_data.get('random_words'),
                'association_prompt': idea_data.get('association_prompt'),
                'association_prompts': idea_data.get('association_prompts')
            }
            save_submission_record(record)
            # Also update the repository-root combined snapshot so the
            # top-level `data.json` (attachment) is kept current on each submission.
            try:
                dump_all_state_to_root_file(Path(__file__).parent / 'data.json')
            except Exception:
                pass
        except Exception:
            pass
        # use socketio.emit (not plain emit) when outside an event handler thread
        socketio.emit('new_idea', idea_data, room=session_id)

        # if bias checker signals interruption, emit a bias_alert
        if bias_checker:
            try:
                interrupt = bias_checker.interrupt_bias_loop(session_id, user, idea_text)
                if interrupt.get('interrupt'):
                    socketio.emit('bias_alert', interrupt, room=session_id)
            except Exception:
                pass

    # Run the AI work in a background thread so the handler returns quickly
    threading.Thread(target=run_ai_logic, daemon=True).start()


if __name__ == '__main__':
    # The monkey patch is already applied at import-time above.
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0',debug=True, port=port)
