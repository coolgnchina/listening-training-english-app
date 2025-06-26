from app import app, db, Sentence

with app.app_context():
    total_sentences = Sentence.query.count()
    print(f'Total sentences in DB: {total_sentences}')
    
    if total_sentences > 0:
        sentences = Sentence.query.limit(3).all()
        print('Sample sentences:')
        for s in sentences:
            print(f'- Course {s.course_id}: {s.text[:50]}...')
    else:
        print('No sentences found in database')