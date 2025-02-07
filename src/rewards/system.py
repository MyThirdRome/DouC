import time
from typing import Dict, List

class DOURewardSystem:
    def __init__(self):
        self.user_rewards: Dict[str, float] = {}
        self.validator_rewards: Dict[str, Dict] = {}
    
    def calculate_message_reward(self, sender: str, is_replied: bool = False) -> float:
        """
        Calculate rewards for messaging activity
        
        :param sender: User's DOU address
        :param is_replied: Whether the message received a reply
        :return: Reward amount in DOU tokens
        """
        base_reward = 0.1  # 0.1 DOU for sending a message
        reply_bonus = 0.05 if is_replied else 0
        
        return base_reward + reply_bonus
    
    def calculate_validator_reward(self, validator_address: str, 
                                    locked_amount: float, 
                                    validator_age: float) -> float:
        """
        Calculate validator rewards based on stake and longevity
        
        :param validator_address: Validator's DOU address
        :param locked_amount: Amount of tokens locked
        :param validator_age: Age of validator in years
        :return: Reward multiplier
        """
        # Base reward multipliers
        base_multipliers = {
            0: 0.50,  # No lock
            1: 1.00,  # Minimum required lock
            1.25: 1.25,  # 1.25x minimum
            1.50: 1.50   # Maximum multiplier
        }
        
        # Longevity bonus
        longevity_bonus = min(0.75, validator_age * 0.25)  # Max 75% bonus
        
        # Determine stake multiplier
        stake_multiplier = min(base_multipliers.get(1.50, 1.50), 
                               base_multipliers.get(locked_amount, 1.00))
        
        return stake_multiplier * (1 + longevity_bonus)
    
    def add_message_reward(self, user_address: str, reward: float):
        """
        Add messaging reward to user's total
        
        :param user_address: User's DOU address
        :param reward: Reward amount
        """
        if user_address not in self.user_rewards:
            self.user_rewards[user_address] = 0
        
        self.user_rewards[user_address] += reward
    
    def add_validator_reward(self, validator_address: str, 
                              base_reward: float, 
                              reward_multiplier: float):
        """
        Add validator reward with multipliers
        
        :param validator_address: Validator's DOU address
        :param base_reward: Base reward amount
        :param reward_multiplier: Reward multiplier
        """
        if validator_address not in self.validator_rewards:
            self.validator_rewards[validator_address] = {
                'total_rewards': 0,
                'reward_history': []
            }
        
        total_reward = base_reward * reward_multiplier
        
        self.validator_rewards[validator_address]['total_rewards'] += total_reward
        self.validator_rewards[validator_address]['reward_history'].append({
            'timestamp': time.time(),
            'reward': total_reward,
            'multiplier': reward_multiplier
        })
    
    def get_user_total_rewards(self, user_address: str) -> float:
        """
        Get total rewards for a user
        
        :param user_address: User's DOU address
        :return: Total rewards
        """
        return self.user_rewards.get(user_address, 0)
    
    def get_validator_total_rewards(self, validator_address: str) -> float:
        """
        Get total rewards for a validator
        
        :param validator_address: Validator's DOU address
        :return: Total rewards
        """
        return self.validator_rewards.get(validator_address, {}).get('total_rewards', 0)
