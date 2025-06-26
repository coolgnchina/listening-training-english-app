from app import app, db, User

with app.app_context():
    # 查找default_user
    default_user = User.query.filter_by(username='default_user').first()
    
    if default_user:
        print('Found default_user, resetting password...')
        # 重置密码为 'password'
        default_user.set_password('password')
        # 确保用户状态正确
        default_user.is_active = True
        default_user.is_vip = True
        default_user.is_admin = True
        
        db.session.commit()
        print('default_user password reset successfully!')
        print('Username: default_user')
        print('Password: password')
        print('Status: Active, VIP, Admin')
    else:
        print('default_user not found!')
        # 创建新的default_user
        print('Creating new default_user...')
        new_user = User(username='default_user', email='admin@example.com')
        new_user.set_password('password')
        new_user.is_vip = True
        new_user.is_admin = True
        new_user.is_active = True
        
        db.session.add(new_user)
        db.session.commit()
        print('New default_user created successfully!')
        print('Username: default_user')
        print('Password: password')