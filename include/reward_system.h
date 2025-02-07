#pragma once

#include "dou_blockchain.h"
#include "message.h"

namespace dou {
    class RewardSystem {
    public:
        // Calculate reward for sending a message
        static double calculate_send_reward(const Message& message);

        // Calculate reward for receiving a reply
        static double calculate_reply_reward(const Message& original_message, 
                                             const Message& reply_message);

        // Calculate activity bonus for consistent users
        static double calculate_activity_bonus(const Address& user, 
                                               int messages_sent_in_period);

        // Total reward calculation
        static double calculate_total_reward(const Message& message, 
                                             bool is_reply = false);

    private:
        // Constants for reward calculation
        static constexpr double BASE_SEND_REWARD = 0.1;
        static constexpr double REPLY_MULTIPLIER = 1.5;
        static constexpr double ACTIVITY_BONUS_THRESHOLD = 10;
    };
}
