import requests

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        if response.status_code == 200:
            ip_address = response.json()['ip']
            return ip_address
        else:
            print('Failed to retrieve public IP.')
    except requests.exceptions.RequestException as e:
        print('Error:', e)

# Example usage
ip_address = get_public_ip()
print('Public IP Address:', ip_address)