#include "../include/dou_blockchain.h"
#include "../include/message.h"
#include "../include/reward_system.h"
#include "../include/spam_prevention.h"
#include "../include/validator.h"

#include <iostream>

int main() {
    // Demonstrate DOU Blockchain core functionality
    try {
        // Create addresses
        dou::Address sender_addr = "DOU_SENDER_123";
        dou::Address receiver_addr = "DOU_RECEIVER_456";

        // Create a message
        dou::Message message(sender_addr, receiver_addr, 
                             "Hello, DOU Blockchain!", 
                             dou::MessageType::PRIVATE);

        // Encrypt message (in real scenario, use proper key management)
        message.encrypt("sample_encryption_key");

        // Check spam prevention
        dou::SpamPrevention spam_checker;
        if (spam_checker.check_rate_limit(sender_addr)) {
            // Calculate rewards
            double send_reward = dou::RewardSystem::calculate_send_reward(message);
            
            std::cout << "Message sent successfully!" << std::endl;
            std::cout << "Sender Reward: " << send_reward << " DOU tokens" << std::endl;
        } else {
            std::cout << "Message blocked: Rate limit exceeded" << std::endl;
        }

        // Validator demonstration
        dou::Validator validator(sender_addr, 500.0);
        double validator_reward = validator.calculate_base_reward();
        
        std::cout << "Validator Base Reward: " << validator_reward << " DOU tokens" << std::endl;
    } 
    catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
