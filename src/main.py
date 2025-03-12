import os
import sys
import subprocess
import requests
import logging
from collections import Counter

def get_log_path(custom_path=None):
    """Determine the appropriate log file path."""
    if custom_path:
        return custom_path
    
    system_log_path = "/var/log/autotz.log"
    user_log_path = os.path.expanduser("~/.autotz/autotz.log")
    
    # If running as root, use system log path
    if os.geteuid() == 0:
        return system_log_path
    
    # Otherwise, use user log path
    os.makedirs(os.path.dirname(user_log_path), exist_ok=True)
    return user_log_path

def setup_logging(log_enabled, log_file=None):
    if log_enabled:
        log_path = get_log_path(log_file)
        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        logging.info(f"Logging started at {log_path}")

def extract_timezone(data, service, log_enabled):
    """Extract the timezone from various API responses, handling different formats."""
    if isinstance(data, dict):
        if "timezone" in data:
            return data["timezone"]
        elif "time_zone" in data:
            return data["time_zone"]
        elif "id" in data:  # Handling ipwho.is structured response
            return data["id"]
    
    if log_enabled:
        logging.warning(f"Service {service} returned an unrecognized timezone format: {data}")
    return None

def get_timezone_from_ip(log_enabled=False):
    services = [
        "http://ip-api.com/json",
        "https://ipwho.is/",
        "https://freegeoip.app/json/",
        "http://ipinfo.io/json"
    ]
    
    timezones = []
    for service in services:
        try:
            response = requests.get(service, timeout=5)
            response.raise_for_status()
            data = response.json()
            timezone = extract_timezone(data, service, log_enabled)
            if isinstance(timezone, str):  # Ensure it's a valid string
                timezones.append(timezone)
                if log_enabled:
                    logging.info(f"Service {service} returned timezone: {timezone}")
            else:
                if log_enabled:
                    logging.warning(f"Service {service} returned an invalid timezone format: {data}")
        except requests.RequestException as e:
            if log_enabled:
                logging.warning(f"Service {service} failed: {e}")
    
    if not timezones:
        return None
    
    # Quorum decision: Select the most common timezone
    timezone_counts = Counter(timezones)
    best_timezone = timezone_counts.most_common(1)[0][0]
    return best_timezone

def update_timezone(timezone, log_enabled=False):
    if not timezone:
        print("Could not determine timezone.")
        sys.exit(1)
    
    try:
        subprocess.run(["sudo", "timedatectl", "set-timezone", timezone], check=True)
        print(f"Timezone updated to {timezone}")
        if log_enabled:
            logging.info(f"Timezone successfully updated to {timezone}")
    except subprocess.CalledProcessError as e:
        print("Failed to update timezone. Ensure you have sudo privileges.")
        if log_enabled:
            logging.error(f"Failed to update timezone: {e}")
        sys.exit(1)

def main():
    log_enabled = "--log" in sys.argv
    log_file = None
    
    if "--log" in sys.argv:
        log_index = sys.argv.index("--log")
        if log_index + 1 < len(sys.argv):
            log_file = sys.argv[log_index + 1]
    
    setup_logging(log_enabled, log_file)
    
    timezone = get_timezone_from_ip(log_enabled)
    if timezone:
        print(f"Detected timezone: {timezone}")
        update_timezone(timezone, log_enabled)
    else:
        print("Could not determine timezone from any service.")
        if log_enabled:
            logging.error("No valid timezone detected from any service")
        sys.exit(1)

if __name__ == "__main__":
    main()
