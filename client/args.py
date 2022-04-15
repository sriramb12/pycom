#!/usr/bin/env python
import argparse

def handleQuery(args):
    cmd = {}
    cmd['cmd'] = args.command
    cmd['file'] = args.txnid
    return cmd

def handleGet(args):
    cmd = {}
    cmd['cmd'] = args.command
    cmd['file'] = args.file
    return cmd

def handlePut(args):
    cmd = {}
    cmd['cmd'] = args.command
    if args.notes == 'file':
        cmd['notesFile'] =  input("Enter name of the notes file :")
    if args.notes == 'message':
        cmd['message'] =  input("Enter a brief message :")
    cmd['cmd'] = args.command
    try:
       cmd['file'] = args.file
    except:
       pass
    try:
       cmd['sender'] = args.sender
    except:
       pass
    try:
       cmd['receivers'] = args.reciever
    except:
       pass
    try:
       cmd['file'] = args.file
    except:
       pass
    try:
       cmd['txnid'] = args.txnid
    except:
       pass
    return (cmd)

def cliparser(command_line=None):
    parser = argparse.ArgumentParser('icom ')
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Print debug info'
    )
    notesHelp = "Enter a message about the transfer or specify a detailed notes in a file"
    cmds = parser.add_subparsers(dest='command')

    put = cmds.add_parser('put', help='put file')
    put.add_argument('--sender', '-s', help='sender email', required=True)
    put.add_argument('--reciever', '-r', nargs = '+', help='sender email', required=True)
    put.add_argument('--file', '-f', help='file to put', required=True)
    put.add_argument('--notes', '-n', choices=('file', 'message'), required=True, help = notesHelp)

    get = cmds.add_parser('get', help='get file')
    get.add_argument('--file', '-f', help='file to get')

    qry = cmds.add_parser('qry' , help='query file')
    qryGrp = qry.add_mutually_exclusive_group(required=True)
    qryGrp.add_argument("--file", '-f')
    qryGrp.add_argument("--txnid", '-i')


    args = parser.parse_args(command_line)
    if not args.command:
      exit("\n   Usage: python icom.py <put|get|qry>\n")
    if args.command == 'put':
       return handlePut(args)
    if args.command == 'get':
       return handleGet(args)
    return handleQuery(args)
   

if __name__ == '__main__':
    cliparser()
