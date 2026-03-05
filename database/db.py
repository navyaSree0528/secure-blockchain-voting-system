import sqlite3
import bcrypt

DATABASE = "voters.db"


# -------------------------
# CREATE DATABASE CONNECTION
# -------------------------
def create_connection():
    return sqlite3.connect(DATABASE)


# -------------------------
# CREATE VOTER TABLE
# -------------------------
def create_table():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS voters(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        voter_id TEXT UNIQUE,
        password BLOB,
        has_voted INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


# -------------------------
# CREATE VOTES TABLE
# -------------------------
def create_vote_table():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS votes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        encrypted_vote TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


# -------------------------
# ADD AUTHENTICATED VOTER
# -------------------------
def add_voter(voter_id, password):

    conn = create_connection()
    cursor = conn.cursor()

    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    cursor.execute(
        "INSERT INTO voters (voter_id,password) VALUES (?,?)",
        (voter_id, hashed_password)
    )

    conn.commit()
    conn.close()


# -------------------------
# VALIDATE LOGIN
# -------------------------
def validate_voter(voter_id, password):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password FROM voters WHERE voter_id=?",
        (voter_id,)
    )

    result = cursor.fetchone()
    conn.close()

    if result and bcrypt.checkpw(password.encode(), result[0]):
        return True

    return False


# -------------------------
# CHECK IF VOTER ALREADY VOTED
# -------------------------
def has_already_voted(voter_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT has_voted FROM voters WHERE voter_id=?",
        (voter_id,)
    )

    result = cursor.fetchone()
    conn.close()

    if result and result[0] == 1:
        return True

    return False


# -------------------------
# MARK VOTER AS VOTED
# -------------------------
def mark_voted(voter_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE voters SET has_voted=1 WHERE voter_id=?",
        (voter_id,)
    )

    conn.commit()
    conn.close()


# -------------------------
# STORE ENCRYPTED VOTE
# -------------------------
def store_vote(encrypted_vote):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO votes (encrypted_vote) VALUES (?)",
        (encrypted_vote,)
    )

    conn.commit()
    conn.close()


# -------------------------
# GET ALL VOTES
# -------------------------
def get_votes():

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT encrypted_vote FROM votes")

    votes = cursor.fetchall()
    conn.close()

    return [v[0] for v in votes]