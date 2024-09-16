"""
Helper functions for importing modules
"""

import importlib
import os
import sys

# Add the project root to the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from common.logger_helper import init_logger

logger = init_logger()


def dynamic_import(module_path: str, alias: str):
    """
    Dynamically imports a module based on the given path.

    Args:
        module_path: Relative path to the module to import
        alias: Alias for the imported module's main function

    Returns:
        Imported module's function
    """
    logger.info(f"Importing module: {module_path}")
    try:
        module = importlib.import_module(module_path)
    except KeyboardInterrupt:
        logger.critical(f"Interrupted while importing module: {module_path}")
        sys.exit(1)

    return getattr(module, alias)
