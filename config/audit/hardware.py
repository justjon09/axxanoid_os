import platform
import subprocess
import shutil

def run_hardware_audit():
    alerts = []

    # 1. Verify Operating System (Darwin = macOS)
    current_os = platform.system()
    if current_os != "Darwin":
        alerts.append(f"CRITICAL OS MISMATCH: Expected Darwin (macOS), detected {current_os}.")

    # 2. Verify Apple Silicone (M4 Pro)
    try:
        # sysclt directly queries the macOS kernel for the exact chip string
        cpu_info = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"]).decode("utf-8").strip()
        
        # Check for "M4" or "M4 Pro"
        if "M4" not in cpu_info:    
            alerts.append(f"HARDWARE DEGRADATION: Expected Apple M4 Pro architecture. Detected: {cpu_info}")
    except Exception as e:
        alerts.append(f"CRITICAL KERNEL ERROR: Failed to query CPU architecture. Details: {str(e)}")

    # 3. Verify VRAM / Storage capacity for ChromaDB 
    # Checking if there is less than 15GB of free space on the primary drive
    total, used, free = shutil.disk_usage("/")
    free_gb = free / (1024 ** 3)
    if free_gb < 15.0:
        alerts.append(f"STORAGE WARNING: Primary drive space critically low. Only {free_gb:.1f} GB remaining. Vector vault expansion at risk.")

    # 4. Output Results
    # If alerts exist, print them. q_heartbeat.py captures this stdout.
    if alerts:
        for alert in alerts:
            print(alert)
    # If nothing is printed, q_heartbeat.py automatically assumes "NOMINAL".