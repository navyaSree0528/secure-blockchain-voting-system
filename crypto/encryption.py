from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)


def encrypt_vote(vote):

    encrypted = cipher.encrypt(vote.encode())
    return encrypted


def decrypt_vote(encrypted_vote):

    vote = cipher.decrypt(encrypted_vote).decode()
    return vote