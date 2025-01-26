from datetime import datetime
import os
import logging

def setup_logging(log_dir):
    """Set up a unified logger for STS and Plugins with dynamic log file names."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")      # Generate a timestamped log file name
    log_file = os.path.join(log_dir, f"STSLOG_{timestamp}.txt")
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger("UnifiedLogger")    # Get the unified logger

    if logger.hasHandlers():        # Explicitly clear existing handlers to avoid duplicates
        logger.handlers.clear()

    class UnifiedFormatter(logging.Formatter):     # Custom formatter for log entries
        def format(self, record):
            prefix = "[__STS__]" if record.name == "STS" else "[PLUGIN ]"
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return f"{prefix} {current_time} [{record.levelname}] - {record.getMessage()}"

    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_file)       # File handler for writing logs to the timestamped file
    file_handler.setFormatter(UnifiedFormatter())
    logger.addHandler(file_handler)
    return logger


def initialize_loggers(logger):
    """Initialize separate loggers for STS and Plugins."""
    
    # STS Logger
    sts_logger = logging.getLogger("STS")
    if sts_logger.handlers:
        sts_logger.handlers.clear()
    sts_logger.propagate = False
    sts_logger.setLevel(logging.DEBUG)
    sts_logger.addHandler(logger.handlers[0])

    # Plugin Logger
    plugin_logger = logging.getLogger("PLUGIN")
    if plugin_logger.handlers:
        plugin_logger.handlers.clear()
    plugin_logger.propagate = False
    plugin_logger.setLevel(logging.DEBUG)
    plugin_logger.addHandler(logger.handlers[0])

    return sts_logger, plugin_logger


