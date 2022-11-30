# Imports
import streamlit as st
from dataclasses import dataclass
from typing import Any, List
import datetime as datetime
import pandas as pd
import hashlib

#the `Record` datclass
#this class contains the user inputs which will be entered into the record.
@dataclass
class Record:
    sender: str
    receiver: str
    amount: float

#the `Block` class
#this class contains the information that will make up each block
@dataclass
class Block:
    #user inputs for the record
    record: Record
    #the block's creator ID which is set to be an integer
    creator_id: int
    #the hash of the previous block which will be used to chain the blocks together
    prev_hash: str = "0"
    #timestamp is set to the time that the block was created
    timestamp: str = datetime.datetime.utcnow().strftime("%H:%M:%S")
    #nonce for completing proof of work
    nonce: int = 0

    def hash_block(self):
        #use the sha256 hashing function to create a hash
        sha = hashlib.sha256()
        #encode the block attributes
        record = str(self.record).encode()
        sha.update(record)

        creator_id = str(self.creator_id).encode()
        sha.update(creator_id)

        timestamp = str(self.timestamp).encode()
        sha.update(timestamp)

        prev_hash = str(self.prev_hash).encode()
        sha.update(prev_hash)

        nonce = str(self.nonce).encode()
        sha.update(nonce)

        return sha.hexdigest()

#the Pychain dataclass
#this class links the blocks together to form a chain
@dataclass
class PyChain:
    chain: List[Block]
    difficulty: int = 4
    #proof of work function that must be completed to add a block to the chain
    def proof_of_work(self, block):
        #assign the hash of the candidate block to a variable
        calculated_hash = block.hash_block()
        #set the proof of work requirement to a certain number of zeros
        num_of_zeros = "0" * self.difficulty
        #increment the nonce of the block until it returns a hash that meets the requirement
        while not calculated_hash.startswith(num_of_zeros):
            block.nonce += 1
            calculated_hash = block.hash_block()
        #print the winning hash
        print("Winning Hash", calculated_hash)
        return block
    #add the block to the chain
    def add_block(self, candidate_block):
        block = self.proof_of_work(candidate_block)
        self.chain += [block]
    #validation function
    def is_valid(self):
        #calculate the hash of the first block in the chain
        block_hash = self.chain[0].hash_block()
        #check the hashes of the remaining blocks in the chain
        #if the hashes don't match, return False
        for block in self.chain[1:]:
            if block_hash != block.prev_hash:
                print("Blockchain is invalid!")
                return False

            block_hash = block.hash_block()
        #if hashes match, return True
        print("Blockchain is Valid")
        return True

################################################################################
# Streamlit Code

# Adds the cache decorator for Streamlit

@st.cache(allow_output_mutation=True)
def setup():
    print("Initializing Chain")
    return PyChain([Block("Genesis", 0)])


st.markdown("# PyChain")
st.markdown("## Store a Transaction Record in the PyChain")

pychain = setup()

# Add an input area where you can get a value for `sender` from the user.
sender = st.text_input("Enter address of sender")

# Add an input area where you can get a value for `receiver` from the user.
receiver = st.text_input("Enter address of receiver")

# Add an input area where you can get a value for `amount` from the user.
amount = st.text_input("Enter an amount to send")

#add a block when the user clicks the "Add Block" button
if st.button("Add Block"):
    prev_block = pychain.chain[-1]
    prev_block_hash = prev_block.hash_block()
    new_block = Block(
        record=Record(sender, receiver, amount),
        creator_id=42,
        prev_hash=prev_block_hash
    )

    pychain.add_block(new_block)
    st.balloons()

################################################################################
# Streamlit Code (continues)

st.markdown("## The PyChain Ledger")

pychain_df = pd.DataFrame(pychain.chain).astype(str)
st.write(pychain_df)

difficulty = st.sidebar.slider("Block Difficulty", 1, 5, 2)
pychain.difficulty = difficulty

st.sidebar.write("# Block Inspector")
selected_block = st.sidebar.selectbox(
    "Which block would you like to see?", pychain.chain
)

st.sidebar.write(selected_block)

if st.button("Validate Chain"):
    st.write(pychain.is_valid())

