import sqlite3
import bcrypt

DATABASE = "voters.db"


# -------------------------
# DATABASE CONNECTION
# -------------------------
def create_connection():
    return sqlite3.connect(DATABASE)


# -------------------------
# CREATE TABLES
# -------------------------
def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    # eligible voters table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS eligible_voters(
        voter_id TEXT PRIMARY KEY,
        name TEXT,
        age INTEGER,
        phone TEXT
    )
    """)

    # registered voters table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS voters(
        voter_id TEXT PRIMARY KEY,
        password BLOB,
        has_voted INTEGER DEFAULT 0
    )
    """)

    # votes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS votes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vote_hash TEXT,
        encrypted_vote BLOB
    )
    """)

    # candidates table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        party TEXT NOT NULL,
        symbol TEXT NOT NULL,
        color TEXT DEFAULT 'blue'
    )
    """)

    # insert default eligible voters
    cursor.execute("SELECT COUNT(*) FROM eligible_voters")
    voter_count = cursor.fetchone()[0]

    if voter_count == 0:
        voters = [
            ("VOTER001", "Ravi", 24, "9876543210"),
    ("VOTER002", "Priya", 30, "9876543211"),
    ("VOTER003", "Anita", 21, "9876543212"),
    ("VOTER004", "Rahul", 28, "9876543213"),
    ("VOTER005", "Sneha", 26, "9876543214"),
    ("VOTER006", "Arjun", 32, "9876543215"),
    ("VOTER007", "Kavya", 24, "9876543216"),
    ("VOTER008", "Ramesh", 35, "9876543217"),
    ("VOTER009", "Divya", 27, "9876543218"),
    ("VOTER010", "Vikram", 29, "9876543219")
            
        ]

        cursor.executemany(
            "INSERT INTO eligible_voters VALUES (?, ?, ?, ?)",
            voters
        )

    # insert default candidates
    cursor.execute("SELECT COUNT(*) FROM candidates")
    candidate_count = cursor.fetchone()[0]

    if candidate_count == 0:
        default_candidates = [
            ("Ananya Sharma", "Lotus Party", "spa", "orange"),
            ("Rahul Verma", "Fist Party", "hand-fist", "green"),
            ("Priya Reddy", "Bicycle Party", "bicycle", "purple"),
            ("Kiran Patel", "Flag Party", "flag", "red")
        ]

        cursor.executemany("""
        INSERT INTO candidates(name, party, symbol, color)
        VALUES (?, ?, ?, ?)
        """, default_candidates)

    conn.commit()
    conn.close()


# -------------------------
# GET PHONE NUMBER
# -------------------------
def get_phone(voter_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT phone FROM eligible_voters WHERE voter_id=?",
        (voter_id,)
    )

    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]

    return None


# -------------------------
# CHECK ELIGIBILITY
# -------------------------
def is_eligible(voter_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT age FROM eligible_voters WHERE voter_id=?",
        (voter_id,)
    )

    result = cursor.fetchone()
    conn.close()

    return result is not None and result[0] >= 18


# -------------------------
# CHECK IF REGISTERED
# -------------------------
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


# -------------------------
# ADD VOTER
# -------------------------
def add_voter(voter_id, password):
    conn = create_connection()
    cursor = conn.cursor()

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    cursor.execute(
        "INSERT INTO voters(voter_id, password) VALUES (?, ?)",
        (voter_id, hashed)
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
# CHECK IF USER HAS VOTED
# -------------------------
def has_voted(voter_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT has_voted FROM voters WHERE voter_id=?",
        (voter_id,)
    )

    result = cursor.fetchone()
    conn.close()

    return result is not None and result[0] == 1


# -------------------------
# MARK USER AS VOTED
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
def store_vote(vote_hash, encrypted_vote):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO votes(vote_hash, encrypted_vote) VALUES (?, ?)",
        (vote_hash, encrypted_vote)
    )

    conn.commit()
    conn.close()


# -------------------------
# GET ALL STORED VOTES
# -------------------------
def get_votes():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT encrypted_vote FROM votes")
    votes = cursor.fetchall()

    conn.close()

    return [vote[0] for vote in votes]


# -------------------------
# VERIFY VOTE HASH
# -------------------------
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


# -------------------------
# GET REGISTERED VOTER COUNT
# -------------------------
def get_voter_count():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM voters")
    count = cursor.fetchone()[0]

    conn.close()
    return count


# -------------------------
# GET ALL CANDIDATES
# -------------------------
def get_candidates():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, name, party, symbol, color
    FROM candidates
    ORDER BY id
    """)

    candidates = cursor.fetchall()
    conn.close()

    return candidates


# -------------------------
# ADD NEW CANDIDATE
# -------------------------
def add_candidate(name, party, symbol, color):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO candidates(name, party, symbol, color)
    VALUES (?, ?, ?, ?)
    """, (name, party, symbol, color))

    conn.commit()
    conn.close()


# -------------------------
# DELETE CANDIDATE
# -------------------------
def delete_candidate(candidate_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM candidates WHERE id=?",
        (candidate_id,)
    )

    conn.commit()
    conn.close()