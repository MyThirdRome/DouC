#pragma once

#include "dou_blockchain.h"
#include <cmath>
#include <random>

namespace dou {
    class Validator {
    public:
        Validator(const Address& address, double initial_stake);

        // Stake management
        void increase_stake(double amount);
        void decrease_stake(double amount);
        double get_stake() const;

        // Age and participation tracking
        void update_validator_age();
        std::chrono::years get_validator_age() const;

        // Reward calculation
        double calculate_base_reward() const;
        double calculate_longevity_bonus() const;
        double calculate_priority_score() const;

        // Validator selection and priority
        bool is_eligible_to_validate() const;

    private:
        Address m_address;
        double m_stake;
        std::chrono::system_clock::time_point m_join_timestamp;

        // Reward constants
        static constexpr double MINIMUM_STAKE = 100.0;
        static constexpr double MAX_STAKE_MULTIPLIER = 1.5;
        static constexpr double BASE_REWARD_RATE = 0.01;

        // Random number generator for fair selection
        std::random_device m_rd;
        std::mt19937 m_gen;
    };

    class ValidatorRegistry {
    public:
        void register_validator(const Validator& validator);
        Validator select_next_validator();
        std::vector<Validator> get_top_validators(int count);

    private:
        std::vector<Validator> m_validators;
    };
}
