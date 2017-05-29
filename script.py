#!/bin/python

import sys
import getopt
from logger_v2 import Logger
from firewall.firewall import Firewall
from proxy.proxyv2 import Proxy
import socket

class FirewallMock:
	def check_message(self, address, command, subcommand):
		return None


def help():
	print('Usage:\n'
	      'python script.py --net-config= --firewall-config= --log-level= --log-file=\n'
	      'python script.py --net-config= --firewall-config= --log-level=0' )
	sys.exit()

def parse_net_config(config):
	server = host_port = None
	try:
		with open(config, 'r') as f:
			server = f.readline().replace('\n', '')
			host_port = f.readline().replace('\n', '')
	except:
		print('Net config error')
		sys.exit()

	server_address, server_port = server.split(':')
	host_address = socket.gethostbyname(socket.gethostname())
	print (host_address, int(host_port)), (server_address, int(server_port))
	return (host_address, int(host_port)), (server_address, int(server_port))


#COMMAND LINE LOOKS LIKE
#python script.py -net-config=path1 -log-level=0
#python script.py -net-config=path1 -firewall-config=path2 -log-level=1|2|3 -log-file=path3
# --net-config [mandatory] specifies proxy port, server ip and server port
# --firewall-config [mandatory]
# --log-level [mandatory]
#	0 - no logs
#	1 - log blocked requests
#	2 - log passed requests
#	3 - log everything
# --log-file [mandatory if log-level != 0] file storing logs

args = sys.argv[1:]
optlist = None

if len(args) != 3 and len(args) != 4:
	help()

if len(args) == 3:
	optlist, args = getopt.getopt(args, '', ['net-config=', 'firewall-config=', 'log-level='])
	if optlist[2][1] != '0': #DIFFERENT PERMUTATION
		help()


if len(args) == 4:
	optlist, args = getopt.getopt(args, '', ['net-config=', 'firewall-config=', 'log-level=', 'log-file='])

net_config = firewall_config = log_level = log_level = None
for opt in optlist:
	if opt[0] == '--net-config':
		net_config = opt[1]
	elif opt[0] == '--firewall-config':
		firewall_config = opt[1]
	elif opt[0] == '--log-level':
		log_level = int(opt[1])
	elif opt[0] == '--log-file':
		log_file = opt[1]

host, server = parse_net_config(net_config)


#firewall = Firewall(firewall_config, logger)
#proxy = Proxy(host, server, firewall)
#proxy.start()

f_logger = Logger(log_file, log_level, 'firewall')
p_logger = Logger('logs/proxy_log.txt', log_level, 'proxy')
firewall = Firewall(firewall_config, f_logger)
proxy = Proxy(host, server, firewall, p_logger)
proxy.start()