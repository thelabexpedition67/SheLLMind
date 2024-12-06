import os

DEBUG_FILE = os.path.join(os.path.dirname(__file__), "debug.log")

def clear_debug_log():
    with open(DEBUG_FILE, "w") as f:
        f.write("Debug Log Initialized\n")

def debug(message):
    with open(DEBUG_FILE, "a") as f:
        f.write(message + "\n")
