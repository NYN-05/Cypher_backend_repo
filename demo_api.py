"""
Lightweight Demo of Humanoid System API

This is a simplified version that demonstrates the API functionality
without requiring heavy ML dependencies. Perfect for testing the logic
and API structure.

Usage:
    python demo_api.py
"""

from flask import Flask, request, jsonify
import random
import time

app = Flask(__name__)

# Simple storage
ideas_storage = {}
idea_counter = 0

class SimpleWordGenerator:
    """Simple word generator for demo purposes"""
    
    WORDS = [
        "ocean", "mountain", "telescope", "butterfly", "lighthouse", "compass",
        "tree", "book", "clock", "bridge", "crystal", "feather", "rainbow"
    ]
    
    ASSOCIATIONS = {
        "ocean": ["depth", "waves", "vastness", "flow", "mystery"],
        "mountain": ["height", "stability", "climbing", "perspective", "strength"], 
        "telescope": ["vision", "distance", "focus", "discovery", "clarity"],
        "tree": ["growth", "roots", "branches", "seasons", "life"],
        "book": ["knowledge", "stories", "chapters", "learning", "wisdom"],
        "clock": ["time", "rhythm", "precision", "cycles", "measurement"],
        "bridge": ["connection", "crossing", "linking", "support", "unity"]
    }
    
    @classmethod
    def get_random_word(cls):
        return random.choice(cls.WORDS)
    
    @classmethod
    def get_associations(cls, word):
        return cls.ASSOCIATIONS.get(word, ["structure", "function", "purpose", "movement", "connection"])

def generate_mock_embedding(text):
    """Generate a mock embedding for demo purposes"""
    # Create deterministic but varied embeddings based on text
    random.seed(hash(text) % (2**32))
    embedding = [round(random.uniform(-0.1, 0.1), 5) for _ in range(384)]
    return embedding, 384

def random_word_technique(idea_text):
    """Simplified Random Word Association"""
    word = SimpleWordGenerator.get_random_word()
    associations = SimpleWordGenerator.get_associations(word)
    
    ideas = []
    for assoc in associations:
        if "app" in idea_text.lower() or "engage" in idea_text.lower():
            idea_templates = {
                "depth": "Create layered experiences that reveal more value over time",
                "waves": "Design notification patterns that flow naturally with user habits",
                "growth": "Build features that evolve as users become more skilled",
                "connection": "Link user actions to their personal goals and achievements",
                "flow": "Optimize user journeys to feel effortless and intuitive"
            }
            idea = idea_templates.get(assoc, f"Apply '{assoc}' principles to enhance user experience")
        else:
            idea = f"Explore how '{assoc}' could transform your approach to {idea_text.lower()}"
        ideas.append(idea)
    
    return ideas[:4]  # Return 4 ideas

def reverse_brainstorming_technique(idea_text):
    """Simplified Reverse Brainstorming"""
    if "engage" in idea_text.lower():
        return [
            "Create intuitive navigation that guides users naturally",
            "Send personalized notifications at optimal times",
            "Design onboarding that delivers immediate value",
            "Build feedback loops that make users feel heard"
        ]
    else:
        return [
            f"Simplify processes related to {idea_text.lower()}",
            f"Create clear feedback mechanisms for {idea_text.lower()}",
            f"Design user-focused solutions for {idea_text.lower()}",
            f"Build iterative improvements into {idea_text.lower()}"
        ]

def lotus_blossom_technique(idea_text):
    """Simplified Lotus Blossom"""
    if "engage" in idea_text.lower():
        return [
            "Implement gamification elements with meaningful rewards",
            "Add social features for community building",
            "Create personalized content recommendations",
            "Design micro-interactions that feel satisfying"
        ]
    else:
        return [
            f"Break {idea_text.lower()} into manageable components",
            f"Create systematic approaches to {idea_text.lower()}",
            f"Develop measurement frameworks for {idea_text.lower()}",
            f"Build collaborative processes around {idea_text.lower()}"
        ]

@app.route('/submit_idea', methods=['POST'])
def submit_idea():
    """NLP Embedding Submission Endpoint"""
    try:
        data = request.get_json()
        if not data or 'idea_text' not in data:
            return jsonify({"status": "error", "message": "Missing 'idea_text'"}), 400
        
        received_idea = data['idea_text']
        
        # Generate mock embedding
        embedding, embedding_length = generate_mock_embedding(received_idea)
        
        # Store idea
        global idea_counter
        current_id = idea_counter
        ideas_storage[current_id] = {
            'text': received_idea,
            'embedding': embedding,
            'timestamp': time.time()
        }
        idea_counter += 1
        
        return jsonify({
            "status": "success",
            "message": "Embedding generated successfully.",
            "idea_id": current_id,
            "received_idea": received_idea,
            "embedding_length": embedding_length,
            "embedding_sample": embedding[:5]
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/generate_idea_variations', methods=['POST'])
def generate_idea_variations():
    """Idea Generation and Variation Endpoint"""
    try:
        data = request.get_json()
        if not data or 'idea_text' not in data:
            return jsonify({"status": "error", "message": "Missing 'idea_text'"}), 400
        
        idea_text = data['idea_text']
        
        # Randomly select technique
        techniques = [
            ("Random Word Association", random_word_technique),
            ("Reverse Brainstorming", reverse_brainstorming_technique),
            ("Lotus Blossom", lotus_blossom_technique)
        ]
        
        method_name, technique_func = random.choice(techniques)
        generated_ideas = technique_func(idea_text)
        
        return jsonify({
            "method_used": method_name,
            "generated_ideas": generated_ideas
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model_loaded": "demo_mode",
        "stored_ideas": len(ideas_storage),
        "mode": "lightweight_demo"
    })

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        "message": "Humanoid System API - Lightweight Demo",
        "version": "demo-1.0",
        "endpoints": {
            "/submit_idea": "POST - Submit idea for embedding",
            "/generate_idea_variations": "POST - Generate creative variations",
            "/health": "GET - Health check"
        },
        "note": "This is a lightweight demo version"
    })

if __name__ == '__main__':
    print("🚀 Starting Humanoid System API (Demo Mode)")
    print("💡 This lightweight version demonstrates the API without heavy ML dependencies")
    print("🌐 Server starting at http://localhost:5000")
    print("📋 Available endpoints:")
    print("   - POST /submit_idea")
    print("   - POST /generate_idea_variations") 
    print("   - GET /health")
    print("   - GET /")
    app.run(debug=True, host='0.0.0.0', port=5000)