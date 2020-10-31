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
	elif method == 'GET':
		request['method'] = 'GET'
	else: raise Exception('Request method not supported.')


if __name__ == "__main__":
	try:
		if len(sys.argv) < 2: raise Exception('Expected at least 2 parameters.')
		elif len(sys.argv) >= 5: SERVER_HOST, SERVER_PORT = str(sys.argv[3]), sys.argv[4] # Host and port specified
		method = str(sys.argv[1]).upper()  # Request method
		fpath = str(sys.argv[2]) # File to send to PUT to server

		sock = socket.create_connection((SERVER_HOST, SERVER_PORT))
		createRequest(method, fpath) # Structure request

		# print(request)
		# r = json.dumps(request).encode()
		# print(r)

		# Send request to server
		print('Sending request...')
		request = json.dumps(request) + '\0' # Add line terminator (null ascii character)
		sock.send(request.encode())

		print('Receiving response...')
		blocks = []
		while buffer := sock.recv(4096).decode(): # Read response
			if buffer[-1] == '\0': # End of response
				blocks.append(buffer[:-1])
				break
			else: blocks.append(buffer)
		response = json.loads(''.join(blocks))
		print(f'{response=}')

		if method == 'GET': # Create file from GET request data
			with open(response['resource'], 'w') as file: file.write(response['data'])

		sock.shutdown(socket.SHUT_RDWR)
		sock.close()
	except Exception as err: print(f'Error: {err}')
