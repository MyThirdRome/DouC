import json
import os
import socket
import threading
from typing import Dict, List, Any

from src.blockchain.core import DOUBlockchain
from src.messaging.system import DOUMessaging
from src.rewards.system import DOURewardSystem

class ValidatorNode:
    def __init__(self, 
                 host: str = '0.0.0.0', 
                 port: int = 5001, 
                 data_dir: str = None,
                 validator_address: str = None):
        """
        Initialize Validator Node with enhanced history tracking
        
        :param host: Host to bind the validator
        :param port: Port to listen on
        :param data_dir: Directory to store persistent data
        :param validator_address: DOU address of the validator
        """
        self.host = host
        self.port = port
        self.validator_address = validator_address
        
        # Use environment variable or default path
        self.data_dir = data_dir or os.environ.get(
            'DOU_DATA_DIR', 
            os.path.expanduser('~/.dou_blockchain')
        )
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Persistent storage paths
        self.users_path = os.path.join(self.data_dir, 'users.json')
        self.messages_path = os.path.join(self.data_dir, 'messages.json')
        self.blockchain_path = os.path.join(self.data_dir, 'blockchain.json')
        
        # Initialize storage
        self._init_storage()
        
        # Blockchain components
        self.blockchain = DOUBlockchain()
        self.messaging = DOUMessaging()
        self.rewards = DOURewardSystem()
        
        # Validator registration
        if validator_address:
            self.blockchain.register_validator(validator_address, 100)  # Default 100 DOU stake
        
        # Server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
    
    def _init_storage(self):
        """Initialize storage files if they don't exist"""
        for path in [self.users_path, self.messages_path, self.blockchain_path]:
            if not os.path.exists(path):
                with open(path, 'w') as f:
                    json.dump([], f)
    
    def get_all_addresses(self) -> List[str]:
        """
        Retrieve all registered addresses across all machines
        
        :return: List of all unique addresses
        """
        try:
            with open(self.users_path, 'r') as f:
                users = json.load(f)
            return [user['address'] for user in users]
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def get_user_history(self, address: str) -> Dict[str, Any]:
        """
        Get comprehensive history for a specific address
        
        :param address: User's blockchain address
        :return: Dictionary with user's history
        """
        try:
            with open(self.users_path, 'r') as f:
                users = json.load(f)
            
            with open(self.messages_path, 'r') as m:
                messages = json.load(m)
            
            user_history = {
                'address': address,
                'total_messages_sent': 0,
                'total_messages_received': 0,
                'messages': []
            }
            
            for msg in messages:
                if msg['sender'] == address:
                    user_history['total_messages_sent'] += 1
                    user_history['messages'].append({
                        'type': 'sent',
                        'content': msg['content'],
                        'timestamp': msg['timestamp']
                    })
                if msg['recipient'] == address:
                    user_history['total_messages_received'] += 1
                    user_history['messages'].append({
                        'type': 'received',
                        'content': msg['content'],
                        'timestamp': msg['timestamp']
                    })
            
            return user_history
        
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                'address': address,
                'error': 'No history found'
            }
    
    def sync_network_data(self, other_validator_host: str):
        """
        Synchronize data with another validator node
        
        :param other_validator_host: IP:Port of another validator
        """
        try:
            host, port = other_validator_host.split(':')
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, int(port)))
                
                # Request and sync users
                s.send(b'SYNC_USERS')
                users_data = s.recv(4096)
                with open(self.users_path, 'wb') as f:
                    f.write(users_data)
                
                # Request and sync messages
                s.send(b'SYNC_MESSAGES')
                messages_data = s.recv(4096)
                with open(self.messages_path, 'wb') as f:
                    f.write(messages_data)
        
        except Exception as e:
            print(f"Sync failed: {e}")
    
    def cli_query(self, query_type: str, param: str = None):
        """
        CLI interface for querying validator data
        
        :param query_type: Type of query (addresses, history)
        :param param: Optional parameter (like address for history)
        """
        if query_type == 'addresses':
            return self.get_all_addresses()
        
        if query_type == 'history' and param:
            return self.get_user_history(param)
        
        return {"error": "Invalid query"}
    
    def validate_message(self, message: Dict[str, Any]) -> bool:
        """
        Validate incoming message
        
        :param message: Message to validate
        :return: Whether message is valid
        """
        try:
            # Check message structure
            if not all(key in message for key in ['sender', 'recipient', 'content']):
                return False
            
            # Optional: Add more validation logic
            # - Check sender's reputation
            # - Verify message signature
            # - Apply rate limiting
            
            return True
        except Exception as e:
            print(f"Message validation error: {e}")
            return False
    
    def process_message(self, message: Dict[str, Any]):
        """
        Process and reward valid messages
        
        :param message: Validated message
        """
        if self.validate_message(message):
            # Calculate and add message reward
            message_tx = self.messaging.send_message(
                sender_address=message['sender'],
                recipient_address=message['recipient'],
                message=message['content'],
                sender_signature=b'dummy_signature'  # Replace with actual signature
            )
            
            # Calculate message reward
            message_reward = self.messaging.get_message_reward(message_tx)
            self.rewards.add_message_reward(message['sender'], message_reward)
            
            print(f"Processed message from {message['sender']} to {message['recipient']}")
            print(f"Reward: {message_reward} DOU")
    
    def start_server(self):
        """Start the validator server"""
        self.server_socket.listen(5)
        print(f"Validator node listening on {self.host}:{self.port}")
        
        while True:
            client_socket, address = self.server_socket.accept()
            client_thread = threading.Thread(
                target=self.handle_client, 
                args=(client_socket, address)
            )
            client_thread.start()
    
    def handle_client(self, client_socket: socket.socket, address: tuple):
        """
        Handle incoming client connections
        
        :param client_socket: Connected client socket
        :param address: Client address
        """
        try:
            # Receive message
            data = client_socket.recv(4096).decode('utf-8')
            message = json.loads(data)
            
            # Process message
            self.process_message(message)
            
            # Respond to client
            response = {
                'status': 'validated',
                'message_id': message.get('message_id')
            }
            client_socket.send(json.dumps(response).encode('utf-8'))
        
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        
        finally:
            client_socket.close()
    
    def run(self):
        """Start the validator node"""
        server_thread = threading.Thread(target=self.start_server)
        server_thread.start()
        return server_thread
