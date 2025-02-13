
# Change PROCESS_NAME to the name of the process you want to monitor
#PROCESS_NAME = "PLACEHOLDER_PROCESS_NAME"
PROCESS_NAME = "podman"

import socket
import psutil
import time
import platform
import requests
import argparse
import subprocess
import os
import signal

parser = argparse.ArgumentParser(description="Client for monitoring system")
parser.add_argument("--server", type=str, default="0.0.0.0", help="Server address",required=True)
parser.add_argument("--port", type=int, default=8090, help="Port number")
parser.add_argument("--interval", type=int, default=10,choices=(5,3600), help="Time interval in seconds range(5,3600)")
args = parser.parse_args()


SERVER_IP = args.server
SERVER_PORT = args.port
INTERVAL = args.interval


def get_disk_path():
    if platform.system() == "Windows":
        return "C:"
    else:
        return "/"


def get_latest_podman_version():
    try:
        result = subprocess.run(["apt-cache", "policy", "podman"], capture_output=True, text=True, check=True)
        lines = result.stdout.split("\n")
        for line in lines:
            if "Candidate:" in line:
                avaliable_version = line.split(":")[1].strip()

            if "Installed:" in line:
                installed_version = line.split(":")[1].strip()

        return (avaliable_version,installed_version)
    except subprocess.CalledProcessError as e:
        print(f"Błąd podczas sprawdzania wersji Podmana: {e}")
    return None

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

def get_process_zombieStatus(process_name):
    system_platform = platform.system()
    if system_platform == "Linux":
        for proc in psutil.process_iter(attrs=['name', 'pid', 'status']):
            try:
                if proc.info['name'].lower() == process_name.lower():
                    if proc.info['status'] == psutil.STATUS_STOPPED:
                        return True
                    os.kill(proc.info['pid'], signal.SIGCONT)
                    return False
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    return False

def get_process_version(process_name):
    for proc in psutil.process_iter(attrs=['name', 'exe']):
        try:
            if proc.info['name'].lower() == process_name.lower() or proc.info['name'].lower() == f"{process_name}.exe":
                process_path = proc.info['exe']
                if process_path:
                    result = subprocess.run([process_path, "--version"], capture_output=True, text=True)
                    return result.stdout.strip("podman version")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return "Version not found"

def podman_update():
    latest_version, installed_version = get_latest_podman_version()
    print(f"Latest version: {latest_version}")
    print(f"Installed version: {installed_version}")
    if latest_version != installed_version:
        print("Updating Podman")

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

    return (get_Clinet_IP(),psutil.cpu_percent(interval=10),
            psutil.virtual_memory().percent,
            psutil.disk_usage(get_disk_path()).percent,
            is_process_running(PROCESS_NAME),
            get_process_version(PROCESS_NAME),
            get_process_zombieStatus(PROCESS_NAME))

def SendToServer():
    while True:
        data = get_system_info()
        try:
            requests.post(f"http://{SERVER_IP}:{SERVER_PORT}/data", json=data)
        except:
            print("Nie udalo sie wyslac zapytania")

    time.sleep(INTERVAL)


podman_update()
SendToServer()
