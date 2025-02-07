import argparse
import json
import sys
import os

# Ensure the project root is in Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.network.validator import ValidatorNode
from src.network.relay import NetworkRelay
from src.blockchain.core import DOUBlockchain
from src.messaging.system import DOUMessaging
from src.rewards.system import DOURewardSystem
from src.cryptography.hazmat.primitives.asymmetric import ec
from src.cryptography.hazmat.primitives import serialization
from src.base64 import base64
from src.socket import socket
from src.time import time

class DOUBlockchainCLI:
    def __init__(self):
        # Use environment variable for data directory, default to current directory
        self.data_dir = os.environ.get('DOU_DATA_DIR', os.path.dirname(__file__))
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create a data subdirectory for persistent storage
        self.data_dir = os.path.join(self.data_dir, 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.blockchain = DOUBlockchain()
        self.messaging = DOUMessaging()
        self.rewards = DOURewardSystem()
        
        # Use data directory for users file
        self.users_file = os.path.join(self.data_dir, 'users.json')
        self.users = self.load_users()

    def load_users(self):
        """Load users from persistent storage"""
        if not os.path.exists(self.users_file):
            return {}
        
        with open(self.users_file, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    def save_users(self):
        """Save users to persistent storage"""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)

    def generate_address(self):
        """Generate a new DOU address"""
        private_key = ec.generate_private_key(ec.SECP256R1())
        public_key = private_key.public_key()
        
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Serialize private key
        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        address = self.messaging.generate_dou_address(public_key_bytes)
        
        # Store user details
        self.users[address] = {
            'public_key': base64.b64encode(public_key_bytes).decode(),
            'private_key': base64.b64encode(private_key_bytes).decode()
        }
        self.save_users()
        
        return address

    def create_user(self, args):
        """Create a new user with a DOU address"""
        max_users = int(os.environ.get('DOU_MAX_USERS', 10))
        if len(self.users) >= max_users:
            print(f"Maximum number of users reached ({max_users}).")
            return None

        address = self.generate_address()
        print(f"Created new user with DOU address: {address}")
        print(f"Data stored in: {self.data_dir}")
        return address

    def list_users(self, args):
        """List all created users"""
        if not self.users:
            print("No users created yet.")
            return

        print("Existing Users:")
        for address in self.users.keys():
            print(f"- {address}")
        print(f"\nUsers stored in: {self.users_file}")

    def send_message(self, args):
        """Send a message between two users"""
        if len(self.users) < 2:
            print("Error: Create at least two users first.")
            return

        # Use first two users if not specified
        users = list(self.users.keys())
        sender_address = users[0]
        recipient_address = users[1]

        try:
            message_tx = self.messaging.send_message(
                sender_address=sender_address, 
                recipient_address=recipient_address, 
                message=args.message, 
                sender_signature=b'dummy_signature'
            )

            # Calculate and add message reward
            message_reward = self.messaging.get_message_reward(message_tx)
            self.rewards.add_message_reward(sender_address, message_reward)

            print(f"Message sent from {sender_address} to {recipient_address}")
            print(f"Message Reward: {message_reward} DOU")
        except Exception as e:
            print(f"Error sending message: {e}")

    def check_rewards(self, args):
        """Check rewards for a user"""
        if not self.users:
            print("Error: Create a user first.")
            return

        # Use first user if not specified
        address = list(self.users.keys())[0]
        user_rewards = self.rewards.get_user_total_rewards(address)
        validator_rewards = self.rewards.get_validator_total_rewards(address)

        print(f"Rewards for {address}:")
        print(f"Messaging Rewards: {user_rewards} DOU")
        print(f"Validator Rewards: {validator_rewards} DOU")

    def register_validator(self, args):
        """Register a user as a validator"""
        if not self.users:
            print("Error: Create a user first.")
            return

        # Use first user if not specified
        address = list(self.users.keys())[0]
        stake = args.stake

        result = self.blockchain.register_validator(address, stake)
        if result:
            print(f"Registered {address} as a validator with {stake} DOU stake")

    def send_network_message(self, args):
        """
        Send a message through the network relay
        
        :param args: Argument namespace containing message details
        """
        if not self.users:
            print("Error: Create a user first.")
            return

        # Use first user as sender if not specified
        sender_address = list(self.users.keys())[0]
        
        # Validate recipient and message
        if not args.recipient or not args.message:
            print("Error: Recipient and message are required.")
            return

        # Network relay configuration
        validator_host = os.environ.get('DOU_VALIDATOR_HOST', 'localhost:5001')
        relay_host = os.environ.get('DOU_RELAY_HOST', 'localhost:5000')

        try:
            # Create network message
            network_message = {
                'sender': sender_address,
                'recipient': args.recipient,
                'content': args.message,
                'timestamp': time.time()
            }

            # Send message via socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                host, port = relay_host.split(':')
                sock.connect((host, int(port)))
                
                # Send serialized message
                sock.send(json.dumps(network_message).encode('utf-8'))
                
                # Receive response
                response = sock.recv(4096).decode('utf-8')
                response_data = json.loads(response)
                
                if response_data.get('status') == 'success':
                    print(f"Message sent successfully!")
                    print(f"Message ID: {response_data.get('message_id')}")
                else:
                    print("Message sending failed.")

        except Exception as e:
            print(f"Network message error: {e}")

    def list_addresses(self, args):
        """List all blockchain addresses"""
        validator = ValidatorNode()
        addresses = validator.cli_query('addresses')
        print(json.dumps(addresses, indent=2))

    def user_history(self, args):
        """Get user message history"""
        validator = ValidatorNode()
        history = validator.cli_query('history', args.address)
        print(json.dumps(history, indent=2))

    def sync_network(self, args):
        """Sync data with another validator"""
        validator = ValidatorNode()
        validator.sync_network_data(args.validator_host)
        print(f"Synced network data with {args.validator_host}")

    def run(self):
        """Run the CLI"""
        parser = argparse.ArgumentParser(description="DOU Blockchain CLI")
        subparsers = parser.add_subparsers(dest='command', help='Commands')

        # Create user command
        create_parser = subparsers.add_parser('create', help='Create a new user')
        create_parser.set_defaults(func=self.create_user)

        # List users command
        list_parser = subparsers.add_parser('list', help='List all users')
        list_parser.set_defaults(func=self.list_users)

        # Send message command
        send_parser = subparsers.add_parser('send', help='Send a message')
        send_parser.add_argument('message', type=str, help='Message to send')
        send_parser.set_defaults(func=self.send_message)

        # Check rewards command
        rewards_parser = subparsers.add_parser('rewards', help='Check user rewards')
        rewards_parser.set_defaults(func=self.check_rewards)

        # Register validator command
        validator_parser = subparsers.add_parser('validate', help='Register as a validator')
        validator_parser.add_argument('stake', type=float, help='Amount of DOU to stake')
        validator_parser.set_defaults(func=self.register_validator)

        # Network message command
        network_parser = subparsers.add_parser('network_send', help='Send a message through network')
        network_parser.add_argument('recipient', type=str, help='Recipient DOU address')
        network_parser.add_argument('message', type=str, help='Message to send')
        network_parser.set_defaults(func=self.send_network_message)

        # Validator query commands
        addresses_parser = subparsers.add_parser('list_addresses', help='List all blockchain addresses')
        addresses_parser.set_defaults(func=self.list_addresses)

        history_parser = subparsers.add_parser('user_history', help='Get user message history')
        history_parser.add_argument('address', help='Blockchain address to query')
        history_parser.set_defaults(func=self.user_history)

        sync_parser = subparsers.add_parser('sync_network', help='Sync data with another validator')
        sync_parser.add_argument('validator_host', help='Validator host to sync with (IP:PORT)')
        sync_parser.set_defaults(func=self.sync_network)

        # Parse arguments
        args = parser.parse_args()
        if hasattr(args, 'func'):
            args.func(args)
        else:
            parser.print_help()

def main():
    cli = DOUBlockchainCLI()
    cli.run()

if __name__ == "__main__":
    main()
