#! python3.8

import os, sys, socket, json

HOST, PORT = 'localhost', 9999 # Default host and port
response = { 'status': 400 } # Default response


def putFile(request, socket):
	global response
	if os.path.exists(request['resource']): # Check if file already exists
		print('resource found, aborting PUT')
		response = {'status': 202, 'body': 'File already exists. PUT aborted.'}
	else: # File does not exists, PUT is executed
		with open(request['resource'], 'w') as file: file.write(request['body']) # Write file to response body
		response = {'status': 201, 'body': 'File PUT successfully.'}


def getFile(request, socket_conn):
	global response
	if os.path.exists(request['resource']): # Check if file exists, send file contents
		print('resource found, getting file')
		with open(request['resource'], 'r') as file: response = {'status': 200, 'body': file.read()}
	else: response = {'status': 404} # File does not exist


handlers = {'GET': getFile, 'PUT': putFile}


if __name__ == "__main__":
	try:
		if len(sys.argv) >= 3: HOST, PORT = sys.argv[1], sys.argv[2] # Change host and ports with user params

		# Setup server
		if not os.path.exists('files'): os.mkdir('./files') # Make file storage directory if it does not exist
		os.chdir('./files') # Change to file storage directory
		sock = socket.socket()
		sock.bind((HOST, PORT))

		sock.listen(10) # Support at most ten connections
		print(f'Listening on port {PORT}...')
		while True: # Listen for connections
			conn, addy = sock.accept()
			print(f'Connected to {addy}')

			if not os.fork(): # Child process
				request = json.loads(conn.recv(4096).decode()) # Parse client request
				print(request)
				handlers[request['method']](request, sock) # Call mapped request handler
				print(response)
				conn.send(json.dumps(response).encode()) # Send response to client
				conn.close() # Close socket connection
				sys.exit() # Exit after request fulfilled
	except Exception as err: print(f'Error: {err}')
	except KeyboardInterrupt: print('Server shutting down...')
