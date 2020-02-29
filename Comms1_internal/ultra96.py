from bluepy import btle
import concurrent
from concurrent import futures
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
                if handshake_flag_dict[beetle_addresses[idx]] is False:
                    # start of dataset
                    if 'D' in data.decode('UTF-8') and ((packet_count_dict[beetle_addresses[idx]] % 1) != 0.5):
                        packet_count_dict[beetle_addresses[idx]] += 0.5
                    # end of dataset
                    if '>' in data.decode('UTF-8') and ((packet_count_dict[beetle_addresses[idx]] % 1) == 0.5):
                        packet_count_dict[beetle_addresses[idx]] += 0.5
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
                            print("beetle: %s" % (beetle_addresses[idx]))
                            print(timestamp_dict[beetle_addresses[idx]])
                            return
                        elif char != '>':
                            if char == '|':  # signify start of next timestamp
                                timestamp_dict[beetle_addresses[idx]].append(
                                    int(timestamp_string_dict[beetle_addresses[idx]]))
                                timestamp_string_dict[beetle_addresses[idx]] = ""
                            else:
                                timestamp_string_dict[beetle_addresses[idx]] += char


def initHandshake(beetle_peripheral, address, clocksync_count):
    global timestamp_dict
    global clocksync_flag_dict
    global handshake_flag_dict

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
                                clock_offset_dict[address].append(calculate_clock_offset(
                                    timestamp_dict[address]))
                                print("beetle %s clock offset: %i" %
                                      (address, clock_offset_dict[address][-1]))
                                # clear timestamp_dict for next clock sync data
                                timestamp_dict[address] = []
                                if clocksync_count != 3:
                                    handshake_flag_dict[address] = True
                                    clocksync_flag_dict[address] = False
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
                    for count in range(1, 4):
                        initHandshake(beetle_peripheral, address, count)
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
            beetles_connection_flag_dict.update(
                {beetle_peri.addr: True})
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
                if packet_count_dict[beetle_peri.addr] == 100.0:
                    print("sufficient datasets received from %s. Processing data now" % (
                        beetle_peri.addr))
                    # reset for next dance move
                    packet_count_dict[beetle_peri.addr] = 0.0
                    # reset for next dance move
                    dataset_count_dict[beetle_peri.addr] = 0
                    return
                continue
        except Exception as e:
            print("disconnecting beetle_peri: %s" % (beetle_peri.addr))
            beetles_connection_flag_dict.update(
                {beetle_peri.addr: False})
            reestablish_connection(beetle_peri, beetle_peri.addr)


@ray.remote
def processData(address, buffer_obj, dataset_count_obj, timestamp_obj, checksum_obj, float_obj, datastring_obj, comma_obj):
    # use buffer_obj as it is, no need for ray.get() then assigning it to buffer_dict
    buffer_dict = buffer_obj
    dataset_count_dict = dataset_count_obj
    timestamp_flag_dict = timestamp_obj
    checksum_dict = checksum_obj
    float_flag_dict = float_obj
    datastring_dict = datastring_obj
    comma_count_dict = comma_obj
    data_dict = {address: {}}
    [data_dict[address].update({idx: []})
     for idx in range(1, 101)]

    for char in buffer_dict[address]:
        if char == 'D':  # start of new dataset
            dataset_count_dict[address] += 1
            timestamp_flag_dict[address] = True
            checksum_dict[address] ^= ord(char)
        if char != 'D' and char != '.' and char != ',' and char != '|' and char != '>' and (float_flag_dict[address] is True or timestamp_flag_dict[address] is True):
            datastring_dict[address] += char
            checksum_dict[address] ^= ord(char)
        elif char == '.':  # integer still belongs to original floating point value
            datastring_dict[address] += char
            checksum_dict[address] ^= ord(char)
        elif char == ',':  # next value
            comma_count_dict[address] += 1
            checksum_dict[address] ^= ord(char)
            if comma_count_dict[address] == 1:  # already past timestamp value
                timestamp_flag_dict[address] = False
                data_dict[address].setdefault(
                    dataset_count_dict[address], []).append(int(datastring_dict[address]))
                float_flag_dict[address] = True
            else:
                data_dict[address][dataset_count_dict[address]].append(
                    float(datastring_dict[address]))
            datastring_dict[address] = ""
        elif char == '>':  # end of current dataset
            print("ultra96 checksum: %i" % (checksum_dict[address]))
            print("beetle checksum: %i" % (int(datastring_dict[address])))
            # received dataset is invalid; drop the dataset from data dictionary
            if checksum_dict[address] != int(datastring_dict[address]):
                del data_dict[address][dataset_count_dict[address]]
            # reset datastring to prepare for next dataset
            datastring_dict[address] = ""
            # reset checksum to prepare for next dataset
            checksum_dict[address] = 0
            comma_count_dict[address] = 0
        elif char == '|' or (float_flag_dict[address] is False and timestamp_flag_dict[address] is False):
            if float_flag_dict[address] is True:
                data_dict[address][dataset_count_dict[address]].append(
                    float(datastring_dict[address]))
                # clear datastring to prepare take in checksum from beetle
                datastring_dict[address] = ""
                float_flag_dict[address] = False
            elif char != '|' and char != '>':
                datastring_dict[address] += char
    return data_dict


"""def executeMachineLearning():"""

"""def send_results_to_servers():

"""

if __name__ == '__main__':
    # global variables
    #beetle_addresses = ["1C:BA:8C:1D:30:22", "50:F1:4A:CB:FE:EE", "78:D8:2F:BF:3F:63"]
    beetle_addresses = ["78:DB:2F:BF:3F:23"]
    global_delegate_obj = []
    global_beetle_periphs = []
    beetles_connection_flag_dict = {}  # {beetle_address1:handshakeflag1,.....}
    handshake_flag_dict = {
        "78:DB:2F:BF:3F:23": True, "78:DB:2F:BF:3B:54": True, "78:DB:2F:BF:2C:E2": True}
    buffer_dict = {"78:DB:2F:BF:3F:23": "",
                   "78:DB:2F:BF:3B:54": "", "78:DB:2F:BF:2C:E2": ""}
    # data global variables
    beetle1_data_dict = {"78:DB:2F:BF:3F:23": {}}
    beetle2_data_dict = {"78:DB:2F:BF:3B:54": {}}
    beetle3_data_dict = {"78:DB:2F:BF:2C:E2": {}}
    datastring_dict = {"78:DB:2F:BF:3F:23": "",
                       "78:DB:2F:BF:3B:54": "", "78:DB:2F:BF:2C:E2": ""}
    packet_count_dict = {"78:DB:2F:BF:3F:23": 0.0,
                         "78:DB:2F:BF:3B:54": 0.0, "78:DB:2F:BF:2C:E2": 0.0}
    dataset_count_dict = {"78:DB:2F:BF:3F:23": 0,
                          "78:DB:2F:BF:3B:54": 0, "78:DB:2F:BF:2C:E2": 0}
    float_flag_dict = {"78:DB:2F:BF:3F:23": False,
                       "78:DB:2F:BF:3B:54": False, "78:DB:2F:BF:2C:E2": False}
    timestamp_flag_dict = {"78:DB:2F:BF:3F:23": False,
                           "78:DB:2F:BF:3B:54": False, "78:DB:2F:BF:2C:E2": False}
    comma_count_dict = {"78:DB:2F:BF:3F:23": 0,
                        "78:DB:2F:BF:3B:54": 0, "78:DB:2F:BF:2C:E2": 0}
    checksum_dict = {"78:DB:2F:BF:3F:23": 0,
                     "78:DB:2F:BF:3B:54": 0, "78:DB:2F:BF:2C:E2": 0}
    # clock synchronization global variables
    timestamp_string_dict = {"78:DB:2F:BF:3F:23": "",
                             "78:DB:2F:BF:3B:54": "", "78:DB:2F:BF:2C:E2": ""}
    clocksync_flag_dict = {"78:DB:2F:BF:3F:23": False,
                           "78:DB:2F:BF:3B:54": False, "78:DB:2F:BF:2C:E2": False}
    timestamp_dict = {"78:DB:2F:BF:3F:23": [],
                      "78:DB:2F:BF:3B:54": [], "78:DB:2F:BF:2C:E2": []}
    clock_offset_dict = {"78:DB:2F:BF:3F:23": [],
                         "78:DB:2F:BF:3B:54": [], "78:DB:2F:BF:2C:E2": []}

    [global_delegate_obj.append(0) for idx in range(len(beetle_addresses))]
    [global_beetle_periphs.append(0) for idx in range(len(beetle_addresses))]
    [beetles_connection_flag_dict.update({beetle_addresses[idx]:False})
     for idx in range(len(beetle_addresses))]
    [beetle1_data_dict["78:DB:2F:BF:3F:23"].update({idx: []})
     for idx in range(1, 101)]
    [beetle2_data_dict["78:DB:2F:BF:3B:54"].update({idx: []})
     for idx in range(1, 101)]
    [beetle3_data_dict["78:DB:2F:BF:2C:E2"].update({idx: []})
     for idx in range(1, 101)]

    ray.init()

    # max_workers = number of beetles
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as connection_executor1:
        connection_futures = {connection_executor1.submit(
            establish_connection, "1C:BA:8C:1D:30:22")}
    connection_executor1.shutdown(wait=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as connection_executor2:
        connection_futures = {connection_executor2.submit(
            establish_connection, "50:F1:4A:CB:FE:EE")}
    connection_executor2.shutdown(wait=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as connection_executor3:
        connection_futures = {connection_executor3.submit(
            establish_connection, "78:D8:2F:BF:3F:63")}
    connection_executor3.shutdown(wait=True)
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as connection_executor4:
        connection_futures = {connection_executor4.submit(
            establish_connection, "78:DB:2F:BF:3F:23")}
    connection_executor4.shutdown(wait=True)
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as connection_executor5:
        connection_futures = {connection_executor5.submit(
            establish_connection, "78:DB:2F:BF:3B:54")}
    connection_executor5.shutdown(wait=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as connection_executor6:
        connection_futures = {connection_executor6.submit(
            establish_connection, "78:DB:2F:BF:2C:E2")}
    connection_executor6.shutdown(wait=True)
    """
    while True:
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as data_executor:
            receive_data_futures = {data_executor.submit(
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
            data_dict_obj = processData.remote(address, buffer_obj, dataset_count_obj, timestamp_obj,
                                               checksum_obj, float_obj, datastring_obj, comma_obj)
            if "78:DB:2F:BF:3F:23" in ray.get(data_dict_obj):
                beetle1_data_dict = ray.get(data_dict_obj)
                # reset buffer for next dance move
                buffer_dict["78:DB:2F:BF:3F:23"] = ""
            elif "78:DB:2F:BF:3B:54" in ray.get(data_dict_obj):
                beetle2_data_dict = ray.get(data_dict_obj)
                # reset buffer for next dance move
                buffer_dict["78:DB:2F:BF:3B:54"] = ""
            elif "78:DB:2F:BF:2C:E2" in ray.get(data_dict_obj):
                beetle3_data_dict = ray.get(data_dict_obj)
                # reset buffer for next dance move
                buffer_dict["78:DB:2F:BF:2C:E2"] = ""
        print(beetle1_data_dict)
        print(beetle2_data_dict)
        print(beetle3_data_dict)
        # synchronization delay

        beetle1_time_ultra96 = calculate_ultra96_time(
            beetle1_data_dict, sum(clock_offset_dict["78:DB:2F:BF:3F:23"])/len(clock_offset_dict["78:DB:2F:BF:3F:23"]))
        beetle2_time_ultra96 = calculate_ultra96_time(
            beetle2_data_dict, sum(clock_offset_dict["78:DB:2F:BF:3B:54"])/len(clock_offset_dict["78:DB:2F:BF:3B:54"]))
        beetle3_time_ultra96 = calculate_ultra96_time(
            beetle3_data_dict, sum(clock_offset_dict["78:DB:2F:BF:2C:E2"])/len(clock_offset_dict["78:DB:2F:BF:2C:E2"]))
        # max(beetle3_time_ultra96, ...) - min(beetle1_time_ultra96, ...)
        sync_delay = max(beetle1_time_ultra96, beetle2_time_ultra96, beetle3_time_ultra96) - \
            min(beetle1_time_ultra96, beetle2_time_ultra96, beetle3_time_ultra96)

        print("Beetle 1 ultra 96 time: ", beetle1_time_ultra96)
        print("Beetle 2 ultra 96 time: ", beetle2_time_ultra96)
        print("Beetle 3 ultra 96 time: ", beetle3_time_ultra96)
        print("Synchronization delay is: ", sync_delay)
        break
        """
        ml_future = futures.ProcessPoolExecutor(max_workers=None)
        ml_process = ml_future.submit(executeMachineLearning)
        ml_process.result()
        send_results = futures.ProcessPoolExecutor(max_workers=None)
        send_results_process = send_results.submit(send_results_to_servers)
        """
        # send data to eval server
        # send data to dashboard server
