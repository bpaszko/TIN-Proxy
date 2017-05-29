import os
python = 'python'
path = os.path.abspath('plc_write1.py')
path2 = os.path.abspath('plc_write2.py')
start_port = 10000
s_start_port = 20000
register = 2000
value = 120

for i in range(10):
	command = ' '.join([python, path, str(register + i), str(value + 1), str(start_port + i)])
	command2 = ' '.join([python, path2, str(register + i), str(value + 1), str(s_start_port + i)])
	os.system(command)	
	os.system(command2)
