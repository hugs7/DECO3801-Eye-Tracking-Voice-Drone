"""
OmegaConf helper functions
"""

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
