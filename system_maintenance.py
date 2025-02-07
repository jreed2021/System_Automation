import os
import shutil
import psutil
import logging
import subprocess
from datetime import datetime

# Set up logging
log_file = "system_maintenance.log"
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(message)s")

# Function to run PowerShell commands
def run_powershell(command):
    try:
        result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        logging.error(f"Error running PowerShell command '{command}': {e}")
        return None

# Function to clear Windows temporary files using PowerShell
def clear_temp_files():
    logging.info("Clearing temporary files...")
    ps_command = 'Remove-Item -Path "$env:TEMP\*" -Force -Recurse'
    run_powershell(ps_command)
    logging.info("Temporary files cleared.")

# Function to flush DNS cache
def flush_dns_cache():
    logging.info("Flushing DNS cache...")
    run_powershell("Clear-DnsClientCache")
    logging.info("DNS cache flushed.")

# Function to restart Windows Explorer (optional)
def restart_explorer():
    logging.info("Restarting Windows Explorer...")
    run_powershell("Stop-Process -Name explorer -Force")
    logging.info("Windows Explorer restarted.")

# Function to check disk usage
def check_disk_usage():
    total, used, free = shutil.disk_usage("/")
    report = f"Disk Usage: {used / (1024**3):.2f}GB used, {free / (1024**3):.2f}GB free"
    logging.info(report)
    return report

# Function to monitor running processes
def list_running_processes():
    process_list = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        process_list.append(f"PID: {proc.info['pid']} | Name: {proc.info['name']} | CPU: {proc.info['cpu_percent']}%")
    logging.info(f"Running Processes Logged ({len(process_list)} total)")
    return "\n".join(process_list)

# Function to retrieve Windows Event Logs
def get_event_logs():
    logging.info("Retrieving Windows Event Logs...")
    ps_command = 'Get-EventLog -LogName System -Newest 5 | Format-Table -AutoSize'
    event_logs = run_powershell(ps_command)
    logging.info("Windows Event Logs retrieved.")
    return event_logs

# Function to clean old log files (more than 7 days old)
def clean_old_logs():
    log_dir = os.getcwd()
    now = datetime.now()
    for file in os.listdir(log_dir):
        if file.endswith(".log"):
            file_path = os.path.join(log_dir, file)
            file_age = now - datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_age.days > 7:
                os.remove(file_path)
                logging.info(f"Deleted old log file: {file}")

# Main execution
if __name__ == "__main__":
    print("Running System Maintenance...")
    logging.info("System Maintenance Started")

    clear_temp_files()
    flush_dns_cache()
    restart_explorer()
    disk_report = check_disk_usage()
    processes = list_running_processes()
    event_logs = get_event_logs()
    clean_old_logs()

    # Generate system report
    with open("system_report.txt", "w", encoding="utf-8") as f:
        f.write("SYSTEM REPORT\n")
        f.write(f"Generated on: {datetime.now()}\n\n")
        f.write(disk_report + "\n\n")
        f.write("Running Processes:\n")
        f.write(processes + "\n\n")
        f.write("Recent Windows Event Logs:\n")
        f.write(event_logs + "\n")

    print("System Maintenance Complete! Check 'system_report.txt' for details.")
    logging.info("System Maintenance Completed Successfully")


