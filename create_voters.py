from database.db import create_table, create_vote_table, add_voter

def create_voters():

    # create tables if they don't exist
    create_table()
    create_vote_table()

    voters = [
        ("voter1", "pass1"),
        ("voter2", "pass2"),
        ("voter3", "pass3"),
        ("voter4", "pass4"),
        ("voter5", "pass5"),
        ("voter6", "pass6"),
        ("voter7", "pass7"),
        ("voter8", "pass8"),
        ("voter9", "pass9"),
        ("voter10", "pass10"),
        ("voter11", "pass11"),
        ("voter12", "pass12"),
        ("voter13", "pass13"),
        ("voter14", "pass14"),
        ("voter15", "pass15")
    ]

    for voter_id, password in voters:
        try:
            add_voter(voter_id, password)
            print(f"{voter_id} added successfully")
        except:
            print(f"{voter_id} already exists")

    print("15 authenticated voters created")

if __name__ == "__main__":
    create_voters()