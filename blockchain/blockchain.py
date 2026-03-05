from blockchain.block import Block


class Blockchain:

    def __init__(self):

        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):

        return Block(0, "Genesis Block", "0")

    def get_last_block(self):

        return self.chain[-1]

    def add_block(self, vote):

        previous = self.get_last_block()

        new_block = Block(
            len(self.chain),
            vote,
            previous.hash
        )

        self.chain.append(new_block)