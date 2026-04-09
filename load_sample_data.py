"""
Sample data loader for testing the Student Progress Tracker
Run this script to populate the database with sample students and sessions
"""

from database import Database
from datetime import datetime, timedelta
import random

def generate_sample_data():
    """Generate realistic sample data"""
    db = Database()
    
    # Sample students
    students = [
        ("John Smith", "john.smith@example.com"),
        ("Maria Garcia", "maria.garcia@example.com"),
        ("Li Wei", "li.wei@example.com"),
        ("Emma Johnson", "emma.johnson@example.com"),
        ("Ahmed Hassan", "ahmed.hassan@example.com")
    ]
    
    print("Creating sample students...")
    for name, email in students:
        db.create_student(name, email)
        print(f"  ✓ Created: {name}")
    
    print("\nGenerating sample sessions...")
    
    # Generate sessions for each student
    for student_name, _ in students:
        # Random number of completed sessions (5-15)
        num_sessions = random.randint(5, 15)
        
        for session_num in range(1, num_sessions + 1):
            # Generate realistic scores with slight improvement over time
            base_score = 5.0 + (session_num * 0.1)  # Gradual improvement
            
            fluency = round(min(9.0, max(1.0, base_score + random.uniform(-0.5, 0.5))), 1)
            lexical = round(min(9.0, max(1.0, base_score + random.uniform(-0.5, 0.5))), 1)
            grammatical = round(min(9.0, max(1.0, base_score + random.uniform(-0.5, 0.5))), 1)
            pronunciation = round(min(9.0, max(1.0, base_score + random.uniform(-0.5, 0.5))), 1)
            
            band_score = round((fluency + lexical + grammatical + pronunciation) / 4, 1)
            
            # Generate session date (weekly sessions)
            session_date = (datetime.now() - timedelta(weeks=(num_sessions - session_num))).date()
            
            # Sample feedback messages
            feedback_templates = [
                "Great improvement in fluency! Keep practicing daily conversations.",
                "Excellent use of vocabulary. Try to incorporate more idioms.",
                "Good progress! Focus on pronunciation of 'th' sounds.",
                "Well done! Your coherence has improved significantly.",
                "Outstanding session! You're ready for more complex topics.",
                "Good effort. Practice linking words for better flow.",
                "Impressive grammatical accuracy. Keep it up!",
                "Nice work! Try to expand your answers with more details.",
            ]
            
            notes_templates = [
                "Student showed good engagement. Recommend focusing on Part 2 preparation.",
                "Needs more practice with question types. Assign homework.",
                "Excellent progress. Moving to advanced topics next session.",
                "Student struggles with anxiety. Provide more encouragement.",
                "Ready for mock test. Schedule for next week.",
            ]
            
            session_data = {
                'session_number': session_num,
                'date': session_date.strftime('%Y-%m-%d'),
                'fluency': fluency,
                'lexical': lexical,
                'grammatical': grammatical,
                'pronunciation': pronunciation,
                'band_score': band_score,
                'teacher_notes': random.choice(notes_templates),
                'student_feedback': random.choice(feedback_templates)
            }
            
            db.save_session(student_name, session_data)
        
        print(f"  ✓ Generated {num_sessions} sessions for {student_name}")
    
    print("\n✅ Sample data loaded successfully!")
    print("\nYou can now run the app with: streamlit run app.py")
    print("\nSample students created:")
    for name, email in students:
        print(f"  - {name} ({email})")

if __name__ == "__main__":
    print("=" * 60)
    print("Student Progress Tracker - Sample Data Generator")
    print("=" * 60)
    print()
    
    response = input("This will create sample students and sessions. Continue? (y/n): ")
    
    if response.lower() == 'y':
        generate_sample_data()
    else:
        print("Cancelled.")
