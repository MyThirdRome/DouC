# DOU Blockchain: Decentralized Messaging Platform

## Overview
DOU Blockchain is a revolutionary decentralized messaging platform that provides free messaging with a unique reward system and robust spam prevention mechanisms.

## Key Features
- 🚀 Free Messaging
- 💰 Reward System for Network Participation
- 🛡️ Advanced Spam Prevention
- 🔒 End-to-End Encryption
- 📊 Fair Validator Selection

## Prerequisites
- C++17 Compiler
- OpenSSL Development Libraries
- CMake 3.10+

## Building the Project
```bash
mkdir build && cd build
cmake ..
make
```

## Running
```bash
./dou_blockchain
```

## Components
- `Message`: Handles message creation, encryption, and storage
- `RewardSystem`: Calculates rewards for network participation
- `SpamPrevention`: Implements rate limits and reputation tracking
- `Validator`: Manages validator selection and rewards

## Roadmap
- [ ] Complete implementation of core components
- [ ] Add comprehensive unit tests
- [ ] Implement networking layer
- [ ] Create wallet and transaction modules

## License
MIT License
