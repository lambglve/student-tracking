import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def send_email_notification(student_email, student_name, session_number, band_score):
    """
    Send email notification to student when a new grade is posted
    
    NOTE: To enable email notifications, set up the following environment variables:
    - SMTP_SERVER (e.g., smtp.gmail.com)
    - SMTP_PORT (e.g., 587)
    - SMTP_USERNAME (your email)
    - SMTP_PASSWORD (your app password)
    - SENDER_EMAIL (sender email address)
    """
    
    # Check if email is configured
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = os.getenv('SMTP_PORT')
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    sender_email = os.getenv('SENDER_EMAIL')
    
    # If email is not configured, just log it
    if not all([smtp_server, smtp_port, smtp_username, smtp_password, sender_email]):
        print(f"📧 Email notification simulated for {student_name}")
        print(f"   Session {session_number} | Band Score: {band_score}")
        return True
    
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = f"New Grade Posted - Session {session_number}"
        message["From"] = sender_email
        message["To"] = student_email
        
        # Create HTML content
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #f8f9fa; padding: 30px; border-radius: 10px;">
              <h2 style="color: #1f77b4; text-align: center;">🎓 New Grade Available!</h2>
              
              <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #333;">Hello {student_name},</h3>
                <p style="font-size: 16px; line-height: 1.6;">
                  Your teacher has posted a new grade for <strong>Session {session_number}</strong>.
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                  <div style="background-color: #d4edda; padding: 20px; border-radius: 8px; display: inline-block;">
                    <p style="margin: 0; font-size: 14px; color: #155724;">Overall Band Score</p>
                    <p style="margin: 10px 0 0 0; font-size: 48px; font-weight: bold; color: #28a745;">
                      {band_score}
                    </p>
                  </div>
                </div>
                
                <p style="font-size: 16px; line-height: 1.6;">
                  Log in to your Student Progress Dashboard to view detailed feedback and your progress roadmap.
                </p>
              </div>
              
              <div style="text-align: center; margin-top: 20px;">
                <p style="font-size: 14px; color: #6c757d;">
                  Keep up the great work! 🌟
                </p>
              </div>
            </div>
          </body>
        </html>
        """
        
        # Create plain text version
        text = f"""
        New Grade Available!
        
        Hello {student_name},
        
        Your teacher has posted a new grade for Session {session_number}.
        
        Overall Band Score: {band_score}
        
        Log in to your Student Progress Dashboard to view detailed feedback and your progress roadmap.
        
        Keep up the great work!
        """
        
        # Attach both versions
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)
        
        # Send email
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, student_email, message.as_string())
        
        print(f"✅ Email sent to {student_email}")
        return True
        
    except Exception as e:
        print(f"❌ Email error: {e}")
        # Don't fail the whole operation if email fails
        return False

def send_browser_notification(student_name, session_number, band_score):
    """
    Alternative notification method using browser toast
    This is a placeholder - actual implementation would use JavaScript
    in the Streamlit frontend
    """
    notification_data = {
        'student_name': student_name,
        'session_number': session_number,
        'band_score': band_score,
        'message': f"New grade posted for Session {session_number}: {band_score}"
    }
    
    return notification_data
