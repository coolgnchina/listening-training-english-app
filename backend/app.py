import os
import srt
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from datetime import timedelta
from functools import wraps

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
basedir = os.path.abspath(os.path.dirname(__file__))

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'uploads')
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a random secret key

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    difficulty = db.Column(db.String(50))
    description = db.Column(db.Text)
    original_audio_path = db.Column(db.String(200))
    srt_path = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creator = db.relationship('User', backref=db.backref('courses', lazy=True))
    sentences = db.relationship('Sentence', backref='course', lazy=True)

    def __repr__(self):
        return f'<Course {self.title}>'

class Sentence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    start_time = db.Column(db.String(50))
    end_time = db.Column(db.String(50))
    audio_segment_path = db.Column(db.String(200))

    def __repr__(self):
        return f'<Sentence {self.id} of Course {self.course_id}>'

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 400

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid username or password'}), 401

    token = jwt.encode(
        {
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        },
        app.config['SECRET_KEY'],
        algorithm='HS256'
    )

    return jsonify({'token': token})

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'message': 'Token is missing or invalid!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@app.route('/api/courses', methods=['POST'])
@token_required
def create_course(current_user):
    if 'audio_file' not in request.files:
        return jsonify({'message': 'No audio file part'}), 400
    audio_file = request.files['audio_file']
    if audio_file.filename == '':
        return jsonify({'message': 'No selected audio file'}), 400

    title = request.form.get('title')
    description = request.form.get('description')

    if not title:
        return jsonify({'message': 'Title is required'}), 400

    audio_filepath = None
    if audio_file:
        audio_filename = audio_file.filename
        audio_filepath = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
        audio_file.save(audio_filepath)

    subtitle_filepath = None
    if 'subtitle_file' in request.files:
        subtitle_file = request.files['subtitle_file']
        if subtitle_file.filename != '':
            subtitle_filename = subtitle_file.filename
            subtitle_filepath = os.path.join(app.config['UPLOAD_FOLDER'], subtitle_filename)
            subtitle_file.save(subtitle_filepath)

    new_course = Course(
        title=title,
        description=description,
        creator=current_user,
        original_audio_path=audio_filepath,
        srt_path=subtitle_filepath
    )
    db.session.add(new_course)
    db.session.commit()

    return jsonify({'message': 'Course created successfully', 'course_id': new_course.id}), 201


@app.route('/api/courses/all', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    return jsonify([{
        'id': course.id, 
        'title': course.title, 
        'description': course.description,
        'user_id': course.user_id
    } for course in courses])

@app.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    course = Course.query.get_or_404(course_id)
    return jsonify({
        'id': course.id,
        'title': course.title,
        'description': course.description,
        'audio_filename': os.path.basename(course.original_audio_path) if course.original_audio_path else None,
        'srt_filename': os.path.basename(course.srt_path) if course.srt_path else None
    })

@app.route('/api/courses/<int:course_id>', methods=['PUT'])
@token_required
def update_course(current_user, course_id):
    course = Course.query.get_or_404(course_id)

    if course.user_id != current_user.id:
        return jsonify({'message': 'Permission denied'}), 403

    course.title = request.form.get('title', course.title)
    course.description = request.form.get('description', course.description)

    if 'audio_file' in request.files:
        audio_file = request.files['audio_file']
        if audio_file.filename != '':
            if course.original_audio_path and os.path.exists(course.original_audio_path):
                os.remove(course.original_audio_path)
            audio_filename = audio_file.filename
            audio_filepath = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
            audio_file.save(audio_filepath)
            course.original_audio_path = audio_filepath

    if 'subtitle_file' in request.files:
        subtitle_file = request.files['subtitle_file']
        if subtitle_file.filename != '':
            if course.srt_path and os.path.exists(course.srt_path):
                os.remove(course.srt_path)
            subtitle_filename = subtitle_file.filename
            subtitle_filepath = os.path.join(app.config['UPLOAD_FOLDER'], subtitle_filename)
            subtitle_file.save(subtitle_filepath)
            course.srt_path = subtitle_filepath

    db.session.commit()
    return jsonify({'message': 'Course updated successfully', 'course_id': course.id})

@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
@token_required
def delete_course(current_user, course_id):
    course = Course.query.get_or_404(course_id)

    if course.user_id != current_user.id:
        return jsonify({'message': 'Permission denied'}), 403

    # Delete associated sentences first
    Sentence.query.filter_by(course_id=course_id).delete()

    # Optional: Delete associated files from the server
    if course.original_audio_path and os.path.exists(course.original_audio_path):
        os.remove(course.original_audio_path)
    if course.srt_path and os.path.exists(course.srt_path):
        os.remove(course.srt_path)

    db.session.delete(course)
    db.session.commit()

    return jsonify({'message': 'Course deleted successfully'}), 200

@app.route('/api/courses/<int:course_id>/sentences', methods=['GET'])
def get_course_sentences(course_id):
    course = Course.query.get_or_404(course_id)
    if not course.srt_path or not os.path.exists(course.srt_path):
        return jsonify({'message': 'SRT file not found'}), 404

    with open(course.srt_path, 'r', encoding='utf-8') as f:
        subtitle_content = f.read()

    subs = list(srt.parse(subtitle_content))
    sentences = []
    for sub in subs:
        sentences.append({
            'id': sub.index,
            'text': sub.content,
            'start_time': sub.start.total_seconds(),
            'end_time': sub.end.total_seconds()
        })

    return jsonify(sentences)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/')
def hello_world():
    return 'Hello, World!'

def seed_data():
    with app.app_context():
        if User.query.count() == 0:
            user = User(username='default_user')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()

        if Course.query.count() == 0:
            user = User.query.first()
            course1 = Course(title='基础英语听力', description='适合初学者的日常对话练习', creator=user)
            course2 = Course(title='商务英语', description='涵盖常见商务场景的听力材料', creator=user)
            db.session.add(course1)
            db.session.add(course2)
            db.session.commit()

import click
from flask.cli import with_appcontext

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    db.create_all()
    seed_data()
    click.echo('Initialized and seeded the database.')

app.cli.add_command(init_db_command)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)