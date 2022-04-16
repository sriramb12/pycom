#Server side of file transfer using TLS
#Load Server Certificate to be shared via TLS handshake to client

import socket, ssl, pickle
import threading
import os
from os.path import exists
import random
import time
from conf import config
import string
import json

class MFTServer:
	def __init__(self):
		self.loadRepoDb()
		certfile = config.get("Settings", "certfile")
		keyfile = config.get("Settings", "keyfile")
		self.packetSize = int(config.get("Settings", "packetSize"))
		self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
		try:
			self.context.load_cert_chain(certfile=certfile, keyfile= keyfile)
		except:
			print("Error in loading cert")
			exit(0)

		#SSL version 2, 3 are insecure so they have been blocked
		self.context.options |= ssl.OP_NO_SSLv2
		self.context.options |= ssl.OP_NO_SSLv3

		#create socket object
		self.srvSocket = socket.socket()
		self.srvSocket.settimeout(1)
		#bind host name to socket on pot number
		self.serverPort = int(config.get("Settings", "icomServerPort"))
		#socket listening for up to 5 connections
		self.srvSocket.listen(5)
		self.repository = 'run/repo/'

		#create socket object
		self.sockServer = socket.socket()
		#bind host name to socket on pot number
		try:
			self.sockServer.bind(('0.0.0.0', self.serverPort))
		except:
			exit("Server already running on port:" + str(self.serverPort))
		#socket listening for up to 5 connections
		try:
			self.sockServer.listen()
		except:
			exit("listen error")
	def loadRepoDb(self):
		self.repoDbFile = config.get("Settings", "repoDbFile")
		try:
			with open(self.repoDbFile, 'r') as self.repoDbHandle:
				self.repoDb = json.load(self.repoDbHandle)
		except:
			self.repoDb = {}
			print("no repo info")

	def saveRepoDb(self):
		self.repoDbFile = config.get("Settings", "repoDbFile")
		print("saverepo")
		jsonObj =  json.dumps(self.repoDb, indent = 4)
		with open(self.repoDbFile, 'w') as self.repoDbHandle:
			self.repoDbHandle.write(jsonObj)

	def genHandle(self):
		char_set = string.ascii_uppercase
		num_set = string.digits
		while True:
			self.handle = ''.join(random.sample(char_set*4, 4)) + ''.join(random.sample(num_set*4, 4)) +'X'
			if not exists(self.repository + self.handle):
				return self.handle
			print("handle" , self.handle)
	def decryptFile(fileName,key):
		f = Fernet(key)
		file_data= ""
		encFile = fileName+ 'en'
		with open(fileName, "rb") as file:
			file_data = file.read()
			# decrypt data
		decrypted_data = f.decrypt(file_data)
		with open(encFile, "wb") as file:
			file.write(decrypted_data)
		return encFile
	
	def sendFile(self, streamSock):
		fileName = self.repository + self.header["fileName"]
		print("SEnding file", fileName) 
		fh = None
		fh = open(fileName, 'rb')
		'''
		try:
			fh = open(fileName, 'rb')
		except:
			exit("no such file in repository: " + fileName)
		'''
		total= 0
		print("sending file", fileName) 
		while True:
			#send data to bound host
			#read remaining bytes until EOF
			data = fh.read(self.packetSize)
			total += len(data)
			if not total%1024:
				print(".")
			streamSock.send(data)
			if len(data) < self.packetSize:
					streamSock.close()
					fh.close()
					break
		print('File '+ fileName + ' sending complete :', total, ' bytes')
			
		
	def recvFile(self, stream):
		self.genHandle()
		fname = self.repository + self.handle
		f = open(fname, 'wb')
		sz = int(self.header['fileSize'])
		print("recv file  ", fname, sz)
		rx = 0
		while rx < sz: 
			try:
				data = stream.recv(self.packetSize)
				f.write(data)
				rx += len(data)
				print("rx:", rx)
			except:
				#write data from stream.recv(..) to file
				break
		self.repoDb[self.handle] = self.header
		f.close()
		self.saveRepoDb()
		print('End Of File received, closing connection...')
		print('-----------------------------------------\n')
		d = {'filehandle': self.handle}
		msg = pickle.dumps(d)
		stream.send(msg)
		
	def dumpRepo(self):
		print(self.repoDb)
	def handleClient(self, stream):
		cmds = ['get', 'put', 'query', 'debug']
		MAX_SZ=1024*1024
		msg = stream.recv()
		print(len(msg))
		self.header = pickle.loads(msg)
		cmd = self.header["cmd"]
		print(self.header)
		print("--------")
		if cmd in cmds:
			print("cmd:", cmd)
		else:
			print("unknown cmd: "+ cmd)
			exit(0)
		if cmd == 'put':
			return self.recvFile(stream)
		if cmd == 'get':
			return self.sendFile(stream)

	def startServer(self):
		while True:
			newSocket, fromaddr = self.sockServer.accept()
			streamSock = self.context.wrap_socket(newSocket, server_side=True)
			#open file to write data to
			#Prints IP address of Client
			print("'Connection established from " + str(fromaddr))
			try:
				#initalise thread to run handle_client(..) function
				p1 = threading.Thread(target=self.handleClient, args=[streamSock])
				#start thread
				p1.start()
			except Exception as err:
				print('\n Error in handling client\n', err)
				break
		print('\n-----------------------------------------')
		print('Server shutting down...\n')

srv = MFTServer()
srv.startServer()
