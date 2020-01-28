import sys
from Crypto import Random

import socket
import threading

import base64
from Crypto.Cipher import AES

#ACTIONS = ['muscle', 'weightlifting', 'shoutout', 'dumbbells', 'tornado', 'facewipe', 'pacman', 'shootingstar', 'logout']

class Client(threading.Thread):
    def __init__(self, ip_addr, port_num, group_id, secret_key):
        super(Client, self).__init__()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (ip_addr, port_num)
        self.secret_key = secret_key
        self.socket.connect(server_address)
        self.shutdown = threading.Event()

        print("client is connected!")


    def encrypt_message(self, position, action, syncdelay):
        plain_text = '#' + position + '|' + action + '|' + syncdelay + '|'
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.secret_key, AES.MODE_CBC, iv)
        encrypted_text = base64.b64encode(iv + cipher.encrypt(plain_text))

        return encrypted_text


    def send_data(self, position, action, syncdelay):
        encrypted_text = self.encrypt_message(position, action, syncdelay)
        send_message = bytes(str(encrypted_text), encoding="utf8")
        self.socket.sendall(send_message)

def main():
    if len(sys.argv) != 5:
        print('Invalid number of arguments')
        print('python client.py [IP address] [Port] [groupID] [secret key]')
        sys.exit()

    ip_addr = sys.argv[1]
    port_num = int(sys.argv[2])
    group_id = sys.argv[3]
    secret_key = sys.argv[4]

    my_client = Client(ip_addr, port_num, group_id, secret_key)
    action = ""
    count = 0
    while action != "logout":
        my_client.send_data("1 2 3", "muscle", "1.00")
        count += 1

if __name__ == '__main__':
    main()

