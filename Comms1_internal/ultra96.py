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
beetle1_packet_count = 0
beetle2_packet_count = 0
beetle3_packet_count = 0
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
# clock synchronization global variables
timestamp_string1 = ""
timestamp_string2 = ""
timestamp_string3 = ""
beetle1_clocksync_flag_dict = {"1C:BA:8C:1D:30:22": False}
beetle2_clocksync_flag_dict = {}
beetle3_clocksync_flag_dict = {}
beetle1_timestamp_list = ["1C:BA:8C:1D:30:22"]
beetle2_timestamp_list = []
beetle3_timestamp_list = []

[global_delegate_obj.append(0) for idx in range(len(beetle_addresses))]
[global_beetle_periphs.append(0) for idx in range(len(beetle_addresses))]
[beetles_connection_flag_dict.update({beetle_addresses[idx]:False})
 for idx in range(len(beetle_addresses))]
[beetle1_data_dict.update({idx: []})
 for idx in range(1, 11)]
[beetle2_data_dict.update({idx: []})
 for idx in range(1, 11)]
[beetle3_data_dict.update({idx: []})
 for idx in range(1, 11)]


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
        global beetle1_packet_count
        global beetle2_packet_count
        global beetle3_packet_count
        ultra96_receiving_timestamp = time.time() * 1000

        for idx in range(len(beetle_addresses)):
            if global_delegate_obj[idx] == self:
                print("receiving data from %s" % (beetle_addresses[idx]))
                print("data: " + data.decode('UTF-8'))
                if beetle_addresses[idx] in beetle1_buffer_dict:
                    if beetle1_handshake_flag_dict[beetle_addresses[idx]] is False:
                        beetle1_packet_count += 1  # 2 packets is 1 full dataset
                    beetle1_buffer_dict[beetle_addresses[idx]
                                        ] += data.decode('UTF-8')
                if beetle_addresses[idx] in beetle2_buffer_dict:
                    if beetle2_handshake_flag_dict[beetle_addresses[idx]] is False:
                        beetle2_packet_count += 1
                    beetle2_buffer_dict[beetle_addresses[idx]
                                        ] += data.decode('UTF-8')
                if beetle_addresses[idx] in beetle3_buffer_dict:
                    if beetle3_handshake_flag_dict[beetle_addresses[idx]] is False:
                        beetle3_packet_count += 1
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
                                beetle1_buffer_dict.update(  # clear serial input buffer to get ready for data packets
                                    {beetle_addresses[idx]: ""})
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
                """


def initHandshake(beetle_peripheral, address):
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
                                beetle1_clock_offset = calculate_clock_offset(
                                    beetle1_timestamp_list)
                                print("beetle1 clock offset: ",
                                      beetle1_clock_offset)
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
                    beetles_connection_flag_dict.update(
                        {address: True})
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
    global beetle1_packet_count
    global beetle2_packet_count
    global beetle3_packet_count
    global beetle1_dataset_count
    global beetle2_dataset_count
    global beetle3_dataset_count
    while True:
        try:
            if beetle_peri.waitForNotifications(20):
                print("getting data...")
                # if number of datasets received from all beetles exceed expectation
                if beetle_peri.addr == "1C:BA:8C:1D:30:22":
                    if beetle1_packet_count >= 20:
                        print("sufficient datasets received. Processing data now")
                        beetle1_packet_count = 0  # reset for next dance move
                        beetle1_dataset_count = 0  # reset for next dance move
                        return
                """
                elif beetle_peri.addr == "1C:BA:8C:1D:30:22":
                    if beetle2_packet_count >= 20:
                        beetle2_packet_count = 0
                        beetle2_dataset_count = 0
                        return
                elif beetle_peri.addr == "1C:BA:8C:1D:30:22":
                    if beetle3_packet_count >= 20:
                        beetle3_packet_count = 0
                        beetle3_dataset_count = 0
                        return
                """
                continue
        except Exception as e:
            print("disconnecting beetle_peri: %s" % (beetle_peri.addr))
            reestablish_connection(beetle_peri, beetle_peri.addr)


def processData():
    global beetle1_buffer_dict
    global float_flag_1
    global timestamp_flag_1
    global beetle1_datastring
    global checksum_1
    global comma_count_1
    global beetle1_data_dict
    global beetle1_dataset_count
    for char in beetle1_buffer_dict["1C:BA:8C:1D:30:22"]:
        # dummy dataset received by serial input: D1234,12.23,15.34,17.26|13>
        if char == 'D':  # start of new dataset
            beetle1_dataset_count += 1
            timestamp_flag_1 = True
            checksum_1 ^= ord(char)
        if char != 'D' and char != '.' and char != ',' and char != '|' and char != '>' and (float_flag_1 is True or timestamp_flag_1 is True):
            beetle1_datastring += char
            checksum_1 ^= ord(char)
        elif char == '.':  # integer still belongs to original floating point value
            beetle1_datastring += char
            checksum_1 ^= ord(char)
        elif char == ',':  # next value
            comma_count_1 += 1
            checksum_1 ^= ord(char)
            if comma_count_1 == 1:  # already past timestamp value
                timestamp_flag_1 = False
                beetle1_data_dict[beetle1_dataset_count].append(
                    int(beetle1_datastring))
                float_flag_1 = True
            else:
                beetle1_data_dict[beetle1_dataset_count].append(
                    float(beetle1_datastring))
            beetle1_datastring = ""
        elif char == '>':  # end of current dataset
            print("checksum_1: %i" % (checksum_1))
            print("beetle1_datastring: %i" % (int(beetle1_datastring)))
            # received dataset is invalid; drop the dataset from data dictionary
            if checksum_1 != int(beetle1_datastring):
                del beetle1_data_dict[beetle1_dataset_count]
            beetle1_datastring = ""  # reset datastring to prepare for next dataset
            checksum_1 = 0  # reset checksum to prepare for next dataset
            comma_count_1 = 0
        elif char == '|' or (float_flag_1 is False and timestamp_flag_1 is False):
            if float_flag_1 is True:
                beetle1_data_dict[beetle1_dataset_count].append(
                    float(beetle1_datastring))
                beetle1_datastring = ""  # clear datastring to prepare take in checksum from beetle
                float_flag_1 = False
            elif char != '|' and char != '>':
                beetle1_datastring += char

    # remember to return the data dicts here as they wont get updated at global level!!
    return beetle1_data_dict


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
        process_data_future = futures.ProcessPoolExecutor(
            max_workers=os.cpu_count())
        data_process = process_data_future.submit(processData)
        # calling result() on future instances wait for the futures to finish running before proceeding
        # remember to assign return value from result() to global data dicts!!
        beetle1_data_dict = data_process.result()
        print(beetle1_data_dict)
        [beetle1_data_dict.update({idx: []})
         for idx in range(1, 11)]
        """
        ml_future = futures.ProcessPoolExecutor(max_workers=os.cpu_count())
        ml_process = ml_future.submit(executeMachineLearning)
        ml_process.result()
        send_results = futures.ProcessPoolExecutor(max_workers=os.cpu_count())
        send_results_process = send_results.submit(send_results_to_servers)
        """
