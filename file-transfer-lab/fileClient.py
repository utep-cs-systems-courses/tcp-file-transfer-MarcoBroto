#! python3.8

import os, sys, socket, json

SERVER_HOST, SERVER_PORT = 'localhost', 9999
request = {}

def putFile(fpath, socket):
	with open(fpath, 'br') as file:
		request['method'] = 'PUT'
		request['resource'] = fpath
		request['body'] = file.read().decode()

def getFile(fpath, socket):
	request['method'] = 'GET'
	request['resource'] = fpath

if __name__ == "__main__":
	try:
		if len(sys.argv) < 2:
			raise Exception('Expected at least 2 parameters.')
			sys.exit(1)
		elif len(sys.argv) >= 5: SERVER_HOST, SERVER_PORT = str(sys.argv[3]), sys.argv[4] # Host and port specified
		fpath = str(sys.argv[1]) # File to send to PUT to server
		method = str(sys.argv[2]).upper() # Request method

		sock = socket.create_connection((SERVER_HOST, SERVER_PORT))
		if method == 'PUT': putFile(fpath, sock) # Send PUT request
		elif method == 'GET': getFile(fpath, sock) # Send GET request
		else: raise Exception('Request method not supported.')

		sock.send(json.dumps(request).encode())
		response = sock.recv(4096).decode()
		print(response)
		sock.shutdown(socket.SHUT_RDWR)
		sock.close()
	except Exception as err: print(f'Error: {err}')
