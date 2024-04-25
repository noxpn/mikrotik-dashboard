from nxapp import web_url
placeholder_data = [{'item': 'item01', 'host_ip': 'IP01'},
                    {'item': 'item02', 'host_ip': 'IP02'},
                    {'item': 'item03', 'host_ip': 'IP03'},
                    {'item': 'item04', 'host_ip': 'IP04'},
                    {'item': 'item05', 'host_ip': 'IP05'},
                    {'item': 'item06', 'host_ip': 'IP06'},
                    {'item': 'item07', 'host_ip': 'IP07'}, ]

# web_port = '5080'
# web_url = '127.0.0.1'
try:
    a_url = 'http://'+web_url
except TypeError:
    a_url = 'http://127.0.0.1:5080'

print(f'DEBUG: {a_url}')

fake_brief_data = {'uptime': '1w1d3h2m38s', 'free-memory': 43,
                   'bad-blocks': '1', 'board-name': 'hEX S',
                   'version': '6.47.3 (stable)', 'free-hdd': 21,
                   'id': '2c671349d6d63e81bc43a172f48da5c4', 'fw_mismatch': 1}


diag_command_list = ['/ping', '/tool/traceroute']

command_list = {'/interface': 0,
                '/ip/address': 1,
                '/ip/service': 0,
                '/interface/bridge/vlan': 0,
                '/interface/bridge/port': 0,
                '/interface/bridge': 0,
                '/ip/route': 1,
                '/interface/ethernet/switch/port': 0,
                '/interface/ethernet/switch/vlan': 0,
                '/user': 0,
                '/user/ssh-keys': 0,
                '/system/scheduler': 0,
                '/system/routerboard': 0,
                '/system/health': 0,
                '/system/resource': 0,
                '/system/clock': 0,
                '/log': 4
                }
