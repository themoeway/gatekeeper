import os
import sqlite3

_CREATE_ATTEMPTS_TABLE = """
CREATE TABLE IF NOT EXISTS attempts (
    discord_user_id INTEGER,
    quiz_level TEXT,
    created_at TIMESTAMP,
    result TEXT
);
"""

_CREATE_ROLES_TABLE = """
CREATE TABLE IF NOT EXISTS roles (
    discord_user_id INTEGER,
    role_id int,
    created_at TIMESTAMP
);
"""

class Store:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(
            db_name, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        with self.conn:
            self.conn.execute(_CREATE_ATTEMPTS_TABLE)
            self.conn.execute(_CREATE_ROLES_TABLE)

    def new_quiz_attempt(self, mainuserid, quizcommand, created_at, result):
        query = 'INSERT INTO attempts (discord_user_id, quiz_level, created_at, result) VALUES (?,?,?,?);'
        with self.conn:
            self.conn.execute(
                query, (mainuserid, quizcommand, created_at, result))

    def get_attempts(self, mainuserid, quizname):
        query = """SELECT EXISTS(
        SELECT * FROM attempts WHERE discord_user_id = ? AND quiz_level = ? AND created_at >= DATE('now', '-' || STRFTIME('%w') || ' days')
        ) AS didTry"""
        cursor = self.conn.cursor()
        cursor.execute(query, (mainuserid, quizname))
        return cursor.fetchall()

    def get_cooldown(self, mainuserid, quizname):
        query = "SELECT quiz_level, created_at FROM attempts WHERE discord_user_id = ? AND quiz_level = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (mainuserid, quizname))
        return cursor.fetchall()

    def save_role_info(self, mainuserid, newrankid, created_at):
        query = """INSERT INTO roles (discord_user_id, role_id, created_at) VALUES (?,?,?);"""
        with self.conn:
            self.conn.execute(query, (mainuserid, newrankid, created_at))

    def get_role_info(self, mainuserid, newrankid):
        query = """SELECT * FROM roles WHERE discord_user_id = ? and role_id = ?"""
        cursor = self.conn.cursor()
        cursor.execute(query, (mainuserid, newrankid))
        return cursor.fetchall()

    def get_unix(self):
        query = "SELECT STRFTIME('%s', DATE('now', '+' || (7 - STRFTIME('%w')) || ' days'));"
        cursor = self.conn.cursor()
        cursor.execute(query)
        return cursor.fetchone()[0]
