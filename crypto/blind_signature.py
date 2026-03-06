from Crypto.PublicKey import RSA
from Crypto.Random import random
from Crypto.Hash import SHA256
from Crypto.Util.number import inverse


key = RSA.generate(2048)
public_key = key.publickey()


def blind_message(message):

    message_hash = int.from_bytes(
        SHA256.new(message.encode()).digest(),
        'big'
    )

    r = random.randint(2, public_key.n - 1)

    blinded = (
        message_hash * pow(r, public_key.e, public_key.n)
    ) % public_key.n

    return blinded, r


def sign_blinded(blinded_message):

    signed = pow(blinded_message, key.d, key.n)

    return signed


def unblind_signature(signed_blinded, r):

    r_inv = inverse(r, key.n)

    signature = (signed_blinded * r_inv) % key.n

    return signature