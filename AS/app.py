import socket
import json
import os

DNS_FILE = 'dns_records.json'

def load_dns_records():
    if os.path.exists(DNS_FILE):
        try:
            with open(DNS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_dns_records(records):
    with open(DNS_FILE, 'w') as f:
        json.dump(records, f, indent=2)

def parse_message(message):
    lines = message.strip().split('\n')
    parsed = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if '=' in line:
            if line.startswith('TYPE='):
                parsed['type'] = line.split('=')[1]
            elif line.startswith('NAME='):
                parts = line.split(' ')
                for part in parts:
                    if '=' in part:
                        key, value = part.split('=', 1)
                        parsed[key.lower()] = value
    
    return parsed

def create_response(name, value, ttl=10):
    return f"TYPE=A\nNAME={name} VALUE={value} TTL={ttl}\n"

def handle_registration(parsed, records):
    name = parsed.get('name')
    value = parsed.get('value')
    ttl = parsed.get('ttl', '10')
    
    if name and value:
        records[name] = {
            'value': value,
            'type': 'A',
            'ttl': ttl
        }
        save_dns_records(records)
        return create_response(name, value, ttl)
    return None

def handle_query(parsed, records):
    name = parsed.get('name')
    
    if name and name in records:
        record = records[name]
        return create_response(name, record['value'], record['ttl'])
    return None

def main():
    print("Starting Authoritative Server...")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.bind(('0.0.0.0', 53533))
        print("Authoritative Server listening on 0.0.0.0:53533...")
    except Exception as e:
        print(f"Error binding to port 53533: {e}")
        return
    
    records = load_dns_records()
    print(f"Loaded {len(records)} existing DNS records")
    
    while True:
        try:
            data, addr = sock.recvfrom(4096)
            message = data.decode()
            
            print(f"\n{'='*50}")
            print(f"Received from {addr}:")
            print(message)
            print('='*50)
            
            parsed = parse_message(message)
            
            if 'value' in parsed:
                response = handle_registration(parsed, records)
                print(f"Registration: {parsed.get('name')} -> {parsed.get('value')}")
            else:
                response = handle_query(parsed, records)
                print(f"Query: {parsed.get('name')}")
            
            if response:
                sock.sendto(response.encode(), addr)
                print(f"Response sent: {response.strip()}")
            else:
                print("No response generated")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down Authoritative Server...")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()