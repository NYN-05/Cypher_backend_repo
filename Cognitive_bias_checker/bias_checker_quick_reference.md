# Cognitive Bias Checker - Quick Reference

## 🚀 Quick Start

```python
from simple_bias_checker import SimpleCognitiveBiasChecker

# Initialize
checker = SimpleCognitiveBiasChecker()

# Detect biases
result = checker.detect_biases("Obviously, this is the best solution ever!")

# Get dynamic prompts  
prompts = checker.get_dynamic_prompts(result)

# Check for real-time interruption
interrupt = checker.interrupt_bias_loop("session_1", "user_1", text)
```

## 🧠 Bias Types Detected

| Bias Type | Example Trigger Words | Counter Strategy |
|-----------|----------------------|------------------|
| **Confirmation Bias** | "obviously", "everyone knows", "clearly" | Challenge assumptions |
| **Anchoring Bias** | "first idea", "original", "based on" | Start fresh perspective |
| **Availability Bias** | "trending", "just saw", "viral" | Explore non-obvious examples |
| **Groupthink** | "we all agree", "consensus", "unanimous" | Assign devil's advocate |
| **Sunk Cost Fallacy** | "already invested", "can't give up" | Consider fresh start |
| **Overconfidence** | "definitely will", "guaranteed", "100%" | Plan for potential failures |

## 📊 Key Methods

### `detect_biases(text, user_id, session_id)`
**Returns:** Bias analysis with scores and severity levels

### `get_dynamic_prompts(detected_biases, num_prompts=2)`  
**Returns:** Contextual questions to counter detected biases

### `interrupt_bias_loop(session_id, user_id, text)`
**Returns:** Real-time intervention decision (interrupt: True/False)

### `get_session_analytics(session_id)`
**Returns:** Comprehensive team analytics and recommendations

## ⚡ Integration Example

```python
def process_team_input(user_input):
    # 1. Detect biases
    analysis = checker.detect_biases(user_input['text'], 
                                   user_input['user_id'], 
                                   user_input['session_id'])
    
    # 2. Check interruption threshold  
    if analysis['overall_bias_score'] > 3.0:
        prompts = checker.get_dynamic_prompts(analysis, 1)
        return {
            'action': 'interrupt',
            'message': '🚨 Bias detected! Let\'s reframe this.',
            'prompt': prompts[0],
            'biases_found': list(analysis['detected_biases'].keys())
        }
    
    # 3. Continue normally
    return {'action': 'continue', 'bias_score': analysis['overall_bias_score']}
```

## 🎯 Scoring System

- **Score Formula:** `(bias_matches / total_words) × 100`
- **Severity Levels:**
  - `HIGH` ≥ 5.0 → Immediate intervention
  - `MEDIUM` 2.0-4.9 → Gentle nudge  
  - `LOW` 0.1-1.9 → Log for analytics
  - `NONE` 0.0 → No bias detected

## 📈 Analytics Dashboard

```python
# Get comprehensive session insights
analytics = checker.get_session_analytics("session_001")

print(f"🔢 Total contributions: {analytics['summary']['total_contributions']}")
print(f"👥 Team members: {analytics['summary']['unique_users']}")  
print(f"⚠️ Biases detected: {analytics['summary']['total_biases_detected']}")
print(f"🎯 Most common bias: {analytics['bias_analysis']['most_common_bias'][0]}")
print(f"📊 User bias counts: {analytics['bias_analysis']['user_bias_counts']}")
```

## 🛠️ Installation

### Lightweight Version (Recommended)
```bash
# No dependencies required
python simple_bias_checker.py
```

### Full Version (With Heatmaps)
```bash
pip install matplotlib seaborn numpy
python cognitive_bias_checker.py
```

## 🔧 Configuration

### Custom Bias Patterns
```python
checker.bias_patterns['custom_bias'] = [
    r'\bcustom_trigger_word\b',
    r'\banother_pattern\b'
]
```

### Custom Prompts
```python
checker.bias_prompts['custom_bias'] = [
    "What if we considered alternatives?",
    "How might this assumption be wrong?"
]
```

## 📋 Best Practices

1. **Set Appropriate Thresholds:** Adjust interruption threshold (default: 3.0) based on team sensitivity
2. **Monitor Session Analytics:** Review bias patterns after sessions for team improvement
3. **Rotate Roles:** Use prompts to assign team members as "devil's advocates" 
4. **Track Progress:** Monitor bias scores over time to measure team growth
5. **Customize Patterns:** Add domain-specific bias patterns for your industry

## 🚨 Real-Time Alerts

### High Priority (Score > 5.0)
```
🚨 Bias Alert! Let's explore this from a different angle.
🎯 What evidence could challenge this assumption?
💡 Take a moment to consider alternative perspectives.
```

### Medium Priority (Score 3.0-5.0)  
```
⚠️ Consider: Multiple viewpoints detected
🎯 How might someone disagree with this?
💡 Let's explore this assumption further.
```

## 📊 Export Options

### Session Data Export
```python
# JSON export
import json
analytics = checker.get_session_analytics("session_001")
with open("session_report.json", "w") as f:
    json.dump(analytics, f, indent=2)

# Bias heatmap (full version only)
heatmap_path = checker.generate_bias_heatmap("session_001")
print(f"Heatmap saved: {heatmap_path}")
```

---

**📚 Full Documentation:** See `cognitive_bias_checker_documentation.md`  
**🔍 Demo:** Run `python simple_bias_checker.py`  
**🆘 Support:** Part of Project Kaleidoscope Innovation Platform