import socket
import json
import threading
from typing import Dict, Any

from blockchain.core import DOUBlockchain
from messaging.system import DOUMessaging
from rewards.system import DOURewardSystem

class ValidatorNode:
    def __init__(self, 
                 host: str = '0.0.0.0', 
                 port: int = 5001,
                 validator_address: str = None):
        """
        Initialize validator node
        
        :param host: Host to bind the server
        :param port: Port to listen on
        :param validator_address: DOU address of the validator
        """
        self.host = host
        self.port = port
        self.validator_address = validator_address
        
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
