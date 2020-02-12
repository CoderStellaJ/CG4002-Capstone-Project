from bluepy import btle
import struct
import os
from concurrent import futures
import threading

# global variables
beetle_addresses = ["1C:BA:8C:1D:30:22"]
global_delegate_obj = []
global_beetle_periphs = []
beetlesFlagDict = {}  # {beetle_address1:handshakeflag1,.....}
# define number of data sets from beetles to be fed into ML algorithm once ML function starts running
global_num_of_datasets = 20
beetle_1CBA8C1D3022_data_dict = {} # store all data that comes from this beetle
beetles_dataset_count_dict = {} # track num of datasets received from each beetle

# global synchronization primitive
condition = threading.Condition()

[global_delegate_obj.append(0) for idx in range(len(beetle_addresses))]
[global_beetle_periphs.append(0) for idx in range(len(beetle_addresses))]
[beetlesFlagDict.update({beetle_addresses[idx]:False}) for idx in range(len(beetle_addresses))]
[beetles_dataset_count_dict.update({beetle_addresses[idx]:0}) for idx in range(len(beetle_addresses))]


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
                print("receiving data from %s" % (beetle_addresses[idx]))
                print(data)
                # ACK packet received from Beetle during handshaking
                if data.decode("utf-8") == 'A':
                    return
                """if data.decode("utf-8") == 'N': # NACK packet received from Beetle
                    return
                if data.decode("utf-8") == 'T': # TIME packet received from Beetle for clock synchronization
                    return
                if data.decode("utf-8") == 'D': # DATA packet received from Beetle for sensor data
                    if beetle_addresses[idx] = "1C:BA:8C:1D:30:22":
                        beetle_1CBA8C1D3022_data_dict.update({})
                        beetles_dataset_count_dict["1C:BA:8C:1D:30:22"] += 1
                    return"""


def initHandshake(beetle_peripheral, address):
    global beetlesFlagDict
    for bdAddress, boolFlag in beetlesFlagDict.items():
        if bdAddress == address and boolFlag == False:
            for characteristic in beetle_peripheral.getCharacteristics():
                if characteristic.uuid == UUIDS.SERIAL_COMMS:
                    characteristic.write(
                        bytes('H', 'utf-8'), withResponse=False)
                    while True:
                        if beetle_peripheral.waitForNotifications(5):
                            characteristic.write(
                                bytes('A', 'utf-8'), withResponse=False)
                            print("handshake with beetle %s succeeded!" %
                                  (bdAddress))
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
                # for initial connections or when any beetle is disconnected
                if beetle_addresses[idx] == address and beetlesFlagDict[address] == False:
                    print("connecting with %s" % (address))
                    beetle_peripheral = btle.Peripheral(addr)
                    global_beetle_periphs[idx] = beetle_peripheral
                    beetle_peri_delegate = Delegate(address)
                    global_delegate_obj[idx] = beetle_peri_delegate
                    beetle_peripheral.withDelegate(beetle_peri_delegate)
                    print("Connected to %s" % (address))
                    while not initHandshake(beetle_peripheral, address):
                        continue
                    # clockSynchronize()
                    getBeetleData(beetle_peripheral)
                if beetle_addresses[idx] == address and beetlesFlagDict[address] == True:
                    getBeetleData(beetle_peripheral)
        except:
            print("failed to connect to %s" % (address))
            continue
        if all(value >= global_num_of_datasets for value in beetles_dataset_count_dict.values()):
            [beetles_dataset_count_dict.update({beetle_addresses[idx]:0}) for idx in range(len(beetle_addresses))] # reset dataset count to 0
            break
        else:
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
    global beetlesFlagDict
    global beetles_dataset_count_dict
    while True:
        try:
            # wait for 5 seconds for data; return false if no data comes after that
            if beetle_peri.waitForNotifications(5.0):
                print("getting data...")
                if all(value >= global_num_of_datasets for value in beetles_dataset_count_dict.values()) # if number of datasets received from all beetles exceed expectation
                    return
                continue
        except:
            try:
                beetle_peri.disconnect()
            except:
                pass
            print("disconnecting beetle_peri: %s" % (beetle_peri.addr))
            beetlesFlagDict.update({beetle_peri.addr: False})
            reestablish_connection(beetle_peri, beetle_peri.addr)


"""def executeMachineLearning():"""

"""def send_results_to_servers():

"""

if __name__ == '__main__':
    while True:
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor: # max_workers = number of beetles
            receive_data_futures = {executor.submit(establish_connection, address): address for address in beetle_addresses}
        executor.shutdown(wait=True)
        """ml_future = futures.ProcessPoolExecutor(max_workers=os.cpu_count())
        ml_process = ml_future.submit(executeMachineLearning)"""
        """with future in concurrent.futures.as_completed(ml_process):
            send_results = futures.ProcessPoolExecutor(max_workers=os.cpu_count())
            send_results_process = send_results.submit(send_results_to_servers)"""
