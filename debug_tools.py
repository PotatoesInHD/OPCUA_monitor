import logging

def inspect_filter(record: logging.LogRecord) -> bool: # use to inspect logs
    print(f"Logger: {record.name} | Level: {record.levelname} ({record.levelno}) | Message: {record.getMessage()}")
    return True  # Let it pass through


'''
process_time = 0
last_time = 0
skip = False
if skip == False:
    last_time = time.perf_counter_ns()

if skip == True:
    process_time = time.perf_counter_ns() - last_time
print(process_time)
skip = not skip'''
