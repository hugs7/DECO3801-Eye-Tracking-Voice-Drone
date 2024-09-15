"""
Helper for importing modules dynamically across the project repository.
Adds the project root to enable imports from outside the entry point.
E.g. if the entry point is /app/src/main.py we can then import from /voice_control/... 
without any issues.
"""

import importlib
import os
import sys

# Add the project root to the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, project_root)

from common.logger_helper import init_logger

logger = init_logger()


def dynamic_import(module_path: str, alias: str) -> object:
    """
    Dynamically imports a module based on the given path. Path should be given as
    a Python module path. E.g. "voice_control.src.voice_controller".

    Args:
        module_path (str): Relative path to the module to import
        alias (str): Alias for the imported module's main function

    Returns:
        (object) Imported module
    """
    logger.info(f"Importing module: {module_path}")

    try:
        module = importlib.import_module(module_path)
    except KeyboardInterrupt:
        logger.critical(f"Interrupted while importing module: {module_path}")
        sys.exit(1)

    return getattr(module, alias)
