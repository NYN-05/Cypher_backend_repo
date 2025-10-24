# Humanoid System API

A conceptual "humanoid system" API implementing NLP techniques for idea processing and creative idea generation.

## 🚀 Features

This API provides two main endpoints:

1. **NLP Embedding Submission** (`/submit_idea`) - Processes ideas and generates vector embeddings
2. **Idea Generation and Variation** (`/generate_idea_variations`) - Creates creative variations using established creativity techniques

## 📋 Requirements

- Python 3.7+
- Flask
- sentence-transformers
- numpy
- torch

## 🛠️ Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the API server**:
   ```bash
   python humanoid_api.py
   ```

The server will start on `http://localhost:5000`

## 📡 API Endpoints

### 1. Submit Idea for NLP Embedding (`/submit_idea`)

**Method**: POST  
**URL**: `http://localhost:5000/submit_idea`

**Input**:
```json
{
    "idea_text": "How can we reduce food waste in urban areas?"
}
```

**Output**:
```json
{
    "status": "success",
    "message": "Embedding generated successfully.",
    "idea_id": 0,
    "received_idea": "How can we reduce food waste in urban areas?",
    "embedding_length": 384,
    "embedding_sample": [0.00584, 0.01184, 0.03224, -0.03182, -0.05536]
}
```

**Features**:
- Uses sentence-transformers model (all-MiniLM-L6-v2) for embeddings
- Returns 384-dimensional embeddings
- Stores ideas with unique IDs
- Provides embedding sample for verification

### 2. Generate Idea Variations (`/generate_idea_variations`)

**Method**: POST  
**URL**: `http://localhost:5000/generate_idea_variations`

**Input**:
```json
{
    "idea_text": "Improve user engagement for an app"
}
```

**Output**:
```json
{
    "method_used": "Random Word Association",
    "generated_ideas": [
        "Create multi-layered content that reveals more value as users dig deeper",
        "Implement rhythmic notifications that come in gentle waves rather than constant pings",
        "Design features that evolve and grow with user proficiency",
        "Build onboarding that transforms complex processes into simple, beautiful experiences",
        "Add smart navigation that guides users to their most valuable actions"
    ]
}
```

**Features**:
- Randomly selects from 3 creativity techniques:
  - Random Word Association
  - Reverse Brainstorming  
  - Lotus Blossom Technique
- Returns 3-5 actionable ideas
- Context-aware idea generation

### 3. Health Check (`/health`)

**Method**: GET  
**URL**: `http://localhost:5000/health`

**Output**:
```json
{
    "status": "healthy",
    "model_loaded": true,
    "stored_ideas": 5
}
```

## 🧪 Testing

Run the test script to see the API in action:

```bash
python test_api.py
```

This will test both endpoints with sample data and show the results.

## 🎨 Creativity Techniques Implemented

### 1. Random Word Association
- Generates random stimulus words
- Creates associations and metaphors
- Forces connections to the original problem
- Produces unexpected, creative solutions

### 2. Reverse Brainstorming
- Inverts the problem (how to make it worse)
- Identifies failure modes and vulnerabilities  
- Flips negative ideas into positive solutions
- Uncovers hidden assumptions

### 3. Lotus Blossom Technique
- Systematic expansion from core concepts
- Multiple parallel solution paths
- Structured ideation process
- Comprehensive coverage of problem space

## 🔧 Technical Implementation

### NLP Embeddings
- Uses Sentence-BERT (all-MiniLM-L6-v2) for semantic embeddings
- 384-dimensional vectors for consistent representation
- Fallback to random embeddings if model loading fails
- In-memory storage for demo purposes

### Idea Generation
- Context-aware templates based on problem type
- Extensive word association database
- Smart connection algorithms
- Quality filtering and refinement

## 📝 Example Usage with curl

### Submit an idea:
```bash
curl -X POST http://localhost:5000/submit_idea \
  -H "Content-Type: application/json" \
  -d '{"idea_text": "How can we make remote work more collaborative?"}'
```

### Generate variations:
```bash
curl -X POST http://localhost:5000/generate_idea_variations \
  -H "Content-Type: application/json" \
  -d '{"idea_text": "Improve customer service response time"}'
```

## 🎯 Use Cases

- **Innovation Workshops**: Generate diverse perspectives on challenges
- **Product Development**: Explore creative feature ideas
- **Problem Solving**: Break through mental blocks with structured creativity
- **Brainstorming**: Augment human creativity with AI-assisted ideation
- **Design Thinking**: Support divergent thinking phases

## 🚨 Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Missing required fields
- **500 Internal Server Error**: Processing errors with detailed messages
- **Model Fallback**: Continues operation even if NLP model fails to load

## 🔮 Future Enhancements

- Database persistence for ideas and embeddings
- User authentication and idea ownership
- Similarity search between ideas
- Custom creativity technique configuration
- Batch processing capabilities
- Integration with external creativity tools

## 📄 License

This project is provided as-is for educational and demonstration purposes.

---

**Note**: This API is designed as a conceptual implementation. For production use, consider adding authentication, rate limiting, data persistence, and enhanced error handling.