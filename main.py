import sys
import os

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from blockchain.core import DOUBlockchain
from messaging.system import DOUMessaging
from rewards.system import DOURewardSystem
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

def generate_key_pair():
    """Generate a new EC key pair"""
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    
    # Serialize public key
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_key, public_key_bytes

def main():
    # Initialize systems
    blockchain = DOUBlockchain()
    messaging = DOUMessaging()
    rewards = DOURewardSystem()

    # Generate two user key pairs
    alice_private_key, alice_public_key = generate_key_pair()
    bob_private_key, bob_public_key = generate_key_pair()

    # Generate DOU addresses
    alice_address = messaging.generate_dou_address(alice_public_key)
    bob_address = messaging.generate_dou_address(bob_public_key)

    print(f"Alice's DOU Address: {alice_address}")
    print(f"Bob's DOU Address: {bob_address}")

    # Register as validators
    blockchain.register_validator(alice_address, 100)  # 100 tokens staked
    blockchain.register_validator(bob_address, 50)    # 50 tokens staked

    # Send a message
    try:
        # Simulate message sending (in real implementation, use proper signing)
        message_tx = messaging.send_message(
            sender_address=alice_address, 
            recipient_address=bob_address, 
            message="Hello, this is a test message!", 
            sender_signature=b'dummy_signature'
        )

        # Calculate and add message reward
        message_reward = messaging.get_message_reward(message_tx)
        rewards.add_message_reward(alice_address, message_reward)

        print(f"\nMessage sent successfully!")
        print(f"Message Reward for Alice: {message_reward} DOU")
        print(f"Alice's Total Rewards: {rewards.get_user_total_rewards(alice_address)} DOU")

    except Exception as e:
        print(f"Error sending message: {e}")

    # Demonstrate validator rewards
    validator_reward_multiplier = rewards.calculate_validator_reward(
        validator_address=alice_address, 
        locked_amount=100, 
        validator_age=0.5  # 6 months
    )
    rewards.add_validator_reward(alice_address, base_reward=10, reward_multiplier=validator_reward_multiplier)

    print(f"\nValidator Rewards for Alice:")
    print(f"Total Validator Rewards: {rewards.get_validator_total_rewards(alice_address)} DOU")

if __name__ == "__main__":
    main()
