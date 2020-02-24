from bluepy import btle
import concurrent
from concurrent import futures
import multiprocessing
import ray
import time
from time_sync import *


class UUIDS:
    SERIAL_COMMS = btle.UUID("0000dfb1-0000-1000-8000-00805f9b34fb")


class Delegate(btle.DefaultDelegate):

    def __init__(self, params):
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        global beetle_addresses
        global global_delegate_obj
        global handshake_flag_dict
        global timestamp_dict
        global clocksync_flag_dict
        global buffer_dict
        global timestamp_dict
        global timestamp_string_dict
        global packet_count_dict
        ultra96_receiving_timestamp = time.time() * 1000

        for idx in range(len(beetle_addresses)):
            if global_delegate_obj[idx] == self:
                print("receiving data from %s" % (beetle_addresses[idx]))
                print("data: " + data.decode('UTF-8'))
                # 2 packets is 1 full dataset
                packet_count_dict[beetle_addresses[idx]] += 1
                buffer_dict[beetle_addresses[idx]] += data.decode('UTF-8')
                for char in buffer_dict[beetle_addresses[idx]]:
                    if char == 'A' or handshake_flag_dict[beetle_addresses[idx]] is True:
                        if char == 'A':
                            ultra96_receiving_timestamp = time.time() * 1000
                            continue
                        if char == '>':  # end of packet
                            timestamp_dict[beetle_addresses[idx]].append(
                                int(timestamp_string_dict[beetle_addresses[idx]]))
                            timestamp_dict[beetle_addresses[idx]].append(
                                ultra96_receiving_timestamp)
                            handshake_flag_dict[beetle_addresses[idx]] = False
                            clocksync_flag_dict[beetle_addresses[idx]] = True
                            # clear serial input buffer to get ready for data packets
                            buffer_dict[beetle_addresses[idx]] = ""
                            packet_count_dict[beetle_addresses[idx]] = 0
                            print("beetle: %s" % (beetle_addresses[idx]))
                            print(timestamp_dict[[beetle_addresses[idx]])
                            return
                        elif char != '>':
                            if char == '|':  # signify start of next timestamp
                                timestamp_dict[beetle_addresses[idx]].append(
                                    int(timestamp_string_dict[beetle_addresses[idx]]))
                                timestamp_string_dict[beetle_addresses[idx]] = ""
                            else:
                                timestamp_string_dict[beetle_addresses[idx]] += char



def initHandshake(beetle_peripheral, address):
    global timestamp_dict
    global clocksync_flag_dict
    global beetle1_clock_offset
    ultra96_sending_timestamp = time.time() * 1000

    for bdAddress, boolFlag in beetles_connection_flag_dict.items():
        if bdAddress == address and boolFlag == False:
            for characteristic in beetle_peripheral.getCharacteristics():
                if characteristic.uuid == UUIDS.SERIAL_COMMS:
                    ultra96_sending_timestamp = time.time() * 1000
                    timestamp_dict[address].append(ultra96_sending_timestamp)
                    characteristic.write(
                        bytes('H', 'utf-8'), withResponse=False)
                    while True:
                        if beetle_peripheral.waitForNotifications(10):
                            if clocksync_flag_dict[address] is True:
                                characteristic.write(
                                    bytes('A', 'utf-8'), withResponse=False)
                                print("handshake succeeded with %s" % (
                                    address))
                                # function for time calibration
                                beetle1_clock_offset = calculate_clock_offset(
                                    timestamp_dict[address])
                                print("beetle1 clock offset: ",
                                      beetle1_clock_offset)
                                break
                            else:
                                continue


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
            getBeetleData(beetle_peri)
        except:
            print("error reconnecting to %s" % (address))
            time.sleep(1)
            continue


def getBeetleData(beetle_peri):
    global packet_count_dict
    global dataset_count_dict
    while True:
        try:
            if beetle_peri.waitForNotifications(20):
                print("getting data...")
                # if number of datasets received from all beetles exceed expectation
                if packet_count_dict[beetle_peri.addr] >= 20:
                    print("sufficient datasets received. Processing data now")
                    packet_count_dict[beetle_peri.addr] = 0  # reset for next dance move
                    dataset_count_dict[beetle_peri.addr] = 0 # reset for next dance move
                    return
                continue
        except Exception as e:
            print("disconnecting beetle_peri: %s" % (beetle_peri.addr))
            reestablish_connection(beetle_peri, beetle_peri.addr)


@ray.remote
def processData(address, buffer_obj, dataset_count_obj, timestamp_obj, checksum_obj, float_obj, datastring_obj, comma_obj):
    buffer_dict = ray.get(buffer_obj)
    dataset_count_dict = ray.get(dataset_count_obj)
    timestamp_flag_dict = ray.get(timestamp_obj)
    checksum_dict = ray.get(checksum_obj)
    float_flag_dict = ray.get(float_obj)
    datastring_dict = ray.get(datastring_obj)
    comma_count_dict = ray.get(comma_obj)

    for address in beetle_addresses:
        for char in buffer_dict[address]:
            if char == 'D':  # start of new dataset


    for char in beetle1_buffer_dict["1C:BA:8C:1D:30:22"]:
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
                beetle1_data_dict.setdefault(
                    beetle1_dataset_count, []).append(int(beetle1_datastring))
                # beetle1_data_dict[beetle1_dataset_count].append(
                #    int(beetle1_datastring))
                float_flag_1 = True
            else:
                beetle1_data_dict[beetle1_dataset_count].append(
                    float(beetle1_datastring))
            beetle1_datastring = ""
        elif char == '>':  # end of current dataset
            print("ultra96 checksum: %i" % (checksum_1))
            print("beetle checksum: %i" % (int(beetle1_datastring)))
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
    # global variables
    beetle_addresses= ["1C:BA:8C:1D:30:22"]
    global_delegate_obj= []
    global_beetle_periphs= []
    beetles_connection_flag_dict= {}  # {beetle_address1:handshakeflag1,.....}
    handshake_flag_dict= {"1C:BA:8C:1D:30:22": True}
    buffer_dict= {"1C:BA:8C:1D:30:22": ""}
    # data global variables
    beetle1_data_dict= {"1C:BA:8C:1D:30:22": {}}
    beetle2_data_dict= {}
    beetle3_data_dict= {}
    beetle1_datastring= ""
    beetle2_datastring= ""
    beetle3_datastring= ""
    packet_count_dict= {"1C:BA:8C:1D:30:22": 0}
    dataset_count_dict= {"1C:BA:8C:1D:30:22": 0}
    float_flag_dict= {"1C:BA:8C:1D:30:22": False}
    timestamp_flag_dict= {"1C:BA:8C:1D:30:22": False}
    comma_count_dict= {"1C:BA:8C:1D:30:22": 0}
    checksum_dict= {"1C:BA:8C:1D:30:22": 0}
    # clock synchronization global variables
    timestamp_string_dict= {{"1C:BA:8C:1D:30:22": ""}
    clocksync_flag_dict= {"1C:BA:8C:1D:30:22": False}
    timestamp_dict= {"1C:BA:8C:1D:30:22": []}

    [global_delegate_obj.append(0) for idx in range(len(beetle_addresses))]
    [global_beetle_periphs.append(0) for idx in range(len(beetle_addresses))]
    [beetles_connection_flag_dict.update({beetle_addresses[idx]:False})
    for idx in range(len(beetle_addresses))]
    [beetle1_data_dict["1C:BA:8C:1D:30:22"].update({idx: []})
    for idx in range(1, 11)]
    [beetle2_data_dict.update({idx: []})
    for idx in range(1, 11)]
    [beetle3_data_dict.update({idx: []})
    for idx in range(1, 11)]

    ray.init()

    # max_workers = number of beetles
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as connection_executor:
        connection_futures= {connection_executor.submit(
            establish_connection, address): address for address in beetle_addresses}
    connection_executor.shutdown(wait=True)
    while True:
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as data_executor:
            receive_data_futures= {data_executor.submit(
                getBeetleData, beetle): beetle for beetle in global_beetle_periphs}
        data_executor.shutdown(wait=True)
        buffer_obj = ray.put(buffer_dict)
        dataset_count_obj = ray.put(dataset_count_dict)
        timestamp_obj = ray.put(timestamp_flag_dict)
        checksum_obj = ray.put(checksum_dict)
        float_obj = ray.put(float_flag_dict)
        datastring_obj = ray.put(datastring_dict)
        comma_obj = ray.put(comma_count_dict)
        for address in beetle_addresses:
            processData.remote(address, buffer_obj, dataset_count_obj, timestamp_obj,
                               checksum_obj, float_obj, datastring_obj, comma_obj)

        print(beetle1_data_dict)
        # synchronization delay
        beetle1_time_ultra96= calculate_ultra96_time(
            beetle1_data_dict, beetle1_clock_offset)
        # max(beetle3_time_ultra96, ...) - min(beetle1_time_ultra96, ...)
        print("Beetle 1 ultra 96 time: ", beetle1_time_ultra96)
        """
        ml_future = futures.ProcessPoolExecutor(max_workers=None)
        ml_process = ml_future.submit(executeMachineLearning)
        ml_process.result()
        send_results = futures.ProcessPoolExecutor(max_workers=None)
        send_results_process = send_results.submit(send_results_to_servers)
        """
        # send data to eval server
        # send data to dashboard server
