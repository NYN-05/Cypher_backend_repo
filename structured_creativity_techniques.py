"""
Structured Creativity Techniques for Project Kaleidoscope
Implements Random Word Association, Reverse Brainstorming, and Lotus Blossom techniques
with built-in templates, instructions, and session trackers
"""

import random
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict
from dataclasses import dataclass, asdict
from enum import Enum
import re
import math
from collections import Counter

class CreativityTechnique(Enum):
    """Enumeration of available creativity techniques"""
    RANDOM_WORD_ASSOCIATION = "random_word_association"
    REVERSE_BRAINSTORMING = "reverse_brainstorming"
    LOTUS_BLOSSOM = "lotus_blossom"

@dataclass
class CreativitySession:
    """Data structure for tracking creativity sessions"""
    session_id: str
    technique: CreativityTechnique
    problem_statement: str
    start_time: datetime
    end_time: Optional[datetime] = None
    participants: List[str] = None
    ideas_generated: List[Dict] = None
    current_step: int = 0
    total_steps: int = 0
    session_data: Dict = None
    
    def __post_init__(self):
        if self.participants is None:
            self.participants = []
        if self.ideas_generated is None:
            self.ideas_generated = []
        if self.session_data is None:
            self.session_data = {}

class NLPProcessor:
    """
    NLP processing utilities for enhanced creativity techniques
    """
    
    def __init__(self):
        # Common English stop words
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'between', 'among', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
        }
        
        # Domain-specific keywords for problem categorization
        self.domain_keywords = {
            'technology': ['software', 'app', 'digital', 'platform', 'system', 'algorithm', 'ai', 'ml', 'data'],
            'business': ['revenue', 'profit', 'market', 'customer', 'sales', 'growth', 'strategy', 'competition'],
            'design': ['user', 'interface', 'experience', 'visual', 'layout', 'aesthetic', 'usability', 'design'],
            'communication': ['team', 'collaboration', 'meeting', 'feedback', 'information', 'message', 'discussion'],
            'process': ['workflow', 'efficiency', 'optimization', 'procedure', 'method', 'process', 'improvement'],
            'people': ['employee', 'staff', 'management', 'leadership', 'culture', 'motivation', 'engagement']
        }
        
    def extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text"""
        # Convert to lowercase and split
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Filter out stop words and short words
        keywords = [word for word in words if word not in self.stop_words and len(word) > 2]
        
        # Count frequency and return most common
        word_freq = Counter(keywords)
        return [word for word, freq in word_freq.most_common(10)]
    
    def categorize_problem(self, problem_text: str) -> Dict[str, float]:
        """Categorize problem into domain areas with confidence scores"""
        problem_words = set(self.extract_keywords(problem_text))
        
        domain_scores = {}
        for domain, keywords in self.domain_keywords.items():
            # Calculate overlap between problem words and domain keywords
            overlap = len(problem_words.intersection(set(keywords)))
            total_domain_words = len(keywords)
            
            # Calculate confidence score
            confidence = overlap / total_domain_words if total_domain_words > 0 else 0
            domain_scores[domain] = confidence
        
        return domain_scores
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts using word overlap"""
        words1 = set(self.extract_keywords(text1))
        words2 = set(self.extract_keywords(text2))
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def suggest_random_words(self, problem_text: str, word_database: List[str], count: int = 3) -> List[Dict[str, Any]]:
        """Suggest random words based on problem analysis"""
        problem_keywords = self.extract_keywords(problem_text)
        domain_scores = self.categorize_problem(problem_text)
        
        # Get primary domain
        primary_domain = max(domain_scores.items(), key=lambda x: x[1])[0] if domain_scores else 'general'
        
        # Select words that are NOT too similar to problem (to ensure randomness)
        suggested_words = []
        
        for word in random.sample(word_database, min(count * 3, len(word_database))):
            # Calculate how different this word is from the problem
            similarity = self.calculate_similarity(problem_text, word)
            
            # Prefer words with low similarity (more random/unexpected)
            randomness_score = 1.0 - similarity
            
            suggested_words.append({
                'word': word,
                'randomness_score': randomness_score,
                'reasoning': f"Low similarity to '{primary_domain}' domain ensures unexpected connections"
            })
        
        # Sort by randomness score and return top suggestions
        suggested_words.sort(key=lambda x: x['randomness_score'], reverse=True)
        return suggested_words[:count]
    
    def analyze_idea_quality(self, idea: str, problem_text: str) -> Dict[str, Any]:
        """Analyze the quality and characteristics of an generated idea"""
        idea_keywords = self.extract_keywords(idea)
        problem_keywords = self.extract_keywords(problem_text)
        
        # Novelty: how different the idea is from the original problem
        novelty_score = 1.0 - self.calculate_similarity(idea, problem_text)
        
        # Complexity: based on number of unique concepts
        complexity_score = min(len(idea_keywords) / 10.0, 1.0)  # Normalize to 0-1
        
        # Specificity: based on length and detail level
        specificity_score = min(len(idea.split()) / 20.0, 1.0)  # Normalize to 0-1
        
        # Overall quality score
        quality_score = (novelty_score * 0.4 + complexity_score * 0.3 + specificity_score * 0.3)
        
        return {
            'novelty_score': round(novelty_score, 2),
            'complexity_score': round(complexity_score, 2),
            'specificity_score': round(specificity_score, 2),
            'quality_score': round(quality_score, 2),
            'key_concepts': idea_keywords[:5]
        }
    
    def detect_idea_clusters(self, ideas: List[str], threshold: float = 0.3) -> List[Dict[str, Any]]:
        """Group similar ideas into clusters"""
        if not ideas:
            return []
        
        clusters = []
        used_ideas = set()
        
        for i, idea1 in enumerate(ideas):
            if i in used_ideas:
                continue
                
            cluster = {
                'representative_idea': idea1,
                'similar_ideas': [idea1],
                'cluster_theme': '',
                'similarity_scores': []
            }
            
            used_ideas.add(i)
            
            # Find similar ideas
            for j, idea2 in enumerate(ideas):
                if j <= i or j in used_ideas:
                    continue
                    
                similarity = self.calculate_similarity(idea1, idea2)
                if similarity >= threshold:
                    cluster['similar_ideas'].append(idea2)
                    cluster['similarity_scores'].append(similarity)
                    used_ideas.add(j)
            
            # Generate cluster theme based on common keywords
            all_cluster_text = ' '.join(cluster['similar_ideas'])
            common_keywords = self.extract_keywords(all_cluster_text)
            cluster['cluster_theme'] = ', '.join(common_keywords[:3]) if common_keywords else 'Mixed concepts'
            
            clusters.append(cluster)
        
        return clusters
    
    def generate_follow_up_questions(self, problem_text: str, technique: str) -> List[str]:
        """Generate intelligent follow-up questions based on problem analysis"""
        domain_scores = self.categorize_problem(problem_text)
        primary_domain = max(domain_scores.items(), key=lambda x: x[1])[0]
        keywords = self.extract_keywords(problem_text)
        
        base_questions = {
            'random_word_association': [
                f"What if we approached this {primary_domain} challenge like a completely different industry?",
                f"How might the concept of '{random.choice(keywords) if keywords else 'innovation'}' be reimagined?",
                "What assumptions about this problem might be completely wrong?",
                "If this problem was solved perfectly, what would that look like?",
                "What would happen if we reversed our typical approach?"
            ],
            'reverse_brainstorming': [
                f"What would make this {primary_domain} problem absolutely catastrophic?",
                "How could we ensure this solution fails spectacularly?",
                "What's the worst possible outcome we could create?",
                "How might we maximize confusion and inefficiency?",
                "What would guarantee stakeholder frustration?"
            ],
            'lotus_blossom': [
                f"What are 8 different perspectives on this {primary_domain} challenge?",
                f"How does '{keywords[0] if keywords else 'the main concept'}' connect to unexpected domains?",
                "What themes emerge when we think systematically?",
                "Which aspects of this problem are we not considering?",
                "How might this problem manifest in different contexts?"
            ]
        }
        
        return base_questions.get(technique, [
            "What new perspectives could we explore?",
            "How might we approach this differently?",
            "What connections are we missing?"
        ])

class StructuredCreativityTechniques:
    """
    Main class implementing structured creativity techniques with templates,
    instructions, and session tracking capabilities enhanced with NLP
    """
    
    def __init__(self):
        self.active_sessions = {}
        self.session_history = []
        self.word_database = self._initialize_word_database()
        self.templates = self._initialize_templates()
        self.instructions = self._initialize_instructions()
        self.nlp_processor = NLPProcessor()
        
    def _initialize_word_database(self) -> List[str]:
        """Initialize database of random words for association technique"""
        return [
            # Objects
            "telescope", "bicycle", "lighthouse", "butterfly", "compass", "bridge", "fountain",
            "garden", "mountain", "river", "canvas", "mirror", "clock", "book", "key",
            "ladder", "door", "window", "tree", "flower", "stone", "feather", "shell",
            
            # Actions  
            "explore", "discover", "transform", "connect", "build", "flow", "dance", "sing",
            "jump", "climb", "swim", "fly", "create", "imagine", "dream", "wonder",
            "search", "find", "gather", "share", "teach", "learn", "grow", "bloom",
            
            # Concepts
            "freedom", "harmony", "balance", "energy", "mystery", "adventure", "journey",
            "discovery", "innovation", "creativity", "inspiration", "imagination", "wonder",
            "curiosity", "passion", "courage", "wisdom", "strength", "peace", "joy",
            
            # Nature
            "ocean", "forest", "desert", "volcano", "glacier", "meadow", "valley", "peak",
            "cloud", "storm", "rainbow", "sunrise", "moonlight", "star", "comet", "planet",
            
            # Technology
            "robot", "satellite", "network", "algorithm", "quantum", "digital", "virtual",
            "artificial", "augmented", "blockchain", "neural", "hologram", "laser", "plasma"
        ]
    
    def _initialize_templates(self) -> Dict[str, Dict]:
        """Initialize templates for each creativity technique"""
        return {
            CreativityTechnique.RANDOM_WORD_ASSOCIATION.value: {
                "problem_analysis": "What is the core challenge we're trying to solve?",
                "word_selection": "Random word: {word}",
                "association_prompts": [
                    "How is this word similar to our problem?",
                    "What properties of this word could inspire solutions?",
                    "If our problem was this word, how would we handle it?",
                    "What metaphors can we draw between this word and our challenge?"
                ],
                "idea_development": "Develop 3-5 concrete ideas inspired by the associations",
                "evaluation": "Which ideas show the most promise and why?"
            },
            
            CreativityTechnique.REVERSE_BRAINSTORMING.value: {
                "problem_inversion": "Instead of solving '{problem}', how could we make it worse?",
                "failure_modes": "What would cause this problem to become catastrophic?",
                "anti_solutions": "List ways to guarantee failure or create more problems",
                "reverse_analysis": "For each anti-solution, what would the opposite action be?",
                "solution_synthesis": "Transform reversed ideas into practical solutions",
                "feasibility_check": "Which solutions are implementable and effective?"
            },
            
            CreativityTechnique.LOTUS_BLOSSOM.value: {
                "core_problem": "Central challenge: {problem}",
                "primary_themes": "Identify 8 key themes/aspects of the problem",
                "theme_expansion": "For each theme, generate 8 related ideas/solutions",
                "connection_mapping": "Find connections between ideas across different themes",
                "solution_clusters": "Group related ideas into solution clusters",
                "implementation_path": "Design implementation roadmap for best clusters"
            }
        }
    
    def _initialize_instructions(self) -> Dict[str, Dict]:
        """Initialize detailed instructions for each technique"""
        return {
            CreativityTechnique.RANDOM_WORD_ASSOCIATION.value: {
                "overview": "Uses random stimulus words to trigger new associations and breakthrough thinking",
                "when_to_use": "When stuck in conventional thinking patterns or need fresh perspectives",
                "duration": "30-45 minutes",
                "participants": "Works with 1-8 people",
                "steps": [
                    "Clearly define the problem or challenge",
                    "Generate or select a random word (system provides this)",
                    "Spend 5 minutes freely associating between word and problem",
                    "Identify interesting connections and metaphors",
                    "Develop 3-5 concrete ideas from strongest associations",
                    "Evaluate and refine most promising concepts"
                ],
                "tips": [
                    "Don't judge associations initially - embrace absurdity",
                    "Use 'How might...' questions to develop associations",
                    "Try multiple random words if first doesn't spark ideas",
                    "Focus on properties, functions, and relationships"
                ]
            },
            
            CreativityTechnique.REVERSE_BRAINSTORMING.value: {
                "overview": "Approaches problems by first considering how to cause or worsen them",
                "when_to_use": "When direct brainstorming isn't working or to identify hidden assumptions",
                "duration": "45-60 minutes", 
                "participants": "Works best with 3-10 people",
                "steps": [
                    "Clearly state the original problem",
                    "Reverse the problem: 'How could we make this worse?'",
                    "Brainstorm ways to cause failure or create more problems",
                    "Don't filter - embrace destructive and absurd ideas",
                    "For each 'anti-solution', identify the opposite action",
                    "Transform reversed ideas into practical solutions"
                ],
                "tips": [
                    "Encourage wild and destructive ideas in reverse phase",
                    "Look for hidden assumptions in anti-solutions",
                    "Some reversals lead to unexpected solution paths",
                    "Use humor to make process engaging and less threatening"
                ]
            },
            
            CreativityTechnique.LOTUS_BLOSSOM.value: {
                "overview": "Systematic idea expansion using 8x8 matrix to explore problem dimensions",
                "when_to_use": "For complex problems requiring comprehensive exploration",
                "duration": "60-90 minutes",
                "participants": "Works with 2-12 people, best with 4-8",
                "steps": [
                    "Place core problem in center of 3x3 grid",
                    "Identify 8 key themes/aspects around the center",
                    "Create new 3x3 grid for each theme",
                    "Generate 8 ideas/solutions for each theme",
                    "Look for patterns and connections across grids",
                    "Cluster related ideas into solution families"
                ],
                "tips": [
                    "Ensure themes are distinct but comprehensive",
                    "Don't worry if some theme grids are easier than others",
                    "Look for unexpected connections between distant ideas",
                    "Use color coding to identify solution clusters"
                ]
            }
        }

    def start_session(self, 
                     technique: CreativityTechnique, 
                     problem_statement: str,
                     participants: List[str] = None,
                     session_id: str = None) -> str:
        """
        Start a new creativity technique session
        
        Args:
            technique: Which creativity technique to use
            problem_statement: The problem or challenge to work on
            participants: List of participant names/IDs
            session_id: Optional custom session ID
            
        Returns:
            Session ID for tracking the session
        """
        if session_id is None:
            session_id = f"{technique.value}_{int(time.time())}"
        
        if participants is None:
            participants = ["default_user"]
        
        # Get technique-specific setup
        instructions = self.instructions[technique.value]
        total_steps = len(instructions["steps"])
        
        session = CreativitySession(
            session_id=session_id,
            technique=technique,
            problem_statement=problem_statement,
            start_time=datetime.now(),
            participants=participants,
            current_step=0,
            total_steps=total_steps
        )
        
        # Initialize technique-specific data
        if technique == CreativityTechnique.RANDOM_WORD_ASSOCIATION:
            session.session_data = {
                "random_words": [],
                "associations": {},
                "selected_ideas": []
            }
        elif technique == CreativityTechnique.REVERSE_BRAINSTORMING:
            session.session_data = {
                "reversed_problem": "",
                "anti_solutions": [],
                "reversed_solutions": [],
                "final_solutions": []
            }
        elif technique == CreativityTechnique.LOTUS_BLOSSOM:
            session.session_data = {
                "core_problem": problem_statement,
                "primary_themes": [],
                "theme_grids": {},
                "connections": [],
                "solution_clusters": []
            }
        
        self.active_sessions[session_id] = session
        
        return session_id
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get current status and next steps for a session"""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        instructions = self.instructions[session.technique.value]
        
        current_step = session.current_step
        total_steps = session.total_steps
        
        # Calculate progress
        progress_percentage = (current_step / total_steps) * 100
        
        # Get current step instruction
        current_instruction = instructions["steps"][current_step] if current_step < total_steps else "Session complete"
        
        # Get next action based on technique and step
        next_action = self._get_next_action(session)
        
        return {
            "session_id": session_id,
            "technique": session.technique.value,
            "problem_statement": session.problem_statement,
            "current_step": current_step + 1,  # Display as 1-indexed
            "total_steps": total_steps,
            "progress_percentage": round(progress_percentage, 1),
            "current_instruction": current_instruction,
            "next_action": next_action,
            "participants": session.participants,
            "ideas_generated": len(session.ideas_generated),
            "session_duration_minutes": self._get_session_duration(session),
            "technique_info": {
                "overview": instructions["overview"],
                "duration": instructions["duration"],
                "when_to_use": instructions["when_to_use"]
            }
        }
    
    def _get_next_action(self, session: CreativitySession) -> Dict[str, Any]:
        """Determine the next action for the current session state"""
        technique = session.technique
        step = session.current_step
        
        if technique == CreativityTechnique.RANDOM_WORD_ASSOCIATION:
            return self._get_random_word_action(session, step)
        elif technique == CreativityTechnique.REVERSE_BRAINSTORMING:
            return self._get_reverse_brainstorming_action(session, step)
        elif technique == CreativityTechnique.LOTUS_BLOSSOM:
            return self._get_lotus_blossom_action(session, step)
        
        return {"action": "complete", "message": "Session completed"}
    
    def _get_random_word_action(self, session: CreativitySession, step: int) -> Dict[str, Any]:
        """Get next action for Random Word Association technique"""
        if step == 0:
            return {
                "action": "acknowledge_problem",
                "message": "Review and confirm the problem statement",
                "prompt": f"Problem: {session.problem_statement}",
                "instruction": "Is this problem statement clear and well-defined?"
            }
        elif step == 1:
            # Generate intelligent random word suggestions using NLP
            word_suggestions = self.nlp_processor.suggest_random_words(
                session.problem_statement, 
                self.word_database, 
                count=3
            )
            
            # Select the most random (least similar) word
            selected_word = word_suggestions[0]['word']
            session.session_data["random_words"].append(selected_word)
            session.session_data["word_analysis"] = word_suggestions[0]
            
            # Generate intelligent follow-up questions
            follow_up_questions = self.nlp_processor.generate_follow_up_questions(
                session.problem_statement, 
                'random_word_association'
            )
            
            return {
                "action": "random_word_generated",
                "message": f"Your random word is: **{selected_word.upper()}**",
                "word": selected_word,
                "reasoning": word_suggestions[0]['reasoning'],
                "alternative_words": [w['word'] for w in word_suggestions[1:]],
                "prompt": "Spend 5 minutes associating this word with your problem",
                "questions": [
                    f"How is '{selected_word}' similar to your problem?",
                    f"What properties of '{selected_word}' could inspire solutions?",
                    f"If your problem was a '{selected_word}', how would you handle it?"
                ],
                "follow_up_questions": follow_up_questions[:3]
            }
        elif step == 2:
            return {
                "action": "collect_associations",
                "message": "Record your associations between the random word and problem",
                "prompt": "What connections did you discover?",
                "instruction": "List at least 5 associations or metaphors"
            }
        elif step == 3:
            # Analyze associations if they exist
            associations = session.session_data.get("associations", {})
            association_analysis = ""
            
            if associations:
                # Analyze the quality of associations
                association_texts = list(associations.values())
                avg_quality = 0
                if association_texts:
                    quality_scores = []
                    for assoc in association_texts:
                        analysis = self.nlp_processor.analyze_idea_quality(assoc, session.problem_statement)
                        quality_scores.append(analysis['quality_score'])
                    avg_quality = sum(quality_scores) / len(quality_scores)
                
                association_analysis = f"Association quality score: {avg_quality:.2f}/1.0"
            
            return {
                "action": "develop_ideas",
                "message": "Transform your best associations into concrete ideas",
                "prompt": "Develop 3-5 actionable solutions from your associations",
                "instruction": "Focus on the most promising connections",
                "association_analysis": association_analysis,
                "suggestion": "Try to be specific and actionable in your idea descriptions"
            }
        elif step == 4:
            return {
                "action": "evaluate_ideas",
                "message": "Evaluate and refine your generated ideas", 
                "prompt": "Which ideas show the most potential?",
                "criteria": ["Feasibility", "Novelty", "Impact", "Resources required"]
            }
        elif step == 5:
            return {
                "action": "complete",
                "message": "Random Word Association session complete!",
                "next_options": [
                    "Try another random word",
                    "Switch to different technique",
                    "Develop selected ideas further"
                ]
            }
        
        return {"action": "complete"}
    
    def _get_reverse_brainstorming_action(self, session: CreativitySession, step: int) -> Dict[str, Any]:
        """Get next action for Reverse Brainstorming technique"""
        if step == 0:
            return {
                "action": "state_original_problem",
                "message": "Confirm the original problem statement",
                "prompt": f"Original problem: {session.problem_statement}",
                "instruction": "Make sure everyone understands the challenge"
            }
        elif step == 1:
            reversed_problem = f"How could we make '{session.problem_statement}' much worse?"
            session.session_data["reversed_problem"] = reversed_problem
            
            return {
                "action": "reverse_problem",
                "message": "Now we'll think backwards - how to make it WORSE",
                "reversed_problem": reversed_problem,
                "prompt": "Brainstorm ways to cause failure or create more problems",
                "encouragement": "Embrace destructive and absurd ideas!"
            }
        elif step == 2:
            return {
                "action": "generate_anti_solutions",
                "message": "Generate anti-solutions (ways to make problem worse)",
                "prompt": "What would guarantee failure?",
                "examples": [
                    "Ignore customer feedback completely",
                    "Use the most expensive materials possible", 
                    "Never test anything before launch",
                    "Hire people with no relevant experience"
                ]
            }
        elif step == 3:
            return {
                "action": "reverse_analysis",
                "message": "Now reverse each anti-solution into a positive approach",
                "prompt": "For each way to make it worse, what's the opposite?",
                "instruction": "Transform destructive ideas into constructive solutions"
            }
        elif step == 4:
            return {
                "action": "synthesize_solutions",
                "message": "Combine and refine your reversed solutions",
                "prompt": "Which reversed ideas offer the best solutions?",
                "instruction": "Look for unexpected insights from the reversal process"
            }
        elif step == 5:
            return {
                "action": "feasibility_check",
                "message": "Evaluate feasibility and implementation potential",
                "prompt": "Which solutions are most implementable?",
                "criteria": ["Practicality", "Resources", "Timeline", "Impact"]
            }
        
        return {"action": "complete"}
    
    def _get_lotus_blossom_action(self, session: CreativitySession, step: int) -> Dict[str, Any]:
        """Get next action for Lotus Blossom technique"""
        if step == 0:
            return {
                "action": "establish_core_problem",
                "message": "Place your core problem at the center",
                "prompt": f"Core problem: {session.problem_statement}",
                "instruction": "This goes in the center of your 3x3 grid"
            }
        elif step == 1:
            return {
                "action": "identify_themes",
                "message": "Identify 8 key themes/aspects around the core problem",
                "prompt": "What are the main dimensions of this problem?",
                "examples": [
                    "Technical aspects", "User experience", "Cost factors", 
                    "Time constraints", "Resource needs", "Risk factors",
                    "Market conditions", "Implementation challenges"
                ],
                "instruction": "These themes will surround your core problem"
            }
        elif step == 2:
            return {
                "action": "expand_themes",
                "message": "Create a new 3x3 grid for each theme",
                "prompt": "For each theme, generate 8 related ideas/solutions",
                "instruction": "You'll create 8 separate grids, one for each theme",
                "tip": "Don't worry if some themes are easier than others"
            }
        elif step == 3:
            return {
                "action": "map_connections",
                "message": "Look for connections between ideas across different themes",
                "prompt": "Which ideas from different grids relate to each other?",
                "instruction": "Draw lines or use colors to show relationships"
            }
        elif step == 4:
            return {
                "action": "cluster_solutions",
                "message": "Group related ideas into solution clusters",
                "prompt": "Which ideas work together as integrated solutions?",
                "instruction": "Create 3-5 solution families from your connections"
            }
        elif step == 5:
            return {
                "action": "implementation_path",
                "message": "Design implementation roadmap for best clusters",
                "prompt": "How would you implement your top solution clusters?",
                "considerations": ["Priority order", "Dependencies", "Resources", "Timeline"]
            }
        
        return {"action": "complete"}
    
    def submit_step_data(self, session_id: str, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit data for the current step and advance to next step
        
        Args:
            session_id: Session identifier
            step_data: Data collected for current step
            
        Returns:
            Response with next step information
        """
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        
        # Store step data based on technique
        self._store_step_data(session, step_data)
        
        # Add to ideas generated if this step produces ideas
        if "ideas" in step_data:
            for idea in step_data["ideas"]:
                # Analyze idea quality using NLP
                idea_analysis = self.nlp_processor.analyze_idea_quality(idea, session.problem_statement)
                
                session.ideas_generated.append({
                    "step": session.current_step,
                    "timestamp": datetime.now().isoformat(),
                    "idea": idea,
                    "participant": step_data.get("participant", "unknown"),
                    "nlp_analysis": idea_analysis
                })
        
        # Advance to next step
        session.current_step += 1
        
        # Check if session is complete
        if session.current_step >= session.total_steps:
            return self.complete_session(session_id)
        
        # Return next step information
        return self.get_session_status(session_id)
    
    def _store_step_data(self, session: CreativitySession, step_data: Dict[str, Any]):
        """Store step-specific data in session"""
        technique = session.technique
        step = session.current_step
        
        if technique == CreativityTechnique.RANDOM_WORD_ASSOCIATION:
            if step == 2:  # Associations step
                session.session_data["associations"] = step_data.get("associations", {})
            elif step == 3:  # Ideas step
                session.session_data["selected_ideas"] = step_data.get("ideas", [])
                
        elif technique == CreativityTechnique.REVERSE_BRAINSTORMING:
            if step == 2:  # Anti-solutions step
                session.session_data["anti_solutions"] = step_data.get("anti_solutions", [])
            elif step == 3:  # Reversed solutions step
                session.session_data["reversed_solutions"] = step_data.get("reversed_solutions", [])
            elif step == 4:  # Final solutions step
                session.session_data["final_solutions"] = step_data.get("final_solutions", [])
                
        elif technique == CreativityTechnique.LOTUS_BLOSSOM:
            if step == 1:  # Themes step
                session.session_data["primary_themes"] = step_data.get("themes", [])
            elif step == 2:  # Theme expansion step
                session.session_data["theme_grids"] = step_data.get("theme_grids", {})
            elif step == 3:  # Connections step  
                session.session_data["connections"] = step_data.get("connections", [])
            elif step == 4:  # Solution clusters step
                session.session_data["solution_clusters"] = step_data.get("solution_clusters", [])
    
    def complete_session(self, session_id: str) -> Dict[str, Any]:
        """Complete a creativity session and generate summary with NLP insights"""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        session.end_time = datetime.now()
        
        # Generate session summary
        summary = self._generate_session_summary(session)
        
        # Add NLP-powered insights
        nlp_insights = self._generate_nlp_insights(session)
        summary.update(nlp_insights)
        
        # Move to history
        self.session_history.append(session)
        del self.active_sessions[session_id]
        
        return {
            "status": "completed",
            "session_id": session_id,
            "technique": session.technique.value,
            "summary": summary,
            "next_options": [
                "Start new session with different technique",
                "Export session results", 
                "Hybrid approach: combine techniques",
                "Develop ideas further with team"
            ]
        }
    
    def _generate_session_summary(self, session: CreativitySession) -> Dict[str, Any]:
        """Generate comprehensive session summary"""
        duration = self._get_session_duration(session)
        
        summary = {
            "technique_used": session.technique.value,
            "problem_statement": session.problem_statement,
            "duration_minutes": duration,
            "participants": session.participants,
            "total_ideas_generated": len(session.ideas_generated),
            "steps_completed": session.current_step,
            "completion_rate": (session.current_step / session.total_steps) * 100
        }
        
        # Add technique-specific insights
        if session.technique == CreativityTechnique.RANDOM_WORD_ASSOCIATION:
            summary.update({
                "random_words_used": session.session_data.get("random_words", []),
                "key_associations": list(session.session_data.get("associations", {}).keys()),
                "selected_ideas": session.session_data.get("selected_ideas", [])
            })
        elif session.technique == CreativityTechnique.REVERSE_BRAINSTORMING:
            summary.update({
                "reversed_problem": session.session_data.get("reversed_problem", ""),
                "anti_solutions_count": len(session.session_data.get("anti_solutions", [])),
                "final_solutions_count": len(session.session_data.get("final_solutions", []))
            })
        elif session.technique == CreativityTechnique.LOTUS_BLOSSOM:
            summary.update({
                "themes_identified": len(session.session_data.get("primary_themes", [])),
                "theme_grids_completed": len(session.session_data.get("theme_grids", {})),
                "solution_clusters": len(session.session_data.get("solution_clusters", []))
            })
        
        return summary
    
    def _get_session_duration(self, session: CreativitySession) -> float:
        """Calculate session duration in minutes"""
        end_time = session.end_time or datetime.now()
        duration = (end_time - session.start_time).total_seconds() / 60
        return round(duration, 1)
    
    def get_technique_instructions(self, technique: CreativityTechnique) -> Dict[str, Any]:
        """Get detailed instructions for a specific technique"""
        return self.instructions[technique.value]
    
    def get_available_techniques(self) -> List[Dict[str, str]]:
        """Get list of available creativity techniques with descriptions"""
        techniques = []
        for technique in CreativityTechnique:
            info = self.instructions[technique.value]
            techniques.append({
                "name": technique.value,
                "display_name": technique.value.replace("_", " ").title(),
                "overview": info["overview"],
                "duration": info["duration"],
                "participants": info["participants"],
                "when_to_use": info["when_to_use"]
            })
        return techniques
    
    def switch_technique(self, session_id: str, new_technique: CreativityTechnique, 
                        preserve_data: bool = True) -> str:
        """
        Switch to a different creativity technique mid-session (hybrid approach)
        
        Args:
            session_id: Current session ID
            new_technique: Technique to switch to
            preserve_data: Whether to preserve ideas from current session
            
        Returns:
            New session ID for the hybrid session
        """
        if session_id not in self.active_sessions:
            raise ValueError("Session not found")
        
        current_session = self.active_sessions[session_id]
        
        # Create new hybrid session ID
        hybrid_session_id = f"hybrid_{int(time.time())}"
        
        # Preserve data from current session if requested
        preserved_ideas = []
        if preserve_data:
            preserved_ideas = current_session.ideas_generated.copy()
        
        # Complete current session
        self.complete_session(session_id)
        
        # Start new session with new technique
        new_session_id = self.start_session(
            technique=new_technique,
            problem_statement=current_session.problem_statement,
            participants=current_session.participants,
            session_id=hybrid_session_id
        )
        
        # Add preserved ideas to new session
        if preserved_ideas:
            new_session = self.active_sessions[new_session_id]
            new_session.ideas_generated.extend(preserved_ideas)
            new_session.session_data["preserved_from_previous"] = {
                "technique": current_session.technique.value,
                "ideas_count": len(preserved_ideas)
            }
        
        return new_session_id
    
    def export_session_data(self, session_id: str, format_type: str = "json") -> str:
        """
        Export session data in specified format
        
        Args:
            session_id: Session to export
            format_type: Export format ("json", "markdown", "csv")
            
        Returns:
            Exported data as string
        """
        # Check both active and historical sessions
        session = None
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
        else:
            # Look in history
            for hist_session in self.session_history:
                if hist_session.session_id == session_id:
                    session = hist_session
                    break
        
        if session is None:
            return f"Session {session_id} not found"
        
        if format_type.lower() == "json":
            return self._export_json(session)
        elif format_type.lower() == "markdown":
            return self._export_markdown(session)
        elif format_type.lower() == "csv":
            return self._export_csv(session)
        else:
            return "Unsupported export format. Use: json, markdown, or csv"
    
    def _export_json(self, session: CreativitySession) -> str:
        """Export session as JSON"""
        export_data = {
            "session_info": {
                "session_id": session.session_id,
                "technique": session.technique.value,
                "problem_statement": session.problem_statement,
                "start_time": session.start_time.isoformat(),
                "end_time": session.end_time.isoformat() if session.end_time else None,
                "participants": session.participants,
                "duration_minutes": self._get_session_duration(session)
            },
            "ideas_generated": session.ideas_generated,
            "technique_data": session.session_data,
            "summary": self._generate_session_summary(session)
        }
        return json.dumps(export_data, indent=2, default=str)
    
    def _export_markdown(self, session: CreativitySession) -> str:
        """Export session as Markdown report"""
        duration = self._get_session_duration(session)
        technique_name = session.technique.value.replace("_", " ").title()
        
        md = f"""# {technique_name} Session Report

## Session Information
- **Session ID:** {session.session_id}
- **Technique:** {technique_name}  
- **Problem Statement:** {session.problem_statement}
- **Duration:** {duration} minutes
- **Participants:** {', '.join(session.participants)}
- **Ideas Generated:** {len(session.ideas_generated)}

## Problem Addressed
{session.problem_statement}

## Ideas Generated
"""
        
        for i, idea in enumerate(session.ideas_generated, 1):
            md += f"{i}. **{idea.get('idea', 'No description')}**\n"
            md += f"   - Step: {idea.get('step', 'Unknown')}\n"
            md += f"   - Participant: {idea.get('participant', 'Unknown')}\n\n"
        
        # Add technique-specific details
        if session.technique == CreativityTechnique.RANDOM_WORD_ASSOCIATION:
            md += f"\n## Random Words Used\n"
            for word in session.session_data.get("random_words", []):
                md += f"- {word}\n"
        
        md += f"\n## Session Summary\n"
        summary = self._generate_session_summary(session)
        for key, value in summary.items():
            md += f"- **{key.replace('_', ' ').title()}:** {value}\n"
        
        return md
    
    def _export_csv(self, session: CreativitySession) -> str:
        """Export session ideas as CSV"""
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(["Idea", "Step", "Participant", "Timestamp"])
        
        # Data rows
        for idea in session.ideas_generated:
            writer.writerow([
                idea.get('idea', ''),
                idea.get('step', ''),
                idea.get('participant', ''), 
                idea.get('timestamp', '')
            ])
        
        return output.getvalue()

# Example usage and demo functions
def demo_structured_creativity_techniques():
    """Comprehensive demo of all structured creativity techniques"""
    
    techniques = StructuredCreativityTechniques()
    problem = "How can we improve team collaboration in remote work environments?"
    
    print("=== Structured Creativity Techniques Demo ===\n")
    
    # Show available techniques
    print("📋 Available Techniques:")
    for technique in techniques.get_available_techniques():
        print(f"- {technique['display_name']}: {technique['overview']}")
    print()
    
    # Demo Random Word Association
    print("🎯 DEMO: Random Word Association")
    print("=" * 50)
    
    session_id = techniques.start_session(
        CreativityTechnique.RANDOM_WORD_ASSOCIATION,
        problem,
        ["Alice", "Bob", "Charlie"]
    )
    
    # Simulate session progress
    for step in range(6):
        status = techniques.get_session_status(session_id)
        print(f"\nStep {step + 1}/{status['total_steps']}: {status['current_instruction']}")
        print(f"Next Action: {status['next_action']['action']}")
        
        if 'message' in status['next_action']:
            print(f"Message: {status['next_action']['message']}")
        
        if 'prompt' in status['next_action']:
            print(f"Prompt: {status['next_action']['prompt']}")
        
        # Simulate step completion
        if step == 2:  # Associations step
            step_data = {
                "associations": {
                    "telescope views distant objects": "Remote work requires tools to 'see' distant team members",
                    "telescope focuses light": "We need to focus scattered communication",
                    "telescope requires clear sky": "Clear communication channels are essential"
                }
            }
        elif step == 3:  # Ideas step  
            step_data = {
                "ideas": [
                    "Virtual 'telescope' dashboard showing team availability and mood",
                    "Focus sessions: dedicated time blocks for deep collaboration",
                    "Clear sky policy: eliminate communication interference"
                ]
            }
        else:
            step_data = {"completed": True}
        
        result = techniques.submit_step_data(session_id, step_data)
        if result.get("status") == "completed":
            print("\n✅ Session completed!")
            print(f"Summary: {result['summary']}")
            break
    
    print("\n" + "=" * 70)
    
    # Demo technique switching (hybrid approach)
    print("\n🔄 DEMO: Technique Switching (Hybrid Approach)")
    print("=" * 50)
    
    # Start with Reverse Brainstorming
    reverse_session = techniques.start_session(
        CreativityTechnique.REVERSE_BRAINSTORMING,
        problem,
        ["Alice", "Bob"]
    )
    
    print("Started Reverse Brainstorming session...")
    
    # Simulate partial completion
    for step in range(3):
        status = techniques.get_session_status(reverse_session)
        print(f"Step {step + 1}: {status['current_instruction']}")
        
        step_data = {"ideas": [f"Reverse idea {step + 1}"]}
        techniques.submit_step_data(reverse_session, step_data)
    
    # Switch to Lotus Blossom
    print("\n🔄 Switching to Lotus Blossom technique...")
    lotus_session = techniques.switch_technique(reverse_session, CreativityTechnique.LOTUS_BLOSSOM)
    
    new_status = techniques.get_session_status(lotus_session)
    print(f"New session: {new_status['technique']}")
    print(f"Preserved ideas: {new_status['ideas_generated']}")
    
    # Demo export functionality
    print("\n📊 DEMO: Export Session Data")
    print("=" * 50)
    
    # Export as Markdown
    md_export = techniques.export_session_data(lotus_session, "markdown")
    print("Markdown Export (first 300 chars):")
    print(md_export[:300] + "...")
    
    print(f"\n📈 Total sessions in history: {len(techniques.session_history)}")
    print("Demo completed! 🎉")

def demo_single_technique():
    """Demo a single technique interactively"""
    
    techniques = StructuredCreativityTechniques()
    
    # Random Word Association demo
    problem = "How to increase user engagement in our mobile app?"
    
    session_id = techniques.start_session(
        CreativityTechnique.RANDOM_WORD_ASSOCIATION,
        problem,
        ["Developer", "Designer", "PM"]
    )
    
    print("🎯 Random Word Association - Interactive Demo")
    print("=" * 50)
    print(f"Problem: {problem}\n")
    
    # Step through the process
    while True:
        status = techniques.get_session_status(session_id)
        
        if status.get("error"):
            print("Session ended.")
            break
        
        print(f"📍 Step {status['current_step']}/{status['total_steps']} ({status['progress_percentage']:.1f}% complete)")
        print(f"Instruction: {status['current_instruction']}")
        
        next_action = status['next_action']
        print(f"Action: {next_action['action']}")
        
        if 'message' in next_action:
            print(f"💬 {next_action['message']}")
        
        if 'prompt' in next_action:
            print(f"❓ {next_action['prompt']}")
        
        if 'questions' in next_action:
            print("Questions to consider:")
            for q in next_action['questions']:
                print(f"  • {q}")
        
        print("-" * 50)
        
        # Simulate user input based on step
        if status['current_step'] == 2:  # Random word step
            input("Press Enter to continue to associations...")
            step_data = {
                "associations": {
                    "lighthouse guides ships": "App should guide users to key features",
                    "lighthouse beam rotates": "Rotate through different engagement features",
                    "lighthouse visible from distance": "Make value proposition visible immediately"
                }
            }
        elif status['current_step'] == 4:  # Ideas step
            step_data = {
                "ideas": [
                    "Rotating feature spotlight that highlights different app capabilities daily",
                    "Navigation beacon system that guides new users through key workflows",
                    "Distance visibility: show immediate value on splash screen"
                ],
                "participant": "Team"
            }
        else:
            step_data = {"completed": True}
        
        result = techniques.submit_step_data(session_id, step_data)
        
        if result.get("status") == "completed":
            print("\n🎉 Session Complete!")
            print("\nFinal Summary:")
            summary = result['summary']
            for key, value in summary.items():
                print(f"  {key}: {value}")
            break
        
        print()

if __name__ == "__main__":
    # Run full demo
    demo_structured_creativity_techniques()
    
    print("\n" + "=" * 70)
    print("Run demo_single_technique() for interactive experience")