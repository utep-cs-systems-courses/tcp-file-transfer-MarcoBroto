#! python3.8

import os.path as path, sys, socket, json, base64

SERVER_HOST, SERVER_PORT = 'localhost', 9999
request = {}

def readResponse():
	try:
		blocks = []
		while buffer := sock.recv(4096).decode():  # Read initial request
			if buffer[-1] == '\0':
				blocks.append(buffer[:-1])
				break
			else: blocks.append(buffer)
		return json.loads(''.join(blocks))
	except json.JSONDecodeError as err:
		print(err)
		return None


def createRequest(method, fpath, withData=False):
	global request
	request = {'method': method, 'resource': path.basename(fpath)}
	if method == 'PUT':
		if withData:
			with open(fpath, 'br') as file:
				try: request['data'] = base64.b64encode(file.read()).decode('ascii')
				except Exception as err: print(err)
	elif method == 'GET': pass # Request is already initialized
	else: raise Exception('Request method not supported.')


def handleResponse(res):
	print(f'{res=}')
	if request['method'] == 'PUT': # Handle secondary response
		if res['status'] == 200:
			createRequest(request['method'], request['resource'], True)
			req = json.dumps(request) + '\0'  # Add line terminator (null ascii character)
			sock.send(req.encode()) # Send PUT request with payload
			res = readResponse()
	elif request['method'] == 'GET' and res['status'] == 200 and 'data' in res:
		with open(request['resource'], 'w') as file: file.write(res['data']) # Write GET data to new file
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
		req = json.dumps(request) + '\0'  # Add line terminator (null ascii character)
		sock.send(req.encode())

		# Receive response to initial request
		print('Receiving response...')
		handleResponse(readResponse())

		sock.close()
	except KeyError as err: print(err)
	except KeyboardInterrupt as err: print(err)
	# except OSError as err: print(f'Error: {err}')
