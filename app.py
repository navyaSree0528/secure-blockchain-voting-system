
from flask import Flask, render_template, request, redirect, session, jsonify
import hashlib
import os
import logging
import matplotlib.pyplot as plt
import random
import time
from datetime import datetime

# -------------------------
# DATABASE IMPORTS
# -------------------------
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
    get_voter_count,
    get_phone,
    get_candidates,
    add_candidate,
    delete_candidate
)

# -------------------------
# CRYPTO IMPORTS
# -------------------------
from crypto.encryption import encrypt_vote, decrypt_vote

# -------------------------
# MIXNET IMPORTS
# -------------------------
from mixnet.mixnet import shuffle_votes

# -------------------------
# BLOCKCHAIN IMPORTS
# -------------------------
from blockchain.blockchain import Blockchain

app = Flask(__name__)
app.secret_key = "securekey123"

# -------------------------
# OTP STORAGE
# -------------------------
otp_store = {}

# -------------------------
# LOGGING
# -------------------------
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/security.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

# -------------------------
# BLOCKCHAIN
# -------------------------
blockchain = Blockchain()

# -------------------------
# ELECTION SETTINGS
# -------------------------
election_settings = {
    "start_time": None,
    "end_time": None,
    "force_open": False,
    "force_closed": False
}

# -------------------------
# ADMIN LOGIN DETAILS
# -------------------------
ADMIN_ID = "admin"
ADMIN_PASSWORD = "admin123"

# -------------------------
# HOME PAGE
# -------------------------
@app.route("/")
def home():
    return render_template("login.html")


# -------------------------
# REGISTER PAGE
# -------------------------
@app.route("/register")
def register():
    return render_template("register.html")


# -------------------------
# SEND REGISTER OTP
# -------------------------
@app.route("/send_register_otp", methods=["POST"])
def send_register_otp():
    voter_id = request.form["voter_id"]

    if not is_eligible(voter_id):
        return render_template(
            "register.html",
            error="You are not an eligible voter."
        )

    if voter_exists(voter_id):
        return render_template(
            "register.html",
            error="You are already registered."
        )

    phone = get_phone(voter_id)

    if not phone:
        return render_template(
            "register.html",
            error="Phone number not found."
        )

    otp = random.randint(100000, 999999)
    otp_store[voter_id] = (otp, time.time())

    print("OTP for", voter_id, "=", otp)

    logging.info(f"OTP sent for voter {voter_id}")

    return render_template(
        "verify_otp.html",
        voter_id=voter_id
    )


# -------------------------
# VERIFY OTP
# -------------------------
@app.route("/verify_otp", methods=["POST"])
def verify_otp():
    voter_id = request.form["voter_id"]
    otp = request.form["otp"]

    if voter_id not in otp_store:
        return render_template(
            "verify_otp.html",
            voter_id=voter_id,
            error="OTP not generated."
        )

    stored_otp, timestamp = otp_store[voter_id]

    if time.time() - timestamp > 300:
        return render_template(
            "verify_otp.html",
            voter_id=voter_id,
            error="OTP expired."
        )

    if str(stored_otp) != otp:
        return render_template(
            "verify_otp.html",
            voter_id=voter_id,
            error="Invalid OTP."
        )

    return render_template(
        "set_password.html",
        voter_id=voter_id
    )


# -------------------------
# SET PASSWORD
# -------------------------
@app.route("/set_password", methods=["POST"])
def set_password():
    voter_id = request.form["voter_id"]
    password = request.form["password"]

    add_voter(voter_id, password)

    logging.info(f"{voter_id} completed registration")

    return redirect("/")


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

    logging.warning(f"Failed login attempt for {voter_id}")

    return render_template(
        "login.html",
        error="Invalid Voter ID or Password"
    )


# -------------------------
# USER DASHBOARD
# -------------------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    now = datetime.now()
    start_time = election_settings["start_time"]
    end_time = election_settings["end_time"]
    force_open = election_settings["force_open"]
    force_closed = election_settings["force_closed"]

    election_open = False
    status_text = "Election schedule has not been set"

    if force_closed:
        election_open = False
        status_text = "Election Closed By Admin"

    elif force_open:
        election_open = True
        status_text = "Election Opened Manually By Admin"

    elif start_time and end_time:
        if now < start_time:
            status_text = "Voting Not Started"

        elif start_time <= now <= end_time:
            election_open = True
            remaining = end_time - now
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)

            status_text = f"Voting Open • {hours}h {minutes}m remaining"

        else:
            status_text = "Voting Closed"

    return render_template(
        "dashboard.html",
        election_open=election_open,
        status_text=status_text,
        start_time=start_time,
        end_time=end_time
    )


# -------------------------
# VOTE PAGE
# -------------------------
@app.route("/vote")
def vote():
    if "user" not in session:
        return redirect("/")

    candidates = get_candidates()

    return render_template(
        "vote.html",
        candidates=candidates
    )


# -------------------------
# SUBMIT VOTE
# -------------------------
@app.route("/submit_vote", methods=["POST"])
def submit_vote():
    if "user" not in session:
        return redirect("/")

    now = datetime.now()
    start_time = election_settings["start_time"]
    end_time = election_settings["end_time"]
    force_open = election_settings["force_open"]
    force_closed = election_settings["force_closed"]

    if force_closed:
        return render_template(
            "dashboard.html",
            election_open=False,
            start_time=start_time,
            end_time=end_time,
            status_text="Election Closed By Admin",
            error="The admin has manually closed voting."
        )

    if not force_open:
        if not start_time or not end_time:
            return render_template(
                "dashboard.html",
                election_open=False,
                start_time=start_time,
                end_time=end_time,
                status_text="Election schedule has not been set.",
                error="Voting is currently unavailable because the election has not been scheduled."
            )

        if now < start_time:
            return render_template(
                "dashboard.html",
                election_open=False,
                start_time=start_time,
                end_time=end_time,
                status_text="Voting Not Started",
                error="Voting has not started yet."
            )

        if now > end_time:
            return render_template(
                "dashboard.html",
                election_open=False,
                start_time=start_time,
                end_time=end_time,
                status_text="Voting Closed",
                error="Voting has already ended."
            )

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

        return render_template(
            "admin_login.html",
            error="Invalid Admin ID or Password"
        )

    return render_template("admin_login.html")

# -------------------------
# ADMIN DASHBOARD
# -------------------------
@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect("/admin")

    votes = get_votes()
    voter_count = get_voter_count()
    candidates = get_candidates()

    now = datetime.now()
    start_time = election_settings["start_time"]
    end_time = election_settings["end_time"]
    force_open = election_settings["force_open"]
    force_closed = election_settings["force_closed"]

    # Lock candidate editing only while election is active
    candidate_edit_locked = False

    if force_open:
        candidate_edit_locked = True

    elif start_time and end_time:
        if start_time <= now <= end_time:
            candidate_edit_locked = True

    return render_template(
        "admin_dashboard.html",
        votes=len(votes),
        voters=voter_count,
        blocks=len(blockchain.chain),
        candidates=candidates,
        start_time=start_time,
        end_time=end_time,
        election_force_open=force_open,
        election_force_closed=force_closed,
        now=now,
        candidate_edit_locked=candidate_edit_locked
    )



# -------------------------
# SET ELECTION TIME
# -------------------------
@app.route("/admin/election_time", methods=["POST"])
def election_time():
    if "admin" not in session:
        return redirect("/admin")

    start = request.form["start_time"]
    end = request.form["end_time"]

    election_settings["start_time"] = datetime.strptime(
        start,
        "%Y-%m-%dT%H:%M"
    )

    election_settings["end_time"] = datetime.strptime(
        end,
        "%Y-%m-%dT%H:%M"
    )

    logging.info(f"Election timing updated: {start} -> {end}")

    return redirect("/admin/dashboard")


# -------------------------
# FORCE OPEN ELECTION
# -------------------------
@app.route("/admin/open_election")
def open_election():
    if "admin" not in session:
        return redirect("/admin")

    election_settings["force_open"] = True
    election_settings["force_closed"] = False

    logging.info("Admin manually opened the election")

    return redirect("/admin/dashboard")


# -------------------------
# FORCE CLOSE ELECTION
# -------------------------
@app.route("/admin/close_election")
def close_election():
    if "admin" not in session:
        return redirect("/admin")

    election_settings["force_open"] = False
    election_settings["force_closed"] = True

    logging.info("Admin manually closed the election")

    return redirect("/admin/dashboard")


# -------------------------
# RESET MANUAL CONTROL
# -------------------------
@app.route("/admin/reset_election_control")
def reset_election_control():
    if "admin" not in session:
        return redirect("/admin")

    election_settings["force_open"] = False
    election_settings["force_closed"] = False

    logging.info("Admin reset election control back to scheduled timing")

    return redirect("/admin/dashboard")


# -------------------------
# ADD CANDIDATE
# -------------------------
@app.route("/admin/add_candidate", methods=["POST"])
def admin_add_candidate():
    if "admin" not in session:
        return redirect("/admin")

    now = datetime.now()
    start_time = election_settings["start_time"]
    end_time = election_settings["end_time"]
    force_open = election_settings["force_open"]

    election_active = False

    if force_open:
        election_active = True

    elif start_time and end_time:
        election_active = start_time <= now <= end_time

    if election_active:
        logging.warning("Admin tried to add candidate while election is active")
        return redirect("/admin/dashboard")

    name = request.form["name"].strip()
    party = request.form["party"].strip()
    symbol = request.form["symbol"]
    color = request.form["color"]

    add_candidate(name, party, symbol, color)

    logging.info(f"Candidate added: {name}")

    return redirect("/admin/dashboard")

# -------------------------
# DELETE CANDIDATE
# -------------------------
@app.route("/admin/delete_candidate/<int:candidate_id>")
def admin_delete_candidate(candidate_id):
    if "admin" not in session:
        return redirect("/admin")

    now = datetime.now()
    start_time = election_settings["start_time"]
    end_time = election_settings["end_time"]
    force_open = election_settings["force_open"]

    election_active = False

    if force_open:
        election_active = True

    elif start_time and end_time:
        election_active = start_time <= now <= end_time

    if election_active:
        logging.warning(
            f"Admin tried to delete candidate {candidate_id} while election is active"
        )
        return redirect("/admin/dashboard")

    delete_candidate(candidate_id)

    logging.info(f"Admin deleted candidate with ID {candidate_id}")

    return redirect("/admin/dashboard")

# -------------------------
# ADMIN RESULTS
# -------------------------
@app.route("/admin/results")
def admin_results():
    if "admin" not in session:
        return redirect("/admin")

    encrypted_votes = get_votes()
    shuffled_votes = shuffle_votes(encrypted_votes)

    count = {}

    for vote in shuffled_votes:
        decrypted_vote = decrypt_vote(vote)

        if decrypted_vote in count:
            count[decrypted_vote] += 1
        else:
            count[decrypted_vote] = 1

    os.makedirs("static/charts", exist_ok=True)

    chart_path = "static/charts/result.png"

    plt.figure(figsize=(8, 5))
    plt.bar(count.keys(), count.values())
    plt.xlabel("Candidates")
    plt.ylabel("Votes")
    plt.title("Election Results")
    plt.tight_layout()
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
    if "admin" not in session:
        return redirect("/admin")

    valid = blockchain.is_chain_valid()

    return render_template(
        "chain_status.html",
        valid=valid,
        start_time=election_settings["start_time"],
        end_time=election_settings["end_time"]
    )


# -------------------------
# EXPORT BLOCKCHAIN
# -------------------------
@app.route("/admin/export_blockchain")
def export_blockchain():
    if "admin" not in session:
        return redirect("/admin")

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

