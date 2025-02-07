# DOU Blockchain: Free Messaging + Rewards Network

## Overview
DOU Blockchain is a decentralized communication platform that offers free messaging with a unique rewards system. Users can send messages without fees and earn DOU tokens for active participation.

## Key Features
- 🆓 Free Messaging
- 💰 Rewards for Network Participation
- 🛡️ Advanced Spam Prevention
- 🔒 Encrypted, Private Communication

## System Components
1. **Blockchain Core**: Manages transactions, blocks, and validator registration
2. **Messaging System**: Handles message encryption, sending, and spam prevention
3. **Rewards System**: Calculates and distributes rewards for messaging and validation

## Installation
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Windows Deployment

### Prerequisites
- Windows 10 or 11
- Python 3.9+ (64-bit)
- Git Bash or Windows Subsystem for Linux (WSL) recommended

### Installation Steps
1. **Install Python**
   - Download from [Python Official Website](https://www.python.org/downloads/windows/)
   - **IMPORTANT**: Check "Add Python to PATH" during installation

2. **Clone the Repository**
   ```powershell
   git clone https://github.com/yourusername/dou-blockchain.git
   cd dou-blockchain
   ```

3. **Set Up Virtual Environment**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

4. **Install Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

5. **Configure Network**
   - Open Command Prompt or PowerShell
   - Set environment variables:
     ```powershell
     $env:DOU_VALIDATOR_HOST = "YOUR_LINUX_MACHINE_IP:5001"
     $env:DOU_RELAY_HOST = "YOUR_LINUX_MACHINE_IP:5000"
     ```

6. **Run Commands**
   ```powershell
   python cli.py create
   python cli.py network_send RECIPIENT_ADDRESS "Your message"
   ```

### Troubleshooting
- Ensure firewall allows Python network connections
- Check that IP address is correct
- Verify Python installation with `python --version`

### Recommended Tools
- [Windows Terminal](https://github.com/microsoft/terminal)
- [Visual Studio Code](https://code.visualstudio.com/)

## Running Tests
```bash
python3 -m pytest tests/
```

## CLI Usage

### Create a New User
```bash
python3 cli.py create
```

### Send a Message
```bash
python3 cli.py send "Hello, DOU Blockchain!"
```

### Check Rewards
```bash
python3 cli.py rewards
```

### Register as a Validator
```bash
python3 cli.py validate 100  # Stake 100 DOU
```

## Cross-Platform Deployment

### Docker Deployment
Deploy the DOU Blockchain anywhere with Docker:

```bash
# Build the Docker image
docker build -t dou-blockchain .

# Run the CLI in a container
docker run -v $(pwd)/data:/app/data dou-blockchain create

# Use environment variables for customization
docker run -e DOU_DATA_DIR=/custom/path -e DOU_MAX_USERS=20 dou-blockchain
```

### Environment Variables
- `DOU_DATA_DIR`: Custom data storage directory
- `DOU_MAX_USERS`: Maximum number of users (default: 10)
- `PYTHONPATH`: Set to `/app/src` in containerized environments

### Supported Platforms
- Linux
- macOS
- Windows (with Docker Desktop)
- Cloud Platforms (AWS, GCP, Azure)

### Minimum Requirements
- Python 3.9+
- Docker (optional, recommended)
- 2GB RAM
- 10GB Disk Space

## Reward Mechanism
- Base reward for sending messages
- Higher rewards for receiving replies
- Validator rewards based on stake and longevity

## Spam Prevention
- Rate limiting
- Personal blacklists
- Proof-of-Message Work (PoMW)

## Contributing
Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License.
