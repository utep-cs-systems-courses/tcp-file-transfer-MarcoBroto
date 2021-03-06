#! python3.8

import os, sys, socket, json, base64

HOST, PORT = 'localhost', 9999 # Default host and port
response = { 'status': 400 } # Default response
sock = socket.socket() # Server socket object

def sendResponse(conn):
	global response
	print('Sending Response...')
	response = json.dumps(response) + '\0' # Add line terminator (null ascii character)
	conn.send(response.encode()) # Send response to client


def putFile(fname, data):
	global response
	print(f'Putting file: {fname}')
	if os.path.exists(fname): # Check if file already exists, skip PUT if true
		print('resource found, PUT aborted')
		response = {'status': 409, 'data': 'A file with this name already exists. PUT aborted.'}
	else: # File does not exist, PUT is executed
		try:
			with open(fname, 'bw') as file: file.write(base64.decodebytes(data.encode())) # Write file to response body
			response = {'status': 201, 'data': 'File PUT successfully'}
		except Exception as err:
			print(err)
			os.remove(fname)  # Delete created file


def getFile(fname):
	print(f'Getting file: {fname}')
	if os.path.exists(fname): # Check if file exists, send file contents
		print('resource found, getting file')
		with open(fname, 'r') as file:
			response['status'] = 200
			response['resource'] = fname
			response['data'] = file.read()
	else: response['status'] = 404 # File does not exist


def handleRequest(req):
	if req['method'] == 'GET': getFile(req['resource'])
	elif req['method'] == 'PUT': putFile(req['resource'], req['data'])


def handleConnection(conn, addr):
	global response
	print(f'\nConnected to {addr}')

	if not os.fork(): # Child process
		blocks = []
		while buffer := conn.recv(4096).decode(): # Read request
			if buffer[-1] == '\0':
				blocks.append(buffer[:-1])
				break
			else: blocks.append(buffer)
		request = json.loads(''.join(blocks))

		handleRequest(request) # Structure response
		print('Sending Response...')
		response = json.dumps(response) + '\0' # Add line terminator (null ascii character)
		conn.send(response.encode()) # Send response to client
		conn.close() # Close socket connection
		print('Connection Terminated')
		os._exit(0) # Exit after request fulfilled


def getArgs():
	if len(sys.argv) == 3: HOST, PORT = sys.argv[1], sys.argv[2] # Change host and ports with user params
	else:
		try: HOST = sys.argv[sys.argv.index('-h')+1]
		except Exception: pass
		try: PORT = sys.argv[sys.argv.index('-p')+1]
		except Exception: pass


def setup():
	if not os.path.exists('db'): os.mkdir('./db') # Make file storage directory if it does not exist
	os.chdir('./db') # Change to file storage directory
	sock.bind((HOST, PORT))
	sock.listen(10) # Support at most ten connections
	print(f'Listening on port {PORT}...')


def listen():
	global response
	while True:
		conn, addy = sock.accept()
		handleConnection(conn, addy)


if __name__ == "__main__":
	try:
		getArgs() # Get command line arguments
		setup() # Configure Server
		listen() # Listen for connections
	except KeyboardInterrupt: print('Server shutting down...')
	except OSError as err: print(f'Error: {err}\n')
	finally:
		print('Shutting down...')
		sock.close()
