#Client side file transfer using TLS to Server
#Create a socket for TCP packets to IPV4 addresses and wrap in TLS context.
#Load Root certificate to verify server Certificate is authentic
#Once connection is establised send file data until entirely sent then close connection.
import socket, ssl, pprint, sys, pickle
import os
from time import time
from conf import config

class Client:
	def __init__(self, args):
		self.header = {}
		self.args = args
		self.chunkSize = 1024
		#create socket to handle TCP packets from IPV4 addresses
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		#custom security settings:
		#context is TLS protocol
		self.context = ssl.SSLContext(ssl.PROTOCOL_TLS)
		#certificate is required
		self.context.verify_mode = ssl.CERT_REQUIRED
		#Do not check host name matches since cert does not match domain name
		self.context.check_hostname = False
		#load CArsa.crt to verify server.crt is authentic
			
		self.context.load_verify_locations(config.get('Settings', 'serverCert'))

		#SSL version 2, 3 are insecure so they have been blocked
		self.context.options |= ssl.OP_NO_SSLv2
		self.context.options |= ssl.OP_NO_SSLv3

		#wrap soc in tls to ensure certificate is verified and used
		self.sslConn = self.context.wrap_socket(self.socket, server_hostname=args['server']) 
		#connect to server via TCP on portNumb

		self.sslConn.connect((self.args['server'], self.args['port']))
	def sendHeader(self):
		msg = pickle.dumps(self.header)
		print(self.header)
		print(len(msg))
		self.sslConn.send(msg)

	def sendData(self):
		fileName = self.header["fileName"]
		fh = open(fileName, 'rb');
		total= 0
		while True:
			#send data to bound host
			#read remaining bytes until EOF
			data = fh.read(self.chunkSize)
			total += len(data)
			if not total%1024:
				print(".")
			self.sslConn.send(data)
			if len(data) < self.chunkSize:
					self.sslConn.close()
					fh.close()
					break
		print('File '+ fileName + ' sending complete :', total, ' bytes')

	#recv
	def query(self, txnId, fileName = ''):
		self.header["cmd"] = 'query'
		self.header["txnid"] = txnId
		self.header["fileName"] = fileName
		
	def get(self, fileName, receiver):
		self.header["cmd"] = 'get'
		self.header["fileName"] = fileName
		self.header["fileSize"] = os.path.getsize(filename)
		self.header["txnid"] = txnId
		self.header["receiver"] = receiver
		self.header["filename"] = self.fileName
		self.sendHeader()

	#send
	def put(self):
		self.header["cmd"] = 'put'
		self.header["fileName"] = self.args['file']
		self.header["fileSize"] = os.path.getsize(self.args['file'])
		self.header["txnid"] = self.args['txnId']
		self.header["sender"] = self.args['sender']
		self.header["receivers"] = self.args['receivers']
		self.sendHeader()
		self.sendData()

#close connection to server
if __name__ == '__main__':
	host = 'localhost'
	port = 5555
	client = Client(host, port)
	try:
		filename = sys.argv[1]
	except:
		filename = 'test.txt'
	client.put(filename, time(), "sriramb@gmail.com")
	try:
		cmd = sys.argv[1]
	except:
		cmd = 'put'
	client.get(filename, time(), "sriramb@gmail.com")