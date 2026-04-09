import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import json
from database import Database
from notification import send_email_notification

# Page configuration
st.set_page_config(
    page_title="Student Progress Tracker",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .session-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .completed {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
    }
    .current {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
    }
    .future {
        background-color: #f8f9fa;
        border-left: 5px solid #6c757d;
    }
    .score-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-weight: bold;
        margin: 0.25rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3rem;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize database
db = Database()

def calculate_band_score(fluency, lexical, grammatical, pronunciation):
    """Calculate the average IELTS band score"""
    scores = [fluency, lexical, grammatical, pronunciation]
    return round(sum(scores) / len(scores), 1)

def get_score_color(score):
    """Return color based on score range"""
    if score >= 8.0:
        return "#28a745"  # Green
    elif score >= 6.5:
        return "#ffc107"  # Yellow
    elif score >= 5.0:
        return "#fd7e14"  # Orange
    else:
        return "#dc3545"  # Red

def create_roadmap_chart(sessions_data):
    """Create an interactive roadmap visualization"""
    session_numbers = []
    scores = []
    colors = []
    labels = []
    
    for i in range(1, 31):
        session_numbers.append(i)
        session = sessions_data.get(str(i))
        
        if session and session.get('band_score'):
            score = session['band_score']
            scores.append(score)
            colors.append(get_score_color(score))
            labels.append(f"Session {i}<br>Score: {score}")
        else:
            scores.append(0)
            colors.append("#e9ecef")
            labels.append(f"Session {i}<br>Not completed")
    
    fig = go.Figure()
    
    # Add bars for sessions
    fig.add_trace(go.Bar(
        x=session_numbers,
        y=scores,
        marker=dict(
            color=colors,
            line=dict(color='white', width=2)
        ),
        text=scores,
        texttemplate='%{text:.1f}',
        textposition='outside',
        hovertext=labels,
        hoverinfo='text'
    ))
    
    # Add reference lines for IELTS bands
    for band, label in [(5.0, 'Band 5'), (6.5, 'Band 6.5'), (8.0, 'Band 8')]:
        fig.add_hline(y=band, line_dash="dash", line_color="gray", opacity=0.5,
                      annotation_text=label, annotation_position="right")
    
    fig.update_layout(
        title="30-Session Learning Roadmap",
        xaxis_title="Session Number",
        yaxis_title="IELTS Band Score",
        yaxis=dict(range=[0, 9.5]),
        height=400,
        showlegend=False,
        hovermode='x unified'
    )
    
    return fig

def teacher_view():
    """Teacher's interface for inputting data"""
    st.markdown('<p class="main-header">👨‍🏫 Teacher Dashboard</p>', unsafe_allow_html=True)
    
    # Student selector
    students = db.get_all_students()
    
    col1, col2 = st.columns([2, 1])
    with col1:
        student_options = ["Add New Student..."] + students
        selected_student = st.selectbox("Select Student", student_options)
    
    with col2:
        if selected_student == "Add New Student...":
            new_student = st.text_input("New Student Name")
            if st.button("Create Student") and new_student:
                db.create_student(new_student, "student@example.com")
                st.success(f"Student '{new_student}' created!")
                st.rerun()
    
    if selected_student and selected_student != "Add New Student...":
        # --- STUDENT MANAGEMENT (DANGER ZONE) ---
        with st.expander("⚠️ Student Management (Danger Zone)"):
            st.warning(f"Warning: Deleting **{selected_student}** will erase all session records permanently.")
            confirm_deletion = st.checkbox(f"I am sure I want to delete all data for {selected_student}")
            
            if st.button(f"🗑️ Delete {selected_student} Permanently", type="secondary"):
                if confirm_deletion:
                    if db.delete_student(selected_student):
                        st.success(f"Successfully deleted {selected_student}.")
                        st.rerun()
                    else:
                        st.error("Something went wrong with the database.")
                else:
                    st.info("Please check the confirmation box first.")
        # ----------------------------------------
        
        st.divider()
        
        # Session selector
        col1, col2 = st.columns([1, 2])
        with col1:
            session_number = st.number_input(
                "Session Number", 
                min_value=1, 
                max_value=30, 
                value=1,
                step=1
            )
        
        with col2:
            session_date = st.date_input("Session Date", datetime.now())
        
        st.subheader("IELTS Speaking Assessment")
        
        # IELTS scoring inputs
        col1, col2 = st.columns(2)
        
        with col1:
            fluency = st.slider(
                "Fluency and Coherence",
                min_value=1.0,
                max_value=9.0,
                value=5.0,
                step=0.5,
                help="Ability to speak smoothly and connect ideas"
            )
            
            lexical = st.slider(
                "Lexical Resource",
                min_value=1.0,
                max_value=9.0,
                value=5.0,
                step=0.5,
                help="Range and accuracy of vocabulary"
            )
        
        with col2:
            grammatical = st.slider(
                "Grammatical Range and Accuracy",
                min_value=1.0,
                max_value=9.0,
                value=5.0,
                step=0.5,
                help="Variety and correctness of grammar structures"
            )
            
            pronunciation = st.slider(
                "Pronunciation",
                min_value=1.0,
                max_value=9.0,
                value=5.0,
                step=0.5,
                help="Clarity and naturalness of speech"
            )
        
        # Calculate band score
        band_score = calculate_band_score(fluency, lexical, grammatical, pronunciation)
        
        st.metric(
            "Overall Band Score",
            f"{band_score}",
            delta=None
        )
        
        # Feedback sections
        st.subheader("Feedback")
        
        teacher_notes = st.text_area(
            "Teacher's Private Notes",
            placeholder="Private notes for your records only...",
            height=100
        )
        
        student_feedback = st.text_area(
            "Student Feedback",
            placeholder="Feedback that will be visible to the student...",
            height=150
        )
        
        # Save session
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("💾 Save Session", type="primary"):
                session_data = {
                    'session_number': session_number,
                    'date': session_date.strftime('%Y-%m-%d'),
                    'fluency': fluency,
                    'lexical': lexical,
                    'grammatical': grammatical,
                    'pronunciation': pronunciation,
                    'band_score': band_score,
                    'teacher_notes': teacher_notes,
                    'student_feedback': student_feedback
                }
                
                db.save_session(selected_student, session_data)
                
                # Send notification to student
                student_email = db.get_student_email(selected_student)
                if student_email:
                    send_email_notification(
                        student_email,
                        selected_student,
                        session_number,
                        band_score
                    )
                
                st.success(f"✅ Session {session_number} saved and notification sent!")
        
        with col2:
            if st.button("🗑️ Delete Session"):
                db.delete_session(selected_student, session_number)
                st.success(f"Session {session_number} deleted!")
                st.rerun()
        
        # Display student progress
        st.divider()
        st.subheader(f"Progress Overview: {selected_student}")
        
        sessions_data = db.get_student_sessions(selected_student)
        
        if sessions_data:
            # Show roadmap
            fig = create_roadmap_chart(sessions_data)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show session list
            st.subheader("Session History")
            for i in range(30, 0, -1):
                session = sessions_data.get(str(i))
                if session:
                    with st.expander(f"Session {i} - {session.get('date', 'N/A')} - Band: {session.get('band_score', 'N/A')}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Fluency:** {session.get('fluency', 'N/A')}")
                            st.write(f"**Lexical:** {session.get('lexical', 'N/A')}")
                        with col2:
                            st.write(f"**Grammatical:** {session.get('grammatical', 'N/A')}")
                            st.write(f"**Pronunciation:** {session.get('pronunciation', 'N/A')}")
                        
                        if session.get('teacher_notes'):
                            st.write("**Private Notes:**")
                            st.info(session['teacher_notes'])
                        
                        if session.get('student_feedback'):
                            st.write("**Student Feedback:**")
                            st.success(session['student_feedback'])

def student_view():
    """Student's interface for viewing progress"""
    st.markdown('<p class="main-header">📖 Student Progress Dashboard</p>', unsafe_allow_html=True)
    
    # Student selector
    students = db.get_all_students()
    
    if not students:
        st.warning("No students found. Please contact your teacher.")
        return
    
    selected_student = st.selectbox("Select Your Name", students)
    
    if selected_student:
        sessions_data = db.get_student_sessions(selected_student)
        
        # Statistics
        completed_sessions = len([s for s in sessions_data.values() if s.get('band_score')])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Completed Sessions", f"{completed_sessions}/30")
        
        with col2:
            if sessions_data:
                scores = [s.get('band_score', 0) for s in sessions_data.values() if s.get('band_score')]
                avg_score = sum(scores) / len(scores) if scores else 0
                st.metric("Average Score", f"{avg_score:.1f}")
            else:
                st.metric("Average Score", "N/A")
        
        with col3:
            if sessions_data:
                scores = [s.get('band_score', 0) for s in sessions_data.values() if s.get('band_score')]
                highest = max(scores) if scores else 0
                st.metric("Highest Score", f"{highest:.1f}")
            else:
                st.metric("Highest Score", "N/A")
        
        with col4:
            if sessions_data:
                last_session_num = max([int(k) for k in sessions_data.keys() if sessions_data[k].get('band_score')], default=0)
                st.metric("Last Session", f"#{last_session_num}" if last_session_num else "N/A")
            else:
                st.metric("Last Session", "N/A")
        
        st.divider()
        
        # Roadmap visualization
        if sessions_data:
            fig = create_roadmap_chart(sessions_data)
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Session details
        st.subheader("Session Details")
        
        for i in range(30, 0, -1):
            session = sessions_data.get(str(i))
            
            if session and session.get('band_score'):
                status_icon = "✅"
                with st.expander(f"{status_icon} Session {i} - {session.get('date', 'N/A')} - Band: {session.get('band_score', 'N/A')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"""
                        <div class='score-badge' style='background-color: {get_score_color(session.get('fluency', 0))}20; color: {get_score_color(session.get('fluency', 0))}'>
                            Fluency: {session.get('fluency', 'N/A')}
                        </div>
                        <div class='score-badge' style='background-color: {get_score_color(session.get('lexical', 0))}20; color: {get_score_color(session.get('lexical', 0))}'>
                            Lexical: {session.get('lexical', 'N/A')}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class='score-badge' style='background-color: {get_score_color(session.get('grammatical', 0))}20; color: {get_score_color(session.get('grammatical', 0))}'>
                            Grammatical: {session.get('grammatical', 'N/A')}
                        </div>
                        <div class='score-badge' style='background-color: {get_score_color(session.get('pronunciation', 0))}20; color: {get_score_color(session.get('pronunciation', 0))}'>
                            Pronunciation: {session.get('pronunciation', 'N/A')}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    if session.get('student_feedback'):
                        st.write("**Teacher's Feedback:**")
                        st.success(session['student_feedback'])
            elif i == completed_sessions + 1:
                st.info(f"🔄 Session {i} - Up Next")
            else:
                pass # Optionally show placeholders for future sessions

def main():
    """Main application"""
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    view_mode = st.sidebar.radio(
        "Select View",
        ["👨‍🏫 Teacher", "📖 Student"],
        index=0
    )
    
    st.sidebar.divider()
    
    st.sidebar.info("""
    **How to use:**
    
    **Teacher Mode:**
    - Select or create a student
    - Choose session number (1-30)
    - Enter IELTS scores
    - Add feedback and notes
    - Save to update student's progress
    
    **Student Mode:**
    - View your progress roadmap
    - Check individual session scores
    - Read teacher's feedback
    """)
    
    # Display appropriate view
    if view_mode == "👨‍🏫 Teacher":
        teacher_view()
    else:
        student_view()

if __name__ == "__main__":
    main()