from bluepy import btle
import struct
import os
from concurrent import futures

# global variables
beetle_addresses = ['1C:BA:8C:1D:30:22']
global_delegate_obj = []
global_beetle_periphs = []
beetlesFlagDict = {}  # {beetle_address1:handshakeflag1,.....}


[global_delegate_obj.append(0) for ii in range(len(beetle_addresses))]
[global_beetle_periphs.append(0) for ii in range(len(beetle_addresses))]


class UUIDS:
    SERIAL_COMMS = btle.UUID("0000dfb1-0000-1000-8000-00805f9b34fb")
    SERIAL_COMMS_SERVICE = btle.UUID("0000dfb0-0000-1000-8000-00805f9b34fb")


class Delegate(btle.DefaultDelegate):

    def __init__(self, params):
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        global beetle_addresses
        global global_delegate_obj

        for idx in range(len(beetle_addresses)):
            if global_delegate_obj[idx] == self:
                print("receiving data...")
                print(data)
                if data.decode("utf-8") == 'A': # ACK packet received from Beetle during handshaking
                    return
                """if data.decode("utf-8") == 'N': # NACK packet received from Beetle
                    return
                if data.decode("utf-8") == 'T': # TIME packet received from Beetle for clock synchronization
                    return
                if data.decode("utf-8") == 'D': # DATA packet received from Beetle for sensor data
                    return"""


def initHandshake(beetle_peripheral, address):
    global beetlesFlagDict
    for bdAddress, boolFlag in beetlesFlagDict.items():
        if bdAddress == address and boolFlag == False:
            for characteristic in beetle_peripheral.getCharacteristics():
                if characteristic.uuid == UUIDS.SERIAL_COMMS:
                    characteristic.write(bytes('H', 'utf-8'), withResponse=False)
                    while True:
                        if beetle_peripheral.waitForNotifications(5):
                            characteristic.write(bytes('A', 'utf-8'), withResponse=False)
                            print("handshake with beetle %s succeeded!" % (bdAddress))
                            beetlesFlagDict.update({bdAddress: True})
                            break
                    return True

"""def clockSynchronize():"""


def establish_connection(address):
    global beetle_addresses
    global global_beetle_periphs
    global global_delegate_obj
    global beetlesFlagDict

    while True:
        try:
            for idx in range(len(beetle_addresses)):
                if beetle_addresses[idx] == address:
                    print("connecting with %s" % (address))
                    beetle_peripheral = btle.Peripheral(addr)
                    global_beetle_periphs[idx] = beetle_peripheral
                    beetle_peri_delegate = Delegate(address)
                    global_delegate_obj[idx] = beetle_peri_delegate
                    beetle_peripheral.withDelegate(beetle_peri_delegate)
                    print("Connected to %s" % (address))
                    beetlesFlagDict.update({address: False})
                    while not initHandshake(beetle_peripheral, address):
                        continue
                    #clockSynchronize()
                    getBeetleData(beetle_peripheral)
        except:
            print("failed to connect to %s" % (address))
            continue


def reestablish_connection(beetle_peri, address):
    while True:
        try:
            print("reconnecting to %s" % (address))
            beetle_peri.connect(address)
            print("re-connected to %s" % (address))
            while not initHandshake(beetle_peri, address):
                continue
            return
        except:
            continue


def getBeetleData(beetle_peri):
    while True:
        try:
            # wait for 5 seconds for data; return false if no data comes after that
            if beetle_peri.waitForNotifications(5.0):
                print("getting data...")
                continue
        except:
            try:
                beetle_peri.disconnect()
            except:
                pass
            print("disconnecting beetle_peri: %s" % (beetle_peri.addr))
            reestablish_connection(beetle_peri, beetle_peri.addr)


if __name__ == '__main__':
    connection = futures.ProcessPoolExecutor(max_workers=os.cpu_count())
    connCall = connection.map(establish_connection, beetle_addresses)
