"""
Test script for the Humanoid System API

This script demonstrates how to use both API endpoints:
1. /submit_idea - Submit an idea and get NLP embeddings
2. /generate_idea_variations - Generate creative variations of an idea

Usage:
    python test_api.py

Note: Make sure the API server is running (python humanoid_api.py)
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:5000"

def test_submit_idea():
    """Test the /submit_idea endpoint"""
    print("🧠 Testing NLP Embedding Submission Endpoint...")
    
    # Test data
    test_ideas = [
        "How can we reduce food waste in urban areas?",
        "Improve user engagement for a mobile app",
        "Create a more sustainable transportation system"
    ]
    
    for idea in test_ideas:
        print(f"\n📝 Submitting idea: '{idea}'")
        
        response = requests.post(
            f"{API_BASE_URL}/submit_idea",
            json={"idea_text": idea},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"   - Idea ID: {result['idea_id']}")
            print(f"   - Embedding Length: {result['embedding_length']}")
            print(f"   - Embedding Sample: {result['embedding_sample']}")
            print(f"   - Status: {result['status']}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")

def test_generate_variations():
    """Test the /generate_idea_variations endpoint"""
    print("\n\n🎨 Testing Idea Generation and Variation Endpoint...")
    
    # Test data
    test_challenges = [
        "Improve user engagement for an app",
        "Reduce customer support response time", 
        "Increase team productivity in remote work",
        "Make online learning more interactive"
    ]
    
    for challenge in test_challenges:
        print(f"\n🎯 Generating variations for: '{challenge}'")
        
        response = requests.post(
            f"{API_BASE_URL}/generate_idea_variations",
            json={"idea_text": challenge},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"   - Method Used: {result['method_used']}")
            print("   - Generated Ideas:")
            for i, idea in enumerate(result['generated_ideas'], 1):
                print(f"     {i}. {idea}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")

def test_health_check():
    """Test the health check endpoint"""
    print("\n🏥 Testing Health Check...")
    
    response = requests.get(f"{API_BASE_URL}/health")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ API is healthy!")
        print(f"   - Model Status: {'Loaded' if result['model_loaded'] else 'Fallback Mode'}")
        print(f"   - Stored Ideas: {result['stored_ideas']}")
    else:
        print(f"❌ Health check failed: {response.status_code}")

def main():
    """Main test function"""
    print("🚀 Starting Humanoid System API Tests")
    print("=" * 50)
    
    try:
        # Check if API is running
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ API is not responding. Make sure to start the server first:")
            print("   python humanoid_api.py")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to API. Make sure to start the server first:")
        print("   python humanoid_api.py")
        return
    
    # Run tests
    test_health_check()
    test_submit_idea()
    test_generate_variations()
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed!")

if __name__ == "__main__":
    main()
    