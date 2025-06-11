# Monitoring System

This project consists of a server and a client for monitoring system resources and the status of a specified process and Podman containers.

## Files

- `Server.py`: The Flask server that collects and displays monitoring data.
- `monitor.py`: The client-side script that gathers system information and sends it to the server.

## Setup and Installation

### Server Setup

1.  **Prerequisites**: Ensure you have Python 3 and `flask`, `paramiko`, and `json` installed.
    ```bash
    pip install Flask paramiko
    ```
2.  **Run the Server**: Execute the `Server.py` script. You can specify the host and port.
    ```bash
    python Server.py --host 0.0.0.0 --port 8090
    ```
    The server will be active at the specified address and port (default: `0.0.0.0:8090`).

### Client Setup

1.  **Prerequisites**: Ensure you have Python 3 and `psutil`, `requests`, `subprocess`, `os`, and `signal` installed.
    ```bash
    pip install psutil requests
    ```
2.  **Configure `monitor.py`**:
    * Set `PROCESS_NAME` in `monitor.py` to the name of the process you want to monitor (e.g., `podman`).
3.  **Run the Client**: Execute the `monitor.py` script, providing the server's IP address and port, and optionally the monitoring interval.
    ```bash
    python monitor.py --server <SERVER_IP> --port <SERVER_PORT> --interval <SECONDS>
    ```
    * `<SERVER_IP>`: The IP address of the machine running `Server.py`.
    * `<SERVER_PORT>`: The port on which the server is listening (default: `8090`).
    * `<SECONDS>`: The interval in seconds between data submissions (default: `10`, range: `5-3600`).

## Features

* **System Resource Monitoring**: Gathers CPU, RAM, and disk usage.
* **Process Monitoring**: Checks if a specified process is running, its version, and its zombie status.
* **Podman Container Monitoring**: Retrieves the status of all Podman containers.
* **Web Interface**: Displays collected data in a user-friendly web interface.
* **Scheduled Updates**: Allows scheduling an OS and Podman update for selected hosts at a specific time (23:35 by default).
* **Update Status Check**: After an update, the system checks the Podman version and container status on updated hosts.

## Usage

1.  Start the `Server.py` on your desired host.
2.  Run `monitor.py` on each client machine you wish to monitor, pointing it to the server's address.
3.  Access the server's web interface in your browser (e.g., `http://<SERVER_IP>:8090`) to view the monitoring data.
4.  From the web interface, you can select hosts and schedule updates.
