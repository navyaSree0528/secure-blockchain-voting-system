from cryptography.fernet import Fernet


# fixed key for demo
key = b'5PzX7Q1oY9mR3xXhBv3cP0L2k8qTjG5V9hZxT4wF6sA='

cipher = Fernet(key)


def encrypt_vote(vote):

    encrypted = cipher.encrypt(vote.encode())

    return encrypted


def decrypt_vote(encrypted_vote):

    vote = cipher.decrypt(encrypted_vote).decode()

    return vote