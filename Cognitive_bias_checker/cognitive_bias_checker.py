"""
Cognitive Bias Checker for Project Kaleidoscope
Automatically detects and visualizes cognitive biases with dynamic prompts and analytics
"""

import re
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Any
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

class CognitiveBiasChecker:
    """
    Cognitive Bias Checker that detects biases, provides dynamic prompts,
    and generates bias heatmaps and session analytics for teams.
    """
    
    def __init__(self):
        self.bias_patterns = self._initialize_bias_patterns()
        self.bias_prompts = self._initialize_bias_prompts()
        self.session_data = defaultdict(list)
        self.team_analytics = {}
        
    def _initialize_bias_patterns(self) -> Dict[str, List[str]]:
        """Initialize regex patterns for detecting different cognitive biases"""
        return {
            'confirmation_bias': [
                r'\b(obviously|clearly|definitely|certainly)\b',
                r'\b(everyone knows|it\'s common sense|goes without saying)\b',
                r'\b(proves my point|confirms what I thought)\b'
            ],
            'anchoring_bias': [
                r'\b(first|initial|original) (idea|thought|suggestion)\b',
                r'\b(start with|begin with|base it on)\b',
                r'\b(similar to|like the first|building on)\b'
            ],
            'availability_bias': [
                r'\b(I just saw|recently read|heard about)\b',
                r'\b(trending|popular|viral|in the news)\b',
                r'\b(everyone\'s talking about|latest)\b'
            ],
            'groupthink': [
                r'\b(we all agree|unanimous|consensus|everyone thinks)\b',
                r'\b(team decision|group choice|collective)\b',
                r'\b(let\'s stick with|go with the flow)\b'
            ],
            'sunk_cost_fallacy': [
                r'\b(already invested|spent so much|too far in)\b',
                r'\b(can\'t give up now|waste all that work)\b',
                r'\b(we\'ve come this far)\b'
            ],
            'overconfidence_bias': [
                r'\b(definitely will|guaranteed|100% sure|certain success)\b',
                r'\b(easy to|simple to|no problem|piece of cake)\b',
                r'\b(obviously better|clearly superior)\b'
            ]
        }
    
    def _initialize_bias_prompts(self) -> Dict[str, List[str]]:
        """Initialize dynamic prompts to counter each bias type"""
        return {
            'confirmation_bias': [
                "What evidence could challenge this assumption?",
                "How might someone with opposite views see this?",
                "What are we potentially overlooking?",
                "Can you play devil's advocate for a moment?"
            ],
            'anchoring_bias': [
                "Let's start fresh - what if we ignore the first idea?",
                "What would this look like from a completely different angle?",
                "How might we approach this if we had no preconceptions?",
                "What's an alternative starting point we haven't considered?"
            ],
            'availability_bias': [
                "What examples are we NOT thinking of?",
                "How might this work in a completely different context?",
                "What's been tried before that isn't trending right now?",
                "Let's explore some unconventional references."
            ],
            'groupthink': [
                "Who might disagree with this consensus and why?",
                "What's a contrarian view we should explore?",
                "Let's assign someone to be the skeptic.",
                "What are the risks of this unanimous thinking?"
            ],
            'sunk_cost_fallacy': [
                "If we started from scratch today, what would we do?",
                "What would a new team member suggest?",
                "Is continuing the best use of our remaining resources?",
                "What opportunities are we missing by not pivoting?"
            ],
            'overconfidence_bias': [
                "What could go wrong with this approach?",
                "What assumptions are we making?",
                "How might we test this hypothesis first?",
                "What's our backup plan if this doesn't work?"
            ]
        }
    
    def detect_biases(self, text: str, user_id: str = None, session_id: str = None) -> Dict[str, Any]:
        """
        Detect cognitive biases in the given text
        
        Args:
            text: Input text to analyze
            user_id: Optional user identifier
            session_id: Optional session identifier
            
        Returns:
            Dictionary containing detected biases, scores, and recommendations
        """
        detected_biases = {}
        bias_scores = {}
        
        # Convert text to lowercase for pattern matching
        text_lower = text.lower()
        
        # Check each bias type
        for bias_type, patterns in self.bias_patterns.items():
            matches = []
            for pattern in patterns:
                pattern_matches = re.findall(pattern, text_lower, re.IGNORECASE)
                matches.extend(pattern_matches)
            
            if matches:
                bias_score = len(matches) / len(text.split()) * 100  # Percentage score
                detected_biases[bias_type] = {
                    'matches': matches,
                    'count': len(matches),
                    'score': round(bias_score, 2),
                    'severity': self._calculate_severity(bias_score)
                }
                bias_scores[bias_type] = bias_score
        
        # Store session data
        if session_id and user_id:
            self._store_session_data(session_id, user_id, text, detected_biases)
        
        return {
            'detected_biases': detected_biases,
            'overall_bias_score': round(sum(bias_scores.values()), 2),
            'analysis_timestamp': datetime.now().isoformat(),
            'text_analyzed': text[:100] + "..." if len(text) > 100 else text
        }
    
    def _calculate_severity(self, score: float) -> str:
        """Calculate bias severity based on score"""
        if score >= 5.0:
            return "HIGH"
        elif score >= 2.0:
            return "MEDIUM"
        elif score > 0:
            return "LOW"
        else:
            return "NONE"
    
    def _store_session_data(self, session_id: str, user_id: str, text: str, biases: Dict):
        """Store session data for analytics"""
        session_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'text': text,
            'biases': biases,
            'bias_count': len(biases)
        }
        self.session_data[session_id].append(session_entry)
    
    def get_dynamic_prompts(self, detected_biases: Dict[str, Any], num_prompts: int = 2) -> List[str]:
        """
        Generate dynamic prompts to counter detected biases
        
        Args:
            detected_biases: Result from detect_biases method
            num_prompts: Number of prompts to return
            
        Returns:
            List of dynamic prompts to encourage new perspectives
        """
        prompts = []
        
        if not detected_biases.get('detected_biases'):
            return ["Great! No significant biases detected. Keep exploring diverse ideas!"]
        
        # Sort biases by severity and score
        sorted_biases = sorted(
            detected_biases['detected_biases'].items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        # Generate prompts for the most significant biases
        for bias_type, bias_info in sorted_biases[:num_prompts]:
            bias_prompts = self.bias_prompts.get(bias_type, [])
            if bias_prompts:
                prompts.append(f"🎯 {bias_prompts[0]} (Detected: {bias_type.replace('_', ' ').title()})")
        
        return prompts
    
    def generate_bias_heatmap(self, session_id: str, save_path: str = None) -> str:
        """
        Generate a bias heatmap for the session
        
        Args:
            session_id: Session to analyze
            save_path: Optional path to save the heatmap image
            
        Returns:
            Path to the generated heatmap image
        """
        if session_id not in self.session_data:
            raise ValueError(f"No data found for session {session_id}")
        
        session_entries = self.session_data[session_id]
        
        # Create bias matrix
        users = list(set(entry['user_id'] for entry in session_entries))
        bias_types = list(self.bias_patterns.keys())
        
        # Initialize matrix
        bias_matrix = np.zeros((len(users), len(bias_types)))
        
        # Fill matrix with bias scores
        for entry in session_entries:
            user_idx = users.index(entry['user_id'])
            for bias_type, bias_info in entry['biases'].items():
                bias_idx = bias_types.index(bias_type)
                bias_matrix[user_idx][bias_idx] += bias_info['score']
        
        # Create heatmap
        plt.figure(figsize=(12, 8))
        sns.heatmap(
            bias_matrix,
            xticklabels=[bt.replace('_', ' ').title() for bt in bias_types],
            yticklabels=users,
            annot=True,
            cmap='YlOrRd',
            fmt='.1f',
            cbar_kws={'label': 'Bias Score'}
        )
        
        plt.title(f'Cognitive Bias Heatmap - Session {session_id}')
        plt.xlabel('Bias Types')
        plt.ylabel('Team Members')
        plt.tight_layout()
        
        # Save heatmap
        if not save_path:
            save_path = f'bias_heatmap_{session_id}_{int(time.time())}.png'
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def get_session_analytics(self, session_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive session analytics
        
        Args:
            session_id: Session to analyze
            
        Returns:
            Dictionary containing session analytics
        """
        if session_id not in self.session_data:
            return {"error": f"No data found for session {session_id}"}
        
        session_entries = self.session_data[session_id]
        
        # Basic statistics
        total_contributions = len(session_entries)
        unique_users = len(set(entry['user_id'] for entry in session_entries))
        
        # Bias analysis
        all_biases = []
        user_bias_counts = defaultdict(int)
        bias_type_counts = Counter()
        
        for entry in session_entries:
            all_biases.extend(entry['biases'].keys())
            user_bias_counts[entry['user_id']] += entry['bias_count']
            for bias_type in entry['biases'].keys():
                bias_type_counts[bias_type] += 1
        
        # Timeline analysis
        timestamps = [datetime.fromisoformat(entry['timestamp']) for entry in session_entries]
        session_duration = (max(timestamps) - min(timestamps)).total_seconds() / 60  # in minutes
        
        # Most problematic user (highest bias count)
        most_biased_user = max(user_bias_counts.items(), key=lambda x: x[1]) if user_bias_counts else ("None", 0)
        
        # Bias improvement over time
        bias_trend = []
        for i, entry in enumerate(session_entries):
            avg_bias_score = sum(bias['score'] for bias in entry['biases'].values()) / max(1, len(entry['biases']))
            bias_trend.append(avg_bias_score)
        
        analytics = {
            'session_id': session_id,
            'summary': {
                'total_contributions': total_contributions,
                'unique_users': unique_users,
                'session_duration_minutes': round(session_duration, 2),
                'total_biases_detected': len(all_biases)
            },
            'bias_analysis': {
                'most_common_bias': bias_type_counts.most_common(1)[0] if bias_type_counts else ("None", 0),
                'bias_distribution': dict(bias_type_counts),
                'user_bias_counts': dict(user_bias_counts),
                'most_biased_user': most_biased_user
            },
            'trends': {
                'bias_scores_over_time': bias_trend,
                'improvement_detected': len(bias_trend) > 1 and bias_trend[-1] < bias_trend[0]
            },
            'recommendations': self._generate_recommendations(bias_type_counts, user_bias_counts)
        }
        
        return analytics
    
    def _generate_recommendations(self, bias_counts: Counter, user_bias_counts: Dict) -> List[str]:
        """Generate actionable recommendations based on session data"""
        recommendations = []
        
        if bias_counts:
            most_common_bias = bias_counts.most_common(1)[0][0]
            recommendations.append(
                f"Focus on addressing {most_common_bias.replace('_', ' ')} - it appeared most frequently"
            )
        
        if user_bias_counts:
            avg_bias_per_user = sum(user_bias_counts.values()) / len(user_bias_counts)
            if avg_bias_per_user > 3:
                recommendations.append("Consider implementing structured bias-checking protocols")
        
        if len(set(user_bias_counts.values())) > 1:
            recommendations.append("Encourage peer review - bias levels vary significantly across team members")
        
        recommendations.append("Use the dynamic prompts feature to interrupt bias loops in real-time")
        
        return recommendations
    
    def interrupt_bias_loop(self, session_id: str, user_id: str, text: str) -> Dict[str, Any]:
        """
        Real-time bias interruption system
        
        Args:
            session_id: Current session ID
            user_id: User submitting the idea
            text: Text to analyze
            
        Returns:
            Interruption response with prompts and suggestions
        """
        # Detect biases
        bias_analysis = self.detect_biases(text, user_id, session_id)
        
        # Check if intervention is needed
        if bias_analysis['overall_bias_score'] > 3.0:  # Threshold for intervention
            prompts = self.get_dynamic_prompts(bias_analysis, num_prompts=1)
            
            return {
                'interrupt': True,
                'message': "🚨 Bias Alert! Let's explore this from a different angle.",
                'detected_biases': list(bias_analysis['detected_biases'].keys()),
                'dynamic_prompt': prompts[0] if prompts else "How might we approach this differently?",
                'severity': 'HIGH' if bias_analysis['overall_bias_score'] > 5.0 else 'MEDIUM',
                'suggestion': "Take a moment to consider alternative perspectives before proceeding."
            }
        
        return {
            'interrupt': False,
            'message': "Great thinking! Continue exploring.",
            'bias_score': bias_analysis['overall_bias_score']
        }

# Example usage and testing functions
def demo_cognitive_bias_checker():
    """Demonstrate the Cognitive Bias Checker functionality"""
    
    checker = CognitiveBiasChecker()
    
    # Example biased texts
    test_texts = [
        "Obviously, this is the best solution. Everyone knows that machine learning is the answer to everything.",
        "We all agree that we should stick with our original idea since we've already invested so much time in it.",
        "I just saw this trending approach on social media. It's definitely going to work for us too.",
        "This approach is completely different from what we've been discussing. Let's explore the potential risks."
    ]
    
    session_id = "demo_session_001"
    
    print("=== Cognitive Bias Checker Demo ===\n")
    
    for i, text in enumerate(test_texts):
        user_id = f"user_{i+1}"
        
        print(f"User {i+1}: {text[:80]}...")
        
        # Detect biases
        result = checker.detect_biases(text, user_id, session_id)
        
        if result['detected_biases']:
            print(f"🚨 Biases detected: {list(result['detected_biases'].keys())}")
            print(f"Overall bias score: {result['overall_bias_score']}")
            
            # Get dynamic prompts
            prompts = checker.get_dynamic_prompts(result)
            print(f"💡 Dynamic prompt: {prompts[0] if prompts else 'None'}")
        else:
            print("✅ No significant biases detected!")
        
        # Check for interruption
        interruption = checker.interrupt_bias_loop(session_id, user_id, text)
        if interruption['interrupt']:
            print(f"⚠️ {interruption['message']}")
            print(f"🎯 {interruption['dynamic_prompt']}")
        
        print("-" * 80)
    
    # Generate session analytics
    analytics = checker.get_session_analytics(session_id)
    print("\n=== Session Analytics ===")
    print(f"Total contributions: {analytics['summary']['total_contributions']}")
    print(f"Biases detected: {analytics['summary']['total_biases_detected']}")
    print(f"Most common bias: {analytics['bias_analysis']['most_common_bias'][0]}")
    print(f"Recommendations: {analytics['recommendations'][:2]}")
    
    # Generate heatmap
    try:
        heatmap_path = checker.generate_bias_heatmap(session_id)
        print(f"\n📊 Bias heatmap saved to: {heatmap_path}")
    except Exception as e:
        print(f"Note: Heatmap generation requires matplotlib/seaborn: {e}")

if __name__ == "__main__":
    demo_cognitive_bias_checker()