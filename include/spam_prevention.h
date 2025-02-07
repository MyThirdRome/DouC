#pragma once

#include "dou_blockchain.h"
#include "message.h"
#include <unordered_map>
#include <chrono>

namespace dou {
    class SpamPrevention {
    public:
        // Check if a message passes rate limits
        bool check_rate_limit(const Address& sender);

        // Implement Proof-of-Message Work (PoMW)
        bool validate_proof_of_message_work(const Message& message);

        // Track and manage user reputation
        void update_user_reputation(const Address& user, bool positive_interaction);
        double get_user_reputation(const Address& user) const;

        // Blacklist management
        void add_to_blacklist(const Address& user);
        bool is_blacklisted(const Address& user) const;

    private:
        // Rate limit tracking
        std::unordered_map<Address, std::vector<std::chrono::system_clock::time_point>> m_message_timestamps;
        
        // Reputation tracking
        std::unordered_map<Address, double> m_user_reputation;
        
        // Blacklist
        std::unordered_set<Address> m_blacklist;

        // Constants
        static constexpr int MAX_MESSAGES_PER_PERIOD = 10;
        static constexpr std::chrono::minutes MESSAGE_PERIOD{5};
    };
}
