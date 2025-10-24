# standard libs
import os

import threading
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
# use eventlet as async mode explicitly
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')  # CORS for any frontend

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


@app.route('/session/<session_id>')
def session_page(session_id):
    # Render a simple collaboration UI using Jinja, passing initial state
    users = list(SESSION_USERS.get(session_id, []))
    ideas = SESSION_IDEAS.get(session_id, [])
    return render_template('collaboration.html', session_id=session_id, users=users, ideas=ideas)

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
        # persist idea and notify room
        SESSION_IDEAS.setdefault(session_id, []).append(idea_data)
        # use socketio.emit (not plain emit) when outside an event handler thread
        socketio.emit('new_idea', idea_data, room=session_id)

    # Run the AI work in a background thread so the handler returns quickly
    threading.Thread(target=run_ai_logic, daemon=True).start()


if __name__ == '__main__':
    # The monkey patch is already applied at import-time above.
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0',debug=True, port=port)
