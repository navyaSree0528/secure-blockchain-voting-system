from cryptography.fernet import Fernet

# Fixed encryption key (generate once and keep it same)
key = b'5PzX7Q1oY9mR3xXhBv3cP0L2k8qTjG5V9hZxT4wF6sA='

cipher = Fernet(key)


def encrypt_vote(vote):
    encrypted_vote = cipher.encrypt(vote.encode())
    return encrypted_vote


def decrypt_vote(encrypted_vote):
    vote = cipher.decrypt(encrypted_vote).decode()
    return vote