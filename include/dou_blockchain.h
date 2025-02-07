#pragma once

#include <string>
#include <vector>
#include <chrono>
#include <ctime>
#include <openssl/sha.h>
#include <openssl/aes.h>

namespace dou {
    // Unique DOU Address type
    using Address = std::string;

    // Unique transaction/message ID
    using TxId = std::string;

    // Enum for message types
    enum class MessageType {
        PRIVATE,
        GROUP
    };

    // Enum for group join types
    enum class GroupJoinType {
        INVITE_ONLY,
        OPEN_AUTO_JOIN,
        OPEN_ADMIN_APPROVAL
    };

    // Utility functions for generating unique IDs and hashes
    namespace utils {
        TxId generate_unique_tx_id();
        std::string sha256(const std::string& input);
    }
}
