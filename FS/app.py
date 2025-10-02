from flask import Flask, request, jsonify
import socket

app = Flask(__name__)

def calculate_fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

def register_with_as(hostname, ip, as_ip, as_port):
    try:
        message = f"TYPE=A\nNAME={hostname} VALUE={ip} TTL=10\n"
        
        print(f"Attempting to register with AS at {as_ip}:{as_port}")
        print(f"Registration message:\n{message}")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        
        sock.sendto(message.encode(), (as_ip, int(as_port)))
        print("Registration message sent successfully")
        
        try:
            response, _ = sock.recvfrom(4096)
            print(f"Received response: {response.decode()}")
        except socket.timeout:
            print("Warning: No response from AS (timeout), but message was sent")
        
        sock.close()
        return True
        
    except Exception as e:
        print(f"Registration error: {e}")
        import traceback
        traceback.print_exc()
        return False

@app.route('/register', methods=['PUT'])
def register():
    try:
        data = request.get_json()
        
        hostname = data.get('hostname')
        ip = data.get('ip')
        as_ip = data.get('as_ip')
        as_port = data.get('as_port')
        
        if not all([hostname, ip, as_ip, as_port]):
            return "Bad request: missing parameters", 400
        
        if register_with_as(hostname, ip, as_ip, as_port):
            return "Registration successful", 201
        else:
            return "Registration failed", 500
            
    except Exception as e:
        return f"Error: {e}", 400

@app.route('/fibonacci', methods=['GET'])
def fibonacci():
    number = request.args.get('number')
    
    if not number:
        return "Bad request: missing number parameter", 400
    
    try:
        n = int(number)
        result = calculate_fibonacci(n)
        return str(result), 200
    except ValueError:
        return "Bad request: number must be an integer", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090, debug=True)