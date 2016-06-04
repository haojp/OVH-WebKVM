#!/usr/bin/env python3

import sys

def print_error(message, exit_code=1):
    print(message, file=sys.stderr)
    if exit_code:
        exit(exit_code)

try:
    import ovh
except ImportError:
    print_error('Missing "ovh" module. Please run the following command:\n'
                '\tpip -r requirements.txt')

def exit_handler(signal, frame):
    proc.terminate()
    print('Goodbye!')
    exit(0)

def get_console_conf(api_client, server):
    return api_client.get('/dedicated/server/{server_name}/features/ipmi/access'
            ''.format(server_name=server), **{'type': ACCESS_TYPE})

import os
import time
import json
import signal
import subprocess
import webbrowser
import urllib.request
import xml.etree.ElementTree as ET
from ovh.exceptions import ResourceNotFoundError

ACCESS_TYPE='kvmipJnlp'

server = sys.argv[1].lower() if len(sys.argv) > 1 else None
if not server:
    print_error('Missing server name.')

script_path = os.path.dirname(__file__)

# Init OVH API client.
client = ovh.Client()

# Retrieve account's servers list.
servers = client.get('/dedicated/server')
if not server in servers:
    print_error('Invalid server "{server_name}". Possible values are: '
                '{servers_list}.'.format( \
                server_name=server, servers_list=', '.join(servers)))

# Checking IPMI console availability.
ipmi = client.get('/dedicated/server/{server_name}/features/ipmi'
                  ''.format(server_name=server))

if not ipmi['activated'] == True:
    print_error('IPMI feature is not avalable on this server.')

# Retrieve public IPv4 address using httpbin.org.
allowed_ip = json.loads(urllib.request.urlopen('https://httpbin.org/ip').read().decode('utf-8'))['origin']
print('You public IP address is: {ip_address}'.format(ip_address=allowed_ip))

# Activating IPMI console access.
try:
    console = get_console_conf(client, server)
except ResourceNotFoundError:
    print('Activating server console...')
    task = client.post('/dedicated/server/{server_name}/features/ipmi/access'
            ''.format(server_name=server), \
            **{'ipToAllow': allowed_ip, 'ttl': 15, 'type': ACCESS_TYPE})

    while True:
        result = client.get('/dedicated/server/{server_name}/task/{task_id}'
                ''.format(server_name=server, task_id=task['taskId']))

        if result['status'] == 'error':
            print_error('Error during IPMI console activation: "{error_msg}".'
                    ''.format(error_msg=result['comment']))

        elif result['status'] == 'done':
            print('Console successfully activated!')
            break

        else:
            time.sleep(2)
    
    console = get_console_conf(client, server)

print('Console access expires at: {expire_date}'.format( \
        expire_date=console['expiration']))

# Retrieve KVM login informations from JNLP file.
print('Retrieving KVM login informations...')
xml = ET.fromstring(console['value'])
kvm_server, kvm_user, kvm_pass, *unused = xml.findall('.//argument')

# Launch websockify.
print('Starting noVNC server on localhost:6080...')
proc = subprocess.Popen(['{script_path}/noVNC/utils/launch.sh'
            ''.format(script_path=script_path), '--listen', '6080', '--vnc', \
            '{kvm_server}:5900'.format(kvm_server=kvm_server.text)], \
            shell=False, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, \
            stderr=subprocess.DEVNULL)

webbrowser.open('http://localhost:6080/vnc.html?host=localhost&port=6080'
            '&password={kvm_user}:{kvm_pass}&autoconnect=true'
            ''.format(kvm_user=kvm_user.text, kvm_pass=kvm_pass.text))

print('')
print('noVNC started. Press Ctrl+C to exit when you\'re done.')
print('')
signal.signal(signal.SIGINT, exit_handler)
signal.pause()
