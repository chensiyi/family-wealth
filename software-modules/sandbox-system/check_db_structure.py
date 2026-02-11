import sqlite3

# 连接到数据库
conn = sqlite3.connect('../data-collector/storage/family_wealth_professional.db')
cursor = conn.cursor()

# 获取所有表名
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print('现有表结构:')
for table in tables:
    print(f'- {table[0]}')

# 检查每个表的结构
for table_name in tables:
    print(f'\n表 {table_name[0]} 的结构:')
    cursor.execute(f"PRAGMA table_info({table_name[0]})")
    columns = cursor.fetchall()
    for col in columns:
        print(f'  {col[1]} ({col[2]})')

conn.close()