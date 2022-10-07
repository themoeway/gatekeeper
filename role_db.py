import os
import sqlite3

import discord

# environment = os.environ['ENV']
# is_prod = environment == 'PROD'

class Store:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(
            db_name, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    
    def new_quiz_attempt(self, mainuserid, quizcommand, created_at, result):
        query = 'INSERT INTO attempts (discord_user_id, quiz_level, created_at, result) VALUES (?,?,?,?);'
        with self.conn:
            self.conn.execute(query, (mainuserid, quizcommand, created_at, result))
            self.conn.commit()
            
    def get_attempts(self, mainuserid, quizname):
        # query = """
        # SELECT * FROM attempts
        # WHERE discord_user_id= ?;
        # """
        query = """SELECT EXISTS(
        SELECT * FROM attempts WHERE discord_user_id = ? AND quiz_level = ? AND created_at >= DATE('now', '-' || STRFTIME('%w') || ' days')
        ) AS didTry"""
        data = (mainuserid, quizname)
        cursor = self.conn.cursor()
        cursor.execute(query, data)
        return cursor.fetchall()
    
    def get_cooldown(self, mainuserid, quizname):
        query = "SELECT quiz_level, created_at FROM attempts WHERE discord_user_id = ? AND quiz_level = ?"
        data = (mainuserid, quizname)
        cursor = self.conn.cursor()
        cursor.execute(query, data)
        return cursor.fetchall()
    
    def save_role_info(self, mainuserid, newrankid, created_at):
        query = """INSERT INTO roles (discord_user_id, role_id, created_at) VALUES (?,?,?);"""
        with self.conn:
            self.conn.execute(query, (mainuserid, newrankid, created_at))
            self.conn.commit()
            
    def get_role_info(self, mainuserid, newrankid):
        query = """SELECT * FROM roles WHERE discord_user_id = ? and role_id = ?"""
        data = (mainuserid, newrankid)
        cursor = self.conn.cursor()
        cursor.execute(query, data)
        return cursor.fetchall()
    
    def get_unix(self):
        query = "SELECT STRFTIME('%s', DATE('now', '+' || (7 - STRFTIME('%w')) || ' days'));"
        cursor = self.conn.cursor()
        cursor.execute(query)
        return cursor.fetchone()
    
def init_tables(db_name):
    return
    conn = sqlite3.connect(db_name)
    with conn:
        conn.execute(_CREATE_ATTEMPTS_TABLE)
        conn.execute(_CREATE_ROLES_TABLE)

_CREATE_ATTEMPTS_TABLE = """
CREATE TABLE IF NOT EXISTS attempts (
    discord_guild_id INTEGER,
    quiz_level TEXT,
    created_at TIMESTAMP,
    result TEXT,
);
"""

_CREATE_ROLES_TABLE = """
CREATE TABLE IF NOT EXISTS roles (
    discord_guild_id INTEGER,
    role_id int,
    created_at TIMESTAMP,
);
"""
