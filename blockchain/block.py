import hashlib
import time


class Block:

    def __init__(self, index, vote, previous_hash):

        self.index = index
        self.vote = vote
        self.timestamp = time.time()
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):

        data = str(self.index) + str(self.vote) + str(self.timestamp) + str(self.previous_hash)

        return hashlib.sha256(data.encode()).hexdigest()