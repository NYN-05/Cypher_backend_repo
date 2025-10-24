# AtriaHack - Humanoid System API

This workspace contains implementations for a conceptual "humanoid system" using NLP techniques and creativity methods.

## 🚀 New: Humanoid System API

**Two API endpoints implementing NLP embeddings and creative idea generation:**

### Quick Demo (No Dependencies Required)
```powershell
python standalone_test.py
```

### Full API Server
```powershell
pip install -r requirements.txt
python humanoid_api.py
```

### Test the API
```powershell
python test_api.py
```

## 📁 Project Structure

- **`humanoid_api.py`** - Full API with NLP embeddings (sentence-transformers)
- **`demo_api.py`** - Lightweight demo version  
- **`standalone_test.py`** - Working demo without dependencies ⭐
- **`test_api.py`** - API test client
- **`API_README.md`** - Complete API documentation
- **`IMPLEMENTATION_SUMMARY.md`** - Technical details and achievements

## 🎯 API Endpoints

1. **`/submit_idea`** - Generate NLP embeddings for ideas (384-dimensional vectors)
2. **`/generate_idea_variations`** - Create variations using creativity techniques:
   - Random Word Association (following attached guide)
   - Reverse Brainstorming
   - Lotus Blossom Technique

## 📊 Example Output

```json
{
  "method_used": "Random Word Association",
  "generated_ideas": [
    "Create multi-layered content that reveals more value as users dig deeper",
    "Design notification patterns that flow naturally with user habits",
    "Build features that evolve as users become more skilled"
  ]
}
```

---

## 📚 Original Summarizer Tool

This workspace also contains `summarizer.py`, a dependency-free module for converting Markdown technique documents into summaries.

### Run the summarizer demo:
```powershell
python summarizer.py
```

### Use as library:
```python
from summarizer import summarize_techniques
summaries = summarize_techniques({'Random Word Association': text})
```
