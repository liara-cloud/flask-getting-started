from flask import Flask
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

@app.route("/")
def index():
  msg = Message(
    'Mailing with Flask-Mail',
    sender =  ("Info", 'info@alinajmabadi.ir'),
    recipients = ['alinajmabadizadeh2002@gmail.com'])

  msg.body = "this is from Flask app, lmk if it works"

  mail.send(msg)

  return "Message sent!"

if __name__ == '__main__':
  app.run(debug=True)