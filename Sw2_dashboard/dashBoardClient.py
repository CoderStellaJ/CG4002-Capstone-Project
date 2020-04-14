#Code for dashboard client
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


class Client():
    def __init__(self, ip_addr, port_num, group_id, secret_key):
        super(Client, self).__init__()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (ip_addr, port_num)
        self.secret_key = secret_key
        self.socket.connect(server_address)
        # self.timeout = 60
        print("[Dashboard Client] client is connected!")

    def add_padding(self, plain_text):
        pad = lambda s: s + (BLOCK_SIZE - (len(s) % BLOCK_SIZE)) * PADDING
        padded_plain_text = pad(plain_text)
        print("[Dashboard Client] padded_plain_text length: ", len(padded_plain_text))
        return padded_plain_text
    
    def send_data_to_DB(self, table, data):
        
        #dataList = list(data.values())
        encrypted_text = self.encrypt_message_DB(table, data)
        print("encrypted_text: ", encrypted_text)
        sent_message = encrypted_text
        print("[Dashboard Client] sent_message length: ", len(sent_message))
        self.socket.sendall(sent_message)

    def encrypt_message_DB(self, table, dataDict):
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
    main()


