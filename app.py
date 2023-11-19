from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os
from flask_mail import Mail, Message

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')
app.config['UPLOAD_FOLDER'] = 'uploads'

# MySQL configuration
app.config['MYSQL_HOST']     = os.getenv('DB_HOST', 'localhost')
app.config['MYSQL_USER']     = os.getenv('DB_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD', '')
app.config['MYSQL_DB']       = os.getenv('DB_NAME', 'db')
app.config['MYSQL_PORT']     = int(os.getenv('DB_PORT', 3306)) 
mysql = MySQL(app)

# Configuring email settings
app.config['MAIL_SERVER']         = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT']           = os.getenv('MAIL_PORT', 587)
app.config['MAIL_USE_TLS']        = os.getenv('MAIL_USE_TLS', True)
app.config['MAIL_USE_SSL']        = False
app.config['MAIL_USERNAME']       = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD']       = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_SENDER')
mail = Mail(app)

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    user_query = """CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(120) NOT NULL);"""
    post_query = """CREATE TABLE IF NOT EXISTS posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    user_id INT,
    image_path  VARCHAR(255) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);"""
    
    cur.execute(user_query)
    cur.execute(post_query)
    mysql.connection.commit()
    cur.close()

    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        show_post_query = """SELECT * FROM posts ORDER BY posts.created_at DESC"""
        cur = mysql.connection.cursor()
        cur.execute(show_post_query)
        posts = cur.fetchall()
        cur.close()
        return render_template('dashboard.html', posts=posts)
    else:
        return redirect(url_for('login'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()

        if user:
            # Set the user's ID in the session
            session['user_id'] = user[0]
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check password match
        if password != confirm_password:
            return render_template('register.html', error="Passwords do not match")

        # Add user to the database using Flask-MySQLdb
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
        mysql.connection.commit()
        cur.close()

        # Send confirmation email to the user
        send_confirmation_email(email)

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/profile')
def profile():
    if 'user_id' in session:
        user_id = session['user_id']

        # Query user information from the database
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        cur.close()
        print(user)
        if user:
            # Pass user information to the profile template
            return render_template('profile.html', user=user)
        else:
            return render_template('profile.html', error='User not found')
    else:
        return redirect(url_for('login'))

@app.route('/compose', methods=['GET', 'POST'])
def compose():
    if 'user_id' in session:
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            user_id = session['user_id']

             # Handle image upload
            if 'image' in request.files:
                image = request.files['image']
                if image.filename != '':
                    image.save(os.path.join('uploads', image.filename))

            # Insert post into the database
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO posts (title, content, user_id, image_path) VALUES (%s, %s, %s, %s)",
                        (title, content, user_id, image.filename if 'image' in request.files else None))
            mysql.connection.commit()
            cur.close()

            return redirect(url_for('dashboard'))

        return render_template('compose.html')
    else:
        return redirect(url_for('login'))
    
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/logout')
def logout():
    # Check if the user is logged in
    if 'user_id' in session:
        # Clear the session
        session.pop('user_id', None)
    
    return redirect(url_for('login'))

def send_confirmation_email(email):
    subject = 'Welcome to Liara Blog'
    body = 'Thank you for registering. If you have any ideas, please reply to this email.\n\n'
    msg = Message(subject, recipients=[email], body=body)
    mail.send(msg)

if __name__ == '__main__':
    app.run(debug=True)
