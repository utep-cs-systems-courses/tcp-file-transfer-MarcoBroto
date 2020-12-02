#! python3.8

import os, sys, socket, json, base64
from threading import Thread, Lock

HOST, PORT = 'localhost', 9999 # Default host and port
response = { 'status': 400 } # Default response
sock = socket.socket() # Server socket object
dbLock = Lock() # Used to prevent unwanted access to db files
fileCache = set()

def isValidRequest(req): return ('method' in req and 'resource' in req)


def putFile(fname, data):
	print(f'Putting file: {fname}')
	dbLock.acquire()
	try:
		with open(fname, 'bw') as file: file.write(base64.decodebytes(data.encode())) # Write file to response body
		res = {'status': 201, 'data': 'File PUT successfully'}
	except Exception as err:
		print(err)
		os.remove(fname)  # Delete created file
		fileCache.remove(fname) # Delete file from fileCache
		res = {'status': 500, 'error': err}
	dbLock.release()
	return res


def getFile(fname):
	print(f'Getting file: {fname}')
	dbLock.acquire()
	if os.path.exists(fname): # Check if file exists, send file contents
		print('resource found, getting file')
		with open(fname, 'r') as file:
			res = {'status': 200, 'resource': fname, 'data': file.read()}
	else: res = {'status': 404} # File does not exist
	dbLock.release()
	return res


def sendResponse(conn, res):
	print('Sending Response...')
	res = json.dumps(res) + '\0'  # Add line terminator (null ascii character)
	conn.send(res.encode())  # Send response to client


def readRequest(conn):
	try:
		blocks = []
		while buffer := conn.recv(4096).decode():  # Read initial request
			if buffer[-1] == '\0':
				blocks.append(buffer[:-1])
				break
			else: blocks.append(buffer)
		return json.loads(''.join(blocks))
	except json.JSONDecodeError as err:
		print(err)
		return None


def fileDoesExist(fname):
	result = True
	dbLock.acquire()
	if not os.path.exists(fname):
		with open(fname, 'bw'): pass # Create new file
		result = False
	dbLock.release()
	return result


def handleRequest_PUT(conn, req):
	if fileDoesExist(req['resource']): # Blocks to check if file exists in database
		print(f"Rejected PUT '{req['resource']}'")
		res = {'status': 406, 'data': 'PUT denied. File already exists.'}
		sendResponse(conn, res)
	else:
		try:
			res = {'status': 200, 'data': 'PUT accepted. Send file data.'}
			sendResponse(conn, res) # Send response to initial request
			pay_req = readRequest(conn) # Payload request
			res = putFile(pay_req['resource'], pay_req['data']) # Blocks for saving file data
		except Exception as err:
			print(err)
			if req['resource'] in fileCache: fileCache.remove(req['resource'])
			res = {'status': 500, 'data': err}
		sendResponse(conn, res)


def handleRequest(conn, req):
	if isValidRequest(req):
		try:
			if req['method'] == 'GET':
				res =  getFile(req['resource'])
				sendResponse(conn, res)
			elif req['method'] == 'PUT':
				handleRequest_PUT(conn, req)
		except KeyError as err: print(err)
	else: sendResponse(conn, {'status': 400}) # Default request response


def handleConnection(conn, addr):
	print(f'\nConnected to {addr}')
	init_req = readRequest(conn)
	handleRequest(conn, init_req) # Handle initial request
	conn.close()  # Close socket connection
	print('Connection Terminated')


def getArgs():
	global HOST, PORT
	if '-h' in sys.argv: HOST = sys.argv[sys.argv.index('-h')+1]
	if '-p' in sys.argv: PORT = int(sys.argv[sys.argv.index('-p')+1])


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
	except KeyboardInterrupt: pass
	except OSError as err: print(f'Error: {err}\n')
	finally:
		print('Shutting down server...')
		sock.close()
