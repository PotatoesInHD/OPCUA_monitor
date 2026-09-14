import logging

def inspect_filter(record: logging.LogRecord) -> bool: # use to inspect logs
    print(f"Logger: {record.name} | Level: {record.levelname} ({record.levelno}) | Message: {record.getMessage()}")
    return True  # Let it pass through
