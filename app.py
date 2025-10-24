from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room
import eventlet

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # CORS for any frontend

SESSION_IDEAS = {}   # session_id -> list of {"user": ..., "idea": ..., "diversity_score": ..., "bias_flag": ...}
SESSION_USERS = {}   # session_id -> set of usernames

def score_diversity(idea, session_ideas):
    # Placeholder: add NLP/embedding logic
    return 0.8

def detect_bias(idea, session_ideas):
    # Placeholder: add bias checker logic
    return "None"

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

@socketio.on('submit_idea')
def handle_submit_idea(data):
    session_id = data['session_id']
    user = data['username']
    idea_text = data['idea']

    def run_ai_logic():
        idea_data = {
            "user": user,
            "idea": idea_text,
            "diversity_score": score_diversity(idea_text, SESSION_IDEAS.get(session_id, [])),
            "bias_flag": detect_bias(idea_text, SESSION_IDEAS.get(session_id, [])),
        }