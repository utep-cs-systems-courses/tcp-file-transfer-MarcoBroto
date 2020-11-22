#! python3.8

import os, sys, socket, json, base64
from threading import Thread, Lock

HOST, PORT = 'localhost', 9999 # Default host and port
response = { 'status': 400 } # Default response
sock = socket.socket() # Server socket object
dbLock = Lock() # Used to prevent unwanted access to db files

def isValidRequest(req): return 'method' in req and 'resource' in req


def putFile(fname, data):
	print(f'Putting file: {fname}')
	res = {}
	dbLock.acquire()
	if os.path.exists(fname): # Check if file already exists, skip PUT if true
		print('resource found, PUT aborted')
		res = {'status': 409, 'data': 'A file with this name already exists. PUT aborted.'}
	else: # File does not exist, PUT is executed
		try:
			with open(fname, 'bw') as file: file.write(base64.decodebytes(data.encode())) # Write file to response body
			res = {'status': 201, 'data': 'File PUT successfully'}
		except Exception as err:
			print(err)
			os.remove(fname)  # Delete created file
			res = {'status': 500, 'error': err}
	dbLock.release()
	return res


def getFile(fname):
	print(f'Getting file: {fname}')
	res = {}
	dbLock.acquire()
	if os.path.exists(fname): # Check if file exists, send file contents
		print('resource found, getting file')
		with open(fname, 'r') as file:
			res['status'] = 200
			res['resource'] = fname
			res['data'] = file.read()
	else: res['status'] = 404 # File does not exist
	dbLock.release()
	return res


def handleRequest(req, res):
	if isValidRequest(req):
		try:
			if req['method'] == 'GET': res =  getFile(req['resource'])
			elif req['method'] == 'PUT': res = putFile(req['resource'], req['data'])
		except KeyError as err:
			print(err)
			res['data'] = 'Invalid Request.'
	return res


def sendResponse(conn, res):
	print('Sending Response...')
	res = json.dumps(res) + '\0' # Add line terminator (null ascii character)
	conn.send(res.encode()) # Send response to client


def handleConnection(conn, addr):
	print(f'\nConnected to {addr}')
	response = {'status': 400} # Default request response

	try:
		blocks = []
		while buffer := conn.recv(4096).decode():  # Read initial request
			if buffer[-1] == '\0':
				blocks.append(buffer[:-1])
				break
			else: blocks.append(buffer)
		request = json.loads(''.join(blocks))
		response = handleRequest(request, response)
	except json.JSONDecodeError as err: print(err)
	finally:
		sendResponse(conn, response)
		conn.close()  # Close socket connection
		print('Connection Terminated')


def getArgs():
	if len(sys.argv) == 3: HOST, PORT = sys.argv[1], sys.argv[2] # Change host and ports with user params
	else:
		if '-h' in sys.argv: HOST = sys.argv[sys.argv.index('-h')+1]
		if '-p' in sys.argv: PORT = sys.argv[sys.argv.index('-p')+1]


def setup():
	if not os.path.exists('db'): os.mkdir('./db') # Make file storage directory if it does not exist
	os.chdir('./db') # Change to file storage directory
	sock.bind((HOST, PORT))
	sock.listen(10) # Support at most ten connections
	print(f'Listening on port {PORT}...')


def listen():
	while True:
		conn, addy = sock.accept()
		Thread(target=handleConnection(conn, addy)).start()


if __name__ == "__main__":
	try:
		getArgs() # Get command line arguments
		setup() # Configure server
		listen() # Listen for connections
	except KeyboardInterrupt: print('Server shutting down...')
	except OSError as err: print(f'Error: {err}\n')
	finally:
		print('Shutting down...')
		sock.close()
