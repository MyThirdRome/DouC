import json
import os
import socket
import threading
import logging
import time
from typing import Dict, List, Any
import fcntl
import sys
import argparse

from src.blockchain.core import DOUBlockchain
from src.messaging.system import DOUMessaging
from src.rewards.system import DOURewardSystem

# Configure logging
def configure_logging(verbose=False):
    """
    Configure logging for the validator
    
    :param verbose: Enable debug logging
    """
    # Base logging configuration
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Log to console
            logging.StreamHandler(sys.stdout),
            # Log to file
            logging.FileHandler('/tmp/dou_validator.log', mode='a')
        ]
    )
    
    # Set logger for key components
    logging.getLogger('ValidatorNode').setLevel(log_level)
    logging.getLogger('DOUBlockchain').setLevel(log_level)
    logging.getLogger('DOUMessaging').setLevel(log_level)

class ValidatorLock:
    """
    Ensure only one validator instance runs at a time
    """
    def __init__(self, lock_file='/tmp/dou_validator.lock'):
        """
        Create a file-based lock to prevent multiple validator instances
        
        :param lock_file: Path to the lock file
        """
        self.lock_file = lock_file
        self.lock_handle = None
    
    def acquire(self):
        """
        Acquire the validator lock
        
        :raises RuntimeError: If another validator is already running
        """
        try:
            self.lock_handle = open(self.lock_file, 'w')
            try:
                # Try to acquire an exclusive, non-blocking lock
                fcntl.flock(self.lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except (IOError, OSError):
                self.lock_handle.close()
                raise RuntimeError("Another validator instance is already running")
            
            # Write current process ID
            self.lock_handle.write(str(os.getpid()))
            self.lock_handle.flush()
            logger.info(f"Validator lock acquired. PID: {os.getpid()}")
        except Exception as e:
            logger.error(f"Failed to acquire validator lock: {e}")
            raise
    
    def release(self):
        """
        Release the validator lock
        """
        try:
            if self.lock_handle:
                fcntl.flock(self.lock_handle.fileno(), fcntl.LOCK_UN)
                self.lock_handle.close()
                os.unlink(self.lock_file)
                logger.info("Validator lock released")
        except Exception as e:
            logger.error(f"Error releasing validator lock: {e}")

class ValidatorNode:
    def __init__(self, 
                 host: str = '0.0.0.0', 
                 port: int = 5001, 
                 data_dir: str = None,
                 validator_address: str = None,
                 max_port_attempts: int = 10):
        """
        Initialize Validator Node with process locking
        """
        # Acquire validator lock before initialization
        self.validator_lock = ValidatorLock()
        try:
            self.validator_lock.acquire()
        except RuntimeError as e:
            logger.error(str(e))
            sys.exit(1)
        
        try:
            # Use environment variables if set
            env_host = os.environ.get('DOU_VALIDATOR_HOST', f'{host}:{port}')
            host, port = env_host.split(':')
            port = int(port)
            
            self.host = host
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
            self.port_file = os.path.join(self.data_dir, 'validator_port.txt')
            
            # Initialize storage
            self._init_storage()
            
            # Load saved port if available
            saved_port = self._load_saved_port()
            if saved_port:
                port = saved_port
            
            # Blockchain components
            self.blockchain = DOUBlockchain()
            self.messaging = DOUMessaging()
            self.rewards = DOURewardSystem()
            
            # Dynamic port selection
            self.port = self._find_available_port(self.host, port, max_port_attempts)
            
            # Persist selected port
            self._save_port()
            
            # Network setup
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            logger.info(f"Binding validator to {self.host}:{self.port}")
            self.server_socket.bind((self.host, self.port))
            
            # Start listening
            self.server_socket.listen(50)
            logger.info(f"Validator node started on {self.host}:{self.port}")
            
            # Update environment variable
            os.environ['DOU_VALIDATOR_HOST'] = f'{self.host}:{self.port}'
            
            # Start accepting connections
            self._start_server()
        
        except Exception as e:
            # Ensure lock is released on any initialization error
            self.validator_lock.release()
            logger.error(f"Failed to initialize validator: {e}")
            raise
    
    def _find_available_port(self, host: str, initial_port: int, max_attempts: int = 10) -> int:
        """
        Find an available port by trying sequential ports
        
        :param host: Host to bind
        :param initial_port: Starting port to try
        :param max_attempts: Maximum number of port attempts
        :return: Available port number
        """
        current_port = initial_port
        for attempt in range(max_attempts):
            try:
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.bind((host, current_port))
                test_socket.close()
                return current_port
            except OSError:
                logger.warning(f"Port {current_port} in use, trying next")
                current_port += 1
        
        raise RuntimeError(f"Could not find an available port after {max_attempts} attempts")

    def _start_server(self):
        """
        Start the server in a separate thread to accept connections
        """
        try:
            # Bind to all interfaces
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind to all available interfaces
            self.server_socket.bind(('0.0.0.0', self.port))
            
            # Listen with a larger backlog
            self.server_socket.listen(50)
            
            logger.info(f"Server listening on all interfaces, port {self.port}")
            
            # Start accepting connections
            server_thread = threading.Thread(target=self._accept_connections)
            server_thread.daemon = True
            server_thread.start()
            
            logger.info("Server thread started successfully")
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            raise
    
    def _accept_connections(self):
        """
        Accept incoming network connections with enhanced logging
        """
        while True:
            try:
                # Accept connection
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
                # Prevent tight loop in case of persistent error
                time.sleep(1)
    
    def _handle_client(self, client_socket, address):
        """
        Handle individual client connections with enhanced logging
        
        :param client_socket: Connected client socket
        :param address: Client address tuple
        """
        try:
            logger.info(f"Received connection from {address}")
            
            # Set socket timeout
            client_socket.settimeout(10)
            
            # Receive data
            data = client_socket.recv(4096).decode('utf-8')
            logger.info(f"Received data from {address}: {data}")
            
            # Parse message
            try:
                message = json.loads(data)
                
                # Validate message
                if self.validate_message(message):
                    # Process message
                    self.process_message(message)
                    
                    # Prepare response
                    response = {
                        'status': 'validated',
                        'message_id': message.get('message_id', 'unknown')
                    }
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    logger.info(f"Sent validation response to {address}")
                else:
                    # Invalid message
                    response = {
                        'status': 'invalid',
                        'message_id': message.get('message_id', 'unknown')
                    }
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    logger.warning(f"Invalid message from {address}")
            
            except json.JSONDecodeError:
                logger.error(f"Failed to decode JSON from {address}")
                client_socket.send(json.dumps({
                    'status': 'error',
                    'message': 'Invalid JSON'
                }).encode('utf-8'))
        
        except socket.timeout:
            logger.error(f"Connection from {address} timed out")
        except Exception as e:
            logger.error(f"Error handling client {address}: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
    
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
        Handle CLI queries from the validator
        
        :param query_type: Type of query (e.g., 'list_addresses')
        :param param: Optional parameter for the query
        :return: Query result
        """
        if query_type == 'list_addresses':
            return self.list_network_addresses()
        
        if query_type == 'addresses':
            return self.get_all_addresses()
        
        if query_type == 'history' and param:
            return self.get_user_history(param)
        
        return {"error": "Invalid query"}
    
    def list_network_addresses(self):
        """
        List all registered network addresses
        
        :return: List of registered addresses
        """
        try:
            # Read users from persistent storage
            with open(self.users_path, 'r') as f:
                users = json.load(f)
                
            # Log and print addresses
            logger.info(f"Network Addresses ({len(users)}):")
            for address in users:
                logger.info(address)
                print(address)
            
            return list(users.keys())
        except FileNotFoundError:
            logger.warning("No users file found")
            print("No users registered in the network")
            return []
        except json.JSONDecodeError:
            logger.error("Error decoding users file")
            print("Error reading network addresses")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing addresses: {e}")
            print(f"Error listing network addresses: {e}")
            return []
    
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
    
    def _save_port(self):
        """
        Save the current port to a persistent file
        """
        try:
            with open(self.port_file, 'w') as f:
                f.write(str(self.port))
            logger.info(f"Saved validator port {self.port} to {self.port_file}")
        except Exception as e:
            logger.error(f"Failed to save port: {e}")

    def _load_saved_port(self):
        """
        Load previously saved port if available
        
        :return: Saved port or None
        """
        try:
            if os.path.exists(self.port_file):
                with open(self.port_file, 'r') as f:
                    saved_port = int(f.read().strip())
                    logger.info(f"Loaded saved port: {saved_port}")
                    return saved_port
        except Exception as e:
            logger.error(f"Error loading saved port: {e}")
        return None

    def run(self):
        """
        Start the validator node with proper cleanup
        """
        try:
            # Start validator logic
            server_thread = threading.Thread(target=self.start_server)
            server_thread.start()
            
            # Wait for server thread
            server_thread.join()
        except KeyboardInterrupt:
            logger.info("Validator interrupted by user")
        except Exception as e:
            logger.error(f"Validator runtime error: {e}")
        finally:
            # Always release the lock
            self.validator_lock.release()
            logger.info("Validator node shutting down")
    
    def __del__(self):
        """
        Ensure lock is released when object is deleted
        """
        try:
            self.validator_lock.release()
        except:
            pass

# Main execution block
if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='DOU Blockchain Validator Node')
    parser.add_argument('--verbose', action='store_true', 
                        help='Enable verbose logging')
    parser.add_argument('--host', type=str, default='0.0.0.0', 
                        help='Host to bind validator')
    parser.add_argument('--port', type=int, default=5001, 
                        help='Initial port to try')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Configure logging based on verbosity
    configure_logging(args.verbose)
    
    # Log startup information
    logger = logging.getLogger('ValidatorNode')
    logger.info("=" * 50)
    logger.info("DOU Blockchain Validator Node")
    logger.info("=" * 50)
    logger.info(f"Starting validator on {args.host}:{args.port}")
    logger.info(f"Verbose mode: {'Enabled' if args.verbose else 'Disabled'}")
    
    try:
        # Create validator instance
        validator = ValidatorNode(
            host=args.host, 
            port=args.port
        )
        
        # Run validator
        validator.run()
    
    except Exception as e:
        # Comprehensive error logging
        logger.error("Critical error during validator startup")
        logger.error(f"Error details: {e}")
        logger.error("Traceback:", exc_info=True)
        
        # Attempt to log system details
        try:
            import platform
            logger.error(f"System: {platform.system()}")
            logger.error(f"Python version: {platform.python_version()}")
        except:
            pass
        
        # Exit with error code
        sys.exit(1)
    
    # Graceful shutdown
    logger.info("Validator node shutdown complete")
    sys.exit(0)
