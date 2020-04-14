#Code for dashboard client

#Melvin, i need to send the last datapoints to the computer
#Steps:
#1. Initialise Client - dashboard_client = Client("127.0.0.2", 8080, 6, "cg40024002group6")
#2. Send dictionary with information type - dashboard_client = Client("<beetleNum/DancerNum>", <Dictionary>)
import sys
import socket
import base64
import time
import json

from Crypto.Cipher import AES
from Crypto import Random

BLOCK_SIZE = 16
PADDING = ' '
testDict = {}


# ACTIONS = ['muscle', 'weightlifting', 'shoutout', 'dumbbells', 'tornado', 'facewipe', 'pacman', 'shootingstar', 'logout']

class Client():
    def __init__(self, ip_addr, port_num, group_id, secret_key):
        super(Client, self).__init__()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (ip_addr, port_num)
        self.secret_key = secret_key
        self.socket.connect(server_address)
        # testing on laptop
        # self.timeout = 60
        print("[Dashboard Client] client is connected!")

    def add_padding(self, plain_text):
        pad = lambda s: s + (BLOCK_SIZE - (len(s) % BLOCK_SIZE)) * PADDING
        padded_plain_text = pad(plain_text)
        print("[Dashboard Client] padded_plain_text length: ", len(padded_plain_text))
        return padded_plain_text
    
    def send_data_to_DB(self, table, data):
        
        #dataList = list(data.values())

        encrypted_text = self.encrypt_message_DB(table, dataDict)
        print("[Dashboard Client] encrypted_text: ", encrypted_text)
        sent_message = encrypted_text
        print("[Dashboard Client] sent_message length: ", len(sent_message))
        self.socket.sendall(sent_message)

    def encrypt_message_DB(self, table, dataDict):
##        plain_text = '#' + table + " | "
##        for dataPoint in data:
##            plain_text += dataPoint + " | "
        plain_text = "#" + table + " | " + str(dataDict)
        print("[Dashboard Client] plain_text: ", plain_text)
        padded_plain_text = self.add_padding(plain_text)
        iv = Random.new().read(AES.block_size)
        aes_key = bytes(str(self.secret_key), encoding="utf8")
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        encrypted_text = base64.b64encode(iv + cipher.encrypt(bytes(padded_plain_text, "utf8")))
        print(type(encrypted_text))
        return encrypted_text

    def stop(self):
        self.connection.close()
        self.shutdown.set()
        self.timer.cancel()

import ast
def processData():
    testStr = """{'78:DB:2F:BF:3B:54': {1: [24080, -176.99, 8.34, 19.38], 2: [24080, -174.17, -0.89, 17.43], 3: [24080, -170.96, -10.04, 14.34], 4: [24080
, -168.26, -17.58, 10.38], 5: [24080, -166.43, -23.79, 5.96], 6: [24080, -165.35, -28.16, 2.3], 7: [28576, 82.96, 41.44, 11.51], 9:
[28576, 77.98, 36.15, 11.79], 10: [28576, 73.59, 30.77, 12.81], 15: [28576, 80.88, 36.19, 13.5], 16: [28576, 83.9, 39.04, 13.62], 17: [28576,
84.96, 39.83, 14.01], 18: [28576, 84.96, 39.83, 14.01], 19: [28576, 66.48, 20.5, 19.28], 20: [28576, 59.77, 12.25, 22.88], 21: [28576,
36.36 , -17.8, 44.93], 22: [28576, 35.78, -16.74, 45.44], 23: [31741, 73.89, 26.91, 18.7], 24: [31741, 67.13, 18.66, 21.94], 25: [31741,
59.58, 9.39, 26.29], 26: [31741, 59.58, 9.39, 26.29], 27: [31741, 56.0, 2.83, 30.13], 28: [31741, 62.98, 9.84, 25.21], 29: [31741, 69.1,
16.17, 21.85], 30: [31741, 74.21, 21.64, 19.79], 31: [31741, 78.42, 26.23, 18.72], 32: [31741, 81.93, 29.95, 18.09], 33: [31741, 84.43, 32.4
, 17.74], 34: [31741, 85.04, 32.76, 17.7], 35: [31741, 82.89, 30.51, 18.5], 36: [31741, 82.89, 30.51, 18.5], 37: [31741, 46.33, -9.57,
38.53], 38: [31741, 44.54, -11.34, 40.87], 39: [31741, 44.67, -10.31, 41.62], 40: [31741, 47.64, -6.39, 39.6], 41: [31741, 53.69, -0.34,
35.16], 42: [26909, -168.75, 69.68, -18.08], 43: [26909, -168.66, 67.78, -15.21], 44: [26909, -168.82, 63.33, -12.11], 45: [26909, -168.82,
 63.33, -12.11], 46: [26909, -157.69, 35.48, -0.91], 47: [26909, -158.38, 41.64, -0.22], 48: [26909, -160.57, 50.3, -0.7], 49: [26909,
 -12.91, 59.96, -2.56], 50: [26909, -164.81, 69.19, -5.64], 51: [26909, -164.32, 75.74, -9.51], 52: [26909, -143.57, 76.4, -13.45],
 53: [2609, -14.83, 72.1, -17.15], 54: [26909, -14.83, 72.1, -17.15], 55: [26909]}}"""
    testDict = ast.literal_eval(testStr)
    testDict = testDict[next(iter(testDict))]
    return testDict

import threading
global i
global j
i=1
j=55
def changeMove():
    #using i as a counter to change variables
    global i,j
    threading.Timer(3.0,changeMove).start()
    i = i+1
    j = j-1

def main():
##    if len(sys.argv) != 5:    
##        print('Invalid number of arguments')
##        print('python eval_client.py [IP address] [Port] [groupID] [secret key]')
##        sys.exit()
##
    ip_addr = sys.argv[1]
##    port_num = int(sys.argv[2])
##    group_id = sys.argv[3]
##    secret_key = sys.argv[4]
    dashboard_client = Client(ip_addr, 8080, 6, "cg40024002group6")
    
    #dashboard_client = Client(ip_addr, port_num, group_id, secret_key)
    pseudoDict  = {1:'YAW', 2: 'PITCH', 3:'RAW'}
    

    action = ""
    # test client on laptop
    time.sleep(10)

    count = 0
    while action != "logout":
        try:
            dashboard_client.send_data_to_DB("Beetle1", testDict[i])#send "Beetle number and array string"
        except:
            print("key: " + str(i) +" does not exist" )
        try:
            dashboard_client.send_data_to_DB("Beetle2", testDict[j])#send "Beetle number and array string"
        except:
            print("key: " + str(j) +" does not exist" )
        try:
            dashboard_client.send_data_to_DB("MLDancer1", "MLSending")#send "Beetle number and array string"
        except:
            print("key: " + str(j) +" does not exist" )
            
        time.sleep(2)
        count += 1
        if(count == 50) :
            my_client.stop()

if __name__ == '__main__':
    testDict = processData()
    changeMove()
    main()


