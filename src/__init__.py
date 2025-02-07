# DOU Blockchain main package

"""
DOU Blockchain Package Initialization
"""

# Package version
__version__ = "0.1.0"

# Import key components for easy access
from .network.validator import ValidatorNode
from .blockchain.core import DOUBlockchain
from .messaging.system import DOUMessaging
from .rewards.system import DOURewardSystem
