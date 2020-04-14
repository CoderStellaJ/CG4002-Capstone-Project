#Dashboard server that interacts with client server of ATMEGA96
#cd Desktop/Github/CG4002-Capstone-Project/Sw2_dashboard
#python dashboardServer.py 192.168.43.248

import os
import sys
import random
import time
import json

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

from dbAPI import showTable,addValue,addML #import function from dbAPI.py

MESSAGE_SIZE = 3 # position, 1 action, sync


class Server(threading.Thread):
    def __init__(self, ip_addr, port_num, group_id):
        super(Server, self).__init__()

        # Create a TCP/IP socket and bind to port
        self.shutdown = threading.Event()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (ip_addr, port_num)
        #server_address = (ip_addr, port_num)
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
                try:
                    message = self.decrypt_message(data)
                    #print(message)
                    if(message != ""):
                        splitStr = message.split(' | ')
                        print(splitStr)
                        try:
                            table = ''
                            #Position 1
                            if(splitStr[0] == "50:F1:4A:CB:FE:EE"):
                                table = "Beetle1"
                                dataPoint = eval(splitStr[1])
                                addValue(table, dataPoint[1], dataPoint[2],dataPoint[3],dataPoint[4],dataPoint[5],dataPoint[6])

                            #Position 2
                            elif(splitStr[0] == "1C:BA:8C:1D:30:22"):
                                dataPoint = eval(splitStr[1])
                                table = "Beetle2"
                                addValue(table, dataPoint[1], dataPoint[2],dataPoint[3],dataPoint[4],dataPoint[5],dataPoint[6])

                            #Position 3
                            elif(splitStr[0] == "78:DB:2F:BF:2C:E2"):
                                dataPoint = eval(splitStr[1])
                                table = "Beetle3"
                                addValue(table, dataPoint[1], dataPoint[2],dataPoint[3],dataPoint[4],dataPoint[5],dataPoint[6])

                            #Emg Data
                            elif(splitStr[0] == "50:F1:4A:CC:01:C4"):
                                print("received: " + splitStr[0])
                                dataPoint = eval(splitStr[1])
                                print("eval: " + str(dataPoint))
                                table = "EMG"
                                addValue(table, dataPoint[0], dataPoint[1],dataPoint[2],dataPoint[3])
                            
                            #Machine Learning Output
                            elif(splitStr[0] == "MLDancer1"):
                                print(splitStr)
                                addValue("MLDancer1", splitStr[1])
                                print("completes function")
                                
                        except Exception as e:
                            print("Error:" + splitStr + "Error Message: " +  str(e))
                except Exception as e:
                    print("Data failure from: " + str(e) )

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
        secret_key = bytes(str(self.secret_key), encoding="iso-8859-1")

        cipher = AES.new(secret_key, AES.MODE_CBC, iv)
        decrypted_message = cipher.decrypt(decoded_message[16:]).strip()
        decrypted_message = decrypted_message.decode('iso-8859-1')

        decrypted_message = decrypted_message[decrypted_message.find('#'):]
        decrypted_message = bytes(decrypted_message[1:], 'iso-8859-1').decode('iso-8859-1')
        
        return decrypted_message



def main():
##    if len(sys.argv) != 4:
##        print('Invalid number of arguments')
##        print('python server.py [IP address] [Port] [groupID]')
##        sys.exit()
##
    ip_addr = sys.argv[1]
    #port_num = int(sys.argv[2])
    #group_id = sys.argv[3]

    my_server = Server(ip_addr, 8080, 6)
    #my_server = Server("172.25.102.237", 8080, 6)
    ##my_server = Server(ip_addr, port_num, group_id)
    my_server.start()

if __name__ == '__main__':
    main()
    
