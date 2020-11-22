#! python3.8

import os.path as path, sys, socket, json, base64

SERVER_HOST, SERVER_PORT = 'localhost', 9999
request = {}

def createRequest(method, fpath):
	request['method'] = method
	request['resource'] = path.basename(fpath)
	if method == 'PUT':
		with open(fpath, 'br') as file:
			try: request['data'] = base64.b64encode(file.read()).decode('ascii')
			except Exception as err: print(err)
	elif method == 'GET': pass
	else: raise Exception('Request method not supported.')


def handleResponse(method):
	# Recieve initial response
	print('Receiving response...')
	blocks = []
	while buffer := sock.recv(4096).decode(): # Read response
		if buffer[-1] == '\0': # End of response
			blocks.append(buffer[:-1])
			break
		else: blocks.append(buffer)
	response = json.loads(''.join(blocks))
	print(f'{response=}')

	if method == 'PUT': pass
	elif method == 'GET':
		with open(response['resource'], 'w') as file: file.write(response['data']) # Write GET data to new file
	else: raise Exception('Method not supported')


def getArgs(): # Parse command line arguments
	if len(sys.argv) < 2: raise Exception('Expected at least 2 parameters.')
	elif len(sys.argv) >= 5:
		global SERVER_HOST, SERVER_PORT
		SERVER_HOST, SERVER_PORT = str(sys.argv[1]), sys.argv[2] # Host and port specified
		method = str(sys.argv[3]).upper()  # Request method
		fpath = str(sys.argv[4])  # File to send to PUT to server
	else:
		method = str(sys.argv[1]).upper()  # Request method
		fpath = str(sys.argv[2]) # File to send to PUT to server
	return method, fpath

if __name__ == "__main__":
	try:
		method, fpath = getArgs()
		sock = socket.create_connection((SERVER_HOST, SERVER_PORT))

		# Send initial request
		createRequest(method, fpath)
		print('Sending request...')
		request = json.dumps(request) + '\0' # Add line terminator (null ascii character)
		sock.send(request.encode())

		# Receive response to initial request
		print('Receiving response...')
		blocks = []
		while buffer := sock.recv(4096).decode(): # Read response
			if buffer[-1] == '\0': # End of response
				blocks.append(buffer[:-1])
				break
			else: blocks.append(buffer)
		response = json.loads(''.join(blocks))
		print(f'{response=}')

		if method == 'GET' and response['status'] == 200:
			with open(response['resource'], 'w') as file: file.write(response['data']) # Write GET data to new file

		sock.close()
	except KeyError as err: print(err)
	except KeyboardInterrupt as err: print(err)
	except OSError as err: print(f'Error: {err}')
