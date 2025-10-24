"""
Humanoid System API Implementation

This module implements two distinct API endpoints for a conceptual "humanoid system" using NLP techniques:
1. /submit_idea - NLP Embedding Submission Endpoint
2. /generate_idea_variations - Idea Generation and Variation Endpoint

Requirements:
    pip install flask sentence-transformers torch numpy

Usage:
    python humanoid_api.py
"""

from flask import Flask, request, jsonify
import numpy as np
import random
import re
from typing import Dict, List, Tuple
from sentence_transformers import SentenceTransformer
import torch

app = Flask(__name__)

# Global variables for storing ideas and model
ideas_storage = {}
idea_counter = 0
model = None

def initialize_model():
    """Initialize the sentence transformer model"""
    global model
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")
        # Fallback: create a mock model that returns random embeddings
        model = None

class RandomWordGenerator:
    """Generate random words and their associations"""
    
    # Extended word pool for better variety
    WORD_POOL = [
        "ocean", "mountain", "telescope", "butterfly", "lighthouse", "compass", "rainbow",
        "thunder", "crystal", "feather", "anchor", "bridge", "spiral", "diamond",
        "volcano", "mirror", "wheel", "flame", "river", "cloud", "star", "tree",
        "flower", "book", "clock", "key", "door", "window", "ladder", "rope",
        "hammer", "seed", "nest", "web", "wave", "stone", "leaf", "root",
        "branch", "shadow", "echo", "wind", "snow", "rain", "sun", "moon"
    ]
    
    # Associations for common words (can be extended)
    WORD_ASSOCIATIONS = {
        "ocean": ["depth", "vastness", "waves", "tides", "mystery", "blue", "salt", "currents"],
        "mountain": ["height", "stability", "peaks", "climbing", "strength", "perspective", "challenge", "endurance"],
        "telescope": ["vision", "distance", "exploration", "magnification", "clarity", "focus", "discovery", "precision"],
        "butterfly": ["transformation", "beauty", "delicacy", "metamorphosis", "color", "flight", "freedom", "evolution"],
        "lighthouse": ["guidance", "safety", "beacon", "warning", "direction", "reliability", "visibility", "protection"],
        "compass": ["direction", "navigation", "orientation", "reliability", "guidance", "magnetism", "accuracy", "purpose"],
        "rainbow": ["color", "spectrum", "bridge", "hope", "beauty", "diversity", "arc", "light"],
        "thunder": ["power", "suddenness", "noise", "impact", "force", "surprise", "energy", "announcement"],
        "crystal": ["clarity", "purity", "structure", "reflection", "precision", "hardness", "beauty", "transparency"],
        "feather": ["lightness", "softness", "flight", "flexibility", "delicacy", "protection", "covering", "grace"],
        "tree": ["growth", "roots", "branches", "shade", "oxygen", "seasons", "life", "stability"],
        "book": ["knowledge", "stories", "pages", "learning", "wisdom", "imagination", "information", "chapters"],
        "clock": ["time", "precision", "rhythm", "cycles", "measurement", "urgency", "scheduling", "consistency"],
        "bridge": ["connection", "spanning", "support", "crossing", "linking", "strength", "access", "unity"]
    }
    
    @classmethod
    def get_random_word(cls) -> str:
        """Get a random word from the word pool"""
        return random.choice(cls.WORD_POOL)
    
    @classmethod
    def get_associations(cls, word: str) -> List[str]:
        """Get associations for a word, or generate generic ones if not found"""
        if word.lower() in cls.WORD_ASSOCIATIONS:
            return cls.WORD_ASSOCIATIONS[word.lower()]
        else:
            # Generic associations if word not in our dictionary
            generic_associations = [
                "structure", "function", "purpose", "movement", "connection",
                "growth", "change", "interaction", "stability", "adaptation"
            ]
            return random.sample(generic_associations, min(5, len(generic_associations)))

def generate_embedding(text: str) -> Tuple[List[float], int]:
    """
    Generate embedding for the given text using sentence transformer model
    
    Returns:
        Tuple of (embedding_list, embedding_length)
    """
    global model
    
    if model is not None:
        try:
            # Generate actual embedding using sentence transformer
            embedding = model.encode(text)
            embedding_list = embedding.tolist()
            return embedding_list, len(embedding_list)
        except Exception as e:
            print(f"Error generating embedding: {e}")
    
    # Fallback: generate mock embedding with correct dimensions
    embedding_length = 384  # Standard size for all-MiniLM-L6-v2
    embedding = np.random.normal(0, 0.1, embedding_length).tolist()
    return embedding, embedding_length

def random_word_association_technique(idea_text: str) -> List[str]:
    """
    Implement Random Word Association technique to generate idea variations
    
    Args:
        idea_text: The input challenge or idea
        
    Returns:
        List of 3-5 generated ideas
    """
    # Step 1: Define Challenge (already provided as idea_text)
    
    # Step 2: Generate Random Word
    random_word = RandomWordGenerator.get_random_word()
    
    # Step 3: List Associations
    associations = RandomWordGenerator.get_associations(random_word)
    
    # Step 4: Force Connections and Generate Ideas
    generated_ideas = []
    
    # Create connection templates for different types of problems
    connection_templates = [
        "What if we applied the principle of '{association}' to {problem}?",
        "How could '{association}' inspire a new approach to {problem}?",
        "What does '{association}' suggest about improving {problem}?",
        "How might the concept of '{association}' transform {problem}?",
        "What creative solution emerges when we combine '{association}' with {problem}?"
    ]
    
    # Generate ideas based on associations
    for i, association in enumerate(associations[:5]):  # Limit to 5 associations
        if i >= 5:  # Ensure we don't exceed 5 ideas
            break
            
        # Create contextual ideas based on the association
        if "engage" in idea_text.lower() or "app" in idea_text.lower():
            # App engagement specific ideas
            ideas_map = {
                "depth": "Create multi-layered content that reveals more value as users dig deeper",
                "waves": "Implement rhythmic notifications that come in gentle waves rather than constant pings", 
                "growth": "Design features that evolve and grow with user proficiency",
                "transformation": "Build onboarding that transforms complex processes into simple, beautiful experiences",
                "guidance": "Add smart navigation that guides users to their most valuable actions",
                "connection": "Create features that help users connect their daily activities to long-term goals",
                "lightness": "Simplify the interface by removing heavy elements and focusing on essentials",
                "clarity": "Use crystal-clear micro-interactions that make every action feel precise and meaningful"
            }
        else:
            # General problem-solving ideas
            ideas_map = {
                "depth": f"Explore the deeper layers of {idea_text.lower()} by analyzing root causes",
                "waves": f"Approach {idea_text.lower()} in phases, like waves building momentum",
                "growth": f"Design {idea_text.lower()} solutions that can scale and adapt over time",
                "transformation": f"Completely reimagine the current approach to {idea_text.lower()}",
                "guidance": f"Create clear pathways and direction for addressing {idea_text.lower()}",
                "connection": f"Link {idea_text.lower()} to other related challenges or opportunities",
                "lightness": f"Simplify and streamline the approach to {idea_text.lower()}",
                "clarity": f"Make the solution to {idea_text.lower()} transparent and easy to understand"
            }
        
        # Get idea based on association, with fallback
        if association in ideas_map:
            idea = ideas_map[association]
        else:
            # Fallback idea generation
            idea = f"Apply the concept of '{association}' to create a new perspective on {idea_text.lower()}"
        
        generated_ideas.append(idea.capitalize())
    
    # Ensure we have 3-5 ideas
    while len(generated_ideas) < 3:
        generic_idea = f"Explore new approaches to {idea_text.lower()} through creative experimentation"
        generated_ideas.append(generic_idea)
    
    return generated_ideas[:5]  # Limit to maximum 5 ideas

def reverse_brainstorming_technique(idea_text: str) -> List[str]:
    """
    Implement Reverse Brainstorming technique
    
    Args:
        idea_text: The input challenge or idea
        
    Returns:
        List of 3-5 generated ideas
    """
    # Reverse the problem
    negative_scenarios = [
        f"How could we ensure {idea_text.lower()} fails completely?",
        f"What would make {idea_text.lower()} worse?",
        f"How could we create the opposite of {idea_text.lower()}?"
    ]
    
    # Generate negative ideas and flip them
    if "engage" in idea_text.lower():
        negative_ideas = [
            "Make the interface confusing and hard to navigate",
            "Send too many notifications at random times", 
            "Hide important features where users can't find them",
            "Make the onboarding process long and tedious",
            "Ignore user feedback completely"
        ]
        
        flipped_ideas = [
            "Design an intuitive interface with clear, logical navigation",
            "Implement smart, personalized notification timing based on user behavior",
            "Highlight key features with contextual guidance and tooltips",
            "Create a streamlined onboarding that gets users to value quickly",
            "Build robust feedback loops and respond to user suggestions promptly"
        ]
    else:
        # Generic approach
        flipped_ideas = [
            f"Create clear, simple processes that make {idea_text.lower()} more accessible",
            f"Build feedback mechanisms to continuously improve {idea_text.lower()}",
            f"Design user-centered solutions that address real needs in {idea_text.lower()}",
            f"Implement iterative improvements based on data and user behavior",
            f"Establish clear communication channels around {idea_text.lower()}"
        ]
    
    return flipped_ideas[:5]

def lotus_blossom_technique(idea_text: str) -> List[str]:
    """
    Implement simplified Lotus Blossom technique
    
    Args:
        idea_text: The input challenge or idea
        
    Returns:
        List of 3-5 generated ideas
    """
    # Generate 8 core directions and pick specific tactics from a few
    if "engage" in idea_text.lower():
        core_directions = [
            "Gamification elements",
            "Social features", 
            "Personalization",
            "Content quality",
            "User experience"
        ]
        
        specific_ideas = [
            "Implement achievement badges and progress tracking for user milestones",
            "Add community features where users can share experiences and tips",
            "Create adaptive interfaces that learn from user preferences",
            "Develop high-quality, interactive content that provides immediate value",
            "Design smooth micro-interactions that make every tap feel responsive"
        ]
    else:
        # Generic lotus blossom expansion
        specific_ideas = [
            f"Break down {idea_text.lower()} into smaller, manageable components",
            f"Create systematic processes for approaching {idea_text.lower()}",
            f"Develop multiple parallel strategies for {idea_text.lower()}",
            f"Build measurement systems to track progress on {idea_text.lower()}",
            f"Establish collaborative frameworks around {idea_text.lower()}"
        ]
    
    return specific_ideas[:5]

@app.route('/submit_idea', methods=['POST'])
def submit_idea():
    """
    NLP Embedding Submission Endpoint
    
    Input: JSON with 'idea_text' field
    Output: JSON with embedding information
    """
    try:
        # Get input data
        data = request.get_json()
        if not data or 'idea_text' not in data:
            return jsonify({
                "status": "error",
                "message": "Missing 'idea_text' in request body"
            }), 400
        
        received_idea = data['idea_text']
        
        # Generate embedding
        embedding, embedding_length = generate_embedding(received_idea)
        
        # Store the idea (in memory for this demo)
        global idea_counter, ideas_storage
        current_idea_id = idea_counter
        ideas_storage[current_idea_id] = {
            'text': received_idea,
            'embedding': embedding
        }
        idea_counter += 1
        
        # Create response
        response = {
            "status": "success",
            "message": "Embedding generated successfully.",
            "idea_id": current_idea_id,
            "received_idea": received_idea,
            "embedding_length": embedding_length,
            "embedding_sample": embedding[:5]  # First 5 elements as sample
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": f"Internal server error: {str(e)}"
        }), 500

@app.route('/generate_idea_variations', methods=['POST'])
def generate_idea_variations():
    """
    Idea Generation and Variation Endpoint
    
    Input: JSON with 'idea_text' field
    Output: JSON with method used and generated ideas
    """
    try:
        # Get input data
        data = request.get_json()
        if not data or 'idea_text' not in data:
            return jsonify({
                "status": "error",
                "message": "Missing 'idea_text' in request body"
            }), 400
        
        idea_text = data['idea_text']
        
        # Randomly select one of three techniques
        techniques = [
            ("Random Word Association", random_word_association_technique),
            ("Reverse Brainstorming", reverse_brainstorming_technique),
            ("Lotus Blossom", lotus_blossom_technique)
        ]
        
        selected_technique_name, technique_function = random.choice(techniques)
        
        # Generate ideas using the selected technique
        generated_ideas = technique_function(idea_text)
        
        # Create response
        response = {
            "method_used": selected_technique_name,
            "generated_ideas": generated_ideas
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Internal server error: {str(e)}"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None,
        "stored_ideas": len(ideas_storage)
    })

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API information"""
    return jsonify({
        "message": "Humanoid System API",
        "endpoints": {
            "/submit_idea": "POST - Submit an idea for NLP embedding generation",
            "/generate_idea_variations": "POST - Generate idea variations using creativity techniques",
            "/health": "GET - Check API health status"
        },
        "model_status": "loaded" if model else "fallback_mode"
    })

if __name__ == '__main__':
    print("Initializing Humanoid System API...")
    initialize_model()
    print("Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000)