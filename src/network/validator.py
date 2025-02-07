import json
import os
import socket
import threading
import logging
from typing import Dict, List, Any

from src.blockchain.core import DOUBlockchain
from src.messaging.system import DOUMessaging
from src.rewards.system import DOURewardSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/dou_validator.log'),
        logging.StreamHandler()  # This will print to console
    ]
)
logger = logging.getLogger('ValidatorNode')

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
        try:
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
            
            # Network setup
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            logger.info(f"Binding validator to {host}:{port}")
            self.server_socket.bind((self.host, self.port))
            
            # Start listening
            self.server_socket.listen(5)
            logger.info(f"Validator node started on {host}:{port}")
            
            # Start accepting connections
            self._start_server()
        
        except Exception as e:
            logger.error(f"Failed to initialize validator: {e}")
            raise
    
    def _start_server(self):
        """
        Start the server in a separate thread to accept connections
        """
        try:
            server_thread = threading.Thread(target=self._accept_connections)
            server_thread.daemon = True
            server_thread.start()
            logger.info("Server thread started successfully")
        except Exception as e:
            logger.error(f"Failed to start server thread: {e}")
    
    def _accept_connections(self):
        """
        Accept incoming network connections
        """
        while True:
            try:
                client_socket, address = self.server_socket.accept()
                logger.info(f"Accepted connection from {address}")
                
                # Handle connection in a separate thread
                client_thread = threading.Thread(
                    target=self._handle_client, 
                    args=(client_socket, address)
                )
                client_thread.start()
            except Exception as e:
                logger.error(f"Error accepting connection: {e}")
    
    def _handle_client(self, client_socket, address):
        """
        Handle individual client connections
        """
        try:
            # Receive data from client
            data = client_socket.recv(1024).decode('utf-8')
            logger.info(f"Received data from {address}: {data}")
            
            # Process the received data
            # Add your network sync logic here
            
            client_socket.close()
        except Exception as e:
            logger.error(f"Error handling client {address}: {e}")
    
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
            logger.error(f"Sync failed: {e}")
    
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
            logger.error(f"Message validation error: {e}")
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
            
            logger.info(f"Processed message from {message['sender']} to {message['recipient']}")
            logger.info(f"Reward: {message_reward} DOU")
    
    def run(self):
        """Start the validator node"""
        server_thread = threading.Thread(target=self.start_server)
        server_thread.start()
        return server_thread

# Main execution
if __name__ == '__main__':
    try:
        # Get host and port from environment or use defaults
        host = os.environ.get('DOU_VALIDATOR_HOST', '0.0.0.0').split(':')[0]
        port = int(os.environ.get('DOU_VALIDATOR_HOST', '0.0.0.0:5001').split(':')[1])
        
        validator = ValidatorNode(host=host, port=port)
        
        # Keep the main thread running
        while True:
            pass
    except Exception as e:
        logger.error(f"Validator startup failed: {e}")
        raise
