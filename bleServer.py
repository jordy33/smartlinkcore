#!/usr/bin/env python
# Jorge Macias. Enero 2014   
# 
# Socket server example in python
# Diincasa

import socket
import pexpect
import time
import sys
#from thread import start_new_thread 
from _thread import *

HOST = ''   # Symbolic name meaning all available interfaces
PORT = 5555 # Arbitrary non-privileged port

#Adquire ble control
persiana01 = 'DE:2D:06:53:4B:AD'
p1 = pexpect.spawn('gatttool -b ' + persiana01 + ' --interactive -t random --listen')
p1.expect('\[LE\]>')
p1.sendline('connect')
p1.expect('Connection successful.*\[LE\]>')
print ("Successfull connection")
#persiana02 = 'C3:7B:B0:D6:1C:D8'
#p2 = pexpect.spawn('gatttool -b ' + persiana02 + ' --interactive -t random --listen')
#p2.expect('\[LE\]>')
#p2.sendline('connect')
#p2.expect('Connection successful.*\[LE\]>')
# Socket Creation 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created') 
#Bind socket to local host and port

try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print('Bind failed. Error Code : ' + str(msg))
    sys.exit()
     
print ('Socket bind complete')
 
#Start listening on socket
s.listen(10)

print ('Socket now listening')
 
#Function for handling connections. This will be used to create threads
def clientthread(conn):
    #Sending message to connected client
    conn.send(str.encode('Welcome to the server. Type something and hit enter\n')) 
    #infinite loop so that function do not terminate and thread do not end.
    while True:
         
        #Receiving from client
        data = conn.recv(1024)
        print(type(data))
        print(data[:4].decode("utf-8"))
        if not data:
            break
        if data[:4].decode("utf-8") == 'p1up':
            print ('entre p1up')
            p1.sendline('char-write-cmd 0x000e 01:00')
            p1.expect('\[LE\]>')
            p1.sendline('char-read-hnd 0x000e')
            p1.expect('descriptor: .*')
            rval = p1.after.split()
            if (rval[1].decode("utf-8") == '01') and (rval[2].decode("utf-8") == '00'):
             reply = 'p1:up:ok\r\n'
            else:
             reply = 'p1:up:nok\r\n' 
            conn.sendall(str.encode(reply))
        if data[:4].decode("utf-8") == 'p1do':
            p1.sendline('char-write-cmd 0x000e 02:00')
            p1.expect('\[LE\]>')
            p1.sendline('char-read-hnd 0x000e')
            p1.expect('descriptor: .*')
            rval = p1.after.split()
            if (rval[1].decode("utf-8") == '02') and (rval[2].decode("utf-8") == '00'):
             reply = 'p1:down:ok\r\n'
            else:
             reply = 'p2:down:nok\r\n'
            conn.sendall(str.encode(reply))
        if data[:4].decode("utf-8") == 'p1st':
            p1.sendline('char-write-cmd 0x000e 00:00')
            p1.expect('\[LE\]>')
            p1.sendline('char-read-hnd 0x000e')
            p1.expect('descriptor: .*')
            rval = p1.after.split()
            if (rval[1].decode("utf-8") == '00') and (rval[2].decode("utf-8") == '00'):
             reply = 'p1:stop:ok\r\n'
            else:
             reply = 'p1:stop:nok\r\n'
            conn.sendall(str.encode(reply))
        if data[:4].decode("utf-8") == 'p2up':
            p2.sendline('char-write-cmd 0x000e 01:00')
            p2.expect('\[LE\]>')
            p2.sendline('char-read-hnd 0x000e')
            p2.expect('descriptor: .*')
            rval = p2.after.split()
            if (rval[1].decode("utf-8") == '01') and (rval[2].decode("utf-8") == '00'):
             reply = 'p2:up:ok\r\n'
            else:
             reply = 'p2:up:nok\r\n'
            conn.sendall(str.encode(reply))
        if data[:4].decode("utf-8") == 'p2do':
            p2.sendline('char-write-cmd 0x000e 02:00')
            p2.expect('\[LE\]>')
            p2.sendline('char-read-hnd 0x000e')
            p2.expect('descriptor: .*')
            rval = p2.after.split()
            if (rval[1].decode("utf-8") == '02') and (rval[2].decode("utf-8") == '00'):
             reply = 'p2:down:ok\r\n'
            else:
             reply = 'p2:down:nok\r\n'
            conn.sendall(str.encode(reply))
        if data[:4].decode("utf-8")  == 'p2st':
            p2.sendline('char-write-cmd 0x000e 00:00')
            p2.expect('\[LE\]>')
            p2.sendline('char-read-hnd 0x000e')
            p2.expect('descriptor: .*')
            rval = p2.after.split()
            if (rval[1].decode("utf-8") == '00') and (rval[2].decode("utf-8") == '00'):
             reply = 'p2:stop:ok\r\n'
            else:
             reply = 'p2:stop:nok\r\n'
        conn.sendall(str.encode(reply))
    #came out of loop
    conn.close()
 
#now keep talking with the client
while 1:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
    print('Connected with ' + addr[0] + ':' + str(addr[1]))
     
    #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    start_new_thread(clientthread ,(conn,))
 
s.close()
p1.sendline('disconnect')

