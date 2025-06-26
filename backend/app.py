import os
import srt
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import jwt
import datetime
from datetime import timedelta
from functools import wraps
import random
import string
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
basedir = os.path.abspath(os.path.dirname(__file__))

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'uploads')
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a random secret key
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 确保上传目录存在
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# 验证码存储（生产环境建议使用Redis）
captcha_store = {}



def validate_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_vip = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    hearts = db.Column(db.Integer, default=5)
    max_hearts = db.Column(db.Integer, default=5)
    last_heart_update = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # 新手保护期相关字段
    is_newbie = db.Column(db.Boolean, default=True)  # 是否为新手
    newbie_protection_count = db.Column(db.Integer, default=3)  # 新手保护次数
    # 连续答对相关字段
    consecutive_correct = db.Column(db.Integer, default=0)  # 连续答对次数
    # 每日重置相关字段
    last_daily_reset = db.Column(db.Date, default=datetime.date.today)
    # 额外心数（超出上限的储备心数）
    bonus_hearts = db.Column(db.Integer, default=0)

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

class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    
    # 创建复合唯一索引，确保每个用户对每个课程只有一条进度记录
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', name='unique_user_course'),)
    
    def __repr__(self):
        return f'<UserProgress User:{self.user_id} Course:{self.course_id} Completed:{self.completed}>'

class LevelCompletion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    level_index = db.Column(db.Integer, nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', 'level_index', name='_user_course_level_uc'),)

    def __repr__(self):
        return f'<LevelCompletion User:{self.user_id} Course:{self.course_id} Level:{self.level_index}>'

# 生成验证码图片
def generate_captcha():
    # 生成随机验证码文本
    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    
    # 创建图片
    width, height = 120, 40
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # 尝试使用系统字体，如果失败则使用默认字体
    try:
        font = ImageFont.truetype('arial.ttf', 20)
    except:
        font = ImageFont.load_default()
    
    # 添加干扰线
    for _ in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill='gray', width=1)
    
    # 绘制验证码文本
    text_width = draw.textlength(captcha_text, font=font)
    text_height = 20
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # 为每个字符添加随机颜色和位置偏移
    for i, char in enumerate(captcha_text):
        char_x = x + i * (text_width // len(captcha_text)) + random.randint(-3, 3)
        char_y = y + random.randint(-3, 3)
        color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
        draw.text((char_x, char_y), char, fill=color, font=font)
    
    # 添加噪点
    for _ in range(50):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.point((x, y), fill='gray')
    
    # 转换为base64
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    image_data = buffer.getvalue()
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    return captcha_text, f"data:image/png;base64,{image_base64}"

@app.route('/captcha', methods=['GET'])
def get_captcha():
    captcha_text, captcha_image = generate_captcha()
    captcha_id = str(uuid.uuid4())
    
    # 存储验证码（5分钟过期）
    captcha_store[captcha_id] = {
        'text': captcha_text.lower(),
        'expires': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    }
    
    return jsonify({
        'id': captcha_id,
        'image': captcha_image
    })

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    captcha_id = data.get('captcha_id')
    captcha_text = data.get('captcha_text')

    # 验证验证码
    captcha_info = captcha_store.get(captcha_id)
    if not captcha_info or captcha_info['text'] != captcha_text.lower():
        return jsonify({'message': '验证码错误'}), 400

    if captcha_info['expires'] < datetime.datetime.utcnow():
        del captcha_store[captcha_id]
        return jsonify({'message': '验证码已过期'}), 400

    del captcha_store[captcha_id]  # 验证后删除

    if not all([username, password]):
        return jsonify({'message': '缺少必填字段'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': '用户名已存在'}), 409



    new_user = User(username=username, email=f'{username}@example.com') # 使用一个虚拟邮箱
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': '注册成功'}), 201





@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        token = jwt.encode({
            'user_id': user.id,
            'username': user.username,
            'is_vip': user.is_vip,
            'is_admin': user.is_admin,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token, 'is_vip': user.is_vip, 'is_admin': user.is_admin}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

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
    # 检查用户是否为VIP或管理员
    if not current_user.is_vip and not current_user.is_admin:
        return jsonify({'message': '只有VIP用户或管理员才能创建课程'}), 403
    
    if 'audio_file' not in request.files:
        return jsonify({'message': 'No audio file part'}), 400
    audio_file = request.files['audio_file']
    if audio_file.filename == '':
        return jsonify({'message': 'No selected audio file'}), 400

    title = request.form.get('title')
    description = request.form.get('description')
    difficulty = request.form.get('difficulty', 'normal')  # 默认为普通难度

    if not title:
        return jsonify({'message': 'Title is required'}), 400
    
    # 验证难度值
    if difficulty not in ['easy', 'normal', 'hard']:
        return jsonify({'message': 'Invalid difficulty level'}), 400

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
        difficulty=difficulty,
        creator=current_user,
        original_audio_path=audio_filepath,
        srt_path=subtitle_filepath
    )
    db.session.add(new_course)
    db.session.commit()
    
    # 解析SRT文件并创建句子记录
    if subtitle_filepath and os.path.exists(subtitle_filepath):
        try:
            with open(subtitle_filepath, 'r', encoding='utf-8') as f:
                subtitle_content = f.read()
            
            subs = list(srt.parse(subtitle_content))
            for sub in subs:
                sentence = Sentence(
                    course_id=new_course.id,
                    text=sub.content,
                    start_time=str(sub.start.total_seconds()),
                    end_time=str(sub.end.total_seconds())
                )
                db.session.add(sentence)
            
            db.session.commit()
        except Exception as e:
            print(f"Error parsing SRT file: {e}")

    return jsonify({'message': 'Course created successfully', 'course_id': new_course.id}), 201


@app.route('/api/courses/all', methods=['GET'])
def get_courses():
    # 获取当前用户ID（如果已登录）
    token = request.headers.get('Authorization')
    current_user_id = None
    if token and token.startswith('Bearer '):
        try:
            token = token.split(' ')[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
        except:
            pass
    
    courses = Course.query.all()
    result = []
    
    for course in courses:
        course_data = {
            'id': course.id, 
            'title': course.title, 
            'description': course.description,
            'difficulty': course.difficulty,
            'user_id': course.user_id,
            'completed': False
        }
        
        # 如果用户已登录，检查学习进度
        if current_user_id:
            progress = UserProgress.query.filter_by(
                user_id=current_user_id, 
                course_id=course.id
            ).first()
            if progress:
                course_data['completed'] = progress.completed
        
        result.append(course_data)
    
    return jsonify(result)

@app.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    course = Course.query.get_or_404(course_id)
    return jsonify({
        'id': course.id,
        'title': course.title,
        'description': course.description,
        'difficulty': course.difficulty,
        'audio_filename': os.path.basename(course.original_audio_path) if course.original_audio_path else None,
        'srt_filename': os.path.basename(course.srt_path) if course.srt_path else None
    })

@app.route('/api/courses/<int:course_id>', methods=['PUT'])
@token_required
def update_course(current_user, course_id):
    course = Course.query.get_or_404(course_id)

    if not current_user.is_admin and course.user_id != current_user.id:
        return jsonify({'message': 'Permission denied'}), 403

    course.title = request.form.get('title', course.title)
    course.description = request.form.get('description', course.description)







@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
@token_required
def delete_course(current_user, course_id):
    try:
        course = Course.query.get_or_404(course_id)

        if not current_user.is_admin and course.user_id != current_user.id:
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
    except Exception as e:
        return jsonify({'message': f'Error deleting course: {str(e)}'}), 500


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
    if User.query.count() == 0:
        user = User(username='default_user', email='admin@example.com')
        user.set_password('password')
        user.is_vip = True  # 设置为VIP
        user.is_admin = True  # 设置为管理员
        db.session.add(user)
        db.session.commit()

    if Course.query.count() == 0:
        user = User.query.first()
        # 获取当前文件所在目录的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sample_srt_path = os.path.join(current_dir, 'sample.srt')
        
        course1 = Course(title='基础英语听力', description='适合初学者的日常对话练习', creator=user, difficulty='easy', srt_path=sample_srt_path)
        course2 = Course(title='商务英语', description='涵盖常见商务场景的听力材料', creator=user, difficulty='normal', srt_path=sample_srt_path)
        db.session.add(course1)
        db.session.add(course2)
        db.session.commit()
        
        # 为示例课程创建句子记录
        for course in [course1, course2]:
            if course.srt_path and os.path.exists(course.srt_path):
                try:
                    with open(course.srt_path, 'r', encoding='utf-8') as f:
                        subtitle_content = f.read()
                    
                    subs = list(srt.parse(subtitle_content))
                    for sub in subs:
                        sentence = Sentence(
                            course_id=course.id,
                            text=sub.content,
                            start_time=str(sub.start.total_seconds()),
                            end_time=str(sub.end.total_seconds())
                        )
                        db.session.add(sentence)
                    
                    db.session.commit()
                except Exception as e:
                    print(f"Error parsing SRT file for course {course.id}: {e}")

import click
from flask.cli import with_appcontext

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    db.drop_all()
    db.create_all()
    seed_data()
    click.echo('Initialized and seeded the database.')

app.cli.add_command(init_db_command)

# User Management APIs
@app.route('/api/users', methods=['GET'])
@token_required
def get_all_users(current_user):
    """获取所有用户列表（仅管理员可访问）"""
    users = User.query.all()
    users_data = []
    for user in users:
        user_data = {
            'id': user.id,
            'username': user.username,
            'created_courses': len(user.courses),
            'is_admin': user.id == 1  # 假设第一个用户是管理员
        }
        users_data.append(user_data)
    return jsonify(users_data), 200

@app.route('/api/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    """获取单个用户详情"""
    user = User.query.get_or_404(user_id)
    user_data = {
        'id': user.id,
        'username': user.username,
        'created_courses': len(user.courses),
        'courses': [{'id': course.id, 'title': course.title} for course in user.courses],
        'is_admin': user.id == 1
    }
    return jsonify(user_data), 200

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(current_user, user_id):
    """更新用户信息（仅管理员可操作）"""
    if not current_user.is_admin:  # 只有管理员可以更新用户
        return jsonify({'message': 'Permission denied'}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'username' in data:
        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'message': 'Username already exists'}), 400
        user.username = data['username']
    
    if 'password' in data and data['password']:
        user.set_password(data['password'])
    
    if 'is_vip' in data:
        user.is_vip = data['is_vip']
    
    db.session.commit()
    return jsonify({'message': 'User updated successfully'}), 200

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, user_id):
    """删除用户（仅管理员可操作，不能删除自己）"""
    if not current_user.is_admin:  # 只有管理员可以删除用户
        return jsonify({'message': 'Permission denied'}), 403
    
    target_user = User.query.get_or_404(user_id)
    if target_user.is_admin:  # 不能删除管理员账户
        return jsonify({'message': 'Cannot delete admin account'}), 400
    
    if user_id == current_user.id:  # 不能删除自己
        return jsonify({'message': 'Cannot delete your own account'}), 400
    
    user = User.query.get_or_404(user_id)
    
    # 删除用户创建的所有课程及相关数据
    for course in user.courses:
        # 删除课程相关的句子
        Sentence.query.filter_by(course_id=course.id).delete()
        
        # 删除音频文件
        if course.original_audio_path and os.path.exists(course.original_audio_path):
            os.remove(course.original_audio_path)
        if course.srt_path and os.path.exists(course.srt_path):
            os.remove(course.srt_path)
        
        # 删除句子音频文件
        sentences = Sentence.query.filter_by(course_id=course.id).all()
        for sentence in sentences:
            if sentence.audio_segment_path and os.path.exists(sentence.audio_segment_path):
                os.remove(sentence.audio_segment_path)
    
    # 删除用户的所有课程
    Course.query.filter_by(user_id=user_id).delete()
    
    # 删除用户
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted successfully'}), 200

@app.route('/api/users/stats', methods=['GET'])
@token_required
def get_user_stats(current_user):
    """获取用户统计信息"""
    total_users = User.query.count()
    total_courses = Course.query.count()
    # 统计用户完成的关卡总数
    total_completed_levels = LevelCompletion.query.count()
    
    stats = {
        'total_users': total_users,
        'total_courses': total_courses,
        'total_sentences': total_completed_levels,
        'average_courses_per_user': round(total_courses / total_users, 2) if total_users > 0 else 0
    }
    
    return jsonify(stats), 200

@app.route('/api/courses/<int:course_id>/levels/completed', methods=['GET'])
@token_required
def get_completed_levels(current_user, course_id):
    completions = LevelCompletion.query.filter_by(user_id=current_user.id, course_id=course_id).all()
    completed_levels = [comp.level_index for comp in completions]
    return jsonify(completed_levels)

@app.route('/api/courses/<int:course_id>/levels/<int:level_index>/complete', methods=['POST'])
@token_required
def mark_level_complete(current_user, course_id, level_index):
    # 检查是否已完成
    existing_completion = LevelCompletion.query.filter_by(
        user_id=current_user.id,
        course_id=course_id,
        level_index=level_index
    ).first()

    if existing_completion:
        return jsonify({'message': 'Level already completed'}), 200

    new_completion = LevelCompletion(
        user_id=current_user.id,
        course_id=course_id,
        level_index=level_index
    )
    db.session.add(new_completion)
    db.session.commit()

    return jsonify({'message': 'Level marked as complete'}), 201

@app.route('/api/courses/<int:course_id>/complete', methods=['POST'])
@token_required
def mark_course_complete(current_user, course_id):
    """标记课程为已完成"""
    # 检查课程是否存在
    course = Course.query.get_or_404(course_id)
    
    # 查找或创建用户进度记录
    progress = UserProgress.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()
    
    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            course_id=course_id,
            completed=True,
            completed_at=datetime.datetime.now()
        )
        db.session.add(progress)
    else:
        progress.completed = True
        progress.completed_at = datetime.datetime.now()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Course marked as completed',
        'completed': True,
        'completed_at': progress.completed_at.isoformat()
    }), 200

@app.route('/api/users/progress', methods=['GET'])
@token_required
def get_user_progress(current_user):
    """获取用户的学习进度"""
    progress_records = UserProgress.query.filter_by(user_id=current_user.id).all()
    
    progress_data = []
    for progress in progress_records:
        course = Course.query.get(progress.course_id)
        if course:
            progress_data.append({
                'course_id': progress.course_id,
                'course_title': course.title,
                'completed': progress.completed,
                'completed_at': progress.completed_at.isoformat() if progress.completed_at else None
            })
    
    return jsonify(progress_data), 200

@app.route('/api/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    """用户修改自己的密码"""
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'message': 'Current password and new password are required'}), 400
    
    # 验证当前密码
    if not current_user.check_password(current_password):
        return jsonify({'message': 'Current password is incorrect'}), 400
    
    # 验证新密码长度
    if len(new_password) < 6:
        return jsonify({'message': 'New password must be at least 6 characters long'}), 400
    
    # 更新密码
    current_user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'}), 200

@app.route('/api/user/hearts', methods=['GET'])
@token_required
def get_user_hearts(current_user):
    now = datetime.datetime.utcnow()
    today = datetime.date.today()
    
    # 检查是否需要每日重置
    if current_user.last_daily_reset < today:
        current_user.hearts = current_user.max_hearts
        current_user.last_daily_reset = today
        current_user.last_heart_update = now
        db.session.commit()
    else:
        # 计算离线期间应该恢复的心数（每小时恢复1颗心）
        time_diff_seconds = (now - current_user.last_heart_update).total_seconds()
        hearts_to_recover = int(time_diff_seconds // (60 * 60))

        if hearts_to_recover > 0 and current_user.hearts < current_user.max_hearts:
            current_user.hearts = min(current_user.max_hearts, current_user.hearts + hearts_to_recover)
            current_user.last_heart_update = now
            db.session.commit()
    
    # 计算下次恢复时间
    next_recovery_time = None
    if current_user.hearts < current_user.max_hearts:
        next_recovery_time = (current_user.last_heart_update + datetime.timedelta(hours=1)).isoformat()

    return jsonify({
        'current_hearts': current_user.hearts,
        'max_hearts': current_user.max_hearts,
        'bonus_hearts': current_user.bonus_hearts,
        'total_hearts': current_user.hearts + current_user.bonus_hearts,
        'last_heart_update': current_user.last_heart_update.isoformat(),
        'next_recovery_time': next_recovery_time,
        'is_newbie': current_user.is_newbie,
        'newbie_protection_count': current_user.newbie_protection_count,
        'consecutive_correct': current_user.consecutive_correct
    })

@app.route('/api/user/hearts/lose', methods=['POST'])
@token_required
def lose_user_heart(current_user):
    data = request.get_json() or {}
    difficulty = data.get('difficulty', 'normal')  # easy, normal, hard
    is_practice_mode = data.get('is_practice_mode', False)
    action_type = data.get('action_type', 'wrong_answer')  # wrong_answer, view_original
    
    # 查看原文不重置连续答对次数
    if action_type != 'view_original':
        current_user.consecutive_correct = 0
    
    # 新手保护期逻辑
    if current_user.is_newbie and current_user.newbie_protection_count > 0:
        current_user.newbie_protection_count -= 1
        if current_user.newbie_protection_count <= 0:
            current_user.is_newbie = False
        db.session.commit()
        return jsonify({
            'success': True, 
            'hearts_lost': 0,
            'remaining_hearts': current_user.hearts + current_user.bonus_hearts,
            'message': '新手保护期，本次错误不扣心',
            'newbie_protection_remaining': current_user.newbie_protection_count
        })
    
    # 练习模式不扣心
    if is_practice_mode:
        db.session.commit()
        return jsonify({
            'success': True, 
            'hearts_lost': 0,
            'remaining_hearts': current_user.hearts + current_user.bonus_hearts,
            'message': '练习模式，不扣除生命值'
        })
    
    # 根据动作类型和难度决定扣心数量
    if action_type == 'view_original':
        hearts_to_lose = 1  # 查看原文固定扣1心
    else:
        # 答题错误统一扣1心（不再根据难度区分）
        hearts_to_lose = 1  # 做错一题扣1心
    
    # 处理扣心逻辑，支持小数扣心
    if hearts_to_lose == 0:
        db.session.commit()
        return jsonify({
            'success': True, 
            'hearts_lost': 0,
            'remaining_hearts': current_user.hearts + current_user.bonus_hearts,
            'message': '无需扣除生命值'
        })
    
    # 扣除生命值（优先扣除额外心数）
    total_hearts = current_user.hearts + current_user.bonus_hearts
    if total_hearts > 0:
        if current_user.bonus_hearts > 0:
            current_user.bonus_hearts -= hearts_to_lose
            if current_user.bonus_hearts < 0:
                current_user.hearts += current_user.bonus_hearts
                current_user.bonus_hearts = 0
        else:
            current_user.hearts -= hearts_to_lose
        
        current_user.last_heart_update = datetime.datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'hearts_lost': hearts_to_lose,
            'remaining_hearts': current_user.hearts + current_user.bonus_hearts,
            'current_hearts': current_user.hearts,
            'bonus_hearts': current_user.bonus_hearts
        })
    
    return jsonify({'success': False, 'message': 'No hearts left'}), 400

@app.route('/api/user/hearts/reward', methods=['POST'])
@token_required
def reward_user_heart(current_user):
    data = request.get_json() or {}
    reward_type = data.get('type', 'correct_answer')  # correct_answer, achievement, perfect_course
    
    if reward_type == 'correct_answer':
        # 连续答对奖励
        current_user.consecutive_correct += 1
        
        hearts_rewarded = 0
        message = ''
        
        # 每连续答对10题奖励1颗心
        if current_user.consecutive_correct % 10 == 0:
            if current_user.hearts < current_user.max_hearts:
                current_user.hearts += 1
                hearts_rewarded = 1
                message = f'连续答对{current_user.consecutive_correct}题！奖励1颗生命值'
            else:
                current_user.bonus_hearts += 1
                hearts_rewarded = 1
                message = f'连续答对{current_user.consecutive_correct}题！奖励1颗额外生命值'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'hearts_rewarded': hearts_rewarded,
            'consecutive_correct': current_user.consecutive_correct,
            'remaining_hearts': current_user.hearts + current_user.bonus_hearts,
            'current_hearts': current_user.hearts,
            'bonus_hearts': current_user.bonus_hearts,
            'message': message
        })
    
    elif reward_type == 'perfect_course':
        # 完美通关课程奖励
        reward_hearts = 2
        current_user.bonus_hearts += reward_hearts
        db.session.commit()
        
        return jsonify({
            'success': True,
            'hearts_rewarded': reward_hearts,
            'remaining_hearts': current_user.hearts + current_user.bonus_hearts,
            'current_hearts': current_user.hearts,
            'bonus_hearts': current_user.bonus_hearts,
            'message': f'完美通关！奖励{reward_hearts}颗额外生命值'
        })
    
    return jsonify({'success': False, 'message': 'Invalid reward type'}), 400


@app.route('/api/hearts/consecutive', methods=['POST'])
@token_required
def update_consecutive_correct(current_user):
    """更新连续答对计数"""
    try:
        data = request.get_json()
        increment = data.get('increment', True)
        
        if increment:
            current_user.consecutive_correct += 1
        else:
            current_user.consecutive_correct = 0
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'consecutive_correct': current_user.consecutive_correct
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # 检查是否需要创建默认用户
        if not User.query.first():
            seed_data()
    app.run(debug=True, host='0.0.0.0', port=5000)