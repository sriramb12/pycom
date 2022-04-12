#Server side of file transfer using TLS
#Load Server Certificate to be shared via TLS handshake to client
#Create server side socket to receive file transfer and write to  file
#Allow up to 5 concurrent connections to server using threads
#Receive data and write to file then close file.

from conf import config
import socket, ssl, sys, pickle
import threading

port = 5555
try:
  port= sys.arg[1]
except:
  pass
class MftServer:
	def __init__(self):
		certfile = config.get("Settings", "certfile")
		keyfile = config.get("Settings", "keyfile")
		self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
		self.context.load_cert_chain(certfile=certfile, keyfile=keyfile)
		#SSL version 2, 3 are insecure so they have been blocked
		self.context.options |= ssl.OP_NO_SSLv2
		self.context.options |= ssl.OP_NO_SSLv3

		#create socket object
		self.srvSocket = socket.socket()
		#bind host name to socket on pot number
		self.srvSocket.bind(('localhost', port))
		#socket listening for up to 5 connections
		self.srvSocket.listen(5)
		self.repository = 'run/repo/'

	def handleClient(self, stream):
		cmds = ['get', 'put', 'query']
		MAX_SZ=1024*1024
		msg = stream.recv()
		print(len(msg))
		header = pickle.loads(msg)
		cmd = header["cmd"]
		print(header)
		print("--------")
		if cmd in cmds:
			print("cmd:", cmd)
		else:
			print("unknown cmd: "+ cmd)
			exit(0)
		if cmd == 'put':
			f = open('repo/' + header["fileName"], 'wb')
		while True:
			try:
				data = stream.recv(MAX_SZ)
				print("rx", len(data))
				f.write(data)
			except:
				#write data from stream.recv(..) to file
				break
			if not len(data):
				f.close()
				break
		print('End Of File received, closing connection...')
		print('-----------------------------------------\n')

	def process(self):
		while True:
			#accept connection, newSocket sends/receives data. fromaddr is client address
			newSocket, fromaddr = self.srvSocket.accept()
			#wrap accepted port with ssl protocol
			stream = self.context.wrap_socket(newSocket, server_side=True)
			#open file to write data to
			#Prints IP address of Client
			print("'Connection established from " + str(fromaddr))
			#try:
				#initalise thread to run handleClient(..) function
			p1 = threading.Thread(target=self.handleClient, args=[stream])
				#start thread
			p1.start()
			#except KeyboardInterrupt:
				#break
			#except Exception:
				#print('\n Error in handling client\n')
				#break
		print('\n-----------------------------------------')
		print('Server shutting down...\n')

if __name__ == '__main__':
   mftServer = MftServer()
   mftServer.process() 
