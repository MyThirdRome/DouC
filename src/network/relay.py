import socket
import json
import threading
import uuid
import sys
import os
from typing import Dict, Any

class NetworkRelay:
    def __init__(self, 
                 host: str = '0.0.0.0', 
                 port: int = 5000, 
                 validator_host: str = None):
        """
        Initialize network relay for DOU Blockchain
        
        :param host: Host to bind the server
        :param port: Port to listen on
        :param validator_host: Address of the main validator node
        """
        self.host = host
        self.port = port
        self.validator_host = validator_host
        
        # Message queue for pending messages
        self.message_queue: Dict[str, Dict[str, Any]] = {}
        
        # Server socket with Windows-specific error handling
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Set socket options for better cross-platform compatibility
        try:
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except Exception as e:
            print(f"Warning: Could not set SO_REUSEADDR: {e}")
        
        # Windows-specific socket option
        if sys.platform.startswith('win'):
            try:
                self.server_socket.ioctl(socket.SIO_KEEPALIVE_VALS, (1, 60000, 30000))
            except Exception as e:
                print(f"Could not set Windows-specific socket options: {e}")
        
        try:
            self.server_socket.bind((self.host, self.port))
        except PermissionError:
            print(f"Permission denied. Try running as administrator or use a port > 1024.")
            sys.exit(1)
        except Exception as e:
            print(f"Binding error: {e}")
            sys.exit(1)
        
        # Validator connection
        self.validator_socket = None
        if validator_host:
            self.connect_to_validator()
    
    def connect_to_validator(self):
        """Establish connection with the validator node"""
        try:
            self.validator_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host, port = self.validator_host.split(':')
            self.validator_socket.connect((host, int(port)))
            print(f"Connected to validator at {self.validator_host}")
        except Exception as e:
            print(f"Could not connect to validator: {e}")
            self.validator_socket = None
    
    def generate_message_id(self) -> str:
        """Generate a unique message ID"""
        return str(uuid.uuid4())
    
    def send_to_validator(self, message: Dict[str, Any]):
        """
        Send message to validator node for validation
        
        :param message: Message dictionary to send
        """
        if not self.validator_socket:
            print("No validator connection available")
            return False
        
        try:
            # Add unique message ID
            message['message_id'] = self.generate_message_id()
            
            # Send serialized message
            serialized_message = json.dumps(message).encode('utf-8')
            self.validator_socket.send(serialized_message)
            return True
        except Exception as e:
            print(f"Error sending message to validator: {e}")
            return False
    
    def broadcast_message(self, message: Dict[str, Any]):
        """
        Broadcast message to network
        
        :param message: Message dictionary to broadcast
        """
        # Add to local message queue
        message_id = self.generate_message_id()
        message['message_id'] = message_id
        self.message_queue[message_id] = message
        
        # Send to validator for validation and global broadcast
        self.send_to_validator(message)
    
    def start_server(self):
        """Start the network relay server"""
        self.server_socket.listen(5)
        print(f"Network relay listening on {self.host}:{self.port}")
        
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
            self.broadcast_message(message)
            
            # Respond to client
            response = {
                'status': 'success',
                'message_id': message.get('message_id')
            }
            client_socket.send(json.dumps(response).encode('utf-8'))
        
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        
        finally:
            client_socket.close()
    
    def run(self):
        """Start the network relay"""
        server_thread = threading.Thread(target=self.start_server)
        server_thread.start()
        return server_thread
