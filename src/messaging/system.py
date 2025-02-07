import time
import hashlib
from typing import Dict, List, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes

class DOUMessaging:
    def __init__(self):
        self.messages: Dict[str, Dict] = {}
        self.blacklists: Dict[str, set] = {}
        self.rate_limits: Dict[str, List[float]] = {}
    
    def generate_dou_address(self, public_key: bytes) -> str:
        """
        Generate a DOU address from a public key
        
        :param public_key: Public key bytes
        :return: DOU address
        """
        return f"DOU-{hashlib.sha256(public_key).hexdigest()[:20].upper()}"
    
    def encrypt_message(self, message: str, recipient_public_key: bytes) -> bytes:
        """
        Encrypt a message using recipient's public key
        
        :param message: Message to encrypt
        :param recipient_public_key: Recipient's public key
        :return: Encrypted message
        """
        # Simplified encryption - replace with proper asymmetric encryption
        key = Fernet.generate_key()
        f = Fernet(key)
        return f.encrypt(message.encode())
    
    def send_message(self, sender_address: str, recipient_address: str, 
                     message: str, sender_signature: bytes) -> Dict:
        """
        Send a message with spam prevention
        
        :param sender_address: Sender's DOU address
        :param recipient_address: Recipient's DOU address
        :param message: Message content
        :param sender_signature: Digital signature
        :return: Message transaction details
        """
        # Rate limit check
        current_time = time.time()
        if sender_address not in self.rate_limits:
            self.rate_limits[sender_address] = []
        
        # Remove timestamps older than 1 minute
        self.rate_limits[sender_address] = [
            t for t in self.rate_limits[sender_address] if current_time - t < 60
        ]
        
        # Check if sender has sent too many messages
        if len(self.rate_limits[sender_address]) >= 10:
            raise ValueError("Rate limit exceeded")
        
        # Check blacklist
        if sender_address in self.blacklists.get(recipient_address, set()):
            raise ValueError("Sender is blacklisted")
        
        # Message hash for on-chain storage
        message_hash = hashlib.sha256(message.encode()).hexdigest()
        
        message_tx = {
            'tx_id': hashlib.sha256(
                f"{sender_address}{recipient_address}{current_time}".encode()
            ).hexdigest(),
            'sender': sender_address,
            'receiver': recipient_address,
            'timestamp': current_time,
            'message_hash': message_hash,
            'signature': sender_signature.hex()
        }
        
        # Store message details
        self.messages[message_tx['tx_id']] = message_tx
        self.rate_limits[sender_address].append(current_time)
        
        return message_tx
    
    def add_to_blacklist(self, user_address: str, blocked_address: str):
        """
        Add an address to user's personal blacklist
        
        :param user_address: User creating the blacklist
        :param blocked_address: Address to block
        """
        if user_address not in self.blacklists:
            self.blacklists[user_address] = set()
        
        self.blacklists[user_address].add(blocked_address)
    
    def get_message_reward(self, message_tx: Dict) -> float:
        """
        Calculate reward for a message based on engagement
        
        :param message_tx: Message transaction details
        :return: Reward amount
        """
        base_reward = 0.1  # 0.1 DOU for sending a message
        
        # Check if message received a reply (simplified)
        replies = [
            msg for msg in self.messages.values() 
            if msg['sender'] == message_tx['receiver'] and 
               msg['receiver'] == message_tx['sender']
        ]
        
        # Bonus for receiving replies
        reply_bonus = 0.05 * len(replies)
        
        return base_reward + reply_bonus
