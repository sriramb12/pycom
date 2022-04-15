import os
from time import time
from conf import config
from util import validateEmail
import getpass
import argparse
from db import MftDb
from util import createLogger
from time import time
from args import cliparser
from tlsClient import Client


class MFTClient:
	def __init__(self, args):
		self.emailSuffix = '@nxp.com'
		self.logger = createLogger("mft_client")
		self.args = args
		print("init", self.args['cmd'])
		try:
			self.args['server'] = config.get('Settings', 'icomServer')
			self.args['port'] = int(config.get('Settings', 'icomServerPort'))
			self.args['serverCert'] = config.get('Settings', 'serverCert')
		except:
			print("icomServer not specified in icom.conf")
		self.egressRecipients = []
		self.internalRecipients = []
		self.sdeUser = None

	def validateFile(self):
		fileName = self.args['file']
		if not os.path.isfile(fileName):
			self.logger.error("The transfer file does not exist: " , fileName)
			return False
		self.filesz = os.path.getsize(fileName)
		#if self.filesz < minFileSz * 1024:
			#self.logger.error("transfer file size below min threshold" , self.filesz, ", min size", minFileSz)
			#return False
		#if self.filesz > maxFileSz *1024 *1024:
			#self.logger.error("transfer file size above max threshold" , self.filesz, ", max size", maxFileSz)
			#return False
		self.logger.debug("valid transfer file size " , self.filesz)
		return True
	def validateSender(self):
		sender = self.args['sender']
		self.logger.error("valid sender:")
		if not validateEmail(sender):
			self.logger.error("incorrect sender email format:" + sender)
			return False
		return True
	def checkParams(self):
		if not self.args['recievers']:
			self.logger.error("no recipients?")
		return False
	def processRecipients(self):
		self.logger.error("processRecipients")
		sender = self.args['sender']
		for rcvr in self.args['receivers']:
			user = rcvr.split('@')[0]
			if not validateEmail(rcvr):
				self.logger.error("incorrect email " + rcvr)
				exit("60")
				return False
			if sender == rcvr:
				self.usage("sender can not be recipient?")
				self.logger.error("sender == rcvr")
				exit("65")
				return False
			if rcvr.endswith(self.emailSuffix) and db.isSdeUser(user):
				print("Rcv:", rcvr.rstrip(), user)
				self.internalRecipients += [rcvr.rstrip()]
			else:
				print("egr ", rcvr)
				self.egressRecipients += [rcvr.strip()]
		return True
	def startApproval():
		pass
		#for internalRx in self.internalRecipients:
	def process(self):
		cmd = self.args['cmd']
		if cmd == 'put':
			self.processPut()
			return
		if cmd == 'get':
			self.processGet()
			return
		self.processQuery()
		return
	def processGet(self):
		self.logger.error("processGet %s", self.args['file'])
		client = Client(self.args)
		client.get()
		return
	def processQuery(self):
		self.logger.error("processQuery %s", self.args['txnid'])
		client = Client(self.args)
		client.query()
		return
	def processPut(self):
		self.args['txnId'] = str(time())
		self.logger.error("processPut: txnid %s", self.args['txnId'])
		if not self.processRecipients():
			self.logger.error("failed")
			return False
		if not self.validateSender():
			return False
		self.logger.error("process: aft val")
		minFileSz = int(config.get('Settings', 'IcomFileSizeMin'))
		maxFileSz = int(config.get('Settings', 'IcomFileSizeMax'))
		if not self.validateFile():
			self.logger.error("validate file")
			return False
		self.logger.error("validate file")
		if not self.isSDESender() and self.egressRecipients:
			# Only SDE user can send to non SDE recipients
			self.logger.error("Only SDE user can send to non SDE recipients: "+ self.args['sender'])
			return False
		self.logger.error("to repo")
		if self.egressRecipients:
			self.requestApproval()
		if self.internalRecipients or self.egressRecipients:
			self.sendToServer()
	def requestApproval(self):
			sender = self.args['sender']
			appreqeml = config.get('Settings', 'approvalEmail')
			approvers = db.getApprovers(sender.split('@')[0])
			self.logger.error("approvers list: " + approvers)
			self.logger.error(approvers)
			recps = ', '.join(i for i in self.egressRecipients)
			print(recps)
			d = {"approvers": approvers ,
				"txnid": self.args['txnId'],
				"senderemail": sender,
				"recipientemail": recps,
				"file": self.args['file']}
			with open(appreqeml) as f:
				buf = f.read()
				for k,v in d.items():
					print(k,v)
					buf = buf.replace(k,v)
	def sendToServer(self):
		#self.logger.error("Transfer to repo: ", self.args['file'], " MB")
		client = Client(self.args)
		client.put()
		pass
	def authenticate(self):
		return True

	def isSDESender(self):
		sender = self.args['sender']
		if sender.endswith(self.emailSuffix) and self.authenticate() and db.isSdeUser(self.args['sender'].split('@')[0]):
			print("Authenticated SDE User ", sender)
			return True
		return False

	def showAll(self):
		print("Server/Port : ", self.server, self.serverPort)
		print("Sender")
		print(self.args['sender'])
		if self.isSDESender() and self.egressRecipients:
			print("Egress flow detected")
		print("Internal Recipients")
		print(self.internalRecipients)
		print("Egress Recipients")
		print(self.egressRecipients)
	def usage(self, errMsg = None):
		if errMsg:
			print(errMsg)

# Python program to execute
# main directly

if __name__ == "__main__":

	db = MftDb()
	cmdArgs = cliparser()
	mftClient = MFTClient(cmdArgs)
	mftClient.process()
