import socket
import psutil
import time
import platform
import requests
import argparse

parser = argparse.ArgumentParser(description="Client for monitoring system")
parser.add_argument("--server", type=str, default="0.0.0.0", help="Server address",required=True)
parser.add_argument("--port", type=int, default=8090, help="Port number")
args = parser.parse_args()


SERVER_IP = args.server
SERVER_PORT = args.port
PROCESS_NAME = ".exe"

def get_disk_path():
    if platform.system() == "Windows":
        return "C:"
    else:
        return "/"


def is_process_running(process_name):
    process_name = process_name.lower()
    is_windows = platform.system() == "Windows"

    for proc in psutil.process_iter(attrs=['name']):
        try:
            proc_name = proc.info['name'].lower()
            if is_windows:
                if proc_name == f"{process_name}.exe" or proc_name == process_name:
                    return True
            else:
                if proc_name == process_name:
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False

def get_Clinet_IP():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"Error getting IP: {e}")
        return "Unknown"
def get_system_info():
    disk_path = get_disk_path()
    proccess_running = is_process_running(PROCESS_NAME)
    return get_Clinet_IP(),psutil.cpu_percent(interval=10), psutil.virtual_memory().percent, psutil.disk_usage(get_disk_path()).percent, proccess_running

def SendToServer():
    while True:
        data = get_system_info()
        try:
            requests.post(f"http://{SERVER_IP}:{SERVER_PORT}/data", json=data)
        except:
            print("Nie udalo sie wyslac zapytania")

    time.sleep(10)

SendToServer()