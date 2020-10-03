#! python3.8

import os, sys, socket

SERVER_HOST, SERVER_PORT = 'localhost', 9999

def putFile(fpath, socket):
	try:
		with open(fpath, 'br') as file: sock.sendfile(file)
	except Exception as err: print(f'Error: {err}')

def getFile(fpath, socket): pass # TODO: Implement GET download request

if __name__ == "__main__":
	if len(sys.argv) < 2: raise Exception()
	elif len(sys.argv) >= 4: SERVER_HOST, SERVER_PORT = str(sys.argv[2]), int(sys.argv[3]) # Host and port specified
	fpath = str(sys.argv[1]) # File to send to PUT to server
	method = str(sys.argv[4]) if len(sys.argv) >= 5 else 'PUT'
	try:
		sock = socket.create_connection((SERVER_HOST, SERVER_PORT))
		if method == 'PUT': putFile(fpath, sock)
		elif method == 'GET': raise Exception('GET not yet implemented')
		else: raise Exception('POST not supported.')

		response = sock.recv(4096).decode()
		sock.shutdown(socket.SHUT_RDWR)
		sock.close()
		print(response)
	except Exception as err: print(f'Error: {err}')
