from app import app, db, User

with app.app_context():
    # 检查coolgn用户是否已存在
    existing_user = User.query.filter_by(username='coolgn').first()
    if existing_user:
        print('User coolgn already exists!')
        # 更新现有用户为VIP和管理员
        existing_user.is_vip = True
        existing_user.is_admin = True
        existing_user.email = 'coolgn@example.com'
        db.session.commit()
        print('User coolgn updated to VIP and Admin!')
    else:
        # 创建coolgn用户
        new_user = User(username='coolgn', email='coolgn@example.com')
        new_user.set_password('password')  # 设置默认密码
        new_user.is_vip = True  # 设置为VIP
        new_user.is_admin = True  # 设置为管理员
        db.session.add(new_user)
        db.session.commit()
        print('User coolgn created successfully as VIP and Admin!')
        print('Username: coolgn')
        print('Password: password')
    
    # 显示所有用户
    users = User.query.all()
    print(f'\nTotal users in database: {len(users)}')
    for user in users:
        print(f'- {user.username}')