import argparse
from flask import Flask, jsonify,render_template_string, request
import time
import paramiko
import json

USERNAME = "user"
PASSWORD = "12345678"


parser = argparse.ArgumentParser(description="Server for monitoring system")
parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address")
parser.add_argument("--port", type=int, default=8090, help="Port number")
args = parser.parse_args()

Host = args.host
Port = args.port

data_list = []

#print(f"Serwer aktywny na adresie: {Host}:{Port}")

app= Flask(__name__)


# usun conol.log
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Monitorowanie Systemu</title>
  <style>
      body { font-family: Arial, sans-serif; text-align: center; }
      table { width: 80%; margin: 20px auto; border-collapse: collapse; }
      th, td { border: 1px solid black; padding: 10px; text-align: center; }
      th { background-color: #4CAF50; color: white; }
      button { margin-bottom: 10px; padding: 10px 20px; font-size: 16px; }
  </style>
  <script>
    // Globalny zbiór przechowujący wybrane hosty
    let selectedHosts = new Set();
    // Flaga określająca, czy wszystkie hosty są zaznaczone
    let allSelected = false;

    async function fetchData() {
      const response = await fetch('/get_data');
      const data = await response.json();
      const tableBody = document.getElementById('data-body');
      tableBody.innerHTML = '';

      data.forEach(item => {
        let containerTable = '<table border="1">';
        containerTable += '<tr><th>Nazwa</th><th>Status</th></tr>';
        item.containers_status.forEach(container => {
          containerTable += `<tr><td>${container.name}</td><td>${container.status}</td></tr>`;
        });
        containerTable += '</table>';

        // Jeśli host jest w zbiorze wybranych, checkbox będzie zaznaczony
        let isChecked = selectedHosts.has(item.host) ? 'checked' : '';

        const row = `<tr>
            <td>
              <input type="checkbox" data-host="${item.host}" ${isChecked} onchange="handleCheckboxChange('${item.host}', this.checked)">
            </td>
            <td>${item.host}</td>
            <td>${item.cpu_usage}</td>
            <td>${item.ram_usage}</td>
            <td>${item.disk_usage}</td>
            <td>${item.process_running ? '✔️' : '❌'}</td>
            <td>${item.process_version}</td>
            <td>${item.zombie_status ? '✔️' : '❌'}</td>
            <td>${containerTable}</td>
            <td>${item.timestamp}</td>
        </tr>`;
        tableBody.innerHTML += row;
      });
    }

    function handleCheckboxChange(host, isChecked) {
      if (isChecked) {
        selectedHosts.add(host);
        // console.log(host);
        document.getElementById('toggleButton').innerText = "Odznacz wszystkie hosty";
      } else {
        selectedHosts.delete(host);
        // Jeśli użytkownik odznaczył pojedynczy checkbox, ustawiamy flagę allSelected na false
        allSelected = false;
        document.getElementById('toggleButton').innerText = "Zaznacz wszystkie hosty";
      }
      sendSelectedHosts();
    }

    function toggleSelectAllHosts() {
      const checkboxes = document.querySelectorAll('input[type="checkbox"][data-host]');
      if (!allSelected) {
        checkboxes.forEach(checkbox => {
          if (!checkbox.checked) {
            checkbox.checked = true;
            const host = checkbox.getAttribute('data-host');
            selectedHosts.add(host);
            // console.log(host);
          }
        });
        allSelected = true;
        document.getElementById('toggleButton').innerText = "Odznacz wszystkie hosty";
      } else {
        checkboxes.forEach(checkbox => {
          if (checkbox.checked) {
            checkbox.checked = false;
            const host = checkbox.getAttribute('data-host');
            selectedHosts.delete(host);
          }
        });
        allSelected = false;
        document.getElementById('toggleButton').innerText = "Zaznacz wszystkie hosty";
      }
      sendSelectedHosts();
    }
    
     function sendSelectedHosts() {
    fetch('/selected-host', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(Array.from(selectedHosts))
    })
    .then(response => response.json())
    .then(data => {
      //console.log("Odpowiedź serwera:", data);
    })
    .catch(error => {
      console.error("Błąd podczas wysyłania danych:", error);
    });
  }

    // Odświeżanie danych co 5 sekund
    setInterval(fetchData, 5000);
    window.onload = fetchData;
  </script>
<script>
  function executeUpdate() {
    fetch('/schedule-update', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(Array.from(selectedHosts))
    })
    .then(response => response.json())
    .then(data => {
     // console.log("Aktualizacja zaplanowana:", data);
      alert("Aktualizacja została zaplanowana na godzinę 23:35!");
    })
    .catch(error => {
      console.error("Błąd podczas planowania aktualizacji:", error);
      alert("Błąd podczas planowania aktualizacji!");
    });
  }
</script>

</head>
<body>
  <h1>Dane z monitorowania systemów</h1>
  <button id="toggleButton" onclick="toggleSelectAllHosts()">Zaznacz wszystkie hosty</button>
  <button id="updateButton" onclick="executeUpdate()">Wykonaj aktualizację</button>
  <table>
      <tr>
          <th>Wybierz</th>
          <th>Host</th>
          <th>CPU (%)</th>
          <th>RAM (%)</th>
          <th>Dysk (%)</th>
          <th>Proces</th>
          <th>Wersja procesu</th>
          <th>Status Zawieszenia</th>
          <th>ContainerStatus</th>
          <th>Ostatnia aktualizacja</th>
      </tr>
      <tbody id="data-body">
      </tbody>
  </table>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, data=data_list)

@app.route("/get_data", methods=["GET"])
def get_data():
    return jsonify(data_list)
@app.route("/data", methods=["POST"])
def data():
    data = request.get_json()
    host = data[0]
    cpu_usage = data[1]
    ram_usage = data[2]
    disk_usage = data[3]
    process_running = data[4]
    process_version = data[5]
    zombie_status = data[6]
    containers_status = data[7]

    if host not in [item['host'] for item in data_list]:
        data_list.append({
            "host": host,
            "cpu_usage": cpu_usage,
            "ram_usage": ram_usage,
            "disk_usage": disk_usage,
            "process_running": process_running,
            "process_version": process_version,
            "zombie_status": zombie_status,
            "containers_statu": containers_status,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
    })
    else:
        for item in data_list:
            if item['host'] == host:
                item['cpu_usage'] = cpu_usage
                item['ram_usage'] = ram_usage
                item['disk_usage'] = disk_usage
                item['process_running'] = process_running
                item['process_version'] = process_version
                item['zombie_status'] = zombie_status
                item['containers_status'] = containers_status
                item['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return jsonify({"status": "OK"})

@app.route("/selected-host", methods=["POST"])
def selected_hosts():
    hosts = request.get_json()


    return jsonify({"status": "OK", "selected": hosts})


import threading
import datetime

scheduled_hosts = []  # Lista hostów do aktualizacji

@app.route("/schedule-update", methods=["POST"])
def schedule_update():
    global scheduled_hosts
    hosts = request.get_json()
    if not hosts:
        return jsonify({"status": "error", "message": "Brak wybranych hostów"}), 400

    scheduled_hosts = hosts
    print(f"Aktualizacja zaplanowana dla hostów: {scheduled_hosts} na 23:35")

    return jsonify({"status": "scheduled", "scheduled_hosts": scheduled_hosts})

def scheduled_task():
    global scheduled_hosts
    now = datetime.datetime.now()
   # scheduled_time = now + datetime.timedelta(minutes=1)  # Zaplanowanie za minutę
    scheduled_hour = 23
    scheduled_minute = 40



    while True:
        now = datetime.datetime.now()
        if now.hour == scheduled_hour and now.minute == scheduled_minute:
            if scheduled_hosts:
                print(f"Rozpoczynam aktualizację dla hostów: {scheduled_hosts}")
                Updater(scheduled_hosts)
                print("Aktualizacja zakończona.")

                # Uruchamiamy sprawdzenie statusu po 10 minutach
                check_thread = threading.Thread(target=check_update_status, daemon=True)
                check_thread.start()

                scheduled_hosts = []
            else:
                print("Brak zaplanowanych hostów do aktualizacji.")
            break
        time.sleep(10)  # Sprawdzamy co 10 sekund


def hosts_Os_update(hostList):
    for host in hostList:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=host, username=USERNAME, password=PASSWORD)

            command = f"echo 'sudo apt update && sudo apt upgrade -y'"

            stdin, stdout, stderr = ssh.exec_command(command)
            print(stdout.read().decode())
            ssh.close()
        except Exception as e:
            print(str(e))


def podman_update(hostList):
    for host in hostList:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=host, username=USERNAME, password=PASSWORD)
            command = "sudo apt upgrade podman -y"
            stdin, stdout, stderr = ssh.exec_command(command)
            print(stdout.read().decode())
            ssh.close()
        except Exception as e:
            print(str(e))


def podman_containers_update(hostList):
    for host in hostList:
        print(f"\n--- Aktualizacja kontenerów Podman na hoście: {host} ---")
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=host, username=USERNAME, password=PASSWORD)
        except Exception as e:
            print(f"Błąd połączenia z hostem {host}: {e}")
            continue

        try:
            stdin, stdout, stderr = ssh.exec_command("podman ps -a --format json")
            output = stdout.read().decode()
            try:
                containers = json.loads(output)
            except json.JSONDecodeError as e:
                print("Błąd dekodowania JSON:", e)
                containers = []

            if not containers:
                print("Brak kontenerów do aktualizacji.")

            for container in containers:
                container_id = container.get("Id", "")
                container_image = container.get("Image", "")

                names_list = container.get("Names", [])
                container_name = names_list[0] if names_list else container_id


                base_image = container_image.rsplit(":", 1)[0] if ':' in container_image else container_image

                new_image = f"{base_image}:latest"

                print(f"\n--- Aktualizacja kontenera: {container_name} (ID: {container_id}) ---")
                print(f"Nowy obraz: {new_image}")

                pull_command = f'podman pull {new_image}'
                try:
                    stdin, stdout, stderr = ssh.exec_command(pull_command)
                    pull_result = stdout.read().decode().strip()
                    pull_error = stderr.read().decode().strip()
                    if pull_error:
                        print(f"Błąd podczas pobierania obrazu {new_image}: {pull_error}")
                    else:
                        print(f"Pobrano obraz {new_image}: {pull_result}")
                except Exception as e:
                    print("Błąd przy pobieraniu obrazu:", e)

                stop_command = f'podman stop {container_id}'
                try:
                    stdin, stdout, stderr = ssh.exec_command(stop_command)
                    stop_result = stdout.read().decode().strip()
                    stop_error = stderr.read().decode().strip()
                    if stop_error:
                        print(f"Błąd podczas zatrzymywania kontenera {container_id}: {stop_error}")
                    else:
                        print(f"Zatrzymano kontener {container_id}: {stop_result}")
                except Exception as e:
                    print("Błąd przy zatrzymywaniu kontenera:", e)


                rm_command = f'podman rm {container_id}'
                try:
                    stdin, stdout, stderr = ssh.exec_command(rm_command)
                    rm_result = stdout.read().decode().strip()
                    rm_error = stderr.read().decode().strip()
                    if rm_error:
                        print(f"Błąd podczas usuwania kontenera {container_id}: {rm_error}")
                    else:
                        print(f"Usunięto kontener {container_id}: {rm_result}")
                except Exception as e:
                    print("Błąd przy usuwaniu kontenera:", e)

                run_command = f'podman run -d --name {container_name} {new_image}'
                try:
                    stdin, stdout, stderr = ssh.exec_command(run_command)
                    run_result = stdout.read().decode().strip()
                    run_error = stderr.read().decode().strip()
                    if run_error:
                        print(f"Błąd podczas uruchamiania nowego kontenera {container_name}: {run_error}")
                    else:
                        print(f"Uruchomiono nowy kontener {container_name}: {run_result}")
                except Exception as e:
                    print("Błąd przy uruchamianiu nowego kontenera:", e)
        finally:
            ssh.close()


def check_update_status():
    global scheduled_hosts
    print("Oczekiwanie 10 minut na sprawdzenie statusu aktualizacji...")
    time.sleep(600)  # Czekamy 10 minut

    failed_hosts = []
    for host in scheduled_hosts:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=host, username="user", password="12345678")

            # Sprawdzenie wersji Podmana
            stdin, stdout, stderr = ssh.exec_command("podman --version")
            podman_version = stdout.read().decode().strip()

            # Sprawdzenie działania kontenerów
            stdin, stdout, stderr = ssh.exec_command("podman ps --format json")
            containers = json.loads(stdout.read().decode())

            if not containers:
                print(f" Brak działających kontenerów na hoście {host}")
                failed_hosts.append(host)

            ssh.close()
        except Exception as e:
            print(f"Błąd podczas sprawdzania hosta {host}: {e}")
            failed_hosts.append(host)

    if failed_hosts:
        print(f" Aktualizacja nie powiodła się na następujących hostach: {failed_hosts}")
    else:
        print("Aktualizacja zakończona pomyślnie na wszystkich hostach.")


def Updater(hostList):
    hosts_Os_update(hostList)
    podman_update(hostList)
    podman_containers_update(hostList)


def add_10_testHosts():
    for i in range(10):
        data_list.append({
            "host": f"test{i}",
            "cpu_usage": 0,
            "ram_usage": 0,
            "disk_usage": 0,
            "process_running": False,
            "process_version": "",
            "zombie_status": False,
            "containers_status": [],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        })

if __name__ == "__main__":
  #  add_10_testHosts()
    import logging
   # logging.getLogger('werkzeug').disabled = True

    scheduler_thread = threading.Thread(target=scheduled_task, daemon=True)
    scheduler_thread.start()

    app.run(host=Host, port=Port,debug=False)














