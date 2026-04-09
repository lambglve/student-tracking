# Student Progress Tracker - Deployment Guide

## 📋 Overview

This is a comprehensive Student Progress Tracker built with Python and Streamlit, featuring:
- Visual 30-session roadmap with progress tracking
- IELTS Speaking grading system (4 criteria: Fluency, Lexical, Grammatical, Pronunciation)
- Automatic band score calculation
- Separate Teacher and Student dashboards
- Email notifications when grades are posted
- SQLite database for data persistence

---

## 🚀 Quick Start (Local Testing)

### 1. Install Python
Make sure you have Python 3.8+ installed:
```bash
python --version
```

### 2. Install Dependencies
```bash
cd student_tracker
pip install -r requirements.txt
```

### 3. Run the Application
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 🌐 Deployment Options

### Option 1: Streamlit Cloud (Recommended - FREE)

**Best for: Easy sharing with students and teachers**

1. **Create a GitHub Account** (if you don't have one)
   - Go to https://github.com
   - Sign up for free

2. **Upload Your Code to GitHub**
   ```bash
   cd student_tracker
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/student-tracker.git
   git push -u origin main
   ```

3. **Deploy to Streamlit Cloud**
   - Go to https://streamlit.io/cloud
   - Sign in with GitHub
   - Click "New app"
   - Select your repository: `student-tracker`
   - Main file path: `app.py`
   - Click "Deploy"

4. **Share the URL**
   - Your app will be live at: `https://YOUR_APP_NAME.streamlit.app`
   - Share this URL with teachers and students
   - Both can access it simultaneously

**Advantages:**
- ✅ Free hosting
- ✅ Automatic HTTPS
- ✅ Easy updates (just push to GitHub)
- ✅ No server management

---

### Option 2: Railway (Alternative - FREE tier available)

1. **Create Account**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Deploy**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will auto-detect Streamlit

3. **Configure**
   - Set custom domain (optional)
   - Share URL with users

---

### Option 3: Heroku (Paid - Deprecated free tier)

1. **Install Heroku CLI**
   ```bash
   # Mac
   brew install heroku/brew/heroku
   
   # Windows - Download from heroku.com
   ```

2. **Create Procfile**
   ```
   web: streamlit run app.py --server.port=$PORT
   ```

3. **Deploy**
   ```bash
   heroku login
   heroku create your-app-name
   git push heroku main
   ```

---

### Option 4: PythonAnywhere (Paid - $5/month)

1. Create account at https://www.pythonanywhere.com
2. Upload files via Web interface
3. Configure web app with Streamlit
4. Set custom domain

---

### Option 5: Self-Hosted (Advanced)

**Best for: Full control, school/company servers**

**Requirements:**
- Linux server (Ubuntu recommended)
- Domain name (optional)
- Basic terminal knowledge

**Setup:**

1. **Install Python and Dependencies**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip nginx
   pip3 install -r requirements.txt
   ```

2. **Run with systemd (Auto-restart)**
   
   Create `/etc/systemd/system/student-tracker.service`:
   ```ini
   [Unit]
   Description=Student Progress Tracker
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/var/www/student-tracker
   ExecStart=/usr/local/bin/streamlit run app.py --server.port 8501
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start:
   ```bash
   sudo systemctl enable student-tracker
   sudo systemctl start student-tracker
   ```

3. **Configure Nginx (Reverse Proxy)**
   
   Create `/etc/nginx/sites-available/student-tracker`:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
       }
   }
   ```

   Enable site:
   ```bash
   sudo ln -s /etc/nginx/sites-available/student-tracker /etc/nginx/sites-enabled/
   sudo systemctl restart nginx
   ```

---

## 📧 Email Notification Setup

### Gmail Setup (Recommended)

1. **Enable 2-Factor Authentication**
   - Go to Google Account Settings
   - Security → 2-Step Verification → Turn On

2. **Create App Password**
   - Security → App passwords
   - Select "Mail" and your device
   - Copy the 16-character password

3. **Configure Environment**
   
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

   Edit `.env`:
   ```
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_password_here
   SENDER_EMAIL=your_email@gmail.com
   ```

4. **For Streamlit Cloud**
   - Go to your app settings
   - Secrets → Edit
   - Paste your `.env` contents

### Other Email Providers

**Outlook/Hotmail:**
```
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

**Yahoo:**
```
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

**Custom SMTP:**
- Contact your email provider for SMTP settings

---

## 👥 Multi-User Access

### How It Works

1. **Teacher Access**
   - Teacher opens the app URL
   - Selects "Teacher" mode in sidebar
   - Can see all students and manage data

2. **Student Access**
   - Student opens the same URL
   - Selects "Student" mode in sidebar
   - Chooses their name from dropdown
   - Views their progress only

### Data Synchronization

The SQLite database (`student_progress.db`) stores all data:
- When deployed, all users access the same database
- Changes by teacher are immediately visible to students
- No separate "teacher" and "student" apps needed

### Adding Authentication (Optional)

For production use, consider adding password protection:

1. **Simple Password (Built-in)**
   
   Add to `app.py`:
   ```python
   import streamlit as st
   
   def check_password():
       """Returns `True` if user has correct password."""
       def password_entered():
           """Checks whether password is correct."""
           if st.session_state["password"] == "your_password_here":
               st.session_state["password_correct"] = True
               del st.session_state["password"]
           else:
               st.session_state["password_correct"] = False
       
       if "password_correct" not in st.session_state:
           st.text_input("Password", type="password", on_change=password_entered, key="password")
           return False
       elif not st.session_state["password_correct"]:
           st.text_input("Password", type="password", on_change=password_entered, key="password")
           st.error("😕 Password incorrect")
           return False
       else:
           return True
   
   if not check_password():
       st.stop()
   ```

2. **OAuth Integration**
   - Use `streamlit-authenticator` package
   - Integrate with Google/Microsoft login

---

## 🔧 Advanced Configuration

### Firebase Backend (Alternative to SQLite)

For better scalability and real-time sync:

1. **Create Firebase Project**
   - Go to https://firebase.google.com
   - Create new project
   - Enable Firestore Database

2. **Update `database.py`**
   - Replace SQLite code with Firestore
   - Use `firebase-admin` package (already in requirements)

3. **Add Firebase Credentials**
   - Download service account JSON
   - Add to `.env` or Streamlit secrets

### Google Sheets Backend (Alternative)

For easier data access and backup:

1. **Install gspread**
   ```bash
   pip install gspread oauth2client
   ```

2. **Setup Google Sheets API**
   - Create service account
   - Share sheet with service account email

3. **Replace database.py**
   - Use gspread to read/write to sheets

---

## 📊 Database Backup

### Automatic Backups

Add to `database.py`:
```python
import shutil
from datetime import datetime

def backup_database():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    shutil.copy('student_progress.db', f'backups/backup_{timestamp}.db')
```

### Manual Backup

```bash
# Copy database file
cp student_progress.db student_progress_backup.db

# Or use git
git add student_progress.db
git commit -m "Database backup"
```

---

## 🎓 Usage Guide

### For Teachers

1. **Create Students**
   - Select "Add New Student" from dropdown
   - Enter name and create
   - (Optional) Add email for notifications

2. **Record Sessions**
   - Select student
   - Choose session number (1-30)
   - Enter IELTS scores using sliders
   - Band score auto-calculates
   - Add private notes (not visible to students)
   - Add student feedback (visible to students)
   - Click "Save Session"

3. **View Progress**
   - Roadmap shows all 30 sessions
   - Color-coded by score level
   - Session history with expandable details

### For Students

1. **View Dashboard**
   - Select your name
   - See completed sessions count
   - Check average and highest scores

2. **Check Roadmap**
   - Visual progress across 30 sessions
   - Color-coded scores
   - Reference lines for IELTS bands

3. **Read Feedback**
   - Expand any completed session
   - View detailed scores
   - Read teacher's feedback

---

## 🐛 Troubleshooting

### App Won't Start

**Error: `ModuleNotFoundError`**
```bash
pip install -r requirements.txt
```

**Error: `Port already in use`**
```bash
streamlit run app.py --server.port 8502
```

### Database Issues

**Database locked:**
- Only one process should access SQLite
- For multi-user, use Firebase or PostgreSQL

**Lost data:**
- Check if `student_progress.db` exists
- Restore from backup

### Email Not Sending

**Check configuration:**
```python
# Test in Python console
from notification import send_email_notification
send_email_notification('test@example.com', 'Test', 1, 7.5)
```

**Common issues:**
- Wrong app password (must use App Password, not regular password)
- 2FA not enabled
- Less secure apps blocked

---

## 📱 Mobile Access

The app is fully responsive and works on:
- Desktop browsers
- Tablets
- Smartphones

Students can check progress on any device!

---

## 🔐 Security Considerations

1. **For Production:**
   - Add authentication (passwords/OAuth)
   - Use HTTPS (automatic with Streamlit Cloud)
   - Backup database regularly
   - Consider role-based access

2. **Data Privacy:**
   - Store minimal student information
   - Don't store sensitive data (SSN, etc.)
   - Comply with local data protection laws

3. **Access Control:**
   - Separate teacher/student credentials
   - Use environment variables for secrets
   - Never commit `.env` to git

---

## 📞 Support

For issues or questions:
1. Check this README
2. Review error messages
3. Check Streamlit documentation: https://docs.streamlit.io
4. Check Python documentation: https://docs.python.org

---

## 🎉 You're Ready!

Your Student Progress Tracker is now set up. Choose your deployment method and share the URL with your students!

**Recommended Path:**
1. Test locally first
2. Deploy to Streamlit Cloud
3. Share URL with students
4. (Optional) Set up email notifications
5. (Optional) Add authentication for production

Good luck with your teaching! 📚✨
