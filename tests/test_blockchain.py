import sys
import os
import pytest

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from blockchain.core import DOUBlockchain
from messaging.system import DOUMessaging
from rewards.system import DOURewardSystem
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

def generate_test_address():
    """Generate a test DOU address"""
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    messaging = DOUMessaging()
    return messaging.generate_dou_address(public_key_bytes)

def test_blockchain_creation():
    """Test blockchain initialization"""
    blockchain = DOUBlockchain()
    assert len(blockchain.chain) == 0
    assert len(blockchain.current_transactions) == 0

def test_new_transaction():
    """Test creating a new transaction"""
    blockchain = DOUBlockchain()
    sender = generate_test_address()
    recipient = generate_test_address()
    
    tx_index = blockchain.new_transaction(sender, recipient, 10.5)
    assert tx_index == 1
    assert len(blockchain.current_transactions) == 1
    assert blockchain.current_transactions[0]['sender'] == sender
    assert blockchain.current_transactions[0]['recipient'] == recipient
    assert blockchain.current_transactions[0]['amount'] == 10.5

def test_validator_registration():
    """Test validator registration"""
    blockchain = DOUBlockchain()
    validator = generate_test_address()
    
    result = blockchain.register_validator(validator, 100)
    assert result is True
    assert len(blockchain.validators) == 1
    assert blockchain.validators[0]['address'] == validator
    assert blockchain.validators[0]['stake'] == 100

def test_validator_priority():
    """Test validator priority calculation"""
    blockchain = DOUBlockchain()
    validator1 = generate_test_address()
    validator2 = generate_test_address()
    
    blockchain.register_validator(validator1, 100)
    blockchain.register_validator(validator2, 50)
    
    # Simulate different join times
    blockchain.validators[0]['join_time'] -= 365 * 24 * 3600  # 1 year older
    
    priority1 = blockchain.calculate_validator_priority(
        blockchain.validators[0], min_stake=50
    )
    priority2 = blockchain.calculate_validator_priority(
        blockchain.validators[1], min_stake=50
    )
    
    assert priority1 > priority2

def test_messaging_system():
    """Test messaging system core functionality"""
    messaging = DOUMessaging()
    sender = generate_test_address()
    recipient = generate_test_address()
    
    message_tx = messaging.send_message(
        sender_address=sender, 
        recipient_address=recipient, 
        message="Test message", 
        sender_signature=b'dummy_signature'
    )
    
    assert 'tx_id' in message_tx
    assert message_tx['sender'] == sender
    assert message_tx['receiver'] == recipient

def test_rewards_system():
    """Test rewards calculation"""
    rewards = DOURewardSystem()
    user = generate_test_address()
    
    # Test message reward
    message_reward = rewards.calculate_message_reward(user, is_replied=True)
    assert message_reward > 0.1  # Base reward + reply bonus
    
    rewards.add_message_reward(user, message_reward)
    total_rewards = rewards.get_user_total_rewards(user)
    assert total_rewards == message_reward
    
    # Test validator reward
    validator_reward_multiplier = rewards.calculate_validator_reward(
        validator_address=user, 
        locked_amount=100, 
        validator_age=0.5
    )
    assert validator_reward_multiplier > 1.0
    
    rewards.add_validator_reward(user, base_reward=10, reward_multiplier=validator_reward_multiplier)
    validator_total_rewards = rewards.get_validator_total_rewards(user)
    assert validator_total_rewards > 10
