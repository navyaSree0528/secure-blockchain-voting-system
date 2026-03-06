import sqlite3
import bcrypt

DATABASE = "voters.db"


# -----------------------------
# DATABASE CONNECTION
# -----------------------------
def create_connection():
    return sqlite3.connect(DATABASE)


# -----------------------------
# CREATE TABLES
# -----------------------------
def create_tables():

    conn = create_connection()
    cursor = conn.cursor()

    # eligible voters list
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS eligible_voters(
        voter_id TEXT PRIMARY KEY,
        name TEXT,
        age INTEGER
    )
    """)

    # registered voters
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS voters(
        voter_id TEXT PRIMARY KEY,
        password BLOB,
        has_voted INTEGER DEFAULT 0
    )
    """)

    # votes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS votes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vote_hash TEXT,
        encrypted_vote BLOB
    )
    """)

    # -----------------------------
    # AUTO INSERT ELIGIBLE VOTERS
    # -----------------------------
    cursor.execute("SELECT COUNT(*) FROM eligible_voters")
    count = cursor.fetchone()[0]

    if count == 0:

        voters = [
            ("VOTER001", "Ravi", 24),
            ("VOTER002", "Priya", 30),
            ("VOTER003", "Arjun", 17),
            ("VOTER004", "Anita", 21),
            ("VOTER005", "Rahul", 28),
            ("VOTER006", "Sneha", 26)
        ]

        cursor.executemany(
            "INSERT INTO eligible_voters VALUES (?,?,?)",
            voters
        )

    conn.commit()
    conn.close()


# -----------------------------
# CHECK ELIGIBLE VOTER
# -----------------------------
def is_eligible(voter_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT age FROM eligible_voters WHERE voter_id=?",
        (voter_id,)
    )

    result = cursor.fetchone()

    conn.close()

    if result and result[0] >= 18:
        return True

    return False


# -----------------------------
# CHECK REGISTERED
# -----------------------------
def voter_exists(voter_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM voters WHERE voter_id=?",
        (voter_id,)
    )

    result = cursor.fetchone()

    conn.close()

    return result is not None


# -----------------------------
# ADD VOTER
# -----------------------------
def add_voter(voter_id, password):

    conn = create_connection()
    cursor = conn.cursor()

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    cursor.execute(
        "INSERT INTO voters(voter_id,password) VALUES(?,?)",
        (voter_id, hashed)
    )

    conn.commit()
    conn.close()


# -----------------------------
# LOGIN VALIDATION
# -----------------------------
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


# -----------------------------
# HAS VOTED
# -----------------------------
def has_voted(voter_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT has_voted FROM voters WHERE voter_id=?",
        (voter_id,)
    )

    result = cursor.fetchone()

    conn.close()

    return result and result[0] == 1


# -----------------------------
# MARK VOTED
# -----------------------------
def mark_voted(voter_id):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE voters SET has_voted=1 WHERE voter_id=?",
        (voter_id,)
    )

    conn.commit()
    conn.close()


# -----------------------------
# STORE VOTE
# -----------------------------
def store_vote(vote_hash, encrypted_vote):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO votes(vote_hash, encrypted_vote) VALUES(?,?)",
        (vote_hash, encrypted_vote)
    )

    conn.commit()
    conn.close()


# -----------------------------
# GET VOTES
# -----------------------------
def get_votes():

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT encrypted_vote FROM votes")

    votes = cursor.fetchall()

    conn.close()

    return [v[0] for v in votes]


# -----------------------------
# VERIFY VOTE
# -----------------------------
def verify_vote(vote_hash):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM votes WHERE vote_hash=?",
        (vote_hash,)
    )

    result = cursor.fetchone()

    conn.close()

    return result is not None


# -----------------------------
# COUNT REGISTERED VOTERS
# -----------------------------
def get_voter_count():

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM voters")

    count = cursor.fetchone()[0]

    conn.close()

    return count