import logging

from lib.constants import *


def initialize_logger(debug_level, action_name):

    color = COLOUR_BLUE
    if action_name == "upload":
        color = COLOUR_GREEN
    elif action_name == "download":
        color = COLOUR_RED

    logging.basicConfig(
        format=f"[%(asctime)s] - [{color}{action_name}{COLOUR_END} %(levelname)s] - %(message)s",
        level=debug_level,
        datefmt="%Y/%m/%d %H:%M:%S",
    )
    logging.debug(f"Setting {logging.getLevelName(debug_level)} log level")

    logger = logging.getLogger(__name__)

    return logger
