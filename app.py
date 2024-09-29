from flask import Flask, request
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Flask-Mail configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_HOST')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USER')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True  # Use TLS for encryption
app.config['MAIL_USE_SSL'] = False  # Don't use SSL, because we are using TLS
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_FROM_ADDRESS')

# Initialize Flask-Mail
mail = Mail(app)

@app.route('/send-test-email', methods=['GET'])
def send_test_email():
    try:
        # Create a message
        msg = Message(subject='Test Email from Flask',
                      recipients=['recipient@example.com'],  # Replace with the recipient's email address
                      body='This is a test email sent from Flask using SMTP on Liara.',
                      extra_headers = {"x-liara-tag": "test_tag"})

        # Send the email
        mail.send(msg)
        return 'Test email sent successfully!', 200

    except Exception as e:
        return f'Failed to send email. Error: {str(e)}', 500

if __name__ == '__main__':
    app.run(debug=True)
