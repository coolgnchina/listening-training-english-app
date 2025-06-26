#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本 - 添加生命值系统新字段
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """迁移数据库，添加新字段"""
    db_path = os.path.join(os.path.dirname(__file__), 'app.db')
    
    # 如果数据库不存在，直接返回
    if not os.path.exists(db_path):
        print("数据库文件不存在，将在启动时自动创建")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查是否已经有新字段
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # 需要添加的新字段
        new_fields = {
            'is_newbie': 'INTEGER DEFAULT 1',
            'newbie_protection_count': 'INTEGER DEFAULT 0', 
            'consecutive_correct': 'INTEGER DEFAULT 0',
            'last_daily_reset': 'TEXT',
            'bonus_hearts': 'INTEGER DEFAULT 0'
        }
        
        # 添加缺失的字段
        for field_name, field_type in new_fields.items():
            if field_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE user ADD COLUMN {field_name} {field_type}")
                    print(f"已添加字段: {field_name}")
                except sqlite3.OperationalError as e:
                    print(f"添加字段 {field_name} 失败: {e}")
        
        # 更新现有用户的默认值
        current_time = datetime.utcnow().isoformat()
        cursor.execute("""
            UPDATE user SET 
                is_newbie = 1,
                newbie_protection_count = 0,
                consecutive_correct = 0,
                last_daily_reset = ?,
                bonus_hearts = 0
            WHERE is_newbie IS NULL
        """, (current_time,))
        
        conn.commit()
        print("数据库迁移完成！")
        
    except Exception as e:
        print(f"迁移过程中出错: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()