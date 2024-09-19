"""
OmegaConf helper functions
"""

from typing import Dict, Optional, Any
from omegaconf import DictConfig, OmegaConf


def safe_get(conf: OmegaConf, attr: str) -> any:
    """
    Get attribute value from OmegaConf object with None if attribute is not found.

    Args:
        conf: OmegaConf object
        attr: Attribute to access in dot notation

    Returns:
        Attribute value or None if not found
    """
    try:
        return OmegaConf.select(conf, attr, default=None)
    except AttributeError:
        return None


def conf_key_from_value(conf: OmegaConf, value: Any) -> Optional[str]:
    """
    Finds key in OmegaConf from value

    Args:
        conf [Omegaconf]: Omegaconfig to find key from by value
        value: [Any]: The value to search by

    Returns:
        [Optional[str]]: The key of the value or None if not found.
    """
    dict = OmegaConf.to_container(conf)

    for key, dict_value in dict.items():
        if value == dict_value:
            return key
