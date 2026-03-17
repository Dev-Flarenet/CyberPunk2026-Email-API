import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# Allow CORS for the frontend domain (or all domains if specified)
CORS(app)

# Configuration from .env
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_EMAIL = os.getenv('SMTP_EMAIL')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

def send_confirmation_email(to_email, name, college, pass_link):
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        raise Exception("SMTP credentials are not configured on the server.")

    # Read the HTML template
    template_path = os.path.join(os.path.dirname(__file__), 'email_template.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Replace placeholders
    html_content = html_content.replace('{{NAME}}', name)
    html_content = html_content.replace('{{COLLEGE}}', college)
    html_content = html_content.replace('{{PASS_LINK}}', pass_link)

    # Set up the email message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "CyberPunk2026 - Registration Confirmed"
    msg['From'] = f"CyberPunk2026 <{SMTP_EMAIL}>"
    msg['To'] = to_email

    # Attach the HTML content
    part = MIMEText(html_content, 'html')
    msg.attach(part)

    # Send the email
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_EMAIL or '', SMTP_PASSWORD or '')
        server.send_message(msg)

@app.route('/send-confirmation', methods=['POST'])
def handle_send_confirmation():
    data = request.json
    if not data:
        return jsonify({"error": "No JSON payload provided"}), 400

    email = data.get('email')
    name = data.get('name')
    college = data.get('college')
    pass_link = data.get('passLink')

    if not all([email, name, college, pass_link]):
        return jsonify({"error": "Missing required fields: email, name, college, passLink"}), 400

    try:
        send_confirmation_email(email, name, college, pass_link)
        return jsonify({"success": True, "message": "Confirmation email sent successfully"}), 200
    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Default to port 5000 
    app.run(host='0.0.0.0', port=5000, debug=True)
