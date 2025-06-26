import sqlite3

conn = sqlite3.connect('app.db')
cursor = conn.cursor()

# 首先查看所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print('数据库中的表:')
for table in tables:
    print(f'- {table[0]}')

# 尝试查询课程数据
try:
    cursor.execute('SELECT id, title, difficulty FROM course')
    print('\n课程数据:')
    for row in cursor.fetchall():
        print(f'ID: {row[0]}, 标题: {row[1]}, 难度: {row[2]}')
except Exception as e:
    print(f'\n查询课程数据时出错: {e}')

conn.close()