import sys
import os
from time import time
from conf import config
from util import validateEmail
import getpass
import argparse
from db import MftDb
from util import createLogger

class MFTSender:
    def __init__(self, sender, recipients, xferFileName, notes):
        self.logger = createLogger("mft_send")     
        self.logger.info("init ")
        try:
            self.server = config.get('Settings', 'icomServer')
            self.serverPort = config.get('Settings', 'icomServer')
        except:
            print("icomServer not specified in icom.conf")
        self.egressRecipients = []
        self.internalRecipients = []
        self.sender = sender
        self.recipients = recipients
        self.time = time()
        self.sdeUser = None
        self.xferFileName = xferFileName 

    def validateFile(self):
 
        if not os.path.isfile(filename):
            self.logger.error("The transfer file does not exist: " , filename)
            return False
        self.filesz = os.path.getsize(filename)
        if filesz < minFileSz * 1024:
            self.logger.error("transfer file size below min threshold" , filesz, ", min size", minFileSz) 
            return False
        if filesz > maxFileSz *1024 *1024:
            self.logger.error("transfer file size above max threshold" , filesz, ", max size", maxFileSz) 
            return False
        self.logger.debug("valid transfer file size " , filesz)
        return True 
    def validateSender(self):
        if not validateEmail(self.sender):
            self.logger.error("incorrect sender email format:" + sender)
            return False
        self.recipients = recipients
        if not self.processRecipients():
             exit(0)
    def checkParams(self):
       if not self.recipients:
         self.usage("no recipients?") 
         return False
    def processRecipients(self): 
        for eml in recipients:
            if sender == eml:
               self.usage("sender can not be recipient?")
               return False
            if not validateEmail(eml):
                self.usage("incorrect recipient email format:" + eml)
        for rcvr in self.recipients:
            if rcvr.rstrip().endswith('@nxp.com') and db.isSdeUser(rcvr.split('@')[0]):
                 self.internalRecipients += [rcvr.strip()]
            else: 
                 self.egressRecipients += [rcvr.strip()]
    def trasferToRepo():
        pass
    def notifyRecipients():
       pass
       #for internalRx in self.internalRecipients:
            
    def process(self):
       if not processRecipients():
          return False
       maxFileSz = int(config.get('Settings', 'IcomFileSizeLimit'))
       minFileSz = int(config.get('Settings', 'IcomFileSizeMin'))
       if not validateFile(self.filename, minFileSz, maxFileSz):
          return False
       if not self.isSDESender() and self.egressRecipients:
          # Only SDE user can send to non SDE recipients
          self.logger.error("Only SDE user can send to non SDE recipients: " , self.sender)
          return False
 
       if self.egressRecipients:
          self.triggerAprovalProcess()
       if self.internalRecipients():
          self.transfer();
    def send():
        self.logger.info("Transfer to repo: ", self.filename, self.filesz/(1024*1024) , " MB")
        pass  
    def authenticate(self):
        return True

    def isSDESender(self):
        if self.sender.endswith('@nxp.com') and self.authenticate() and db.isSdeUser(self.sender.split('@')[0]):
            print("Authenticated SDE User ", sender)
            return True
        return False

    def showAll(self):
      print("Server/Port")
      print(self.server, self.serverPort)   
      print("Sender")
      print(self.sender)
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

     # Create the parser
     maxNoteSz = int(config.get('Settings', 'noteSizeLimit'))
     minNoteSz = int(config.get('Settings', 'noteSizeMin'))
     db = MftDb()
     my_parser = argparse.ArgumentParser(description="Send files using icom application to/from NXP.com")

     # Add the arguments
     my_parser.add_argument('--file', '-f', action='store', type=str, required=True)
     my_parser.add_argument('--sender', '-s', action='store', type=str, required=True)
     my_parser.add_argument('--recipients','-r', nargs='+', required=True, help='list of reciepients (emails) separated by comma')
     notesHelp = "Enter a message about the transfer or specify a detailed notes in a file (" + str(maxNoteSz) + ")kb)"
     my_parser.add_argument('--notes', choices=('file', 'message'), required=True, help="Enter a message about the transfer or specify a detailed notes in a file")

    # Execute the parse_args() method
     args = my_parser.parse_args()
     logger = createLogger("main", "debug")     

     filename  = args.file
     recipients = args.recipients
     sender = args.sender

     if(args.notes == 'file'):
        notesFile = input("Enter filename with the detailed description about this transfer: ")
        try:
          fileHandle = open(notesFile, 'r')
        except:
          print("note file " + notesFile, "doesn't exist")
          exit(0) 
        filesz = os.path.getsize(notesFile)
        if filesz > maxNoteSz *1024:
            print("notes file is of " + str(filesz) + " bytes, Enter a smaller description file upto " + str(maxNoteSz)+ "kb") 
            exit(0) 
        notes = fileHandle.read()
     else:
        notes = input("Enter a brief message about this transfer: ")
     if len(notes) < minNoteSz:
        print("Transfer notes too small! Enter a minimum of ", str(minNoteSz) , "bytes description")
        exit(0) 
     mftSend = MFTSender(sender, recipients, filename, notes)
     mftSend.showAll()
