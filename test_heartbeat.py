import sys
import os

# Ensure the root directory is in the Python path so absolute imports work
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from q_heartbeat import run_heartbeat

def main():
    print(">>> [TEST] Forcing manual execution of Q's Heartbeat...")
    run_heartbeat()
    print("\n>>> [TEST] Heartbeat execution finished.")

if __name__ == "__main__":
    run_heartbeat()