#include "../include/reward_system.h"
#include <cmath>
#include <unordered_map>

namespace dou {
    // Track message history for reward calculation
    static std::unordered_map<Address, std::vector<Message>> message_history;

    double RewardSystem::calculate_send_reward(const Message& message) {
        // Base reward for sending a message
        double base_reward = BASE_SEND_REWARD;

        // Store message in history
        message_history[message.get_sender()].push_back(message);

        return base_reward;
    }

    double RewardSystem::calculate_reply_reward(const Message& original_message, 
                                                const Message& reply_message) {
        // Higher reward for replies to encourage conversation
        double reply_reward = BASE_SEND_REWARD * REPLY_MULTIPLIER;

        // Additional logic could include checking message content quality
        return reply_reward;
    }

    double RewardSystem::calculate_activity_bonus(const Address& user, 
                                                  int messages_sent_in_period) {
        // Bonus for consistent network participation
        if (messages_sent_in_period >= ACTIVITY_BONUS_THRESHOLD) {
            return BASE_SEND_REWARD * 0.5;  // 50% bonus
        }
        return 0.0;
    }

    double RewardSystem::calculate_total_reward(const Message& message, bool is_reply) {
        double total_reward = 0.0;

        // Base send reward
        total_reward += calculate_send_reward(message);

        // Reply bonus if applicable
        if (is_reply) {
            // In a real implementation, you'd pass the original message
            total_reward += calculate_reply_reward(message, message);
        }

        // Check activity bonus
        auto& user_messages = message_history[message.get_sender()];
        int messages_in_period = user_messages.size();
        total_reward += calculate_activity_bonus(message.get_sender(), messages_in_period);

        return total_reward;
    }
}
