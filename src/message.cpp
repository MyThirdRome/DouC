#include "../include/message.h"
#include <openssl/evp.h>
#include <stdexcept>
#include <random>

namespace dou {
    Message::Message(const Address& sender, const Address& receiver, 
                     const std::string& content, MessageType type)
        : m_tx_id(utils::generate_unique_tx_id()),
          m_sender(sender),
          m_receiver(receiver),
          m_content_hash(utils::sha256(content)),
          m_timestamp(std::chrono::system_clock::now()),
          m_type(type) {
        // Placeholder for content - in real implementation, this would be more secure
        m_encrypted_content = content;
    }

    void Message::encrypt(const std::string& key) {
        // Simplified encryption - in production, use more robust methods
        // This is a placeholder implementation
        std::string salt = utils::sha256(m_tx_id);
        m_encrypted_content = salt + m_encrypted_content;
    }

    std::string Message::decrypt(const std::string& key) {
        // Simplified decryption - in production, use more robust methods
        if (m_encrypted_content.length() <= 64) {
            throw std::runtime_error("Invalid encrypted content");
        }
        return m_encrypted_content.substr(64);
    }

    TxId Message::get_tx_id() const { return m_tx_id; }
    Address Message::get_sender() const { return m_sender; }
    Address Message::get_receiver() const { return m_receiver; }
    std::string Message::get_content_hash() const { return m_content_hash; }
    std::chrono::system_clock::time_point Message::get_timestamp() const { return m_timestamp; }
    MessageType Message::get_type() const { return m_type; }

    bool Message::is_expired() const {
        auto now = std::chrono::system_clock::now();
        auto expiry = m_timestamp + std::chrono::hours(24);
        return now > expiry;
    }

    void Message::extend_storage(int days) {
        m_storage_expiry = m_timestamp + std::chrono::days(days);
    }

    // Group Message Implementation
    GroupMessage::GroupMessage(const Address& sender, const std::string& group_id, 
                               const std::string& content)
        : Message(sender, "", content, MessageType::GROUP), 
          m_group_id(group_id) {}

    std::string GroupMessage::get_group_id() const {
        return m_group_id;
    }

    // Utility function implementations
    namespace utils {
        TxId generate_unique_tx_id() {
            // Use a combination of timestamp and random number
            std::random_device rd;
            std::mt19937 gen(rd());
            std::uniform_int_distribution<> dis(0, 99999);

            auto now = std::chrono::system_clock::now();
            auto timestamp = std::chrono::duration_cast<std::chrono::milliseconds>(
                now.time_since_epoch()).count();

            return "DOU-" + std::to_string(timestamp) + "-" + std::to_string(dis(gen));
        }

        std::string sha256(const std::string& input) {
            unsigned char hash[SHA256_DIGEST_LENGTH];
            SHA256_CTX sha256;
            SHA256_Init(&sha256);
            SHA256_Update(&sha256, input.c_str(), input.size());
            SHA256_Final(hash, &sha256);

            std::stringstream ss;
            for(int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
                ss << std::hex << std::setw(2) << std::setfill('0') << (int)hash[i];
            }
            return ss.str();
        }
    }
}
