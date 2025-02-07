#pragma once

#include "dou_blockchain.h"
#include <optional>
#include <chrono>

namespace dou {
    class Message {
    public:
        Message(const Address& sender, const Address& receiver, 
                const std::string& content, MessageType type);

        // Encrypt message using AES-256
        void encrypt(const std::string& key);

        // Decrypt message
        std::string decrypt(const std::string& key);

        // Getters
        TxId get_tx_id() const;
        Address get_sender() const;
        Address get_receiver() const;
        std::string get_content_hash() const;
        std::chrono::system_clock::time_point get_timestamp() const;
        MessageType get_type() const;

        // Check message expiry (24 hours default)
        bool is_expired() const;

        // Optional: Extend message storage
        void extend_storage(int days);

    private:
        TxId m_tx_id;
        Address m_sender;
        Address m_receiver;
        std::string m_encrypted_content;
        std::string m_content_hash;
        std::chrono::system_clock::time_point m_timestamp;
        MessageType m_type;
        std::optional<std::chrono::system_clock::time_point> m_storage_expiry;
    };

    class GroupMessage : public Message {
    public:
        GroupMessage(const Address& sender, const std::string& group_id, 
                     const std::string& content);

        std::string get_group_id() const;

    private:
        std::string m_group_id;
    };
}
