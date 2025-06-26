from app import app, db, User

with app.app_context():
    print('Checking database...')
    try:
        users = User.query.all()
        print(f'Found {len(users)} users:')
        for user in users:
            print(f'- Username: {user.username}')
            print(f'  Email: {user.email}')
            print(f'  Is Active: {user.is_active}')
            print(f'  Is VIP: {user.is_vip}')
            print(f'  Is Admin: {user.is_admin}')
            print(f'  Has Password: {"Yes" if user.password_hash else "No"}')
            print(f'  Hearts: {user.hearts}/{user.max_hearts}')
            print('---')
        if len(users) == 0:
            print('No users found in database!')
    except Exception as e:
        print(f'Error querying users: {e}')