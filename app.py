from flask import Flask, request
from flask_mail import Mail, Message
import os

# # uncomment in development environment
# from dotenv import load_dotenv
# load_dotenv()

app = Flask(__name__)

app.config['MAIL_SERVER'] = os.getenv('MAIL_HOST')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USER')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True 
app.config['MAIL_USE_SSL'] = False 
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_FROM_ADDRESS')

cc_mail = ['alinajmabadizadeh2002@gmail.com', 'alinajmabadi@liara.ir']
# bcc_mail = ['alinajmabadizadeh2002@gmail.com', 'alinajmabadi@liara.ir']

mail = Mail(app)

@app.route('/send-test-email', methods=['GET'])
def send_test_email():
    try:
        msg = Message(subject='Test Email from Flask',
                      recipients=['some@looms.ir'],  
                      body='This is a test email sent from Flask using SMTP on Liara.',
                      cc=cc_mail,
                    #   bcc=bcc_mail,
                      extra_headers = {"x-liara-tag": "test_tag"})

        mail.send(msg)
        return 'Test email sent successfully!', 200

    except Exception as e:
        return f'Failed to send email. Error: {str(e)}', 500

if __name__ == '__main__':
    app.run(debug=True)
