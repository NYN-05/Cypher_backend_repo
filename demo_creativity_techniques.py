"""
Quick Demo for Structured Creativity Techniques
"""

from structured_creativity_techniques import (
    StructuredCreativityTechniques, 
    CreativityTechnique
)

def quick_demo():
    """Quick demonstration of structured creativity techniques"""
    
    techniques = StructuredCreativityTechniques()
    
    print("🎯 Structured Creativity Techniques - Quick Demo")
    print("=" * 60)
    
    # Show available techniques
    print("\n📋 Available Techniques:")
    available = techniques.get_available_techniques()
    for i, technique in enumerate(available, 1):
        print(f"{i}. {technique['display_name']}")
        print(f"   {technique['overview']}")
        print(f"   Duration: {technique['duration']}, Participants: {technique['participants']}")
        print()
    
    # Demo Random Word Association
    print("🎯 DEMO 1: Random Word Association")
    print("-" * 40)
    
    problem = "How to improve team productivity?"
    session_id = techniques.start_session(
        CreativityTechnique.RANDOM_WORD_ASSOCIATION,
        problem,
        ["Alice", "Bob"]
    )
    
    # Show first few steps
    for step_num in range(3):
        status = techniques.get_session_status(session_id)
        print(f"\nStep {step_num + 1}: {status['current_instruction']}")
        
        next_action = status['next_action']
        if 'message' in next_action:
            print(f"💬 {next_action['message']}")
        if 'word' in next_action:
            print(f"🔤 Random word: **{next_action['word']}**")
        if 'questions' in next_action:
            print("Questions to explore:")
            for q in next_action['questions'][:2]:
                print(f"  • {q}")
        
        # Submit dummy data to advance
        if step_num == 1:
            step_data = {"associations": {"sample": "association"}}
        else:
            step_data = {"completed": True}
        
        techniques.submit_step_data(session_id, step_data)
    
    print("\n" + "=" * 60)
    
    # Demo Reverse Brainstorming
    print("\n🎯 DEMO 2: Reverse Brainstorming")
    print("-" * 40)
    
    reverse_session = techniques.start_session(
        CreativityTechnique.REVERSE_BRAINSTORMING,
        "How to reduce customer complaints?",
        ["Team"]
    )
    
    # Show first two steps
    for step_num in range(2):
        status = techniques.get_session_status(reverse_session)
        print(f"\nStep {step_num + 1}: {status['current_instruction']}")
        
        next_action = status['next_action']
        if 'message' in next_action:
            print(f"💬 {next_action['message']}")
        if 'reversed_problem' in next_action:
            print(f"🔄 Reversed: {next_action['reversed_problem']}")
        
        techniques.submit_step_data(reverse_session, {"completed": True})
    
    print("\n" + "=" * 60)
    
    # Demo Lotus Blossom
    print("\n🎯 DEMO 3: Lotus Blossom")
    print("-" * 40)
    
    lotus_session = techniques.start_session(
        CreativityTechnique.LOTUS_BLOSSOM,
        "How to innovate our product line?",
        ["Innovation Team"]
    )
    
    status = techniques.get_session_status(lotus_session)
    print(f"Step 1: {status['current_instruction']}")
    
    next_action = status['next_action']
    if 'examples' in next_action:
        print("Theme examples:")
        for example in next_action['examples'][:4]:
            print(f"  • {example}")
    
    print("\n" + "=" * 60)
    
    # Demo technique switching
    print("\n🔄 DEMO 4: Technique Switching (Hybrid)")
    print("-" * 40)
    
    print("Starting with Random Word Association...")
    hybrid_start = techniques.start_session(
        CreativityTechnique.RANDOM_WORD_ASSOCIATION,
        "How to increase user engagement?",
        ["Team"]
    )
    
    # Add some ideas
    techniques.submit_step_data(hybrid_start, {
        "ideas": ["Gamification elements", "Personalized content"]
    })
    
    print("Switching to Lotus Blossom technique...")
    hybrid_session = techniques.switch_technique(
        hybrid_start, 
        CreativityTechnique.LOTUS_BLOSSOM,
        preserve_data=True
    )
    
    hybrid_status = techniques.get_session_status(hybrid_session)
    print(f"New technique: {hybrid_status['technique']}")
    print(f"Ideas preserved: {hybrid_status['ideas_generated']}")
    
    print("\n" + "=" * 60)
    
    # Demo export
    print("\n📊 DEMO 5: Session Export")
    print("-" * 40)
    
    # Complete a session and export it
    export_session = techniques.start_session(
        CreativityTechnique.RANDOM_WORD_ASSOCIATION,
        "Export demo problem",
        ["User"]
    )
    
    # Add some sample data
    techniques.submit_step_data(export_session, {
        "ideas": ["Export idea 1", "Export idea 2"]
    })
    
    # Export as markdown
    md_export = techniques.export_session_data(export_session, "markdown")
    
    print("Markdown Export (first 200 characters):")
    print(md_export[:200] + "...")
    
    print("\n✅ Demo completed! All techniques are working properly.")
    
    # Show session statistics
    print(f"\n📊 Session Statistics:")
    print(f"Active sessions: {len(techniques.active_sessions)}")
    print(f"Completed sessions: {len(techniques.session_history)}")

if __name__ == "__main__":
    quick_demo()