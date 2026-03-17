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

import resend

# Hardcoded configuration
# 1. Get your API key from https://resend.com (It's free!)
# 2. Recommended: Add RESEND_API_KEY to your Render/HuggingFace Environment Variables
RESEND_API_KEY = os.getenv('RESEND_API_KEY', 're_XXXXXXXXXXXXXXXXXXXXXX') 
resend.api_key = RESEND_API_KEY

def send_confirmation_email(to_email, name, college, pass_link):
    if not RESEND_API_KEY or RESEND_API_KEY.startswith('re_XXX'):
        raise Exception("Resend API Key is not configured correctly.")

    # Read the HTML template
    template_path = os.path.join(os.path.dirname(__file__), 'email_template.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Replace placeholders
    html_content = html_content.replace('{{NAME}}', name)
    html_content = html_content.replace('{{COLLEGE}}', college)
    html_content = html_content.replace('{{PASS_LINK}}', pass_link)

    # Send the email via Resend HTTP API (Not blocked by HF/Render)
    params = {
        "from": "CyberPunk2026 <onboarding@resend.dev>",
        "to": [to_email],
        "subject": "CyberPunk2026 - Registration Confirmed",
        "html": html_content,
    }

    resend.Emails.send(params)

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
        import traceback
        error_details = traceback.format_exc()
        print("====== EMAIL SEND ERROR ======")
        print(error_details)
        print("==============================")
        return jsonify({
            "error": "Failed to send email", 
            "details": str(e),
            "traceback": error_details
        }), 500

if __name__ == '__main__':
    # Hugging Face Spaces expose port 7860
    port = int(os.getenv('PORT', 7860))
    app.run(host='0.0.0.0', port=port, debug=False)
