#Dashboard server that interacts with client server of ATMEGA96
import os
import sys
import random
import time

import socket
import threading

import base64
import numpy as np
from tkinter import Label, Tk
import pandas as pd
from Crypto.Cipher import AES

import psycopg2
from random import seed
from random import random

from dbAPI import showTable,addValue #import function from

MESSAGE_SIZE = 3 # position, 1 action, sync


class Server(threading.Thread):
    def __init__(self, ip_addr, port_num, group_id):
        super(Server, self).__init__()

        # Create a TCP/IP socket and bind to port
        self.shutdown = threading.Event()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (ip_addr, port_num)

        print('starting up on %s port %s' % server_address, file=sys.stderr)
        self.socket.bind(server_address)

         # Listen for incoming connections
        self.socket.listen(1)
        #set up a connection
        self.client_address, self.secret_key = self.setup_connection()
        

    def setup_connection(self):
        # Wait for a connection
        print('waiting for a connection', file=sys.stderr)
        self.connection, client_address = self.socket.accept()

        print("Enter the secret key: ")
        secret_key = sys.stdin.readline().strip()

        print('connection from', client_address, file=sys.stderr)
        if len(secret_key) == 16 or len(secret_key) == 24 or len(secret_key) == 32:
            pass
        else:
            print("AES key must be either 16, 24, or 32 bytes long")
            self.stop()
        
        return client_address, secret_key # forgot to return the secret key


#Function that runs the receiving of messages
    def run(self):
        while not self.shutdown.is_set():
            data = self.connection.recv(1024)

            if data:
                obj = self.decrypt_message(data)
                print(obj)
                #print(self.decrypt_message(data))
                #addValue("testTable", obj['position'],obj['action'],str((float(obj['sync']) + self.i)))
                #self.i += 1.0 # generate a random value

                #set a timer of every 5s change a dance move
                

            else:
                print('no more data from', self.client_address, file=sys.stderr)
                self.stop()
                
    def stop(self):
        self.connection.close()
        self.shutdown.set()
        self.timer.cancel()

    def decrypt_message(self, cipher_text):
        decoded_message = base64.b64decode(cipher_text)
        iv = decoded_message[:16]
        secret_key = bytes(str(self.secret_key), encoding="utf8")

        cipher = AES.new(secret_key, AES.MODE_CBC, iv)
        decrypted_message = cipher.decrypt(decoded_message[16:]).strip()
        decrypted_message = decrypted_message.decode('utf8')

        decrypted_message = decrypted_message[decrypted_message.find('#'):]
        decrypted_message = bytes(decrypted_message[1:], 'utf8').decode('utf8')

        messages = decrypted_message.split('|')
        position, action, sync = messages[:MESSAGE_SIZE]
        return {
            'position': position, 'action': action, 'sync':sync
        }

import threading
global i
i=0
def changeMove():
    #using i as a counter to change variables
    global i
    threading.Timer(5.0,changeMove).start()
    i = i+1
    if(i==10):
        i = i - 1
    

def fakeData():
    global i
    threading.Timer(1.0, fakeData).start()
    arr = ["shoutout","transition",
           "weightlift","transition",
           "muscle","transition",
           "shoutout","transition",
           "weightlift","transition"]
    if (arr[i] == "shoutout"):
        addValue("Dancer1",1.0, 1.0, 1.0)
    elif (arr[i] == "weightlift"):
        addValue("Dancer1",2.0, 3.0, 5.0)
    elif (arr[i] == "muscle"):
        addValue("Dancer1",3.0, 4.0, 4.0)
    elif (arr[i] == "transition"):
        addValue("Dancer1", 0, 0, 0)
    

def main():
##    if len(sys.argv) != 4:
##        print('Invalid number of arguments')
##        print('python server.py [IP address] [Port] [groupID]')
##        sys.exit()
##
    ip_addr = sys.argv[1]
    port_num = int(sys.argv[2])
    group_id = sys.argv[3]

    my_server = Server(ip_addr, port_num, group_id)
    my_server.start()

if __name__ == '__main__':
    #showTable("testTable")
    #changeMove()
    #fakeData()
    main()
    
