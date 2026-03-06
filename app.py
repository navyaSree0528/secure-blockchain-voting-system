from flask import Flask, render_template, request, redirect, session, jsonify
import hashlib
import os
import logging
import matplotlib.pyplot as plt

# database
from database.db import (
    create_tables,
    add_voter,
    validate_voter,
    has_voted,
    mark_voted,
    store_vote,
    get_votes,
    verify_vote,
    voter_exists,
    is_eligible,
    get_voter_count
)

# crypto
from crypto.encryption import encrypt_vote, decrypt_vote

# mixnet
from mixnet.mixnet import shuffle_votes

# blockchain
from blockchain.blockchain import Blockchain


app = Flask(__name__)
app.secret_key = "securekey123"


# -------------------------
# Logging
# -------------------------
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/security.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)


# -------------------------
# Blockchain
# -------------------------
blockchain = Blockchain()


# -------------------------
# Election control
# -------------------------
election_open = True


# -------------------------
# Admin credentials
# -------------------------
ADMIN_ID = "admin"
ADMIN_PASSWORD = "admin123"


# -------------------------
# HOME
# -------------------------
@app.route("/")
def home():
    return render_template("login.html")


# -------------------------
# REGISTER
# -------------------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        voter_id = request.form["voter_id"]
        password = request.form["password"]

        if not is_eligible(voter_id):
            return "You are not found in the voter database."

        if voter_exists(voter_id):
            return "You are already registered."

        add_voter(voter_id, password)

        logging.info(f"{voter_id} registered")

        return redirect("/")

    return render_template("register.html")


# -------------------------
# LOGIN
# -------------------------
@app.route("/login", methods=["POST"])
def login():

    voter_id = request.form["voter_id"]
    password = request.form["password"]

    if validate_voter(voter_id, password):

        session["user"] = voter_id

        logging.info(f"{voter_id} logged in")

        return redirect("/dashboard")

    logging.warning(f"Failed login attempt {voter_id}")

    return "Invalid credentials"


# -------------------------
# USER DASHBOARD
# -------------------------
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    return render_template("dashboard.html")


# -------------------------
# VOTE PAGE
# -------------------------
@app.route("/vote")
def vote():

    if "user" not in session:
        return redirect("/")

    return render_template("vote.html")


# -------------------------
# SUBMIT VOTE
# -------------------------
@app.route("/submit_vote", methods=["POST"])
def submit_vote():

    global election_open

    if not election_open:
        return "Voting is currently closed."

    if "user" not in session:
        return redirect("/")

    voter = session["user"]

    if has_voted(voter):
        return render_template("already_voted.html")

    candidate = request.form["candidate"]

    encrypted_vote = encrypt_vote(candidate)

    vote_hash = hashlib.sha256(encrypted_vote).hexdigest()

    store_vote(vote_hash, encrypted_vote)

    blockchain.add_block(encrypted_vote)

    mark_voted(voter)

    logging.info(f"{voter} cast vote")

    return render_template(
        "vote_success.html",
        vote_hash=vote_hash
    )


# -------------------------
# VERIFY VOTE
# -------------------------
@app.route("/verify_vote", methods=["GET", "POST"])
def verify():

    if request.method == "POST":

        vote_hash = request.form["vote_hash"]

        valid = verify_vote(vote_hash)

        return render_template(
            "verify_result.html",
            valid=valid
        )

    return render_template("verify_vote.html")


# -------------------------
# BLOCKCHAIN VIEW
# -------------------------
@app.route("/blockchain")
def blockchain_view():

    return render_template(
        "blockchain_view.html",
        chain=blockchain.chain
    )


# -------------------------
# ADMIN LOGIN
# -------------------------
@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":

        admin_id = request.form["admin_id"]
        password = request.form["password"]

        if admin_id == ADMIN_ID and password == ADMIN_PASSWORD:

            session["admin"] = admin_id

            logging.info("Admin logged in")

            return redirect("/admin/dashboard")

        return "Invalid credentials"

    return render_template("admin_login.html")


# -------------------------
# ADMIN DASHBOARD
# -------------------------
@app.route("/admin/dashboard")
def admin_dashboard():

    votes = get_votes()

    voter_count = get_voter_count()

    return render_template(
        "admin_dashboard.html",
        votes=len(votes),
        voters=voter_count,
        blocks=len(blockchain.chain)
    )


# -------------------------
# OPEN ELECTION
# -------------------------
@app.route("/admin/open_election")
def open_election():

    global election_open

    election_open = True

    logging.info("Election opened")

    return redirect("/admin/dashboard")


# -------------------------
# CLOSE ELECTION
# -------------------------
@app.route("/admin/close_election")
def close_election():

    global election_open

    election_open = False

    logging.info("Election closed")

    return redirect("/admin/dashboard")


# -------------------------
# ADMIN RESULTS
# -------------------------
@app.route("/admin/results")
def admin_results():

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

    return render_template(
        "admin_results.html",
        count=count,
        chart=chart_path
    )


# -------------------------
# VERIFY BLOCKCHAIN
# -------------------------
@app.route("/admin/verify_chain")
def verify_chain():

    valid = blockchain.is_chain_valid()

    return render_template(
        "chain_status.html",
        valid=valid
    )


# -------------------------
# EXPORT BLOCKCHAIN
# -------------------------
@app.route("/admin/export_blockchain")
def export_blockchain():

    data = []

    for block in blockchain.chain:

        data.append({
            "index": block.index,
            "vote": str(block.vote),
            "hash": block.hash,
            "previous_hash": block.previous_hash
        })

    return jsonify(data)


# -------------------------
# LOGOUT
# -------------------------
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# -------------------------
# START SERVER
# -------------------------
if __name__ == "__main__":

    create_tables()

    app.run(debug=True)