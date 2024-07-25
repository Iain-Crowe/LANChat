from __future__ import annotations

import logging
import platform

# ANSI escape codes for colors
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BOLD_BLUE = "\033[1m\033[34m"
CYAN = "\033[36m"
BOLD_RED = "\033[1m\033[31m"

# Enable ANSI escape sequences on Windows
if platform.system() == "Windows":
    import ctypes

    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

class LogFormatter(logging.Formatter):
    def format(self, record):
        log_colors = {
            logging.DEBUG: CYAN,
            logging.INFO: GREEN,
            logging.WARNING: YELLOW,
            logging.ERROR: RED,
            logging.CRITICAL: BOLD_RED,
        }
        color = log_colors.get(record.levelno, RESET)
        record.asctime = f"{BOLD_BLUE}{self.formatTime(record, self.datefmt)}{RESET}"
        record.levelname = f"{color}{record.levelname}{RESET}"
        return f"{record.asctime}: {record.levelname} - {record.msg}"


def init_logger() -> None:
    """
    Initialize the logger using custom `LogFormatter`
    """
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    formatter = LogFormatter(
        "%(asctime)s: %(levelname)s - %(message)s", datefmt="%H:%M:%S %Y-%m-%d"
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

# Import this logger to use elsewhere
logger = logging.getLogger(__name__)
init_logger()