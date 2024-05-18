from datetime import datetime
from flask import jsonify, request, render_template, redirect, session, url_for, Blueprint, flash, send_from_directory
from flask_login import login_user, login_required, logout_user
import os
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Question, User

main = Blueprint("main", __name__)

# Temporary data storage
questions = []
answers = []

# Configure upload folder and allowed extensions
PROJ='intelliShare'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
# Check if the uploaded file is allowed
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/')
def home():
    posts = get_posts_from_database(0, 2)
    return render_template('index.html', posts=posts)

class Post:
    def __init__(self, question_id, question, username, timestamp, content):
        self.question_id = question_id
        self.question = question
        self.username = username
        self.timestamp = timestamp
        self.content = content

def get_posts_from_database(start, limit):
    all_posts = [
        Post(1, 'What is the smartest animal?', 'John', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), 'Pantabangan town was submerged in the 1970s to build a reservoir...'),
        Post(2, 'What is the smartest animal?', 'John', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), 'Pantabangan town was submerged in the 1970s to build a reservoir...'),
        Post(3, 'What is the smartest animal?', 'John', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), 'Pantabangan town was submerged in the 1970s to build a reservoir...'),
        Post(4, 'What is the smartest animal?', 'John', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), 'Pantabangan town was submerged in the 1970s to build a reservoir...')
    ]
    return all_posts[start:start+limit]

@main.route('/login', methods=['GET', 'POST'])
def login():
    #[TODO]
    return "<h2>login</h2>"

@main.route('/register', methods=['GET', 'POST'])
def register():
    #[TODO]
    return "<h2>Register</h2>"

@main.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    session.pop('username', None)
    return redirect(url_for("main.home"))

# create new question
@main.route('/addQuestion_v1', methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        title = request.form['title']
        subtitle = request.form['subtitle']
        question_text = request.form['question']
        username = "Andrianto Hadi"  # Should be dynamically set based on the logged-in user
        submission_time = datetime.now().strftime('%d %b %Y %H:%M:%S')
        
        filename = None
        if 'cover' in request.files:
            file = request.files['cover']
            if file and allowed_file(file.filename):
                filename = file.filename
                filepath = os.path.join(PROJ, UPLOAD_FOLDER, filename)
                file.save(filepath)

        question_id = len(questions) + 1
        questions.append({
            'id': question_id,
            'title': title,
            'subtitle': subtitle,
            'question': question_text,
            'cover': filename,
            'username': username,
            'submission_time': submission_time
        })
        
        return redirect(url_for('main.question_details', question_id=question_id))
    
    return render_template('addQuestion_v1.html')

@main.route('/addQuestion_v1.html')
def add():
    return render_template('addQuestion_v1.html')

@main.route('/questionDetails_v1.html')
def details():
    return render_template('questionDetails_v1.html')

# Route to handle answer submissions
@main.route('/questionDetails_v1.html', methods=['GET','POST'])
def answer():
    question_id = int(request.form['question_id'])
    answer_text = request.form['answer']
    answer_time = datetime.now().strftime('%d %b %Y %H:%M:%S')
    answer = {
        'question_id': question_id,
        'text': answer_text,
        'username': "User",  # This should be dynamically set based on the current user in a real app
        'answer_time': answer_time
    }

    # Handle file upload
    if 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(PROJ, UPLOAD_FOLDER, filename)
            file.save(filepath)

            answer['image'] = filename

    answers.append(answer)
    return redirect(url_for('main.question_details', question_id=question_id))

@main.route('/profile', methods=['GET', 'POST'])
def profile():
    #[TODO]
    return "<h2>profile</h2>"

# Route to display question details and answers
@main.route('/questionDetails_v1.html/<int:question_id>')
def question_details(question_id):
    question = next((q for q in questions if q['id'] == question_id), None)
    if not question:
        return "Question not found", 404
    question_answers = [a for a in answers if a['question_id'] == question_id]
    return render_template('questionDetails_v1.html', question=question, answers=question_answers)

@main.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('query')
    results = []

    if query:  # only search if a query is provided
        all_posts = get_posts_from_database(0, 100)  # get all posts
        results = [post for post in all_posts if query in post.question]  # search in post question

        if not results:
            flash('No results found!')

    return render_template('search.html', results=results)



    # Serve uploaded files
@main.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
