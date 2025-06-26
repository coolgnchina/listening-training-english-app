from app import app, db, User, Course, seed_data

from app import app, db, User, Course, seed_data

with app.app_context():
    db.create_all()
    seed_data()
    print('Database created and seeded successfully')
    print(f'Total users: {User.query.count()}')
    print(f'Total courses: {Course.query.count()}')