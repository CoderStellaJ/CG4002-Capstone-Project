from bluepy import btle
import struct  # remove if using data.decode('UTF-8')
import os
import concurrent
from concurrent import futures
import threading
import time
from time_calibration import *

# global variables
beetle_addresses = ["1C:BA:8C:1D:30:22"]
global_delegate_obj = []
global_beetle_periphs = []
beetles_connection_flag_dict = {}  # {beetle_address1:handshakeflag1,.....}
beetle1_handshake_flag_dict = {"1C:BA:8C:1D:30:22": True}
beetle2_handshake_flag_dict = {}
beetle3_handshake_flag_dict = {}
beetle1_buffer_dict = {"1C:BA:8C:1D:30:22": ""}
beetle2_buffer_dict = {}
beetle3_buffer_dict = {}
# data global variables
beetle1_data_dict = {}  # for beetle 1C:BA:8C:1D:30:22
beetle2_data_dict = {}
beetle3_data_dict = {}
beetle1_datastring = ""
beetle2_datastring = ""
beetle3_datastring = ""
beetle1_dataset_count = 0
beetle2_dataset_count = 0
beetle3_dataset_count = 0
float_flag_1 = False
float_flag_2 = False
float_flag_3 = False
timestamp_flag_1 = False
timestamp_flag_2 = False
timestamp_flag_3 = False
comma_count_1 = 0
comma_count_2 = 0
comma_count_3 = 0
checksum_1 = 0
checksum_2 = 0
checksum_3 = 0
is_checksum_1 = False
is_checksum_2 = False
is_checksum_3 = False
# clock synchronization global variables
timestamp_string1 = ""
timestamp_string2 = ""
timestamp_string3 = ""
beetle1_clocksync_flag_dict = {"1C:BA:8C:1D:30:22": False}
beetle2_clocksync_flag_dict = {}
beetle3_clocksync_flag_dict = {}
# [address,t1,t2,t3,t4,t1,t2,t3,t4,t1,t2,t3,t4]
beetle1_timestamp_list = ["1C:BA:8C:1D:30:22"]
beetle2_timestamp_list = []
beetle3_timestamp_list = []

[global_delegate_obj.append(0) for idx in range(len(beetle_addresses))]
[global_beetle_periphs.append(0) for idx in range(len(beetle_addresses))]
[beetles_connection_flag_dict.update({beetle_addresses[idx]:False})
 for idx in range(len(beetle_addresses))]
[beetle1_data_dict.update({idx: []})
 for idx in range(1, 101)]
[beetle2_data_dict.update({idx: []})
 for idx in range(1, 101)]
[beetle3_data_dict.update({idx: []})
 for idx in range(1, 101)]


class UUIDS:
    SERIAL_COMMS = btle.UUID("0000dfb1-0000-1000-8000-00805f9b34fb")


class Delegate(btle.DefaultDelegate):

    def __init__(self, params):
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        global beetle_addresses
        global global_delegate_obj
        global beetle1_handshake_flag_dict
        global beetle2_handshake_flag_dict
        global beetle3_handshake_flag_dict
        global beetle1_timestamp_list
        global beetle2_timestamp_list
        global beetle3_timestamp_list
        global beetle1_clocksync_flag_dict
        global beetle2_clocksync_flag_dict
        global beetle3_clocksync_flag_dict
        global beetle1_buffer_dict
        global beetle2_buffer_dict
        global beetle3_buffer_dict
        global timestamp_string1
        global timestamp_string2
        global timestamp_string3
        global beetle1_datastring
        global beetle2_datastring
        global beetle3_datastring
        global float_flag_1
        global float_flag_2
        global float_flag_3
        global timestamp_flag_1
        global timestamp_flag_2
        global timestamp_flag_3
        global comma_count_1
        global comma_count_2
        global comma_count_3
        global beetle1_dataset_count
        global beetle2_dataset_count
        global beetle3_dataset_count
        global checksum_1
        global checksum_2
        global checksum_3
        global is_checksum_1
        global is_checksum_2
        global is_checksum_3
        ultra96_receiving_timestamp = time.time() * 1000

        for idx in range(len(beetle_addresses)):
            if global_delegate_obj[idx] == self:
                print("receiving data from %s" % (beetle_addresses[idx]))
                print("data: " + data.decode('UTF-8'))
                if beetle_addresses[idx] in beetle1_buffer_dict:
                    beetle1_buffer_dict[beetle_addresses[idx]
                                        ] += data.decode('UTF-8')
                if beetle_addresses[idx] in beetle2_buffer_dict:
                    beetle2_buffer_dict[beetle_addresses[idx]
                                        ] += data.decode('UTF-8')
                if beetle_addresses[idx] in beetle3_buffer_dict:
                    beetle3_buffer_dict[beetle_addresses[idx]
                                        ] += data.decode('UTF-8')
                if beetle_addresses[idx] in beetle1_buffer_dict:
                    for char in beetle1_buffer_dict[beetle_addresses[idx]]:
                        if char == 'A' or beetle1_handshake_flag_dict[beetle_addresses[idx]] is True:
                            if char == 'A':
                                ultra96_receiving_timestamp = time.time() * 1000
                                continue
                            if char == '>':  # end of packet
                                beetle1_timestamp_list.append(
                                    int(timestamp_string1))
                                beetle1_timestamp_list.append(
                                    ultra96_receiving_timestamp)
                                beetle1_handshake_flag_dict.update(
                                    {beetle_addresses[idx]: False})
                                beetle1_clocksync_flag_dict.update(
                                    {beetle_addresses[idx]: True})
                                beetle1_buffer_dict.update(
                                    {"1C:BA:8C:1D:30:22": ""})
                                print(beetle1_timestamp_list)
                                return
                            elif char != '>':
                                if char == '|':
                                    # signify start of next timestamp
                                    beetle1_timestamp_list.append(
                                        int(timestamp_string1))
                                    timestamp_string1 = ""
                                else:
                                    timestamp_string1 += char
                        elif char == 'D' or beetle1_handshake_flag_dict[beetle_addresses[idx]] is False:
                            
                            """
                            if char == '|' or is_checksum_1 is True: # checksum value is next
                                is_checksum_1 = True
                                if char != '|':
                                    beetle1_datastring += char
                                checksum_1 = beetle1_datastring
                            elif char != '|' and is_checksum_1 is False:
                                checksum_1 ^= char
                            """
                            """
                            if char != 'D' and char != '.' and char != ',' and (float_flag_1 is True or timestamp_flag_1 is True):
                                beetle1_datastring += char
                            elif char == '.':  # integer still belongs to original floating point value
                                beetle1_datastring += char
                                float_flag_1 = True
                            elif char == ',':  # next value
                                comma_count_1 += 1
                                if comma_count_1 == 2:  # already past timestamp value
                                    timestamp_flag_1 = False
                                    beetle1_data_dict[beetle1_dataset_count].append(int(beetle1_datastring))
                                elif (comma_count_1 > 2 and comma_count_1 < 9) or (comma_count_1 > 2 and comma_count_1 < 9):
                                    # (D,ts,acc1,acc2,acc3|D,gy1,gy2,gy3|D,ts,acc1,acc2,acc3|D,gy1,gy2,gy3)
                                    # D,ts,acc1,acc2,acc3,gy1,gy2,gy3,D,ts,acc1,acc2,acc3,gy1,gy2,gy3
                                    beetle1_data_dict[beetle1_dataset_count].append(float(beetle1_datastring))
                                beetle1_datastring = ""
                            elif char == 'D':  # start of another packet
                                if comma_count_1 == 14:

                                beetle1_dataset_count += 1
                                timestamp_flag_1 = True
                            """

                """
                if beetle_addresses[idx] in beetle2_buffer_dict:
                    for char in beetle2_buffer_dict[beetle_addresses[idx]]:
                        if char == 'A' or beetle2_handshake_flag_dict[beetle_addresses[idx]] is True:
                            if beetle2_handshake_flag_dict[beetle_addresses[idx]] == True:
                                if char == '>':  # end of packet
                                    ultra96_receiving_timestamp = time.time()
                                    beetle2_timestamp_list.append(
                                        ultra96_receiving_timestamp)
                                    beetle2_handshake_flag_dict.update(
                                        {beetle_addresses[idx]: False})
                                    beetle2_clocksync_flag_dict.update(
                                        {beetle_addresses[idx]: True})
                                    #beetle1_buffer_dict.update({"1C:BA:8C:1D:30:22":""})
                                    return
                                elif char != '>':
                                    if char == '|':
                                        # signify start of next timestamp
                                        beetle2_timestamp_list.append(
                                            int(timestamp_string2))
                                        timestamp_string2 = ""
                                    else:
                                        timestamp_string2 += char
                            else:
                                pass
                        elif char == 'D' or beetle2_handshake_flag_dict[beetle_addresses[idx]] is False:
                            pass
                        if beetle_addresses[idx] in beetle1_buffer_dict:
                    for char in beetle3_buffer_dict[beetle_addresses[idx]]:
                        if char == 'A' or beetle3_handshake_flag_dict[beetle_addresses[idx]] is True:
                            if beetle3_handshake_flag_dict[beetle_addresses[idx]] == True:
                                if char == '>':  # end of packet
                                    ultra96_receiving_timestamp = time.time()
                                    beetle3_timestamp_list.append(
                                        ultra96_receiving_timestamp)
                                    beetle3_handshake_flag_dict.update(
                                        {beetle_addresses[idx]: False})
                                    beetle3_clocksync_flag_dict.update(
                                        {beetle_addresses[idx]: True})
                                    #beetle1_buffer_dict.update({"1C:BA:8C:1D:30:22":""})
                                    return
                                elif char != '>':
                                    if char == '|':
                                        # signify start of next timestamp
                                        beetle3_timestamp_list.append(
                                            int(timestamp_string3))
                                        timestamp_string3 = ""
                                    else:
                                        timestamp_string3 += char
                            else:
                                pass
                        elif char == 'D' or beetle3_handshake_flag_dict[beetle_addresses[idx]] is False:
                            pass
                """


def initHandshake(beetle_peripheral, address):
    global beetles_connection_flag_dict
    global beetle1_timestamp_list
    global beetle2_timestamp_list
    global beetle3_timestamp_list
    global beetle1_clocksync_flag_dict
    global beetle2_clocksync_flag_dict
    global beetle3_clocksync_flag_dict
    global beetle1_clock_offset
    ultra96_sending_timestamp = time.time() * 1000
    for bdAddress, boolFlag in beetles_connection_flag_dict.items():
        if bdAddress == address and boolFlag == False:
            for characteristic in beetle_peripheral.getCharacteristics():
                if characteristic.uuid == UUIDS.SERIAL_COMMS:
                    ultra96_sending_timestamp = time.time() * 1000
                    if address == beetle1_timestamp_list[0]:
                        beetle1_timestamp_list.append(
                            ultra96_sending_timestamp)
                        beetles_connection_flag_dict.update(
                            {address: True})
                    # uncomment below lines if testing all beetles
                    """elif address == beetle2_timestamp_list[0]:
                        beetle2_timestamp_list.append(
                            ultra96_sending_timestamp)
                    elif address == beetle3_timestamp_list[0]:
                        beetle3_timestamp_list.append(ultra96_sending_timestamp)"""
                    characteristic.write(
                        bytes('H', 'utf-8'), withResponse=False)
                    while True:
                        if beetle_peripheral.waitForNotifications(10):
                            if address in beetle1_clocksync_flag_dict and beetle1_clocksync_flag_dict[address] is True:
                                characteristic.write(
                                    bytes('A', 'utf-8'), withResponse=False)
                                print("handshake succeeded with %s" % (
                                    address))
                                # function for time calibration
                                beetle1_clock_offset = calculate_clock_offset(beetle1_timestamp_list)
                                print("beetle1 clock offset: ", beetle1_clock_offset)
                                break
                            else:
                                continue
                            """
                            if address in beetle2_clocksync_flag_dict and beetle2_clocksync_flag_dict[address] is True:
                                characteristic.write(
                                    bytes('A', 'utf-8'), withResponse=False)
                                print("handshake succeeded with %s" % (
                                    address))
                                break
                            else:
                                continue
                            if address in beetle3_clocksync_flag_dict and beetle3_clocksync_flag_dict[address] is True:
                                characteristic.write(
                                    bytes('A', 'utf-8'), withResponse=False)
                                print("handshake succeeded with %s" % (
                                    address))
                                break
                            else:
                                continue
                            """


def establish_connection(address):
    global beetle_addresses
    global global_beetle_periphs
    global global_delegate_obj
    global beetles_connection_flag_dict

    while True:
        try:
            for idx in range(len(beetle_addresses)):
                # for initial connections or when any beetle is disconnected
                if beetle_addresses[idx] == address and beetles_connection_flag_dict[beetle_addresses[idx]] is False:
                    print("connecting with %s" % (address))
                    beetle_peripheral = btle.Peripheral(address)
                    global_beetle_periphs[idx] = beetle_peripheral
                    beetle_peri_delegate = Delegate(address)
                    global_delegate_obj[idx] = beetle_peri_delegate
                    beetle_peripheral.withDelegate(beetle_peri_delegate)
                    initHandshake(beetle_peripheral, address)
                    print("Connected to %s" % (address))
            break
        except:
            print("failed to connect to %s" % (address))
            time.sleep(1)
            continue


def reestablish_connection(beetle_peri, address):
    while True:
        try:
            print("reconnecting to %s" % (address))
            beetle_peri.connect(address)
            print("re-connected to %s" % (address))
            # is handshaking needed after re-connection??
            """initHandshake(beetle_peripheral, address):"""
            getBeetleData(beetle_peri)
        except:
            print("error reconnecting to %s" % (address))
            time.sleep(1)
            continue


def getBeetleData(beetle_peri):
    while True:
        try:
            if beetle_peri.waitForNotifications(20):
                print("getting data...")
                # if number of datasets received from all beetles exceed expectation
                if beetle_peri.addr == "1C:BA:8C:1D:30:22":
                    if len(beetle1_data_dict) >= 100:
                        return
                """
                elif beetle_peri.addr == "1C:BA:8C:1D:30:22":
                    if len(beetle2_data_dict) >= 100:
                        return
                elif beetle_peri.addr == "1C:BA:8C:1D:30:22":
                    if len(beetle3_data_dict) >= 100:
                        return
                """
                continue
        except Exception as e:
            print(e)
            """
            try:
                beetle_peri.disconnect()
            except:
                pass
            """
            print("disconnecting beetle_peri: %s" % (beetle_peri.addr))
            reestablish_connection(beetle_peri, beetle_peri.addr)


"""def executeMachineLearning():"""

"""def send_results_to_servers():

"""

if __name__ == '__main__':
    # max_workers = number of beetles
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as connection_executor:
        connection_futures = {connection_executor.submit(
            establish_connection, address): address for address in beetle_addresses}
    connection_executor.shutdown(wait=True)

    while True:
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as data_executor:
            receive_data_futures = {data_executor.submit(
                getBeetleData, beetle): beetle for beetle in global_beetle_periphs}
        data_executor.shutdown(wait=True)
        """
        ml_future = futures.ProcessPoolExecutor(max_workers=os.cpu_count())
        ml_process = ml_future.submit(executeMachineLearning)
        with future in concurrent.futures.as_completed(ml_process):
            ml_future.shutdown(wait=True)
            send_results = futures.ProcessPoolExecutor(max_workers=os.cpu_count())
            send_results_process = send_results.submit(send_results_to_servers)
        """
