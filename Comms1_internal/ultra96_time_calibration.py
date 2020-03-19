from bluepy import btle
import concurrent
from concurrent import futures
import multiprocessing
import time
from time_sync import *
import eval_client
import dashBoardClient


class UUIDS:
    SERIAL_COMMS = btle.UUID("0000dfb1-0000-1000-8000-00805f9b34fb")


class Delegate(btle.DefaultDelegate):

    def __init__(self, params):
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        ultra96_receiving_timestamp = time.time() * 1000

        for idx in range(len(beetle_addresses)):
            if global_delegate_obj[idx] == self:
                print("receiving data from %s" % (beetle_addresses[idx]))
                print("data: " + data.decode('UTF-8'))
                if handshake_flag_dict[beetle_addresses[idx]] is True:
                    buffer_dict[beetle_addresses[idx]] += data.decode('UTF-8')
                    if '>' not in data.decode('UTF-8'):
                        pass
                    else:
                        for char in buffer_dict[beetle_addresses[idx]]:
                            if char == 'A':
                                ultra96_receiving_timestamp = time.time() * 1000
                                continue
                            if char == '>':  # end of packet
                                timestamp_dict[beetle_addresses[idx]].append(
                                    int(datastring_dict[beetle_addresses[idx]]))
                                timestamp_dict[beetle_addresses[idx]].append(
                                    ultra96_receiving_timestamp)
                                handshake_flag_dict[beetle_addresses[idx]] = False
                                clocksync_flag_dict[beetle_addresses[idx]] = True
                                # clear serial input buffer to get ready for data packets
                                datastring_dict[beetle_addresses[idx]] = ""
                                buffer_dict[beetle_addresses[idx]] = ""
                                print("beetle: %s" % (beetle_addresses[idx]))
                                print(timestamp_dict[beetle_addresses[idx]])
                                return
                            elif char != '>':
                                if char == '|':  # signify start of next timestamp
                                    timestamp_dict[beetle_addresses[idx]].append(
                                        int(datastring_dict[beetle_addresses[idx]]))
                                    datastring_dict[beetle_addresses[idx]] = ""
                                else:
                                    datastring_dict[beetle_addresses[idx]] += char
                else:
                    if '>' in data.decode('UTF-8'):
                        buffer_dict[beetle_addresses[idx]
                                    ] += data.decode('UTF-8')
                        packet_count_dict[beetle_addresses[idx]] += 1
                    else:
                        buffer_dict[beetle_addresses[idx]
                                    ] += data.decode('UTF-8')


def initHandshake(beetle_peripheral):
    ultra96_sending_timestamp = time.time() * 1000
    handshake_flag_dict[beetle_peripheral.addr] = True
    for characteristic in beetle_peripheral.getCharacteristics():
        if characteristic.uuid == UUIDS.SERIAL_COMMS:
            ultra96_sending_timestamp = time.time() * 1000
            timestamp_dict[beetle_peripheral.addr].append(
                ultra96_sending_timestamp)
            """
            characteristic.write(
                bytes('T', 'utf-8'), withResponse=False)
            """
            characteristic.write(
                bytes('H', 'utf-8'), withResponse=False)
            while True:
                try:
                    if beetle_peripheral.waitForNotifications(10):
                        if clocksync_flag_dict[beetle_peripheral.addr] is True:
                            characteristic.write(
                                bytes('A', 'utf-8'), withResponse=False)
                            # function for time calibration
                            clock_offset_dict[beetle_peripheral.addr].append(calculate_clock_offset(
                                timestamp_dict[beetle_peripheral.addr]))
                            timestamp_dict[beetle_peripheral.addr].clear()
                            print("beetle %s clock offset: %i" %
                                  (beetle_peripheral.addr, clock_offset_dict[beetle_peripheral.addr][-1]))
                            clocksync_flag_dict[beetle_peripheral.addr] = False
                            return
                        else:
                            continue
                except Exception as e:
                    print(e)
                    reestablish_connection(
                        beetle_peripheral, beetle_peripheral.addr)


def establish_connection(address):
    while True:
        try:
            for idx in range(len(beetle_addresses)):
                # for initial connections or when any beetle is disconnected
                if beetle_addresses[idx] == address:
                    print("connecting with %s" % (address))
                    beetle_peripheral = btle.Peripheral(address)
                    global_beetle_periphs[idx] = beetle_peripheral
                    beetle_peri_delegate = Delegate(address)
                    global_delegate_obj[idx] = beetle_peri_delegate
                    beetle_peripheral.withDelegate(beetle_peri_delegate)
                    time.sleep(1)
                    initHandshake(beetle_peripheral)
                    print("Connected to %s" % (address))
                    return
        except Exception as e:
            print(e)
            time.sleep(1)
            continue


def reestablish_connection(beetle_peri, address):
    while True:
        try:
            print("reconnecting to %s" % (address))
            beetle_peri.connect(address)
            print("re-connected to %s" % (address))
            return
        except:
            return


def getBeetleData(beetle_peri):
    while True:
        try:
            if beetle_peri.waitForNotifications(20):
                print("getting data...")
                print(packet_count_dict[beetle_peri.addr])
                # if number of datasets received from all beetles exceed expectation
                if packet_count_dict[beetle_peri.addr] >= num_datasets:
                    print("sufficient datasets received from %s. Processing data now" % (
                        beetle_peri.addr))
                    # reset for next dance move
                    packet_count_dict[beetle_peri.addr] = 0
                    # reset for next dance move
                    dataset_count_dict[beetle_peri.addr] = 0
                    return
                continue
        except Exception as e:
            print(e)
            reestablish_connection(beetle_peri, beetle_peri.addr)


def processData(address):
    data_dict = {address: {}}
    for character in "\r\n":
        buffer_dict[address] = buffer_dict[address].replace(character, "")
    for char in buffer_dict[address]:
        if char == 'D' or end_flag[address] is True:  # start of new dataset
            # 2nd part of dataset lost or '>' lost in transmission
            if start_flag[address] is True:
                try:
                    # if only '>' lost in transmission, can keep dataset. Else delete
                    if checksum_dict[address] != int(datastring_dict[address]):
                        del data_dict[address][dataset_count_dict[address]]
                except Exception:  # 2nd part of dataset lost
                    try:
                        del data_dict[address][dataset_count_dict[address]]
                    except Exception:
                        pass
                # reset datastring to prepare for next dataset
                datastring_dict[address] = ""
                # reset checksum to prepare for next dataset
                checksum_dict[address] = 0
                comma_count_dict[address] = 0
            dataset_count_dict[address] += 1
            timestamp_flag_dict[address] = True
            checksum_dict[address] ^= ord(char)
            start_flag[address] = True
            end_flag[address] = False
        if char != 'D' and char != ',' and char != '|' and char != '>' and (char == '-' or char == '.' or float_flag_dict[address] is True or timestamp_flag_dict[address] is True):
            datastring_dict[address] += char
            checksum_dict[address] ^= ord(char)
        elif char == ' ':
            datastring_dict[address] += char
            checksum_dict[address] ^= ord(char)
        elif char == ',':  # next value
            comma_count_dict[address] += 1
            checksum_dict[address] ^= ord(char)
            if comma_count_dict[address] == 1:  # already past timestamp value
                timestamp_flag_dict[address] = False
                try:
                    data_dict[address].setdefault(
                        dataset_count_dict[address], []).append(int(datastring_dict[address]))
                except Exception:
                    try:
                        del data_dict[address][dataset_count_dict[address]]
                    except Exception:
                        pass
                float_flag_dict[address] = True
            else:
                try:
                    data_dict[address][dataset_count_dict[address]].append(
                        float(datastring_dict[address]))
                except Exception:
                    try:
                        del data_dict[address][dataset_count_dict[address]]
                    except Exception:
                        pass
            datastring_dict[address] = ""
        elif char == '>':  # end of current dataset
            # print("ultra96 checksum: %i" % (checksum_dict[address]))
            # print("beetle checksum: %i" % (int(datastring_dict[address])))
            # received dataset is invalid; drop the dataset from data dictionary
            try:
                if checksum_dict[address] != int(datastring_dict[address]):
                    del data_dict[address][dataset_count_dict[address]]
            except Exception:
                try:
                    del data_dict[address][dataset_count_dict[address]]
                except Exception:
                    pass
            # reset datastring to prepare for next dataset
            datastring_dict[address] = ""
            # reset checksum to prepare for next dataset
            checksum_dict[address] = 0
            comma_count_dict[address] = 0
            start_flag[address] = False
            end_flag[address] = True
        elif char == '|' or (float_flag_dict[address] is False and timestamp_flag_dict[address] is False):
            if float_flag_dict[address] is True:
                try:
                    data_dict[address][dataset_count_dict[address]].append(
                        float(datastring_dict[address]))
                except Exception:
                    try:
                        del data_dict[address][dataset_count_dict[address]]
                    except Exception:
                        pass
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
    beetle_addresses = ["50:F1:4A:CB:FE:EE", "78:DB:2F:BF:3B:54"]
    global_delegate_obj = []
    global_beetle_periphs = []
    handshake_flag_dict = {"1C:BA:8C:1D:30:22": True, "50:F1:4A:CB:FE:EE": True, "78:D8:2F:BF:3F:63": True,
                           "78:DB:2F:BF:3F:23": True, "78:DB:2F:BF:3B:54": True, "78:DB:2F:BF:2C:E2": True}
    buffer_dict = {"1C:BA:8C:1D:30:22": "", "50:F1:4A:CB:FE:EE": "", "78:D8:2F:BF:3F:63": "", "78:DB:2F:BF:3F:23": "",
                   "78:DB:2F:BF:3B:54": "", "78:DB:2F:BF:2C:E2": ""}
    buffer_dataset_dict = {"1C:BA:8C:1D:30:22": "", "50:F1:4A:CB:FE:EE": "", "78:D8:2F:BF:3F:63": "", "78:DB:2F:BF:3F:23": "",
                           "78:DB:2F:BF:3B:54": "", "78:DB:2F:BF:2C:E2": ""}
    # data global variables
    num_datasets = 50
    # {"78:DB:2F:BF:3F:23": {1: [100, 12.23, 14.45, 15.67]}, {2: [100, 14.56, -23.24, -16.78]}}
    beetle1_data_dict = {"1C:BA:8C:1D:30:22": {}}
    beetle2_data_dict = {"50:F1:4A:CB:FE:EE": {}}
    beetle3_data_dict = {"78:D8:2F:BF:3F:63": {}}
    beetle4_data_dict = {"78:DB:2F:BF:3F:23": {}}
    beetle5_data_dict = {"78:DB:2F:BF:3B:54": {}}
    beetle6_data_dict = {"78:DB:2F:BF:2C:E2": {}}
    datastring_dict = {"1C:BA:8C:1D:30:22": "", "50:F1:4A:CB:FE:EE": "", "78:D8:2F:BF:3F:63": "", "78:DB:2F:BF:3F:23": "",
                       "78:DB:2F:BF:3B:54": "", "78:DB:2F:BF:2C:E2": ""}
    packet_count_dict = {"1C:BA:8C:1D:30:22": 0, "50:F1:4A:CB:FE:EE": 0, "78:D8:2F:BF:3F:63": 0, "78:DB:2F:BF:3F:23": 0,
                         "78:DB:2F:BF:3B:54": 0, "78:DB:2F:BF:2C:E2": 0}
    dataset_count_dict = {"1C:BA:8C:1D:30:22": 0, "50:F1:4A:CB:FE:EE": 0, "78:D8:2F:BF:3F:63": 0, "78:DB:2F:BF:3F:23": 0,
                          "78:DB:2F:BF:3B:54": 0, "78:DB:2F:BF:2C:E2": 0}
    float_flag_dict = {"1C:BA:8C:1D:30:22": False, "50:F1:4A:CB:FE:EE": False, "78:D8:2F:BF:3F:63": False, "78:DB:2F:BF:3F:23": False,
                       "78:DB:2F:BF:3B:54": False, "78:DB:2F:BF:2C:E2": False}
    timestamp_flag_dict = {"1C:BA:8C:1D:30:22": False, "50:F1:4A:CB:FE:EE": False, "78:D8:2F:BF:3F:63": False, "78:DB:2F:BF:3F:23": False,
                           "78:DB:2F:BF:3B:54": False, "78:DB:2F:BF:2C:E2": False}
    comma_count_dict = {"1C:BA:8C:1D:30:22": 0, "50:F1:4A:CB:FE:EE": 0, "78:D8:2F:BF:3F:63": 0, "78:DB:2F:BF:3F:23": 0,
                        "78:DB:2F:BF:3B:54": 0, "78:DB:2F:BF:2C:E2": 0}
    checksum_dict = {"1C:BA:8C:1D:30:22": 0, "50:F1:4A:CB:FE:EE": 0, "78:D8:2F:BF:3F:63": 0, "78:DB:2F:BF:3F:23": 0,
                     "78:DB:2F:BF:3B:54": 0, "78:DB:2F:BF:2C:E2": 0}
    start_flag = {"1C:BA:8C:1D:30:22": False, "50:F1:4A:CB:FE:EE": False, "78:D8:2F:BF:3F:63": False, "78:DB:2F:BF:3F:23": False,
                  "78:DB:2F:BF:3B:54": False, "78:DB:2F:BF:2C:E2": False}
    end_flag = {"1C:BA:8C:1D:30:22": False, "50:F1:4A:CB:FE:EE": False, "78:D8:2F:BF:3F:63": False, "78:DB:2F:BF:3F:23": False,
                "78:DB:2F:BF:3B:54": False, "78:DB:2F:BF:2C:E2": False}
    # clock synchronization global variables
    dance_count = 0
    clocksync_flag_dict = {"1C:BA:8C:1D:30:22": False, "50:F1:4A:CB:FE:EE": False, "78:D8:2F:BF:3F:63": False, "78:DB:2F:BF:3F:23": False,
                           "78:DB:2F:BF:3B:54": False, "78:DB:2F:BF:2C:E2": False}
    timestamp_dict = {"1C:BA:8C:1D:30:22": [], "50:F1:4A:CB:FE:EE": [], "78:D8:2F:BF:3F:63": [], "78:DB:2F:BF:3F:23": [],
                      "78:DB:2F:BF:3B:54": [], "78:DB:2F:BF:2C:E2": []}
    clock_offset_dict = {"1C:BA:8C:1D:30:22": [], "50:F1:4A:CB:FE:EE": [], "78:D8:2F:BF:3F:63": [], "78:DB:2F:BF:3F:23": [],
                         "78:DB:2F:BF:3B:54": [], "78:DB:2F:BF:2C:E2": []}

    [global_delegate_obj.append(0) for idx in range(len(beetle_addresses))]
    [global_beetle_periphs.append(0) for idx in range(len(beetle_addresses))]
    """
    establish_connection("1C:BA:8C:1D:30:22")
    time.sleep(1)
    """
    
    establish_connection("50:F1:4A:CB:FE:EE")
    time.sleep(1)
    
    """
    establish_connection("78:DB:2F:BF:3F:63")
    time.sleep(1)
    """
    """
    establish_connection("78:DB:2F:BF:3F:23")
    time.sleep(1)
    """
    
    establish_connection("78:DB:2F:BF:3B:54")
    
    """
    establish_connection("78:DB:2F:BF:2C:E2")
    """
    """
    try:
        eval_client = eval_client.Client(
            "192.168.1.101", 8080, 6, "cg40024002group6")  # ip address is address of server
    except Exception as e:
        print(e)
    print("connected to eval")
    """
    while True:
        with concurrent.futures.ThreadPoolExecutor(max_workers=7) as data_executor:
            receive_data_futures = {data_executor.submit(
                getBeetleData, beetle): beetle for beetle in global_beetle_periphs}
        data_executor.shutdown(wait=True)
        pool = multiprocessing.Pool()
        workers = [pool.apply_async(processData, args=(address, ))
                   for address in beetle_addresses]
        result = [worker.get() for worker in workers]
        for idx in range(0, len(result)):
            for address in result[idx].keys():
                if address == "1C:BA:8C:1D:30:22":
                    beetle1_data_dict[address] = result[idx][address]
                elif address == "50:F1:4A:CB:FE:EE":
                    beetle2_data_dict[address] = result[idx][address]
                elif address == "78:D8:2F:BF:3F:63":
                    beetle3_data_dict[address] = result[idx][address]
                elif address == "78:DB:2F:BF:3F:23":
                    beetle4_data_dict[address] = result[idx][address]
                elif address == "78:DB:2F:BF:3B:54":
                    beetle5_data_dict[address] = result[idx][address]
                elif address == "78:DB:2F:BF:2C:E2":
                    beetle6_data_dict[address] = result[idx][address]
        # clear buffer for next move
        for address in buffer_dict.keys():
            buffer_dict[address] = ""
        print(beetle1_data_dict)
        print(beetle2_data_dict)
        print(beetle3_data_dict)
        print(beetle4_data_dict)
        print(beetle5_data_dict)
        print(beetle6_data_dict)

        # synchronization delay
        """
        beetle1_time_ultra96 = calculate_ultra96_time(
            beetle1_data_dict, clock_offset_dict["1C:BA:8C:1D:30:22"][0])
        """
        
        beetle2_time_ultra96 = calculate_ultra96_time(
            beetle2_data_dict, clock_offset_dict["50:F1:4A:CB:FE:EE"][0])
        
        """
        beetle3_time_ultra96 = calculate_ultra96_time(
            beetle3_data_dict, clock_offset_dict["78:DB:2F:BF:3F:63"][0])
        """
        """
        beetle4_time_ultra96 = calculate_ultra96_time(
            beetle4_data_dict, clock_offset_dict["78:DB:2F:BF:3F:23"][0])
        """
        
        beetle5_time_ultra96 = calculate_ultra96_time(
            beetle5_data_dict, clock_offset_dict["78:DB:2F:BF:3B:54"][0])
        
        """
        beetle6_time_ultra96 = calculate_ultra96_time(
            beetle6_data_dict, clock_offset_dict["78:DB:2F:BF:2C:E2"][0])
        """
        sync_delay = max(beetle2_time_ultra96, beetle5_time_ultra96) - \
            min(beetle2_time_ultra96, beetle5_time_ultra96)
        #print("Beetle 1 ultra 96 time: ", beetle1_time_ultra96)
        #print("Beetle 2 ultra 96 time: ", beetle2_time_ultra96)
        #print("Beetle 3 ultra 96 time: ", beetle3_time_ultra96)
        #print("Beetle 4 ultra 96 time: ", beetle4_time_ultra96)
        #print("Beetle 5 ultra 96 time: ", beetle5_time_ultra96)
        #print("Beetle 6 ultra 96 time: ", beetle6_time_ultra96)
        print("Synchronization delay is: ", sync_delay)
        """
        ml_result = ("1 2 3", "muscle")
        # send data to eval server
        # send data to dashboard server
        eval_client.send_data(ml_result[0], ml_result[1], str(sync_delay))
        """
        """
        dance_count += 1
        # do calibration once every 2 moves; change 2 to other values according to time calibration needs
        if dance_count == 2:
            print("Proceed to do time calibration...")
            # clear clock_offset_dict for next time calibration
            for address in clock_offset_dict.keys():
                clock_offset_dict[address].clear()
            time.sleep(5)
            with concurrent.futures.ThreadPoolExecutor(max_workers=7) as time_executor:
                time_calibrate_futures = {time_executor.submit(
                    initHandshake, beetle): beetle for beetle in global_beetle_periphs}
            time_executor.shutdown(wait=True)
            dance_count = 0
        else:
            for beetle_peri in global_beetle_periphs:
                for characteristic in beetle_peri.getCharacteristics():
                    if characteristic.uuid == UUIDS.SERIAL_COMMS:
                        characteristic.write(
                            bytes('S', 'utf-8'), withResponse=False)
        """
        """
        ml_future = futures.ProcessPoolExecutor(max_workers=None)
        ml_process = ml_future.submit(executeMachineLearning)
        ml_process.result()
        send_results = futures.ProcessPoolExecutor(max_workers=None)
        send_results_process = send_results.submit(send_results_to_servers)
        """
        # send data to eval server
        # send data to dashboard server
        # clear the data dictionaries for next dance move
        beetle1_data_dict = {"1C:BA:8C:1D:30:22": {}}
        beetle2_data_dict = {"50:F1:4A:CB:FE:EE": {}}
        beetle3_data_dict = {"78:D8:2F:BF:3F:63": {}}
        beetle4_data_dict = {"78:DB:2F:BF:3F:23": {}}
        beetle5_data_dict = {"78:DB:2F:BF:3B:54": {}}
        beetle6_data_dict = {"78:DB:2F:BF:2C:E2": {}}
