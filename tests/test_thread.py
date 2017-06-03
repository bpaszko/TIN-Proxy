import os
import thread

python_str = 'python'
path = os.path.abspath('plc_write3.py')
#path2 = os.path.abspath('plc_write2.py')
start_port = 10000
s_start_port = 20000
register = 2000
value = 120



def send_request(path, port, register, value):

	for i in range(10):
		command = ' '.join([python_str, path, str(register + i), str(value + i), str(port + i)])
		#command2 = ' '.join([python_str, path2, str(register + i), str(value + 1), str(s_start_port + i)])
		os.system(command)	
		#os.system(command2)

def create_threads():
    try:
        a = thread.start_new_thread( send_request, (path, start_port, register, value, ) )
        b = thread.start_new_thread( send_request, (path, s_start_port, register, value, ))
    except:
        print('Unable to create threads.')
    finally:
        a.join()
        b.join()


create_threads()
