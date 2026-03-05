from flask import Flask, render_template, request, redirect, session
from datetime import datetime, timedelta
from threading import Lock
import os
import logging

# database
from database.db import (
    create_table,
    create_vote_table,
    add_voter,
    validate_voter,
    mark_voted,
    has_already_voted,
    store_vote,
    get_votes
)

# crypto
from crypto.encryption import encrypt_vote, decrypt_vote
from crypto.blind_signature import blind_message, sign_blinded, unblind_signature

# mixnet
from mixnet.mixnet import shuffle_votes

# blockchain
from blockchain.blockchain import Blockchain


app = Flask(__name__)
app.secret_key = "supersecurekey"

# --------------------------
# Logging setup
# --------------------------

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/security.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

# --------------------------
# Intrusion Detection
# --------------------------

failed_attempts = {}
MAX_ATTEMPTS = 5
BLOCK_TIME = 120

# --------------------------
# Blockchain
# --------------------------

blockchain = Blockchain()

# --------------------------
# Concurrency lock
# --------------------------

vote_lock = Lock()

# --------------------------
# Admin credentials
# --------------------------

ADMIN_ID = "admin"
ADMIN_PASSWORD = "admin123"

# --------------------------
# HOME
# --------------------------

@app.route("/")
def home():
    return render_template("login.html")


# --------------------------
# LOGIN
# --------------------------

@app.route("/login", methods=["POST"])
def login():

    voter_id = request.form["voter_id"]
    password = request.form["password"]

    now = datetime.now()

    if voter_id in failed_attempts:

        attempts, block_until = failed_attempts[voter_id]

        if block_until and now < block_until:
            return "Account temporarily blocked."

    if validate_voter(voter_id, password):

        session["user"] = voter_id

        if voter_id in failed_attempts:
            del failed_attempts[voter_id]

        return redirect("/dashboard")

    if voter_id not in failed_attempts:
        failed_attempts[voter_id] = [1, None]
    else:
        failed_attempts[voter_id][0] += 1

    attempts = failed_attempts[voter_id][0]

    if attempts >= MAX_ATTEMPTS:

        failed_attempts[voter_id][1] = now + timedelta(seconds=BLOCK_TIME)

        return "Too many failed attempts."

    return "Invalid Voter ID or Password"


# --------------------------
# DASHBOARD
# --------------------------

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    return render_template("dashboard.html")


# --------------------------
# VOTING PAGE
# --------------------------

@app.route("/vote")
def vote():

    if "user" not in session:
        return redirect("/")

    return render_template("vote.html")


# --------------------------
# SUBMIT VOTE
# --------------------------

@app.route("/submit_vote", methods=["POST"])
def submit_vote():

    if "user" not in session:
        return redirect("/")

    voter_id = session["user"]

    if has_already_voted(voter_id):
        return "You have already voted!"

    candidate = request.form["candidate"]

    # blind signature process
    blinded, r = blind_message(candidate)
    signed = sign_blinded(blinded)
    signature = unblind_signature(signed, r)

    encrypted_vote = encrypt_vote(candidate)

    with vote_lock:

        store_vote(encrypted_vote)

        blockchain.add_block(encrypted_vote)

    mark_voted(voter_id)

    return redirect("/result")


# --------------------------
# RESULTS
# --------------------------

@app.route("/result")
def result():

    if "user" not in session:
        return redirect("/")

    # Import matplotlib ONLY here (faster startup)
    import matplotlib.pyplot as plt

    encrypted_votes = get_votes()

    shuffled_votes = shuffle_votes(encrypted_votes)

    count = {}

    for v in shuffled_votes:

        vote = decrypt_vote(v)

        if vote in count:
            count[vote] += 1
        else:
            count[vote] = 1

    candidates = list(count.keys())
    votes = list(count.values())

    os.makedirs("static/charts", exist_ok=True)

    chart_path = "static/charts/result.png"

    plt.figure()

    plt.bar(candidates, votes)

    plt.xlabel("Candidates")
    plt.ylabel("Votes")
    plt.title("Election Results")

    plt.savefig(chart_path)

    plt.close()

    return render_template("result.html", count=count, chart=chart_path)


# --------------------------
# BLOCKCHAIN VIEW
# --------------------------

@app.route("/blockchain")
def blockchain_view():

    if "user" not in session:
        return redirect("/")

    return render_template(
        "blockchain_view.html",
        chain=blockchain.chain
    )


# --------------------------
# LOGOUT
# --------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# --------------------------
# ADMIN LOGIN
# --------------------------

@app.route("/admin", methods=["GET","POST"])
def admin_login():

    if request.method == "POST":

        admin_id = request.form["admin_id"]
        password = request.form["password"]

        if admin_id == ADMIN_ID and password == ADMIN_PASSWORD:

            session["admin"] = admin_id

            return redirect("/admin/dashboard")

        return "Invalid Admin Credentials"

    return render_template("admin_login.html")


# --------------------------
# ADMIN DASHBOARD
# --------------------------

@app.route("/admin/dashboard")
def admin_dashboard():

    if "admin" not in session:
        return redirect("/admin")

    votes = get_votes()

    return render_template(
        "admin_dashboard.html",
        voters=len(votes),
        blocks=len(blockchain.chain)
    )


# --------------------------
# VERIFY BLOCKCHAIN
# --------------------------

@app.route("/admin/verify_chain")
def verify_chain():

    if "admin" not in session:
        return redirect("/admin")

    valid = True

    chain = blockchain.chain

    for i in range(1, len(chain)):

        current = chain[i]
        previous = chain[i-1]

        if current.previous_hash != previous.hash:
            valid = False
            break

    return render_template("chain_status.html", valid=valid)


# --------------------------
# START SERVER
# --------------------------

if __name__ == "__main__":

    create_table()
    create_vote_table()

    # Create voters only if database empty
    if len(get_votes()) == 0:

        voters = [
            ("VOTER001","1234"),
            ("VOTER002","1234"),
            ("VOTER003","1234"),
            ("VOTER004","1234"),
            ("VOTER005","1234"),
            ("VOTER006","1234"),
            ("VOTER007","1234"),
            ("VOTER008","1234"),
            ("VOTER009","1234"),
            ("VOTER010","1234"),
            ("VOTER011","1234"),
            ("VOTER012","1234"),
            ("VOTER013","1234"),
            ("VOTER014","1234"),
            ("VOTER015","1234")
        ]

        for v in voters:

            try:
                add_voter(v[0], v[1])
            except:
                pass

    app.run(debug=True)