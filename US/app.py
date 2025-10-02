from flask import Flask, request, jsonify
import socket
import requests

app = Flask(__name__)

def dns_query(hostname, as_ip, as_port):
    try:
        query = f"TYPE=A\nNAME={hostname}\n"

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        
        sock.sendto(query.encode(), (as_ip, int(as_port)))
        
        response, _ = sock.recvfrom(4096)
        sock.close()
        
        lines = response.decode().strip().split('\n')
        for line in lines:
            if line.startswith('NAME='):
                parts = line.split(' ')
                for part in parts:
                    if part.startswith('VALUE='):
                        return part.split('=')[1]
        
        return None
    except Exception as e:
        print(f"DNS query error: {e}")
        return None

@app.route('/fibonacci', methods=['GET'])
def fibonacci():
    hostname = request.args.get('hostname')
    fs_port = request.args.get('fs_port')
    number = request.args.get('number')
    as_ip = request.args.get('as_ip')
    as_port = request.args.get('as_port')
    
    if not all([hostname, fs_port, number, as_ip, as_port]):
        return "Bad request: missing parameters", 400
    
    fs_ip = dns_query(hostname, as_ip, as_port)
    if not fs_ip:
        return "Failed to resolve hostname", 500
    
    try:
        fs_url = f"http://{fs_ip}:{fs_port}/fibonacci?number={number}"
        response = requests.get(fs_url, timeout=5)
        
        if response.status_code == 200:
            return response.text, 200
        else:
            return response.text, response.status_code
    except Exception as e:
        return f"Error contacting Fibonacci Server: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)