import argparse
from flask import Flask, jsonify,render_template_string, request
import time

parser = argparse.ArgumentParser(description="Server for monitoring system")
parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address")
parser.add_argument("--port", type=int, default=8090, help="Port number")
args = parser.parse_args()

Host = args.host
Port = args.port

data_list = []

#print(f"Serwer aktywny na adresie: {Host}:{Port}")

app= Flask(__name__)

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
    </style>
    <script>
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
                
                const row = `<tr>
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
        setInterval(fetchData, 5000);
        window.onload = fetchData;
    </script>
</head>
<body>
    <h1>Dane z monitorowania systemów</h1>
    <table>
        <tr>
            <th>Host</th>
            <th>CPU (%)</th>
            <th>RAM (%)</th>
            <th>Dysk (%)</th>
            <th>Proces</th>
            <th>Wersja procesu</th>
            <th>Status Zawieszenia</th>
            <th>ContainerStatus</th>
            <th>Ostatnia aktualizacja o parametrach klienta</th>
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

if __name__ == "__main__":
    app.run(host=Host, port=Port)









