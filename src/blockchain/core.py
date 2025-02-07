import hashlib
import time
import json
from typing import List, Dict, Any
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes

class DOUBlockchain:
    def __init__(self):
        self.chain: List[Dict[str, Any]] = []
        self.current_transactions: List[Dict[str, Any]] = []
        self.validators: List[Dict[str, Any]] = []
        
    def create_block(self, proof: int, previous_hash: str) -> Dict[str, Any]:
        """
        Create a new block in the blockchain
        
        :param proof: The proof given by the Proof of Work algorithm
        :param previous_hash: Hash of previous block
        :return: New block
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash
        }
        
        # Reset the current list of transactions
        self.current_transactions = []
        
        self.chain.append(block)
        return block
    
    def new_transaction(self, sender: str, recipient: str, amount: float, message_hash: str = None) -> int:
        """
        Creates a new transaction to go into the next mined block
        
        :param sender: Address of the sender
        :param recipient: Address of the recipient
        :param amount: Amount of tokens
        :param message_hash: Optional encrypted message hash
        :return: The index of the block that will hold this transaction
        """
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'message_hash': message_hash,
            'timestamp': time.time()
        }
        
        self.current_transactions.append(transaction)
        return len(self.chain) + 1
    
    def hash_block(self, block: Dict[str, Any]) -> str:
        """
        Creates a SHA-256 hash of a block
        
        :param block: Block to hash
        :return: Hash of the block
        """
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def register_validator(self, address: str, stake: float) -> bool:
        """
        Register a new validator with their stake
        
        :param address: Validator's DOU address
        :param stake: Amount of tokens staked
        :return: Whether registration was successful
        """
        validator = {
            'address': address,
            'stake': stake,
            'join_time': time.time()
        }
        
        self.validators.append(validator)
        return True
    
    def calculate_validator_priority(self, validator: Dict[str, Any], min_stake: float) -> float:
        """
        Calculate validator priority based on stake and age
        
        :param validator: Validator details
        :param min_stake: Minimum stake requirement
        :return: Priority score
        """
        stake_factor = min(1.5, validator['stake'] / min_stake) * 0.4
        age_factor = (time.time() - validator['join_time']) / (365 * 24 * 3600)  # Years
        random_factor = hashlib.sha256(str(validator['address']).encode()).hexdigest()
        random_factor = int(random_factor, 16) / (2**256 - 1)
        
        return stake_factor + age_factor + random_factor
