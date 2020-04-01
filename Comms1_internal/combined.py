from bluepy import btle
import concurrent
from concurrent import futures
import threading
import multiprocessing
import time
from time_sync import *
import eval_client
import dashBoardClient
from joblib import dump, load
import numpy  # to count labels and store in dict
import operator  # to get most predicted label
import json


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
                print("data: " + data.decode('ISO-8859-1'))
                if beetle_addresses[idx] == "50:F1:4A:CC:01:C4":  # emg beetle data
                    emg_buffer[beetle_addresses[idx]
                               ] += data.decode('ISO-8859-1')
                    if '>' in data.decode('ISO-8859-1'):
                        arr = emg_buffer[beetle_addresses[idx]].split(">")[0]
                        final_arr = arr.split(",")
                        board_client.send_data_to_DB(
                            beetle_addresses[idx], final_arr)
                        emg_buffer[beetle_addresses[idx]] = ""
                else:
                    if incoming_data_flag[beetle_addresses[idx]] is True:
                        if handshake_flag_dict[beetle_addresses[idx]] is True:
                            buffer_dict[beetle_addresses[idx]
                                        ] += data.decode('ISO-8859-1')
                            if '>' not in data.decode('ISO-8859-1'):
                                pass
                            else:
                                if 'A' in buffer_dict[beetle_addresses[idx]]:
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
                                            print("beetle: %s" %
                                                  (beetle_addresses[idx]))
                                            print(
                                                timestamp_dict[beetle_addresses[idx]])
                                            return
                                        elif char != '>':
                                            if char == '|':  # signify start of next timestamp
                                                timestamp_dict[beetle_addresses[idx]].append(
                                                    int(datastring_dict[beetle_addresses[idx]]))
                                                datastring_dict[beetle_addresses[idx]] = ""
                                            else:
                                                datastring_dict[beetle_addresses[idx]] += char
                                else:
                                    pass
                        else:
                            if '>' in data.decode('ISO-8859-1'):
                                buffer_dict[beetle_addresses[idx]
                                            ] += data.decode('ISO-8859-1')
                                print("storing dance dataset")
                                packet_count_dict[beetle_addresses[idx]] += 1
                            else:
                                buffer_dict[beetle_addresses[idx]
                                            ] += data.decode('ISO-8859-1')


"""
class EMGThread(beetle):
    def __init__(self):
        thread = threading.Thread(target=self.getEMGData, args=(beetle, ))
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def getEMGData(beetle):
        while True:
            try:
                if beetle.waitForNotifications(2):
                    continue
            except Exception as e:
                reestablish_connection(beetle)
"""


def initHandshake(beetle):
    ultra96_sending_timestamp = time.time() * 1000
    incoming_data_flag[beetle.addr] = True
    handshake_flag_dict[beetle.addr] = True
    for characteristic in beetle.getCharacteristics():
        if characteristic.uuid == UUIDS.SERIAL_COMMS:
            ultra96_sending_timestamp = time.time() * 1000
            timestamp_dict[beetle.addr].append(
                ultra96_sending_timestamp)
            print("Sending 'T' and 'H' and 'Z' packets to %s" % (beetle.addr))
            characteristic.write(
                bytes('T', 'UTF-8'), withResponse=False)
            characteristic.write(
                bytes('H', 'UTF-8'), withResponse=False)
            characteristic.write(
                bytes('Z', 'UTF-8'), withResponse=False)
            while True:
                try:
                    if beetle.waitForNotifications(2):
                        if clocksync_flag_dict[beetle.addr] is True:
                            # function for time calibration
                            clock_offset_dict[beetle.addr].append(calculate_clock_offset(
                                timestamp_dict[beetle.addr]))
                            timestamp_dict[beetle.addr].clear()
                            print("beetle %s clock offset: %i" %
                                  (beetle.addr, clock_offset_dict[beetle.addr][-1]))
                            clocksync_flag_dict[beetle.addr] = False
                            incoming_data_flag[beetle.addr] = False
                            return
                        else:
                            continue
                    else:
                        print(
                            "Failed to receive timestamp, sending 'Z', 'T', 'H', and 'R' packet to %s" % (beetle.addr))
                        characteristic.write(
                            bytes('R', 'UTF-8'), withResponse=False)
                        characteristic.write(
                            bytes('T', 'UTF-8'), withResponse=False)
                        characteristic.write(
                            bytes('H', 'UTF-8'), withResponse=False)
                        characteristic.write(
                            bytes('Z', 'UTF-8'), withResponse=False)
                except Exception as e:
                    reestablish_connection(beetle)


def establish_connection(address):
    while True:
        try:
            for idx in range(len(beetle_addresses)):
                # for initial connections or when any beetle is disconnected
                if beetle_addresses[idx] == address:
                    if global_beetle[idx] != 0:  # do not reconnect if already connected
                        return
                    else:
                        print("connecting with %s" % (address))
                        beetle = btle.Peripheral(address)
                        global_beetle[idx] = beetle
                        beetle_delegate = Delegate(address)
                        global_delegate_obj[idx] = beetle_delegate
                        beetle.withDelegate(beetle_delegate)
                        if address != "50:F1:4A:CC:01:C4":
                            initHandshake(beetle)
                        print("Connected to %s" % (address))
                        return
        except Exception as e:
            print(e)
            time.sleep(1)


def reestablish_connection(beetle):
    while True:
        try:
            print("reconnecting to %s" % (beetle.addr))
            beetle.connect(beetle.addr)
            print("re-connected to %s" % (beetle.addr))
            return
        except:
            time.sleep(1)
            continue


def getDanceData(beetle):
    timeout_count = 0
    retries = 0
    incoming_data_flag[beetle.addr] = True
    for characteristic in beetle.getCharacteristics():
        if characteristic.uuid == UUIDS.SERIAL_COMMS:
            while True:
                if retries >= 5:
                    retries = 0
                    break
                print(
                    "sending 'A' to beetle %s to collect dancing data", (beetle.addr))
                characteristic.write(
                    bytes('A', 'UTF-8'), withResponse=False)
                retries += 1
                time.sleep(0.1)
            while True:
                try:
                    if beetle.waitForNotifications(2):
                        print("getting data...")
                        print(packet_count_dict[beetle.addr])
                        # if number of datasets received from all beetles exceed expectation
                        if packet_count_dict[beetle.addr] >= num_datasets:
                            print("sufficient datasets received from %s. Processing data now" % (
                                beetle.addr))
                            # reset for next dance move
                            packet_count_dict[beetle.addr] = 0
                            incoming_data_flag[beetle.addr] = False
                            while True:
                                if retries >= 8:
                                    break
                                characteristic.write(
                                    bytes('Z', 'UTF-8'), withResponse=False)
                                retries += 1
                                time.sleep(0.25)
                            return
                        continue
                    # beetle finish transmitting, but got packet losses
                    elif packet_count_dict[beetle.addr] >= num_datasets / 2:
                        print("sufficient datasets received from %s with packet losses. Processing data now" % (
                            beetle.addr))
                        # reset for next dance move
                        packet_count_dict[beetle.addr] = 0
                        incoming_data_flag[beetle.addr] = False
                        while True:
                            if retries >= 8:
                                break
                            characteristic.write(
                                bytes('Z', 'UTF-8'), withResponse=False)
                            retries += 1
                            time.sleep(0.25)
                        return
                    elif timeout_count >= 2:
                        incoming_data_flag[beetle.addr] = False
                        packet_count_dict[beetle.addr] = 0
                        timeout_count = 0
                        return
                    else:  # beetle did not start transmitting despite ultra96 sending 'A' previously, or still stuck at relative position
                        timeout_count += 1
                        packet_count_dict[beetle.addr] = 0
                        print(
                            "Failed to receive data, resending 'A' and 'B' packet to %s" % (beetle.addr))
                        characteristic.write(
                            bytes('A', 'UTF-8'), withResponse=False)
                        characteristic.write(
                            bytes('B', 'UTF-8'), withResponse=False)
                except Exception as e:
                    reestablish_connection(beetle)


def processData(address):
    if address != "50:F1:4A:CC:01:C4":
        position_dict = {address: {}}
        data_dict = {address: {}}

        def deserialize(buffer_dict, result_dict, address):
            for char in buffer_dict[address]:
                # start of new dataset
                if char == 'D' or end_flag[address] is True:
                    # 2nd part of dataset lost or '>' lost in transmission
                    if start_flag[address] is True:
                        try:
                            # if only '>' lost in transmission, can keep dataset. Else delete
                            if checksum_dict[address] != int(datastring_dict[address]):
                                del result_dict[address][dataset_count_dict[address]]
                        except Exception:  # 2nd part of dataset lost
                            try:
                                del result_dict[address][dataset_count_dict[address]]
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
                    # already past timestamp value
                    if comma_count_dict[address] == 1:
                        timestamp_flag_dict[address] = False
                        try:
                            result_dict[address].setdefault(
                                dataset_count_dict[address], []).append(int(datastring_dict[address]))
                        except Exception:
                            try:
                                del result_dict[address][dataset_count_dict[address]]
                            except Exception:
                                pass
                        float_flag_dict[address] = True
                    elif comma_count_dict[address] < 5:  # yaw, pitch, roll floats
                        try:
                            result_dict[address][dataset_count_dict[address]].append(
                                float("{0:.2f}".format((int(datastring_dict[address]) / divide_get_float))))
                        except Exception:
                            try:
                                del result_dict[address][dataset_count_dict[address]]
                            except Exception:
                                pass
                    else:  # accelerometer integers
                        try:
                            result_dict[address][dataset_count_dict[address]].append(
                                int(int(datastring_dict[address]) / divide_get_float))
                        except Exception:
                            try:
                                del result_dict[address][dataset_count_dict[address]]
                            except Exception:
                                pass
                    datastring_dict[address] = ""
                elif char == '>':  # end of current dataset
                    # print("ultra96 checksum: %i" % (checksum_dict[address]))
                    # print("beetle checksum: %i" % (int(datastring_dict[address])))
                    # received dataset is invalid; drop the dataset from data dictionary
                    try:
                        if checksum_dict[address] != int(datastring_dict[address]):
                            del result_dict[address][dataset_count_dict[address]]
                    except Exception:
                        try:
                            del result_dict[address][dataset_count_dict[address]]
                        except Exception:
                            pass
                    # reset datastring to prepare for next dataset
                    datastring_dict[address] = ""
                    # reset checksum to prepare for next dataset
                    checksum_dict[address] = 0
                    comma_count_dict[address] = 0
                    start_flag[address] = False
                    end_flag[address] = True
                    # missing data in previous dataset
                    try:
                        if len(result_dict[address][list(result_dict[address].keys())[-1]]) < 7:
                            del result_dict[address][list(
                                result_dict[address].keys())[-1]]
                    except Exception as e:
                        print(e)
                        print("error in processData in line 379")
                elif char == '|' or (float_flag_dict[address] is False and timestamp_flag_dict[address] is False):
                    if float_flag_dict[address] is True:
                        try:
                            result_dict[address][dataset_count_dict[address]].append(
                                int(int(datastring_dict[address]) / divide_get_float))
                        except Exception:
                            try:
                                del result_dict[address][dataset_count_dict[address]]
                            except Exception:
                                pass
                        # clear datastring to prepare take in checksum from beetle
                        datastring_dict[address] = ""
                        float_flag_dict[address] = False
                    elif char != '|' and char != '>':
                        datastring_dict[address] += char
            try:
                if len(result_dict[address][list(result_dict[address].keys())[-1]]) < 7:
                    del result_dict[address][list(
                        result_dict[address].keys())[-1]]
            except Exception as e:
                print(e)
                print("error in processData in line 478")
        for character in "\r\n":
            buffer_dict[address] = buffer_dict[address].replace(character, "")
        deserialize(buffer_dict, data_dict, address)
        dataset_count_dict[address] = 0
        data_tuple = (position_dict, data_dict)
        return data_tuple


def parse_hand_data(dic_data):

    # collect hand data
    data = []

    for v in dic_data[hand].values():  # k = data point no, v = data collected
        ypr = []  # yaw, pitch, roll, accx, y, z
        for i in range(1, 7):
            ypr.append(v[i])
        data.append(ypr)

    return(data)


def get_prediction(dic_data):
    ypr_data = parse_hand_data(dic_data)
    mlp = load('mlp_dance.joblib')
    y_pred = mlp.predict(ypr_data)
    unique, counts = numpy.unique(y_pred, return_counts=True)
    y_pred_count = dict(zip(unique, counts))
    prediction = max(y_pred_count.items(), key=operator.itemgetter(1))[0]
    return prediction


if __name__ == '__main__':
    # 50:F1:4A:CB:FE:EE: position 1, 1C:BA:8C:1D:30:22: position 2, 78:DB:2F:BF:2C:E2: position 3
    start_time = time.time()
    # global variables
    """
    beetle_addresses = ["50:F1:4A:CC:01:C4", "50:F1:4A:CB:FE:EE", "78:DB:2F:BF:2C:E2",
                        "1C:BA:8C:1D:30:22"]
    """
    beetle_addresses = ["50:F1:4A:CB:FE:EE",
                        "78:DB:2F:BF:2C:E2", "1C:BA:8C:1D:30:22"]
    divide_get_float = 100.0
    global_delegate_obj = []
    global_beetle = []
    handshake_flag_dict = {"50:F1:4A:CB:FE:EE": True,
                           "78:DB:2F:BF:2C:E2": True, "1C:BA:8C:1D:30:22": True}
    emg_buffer = {"50:F1:4A:CC:01:C4": ""}
    buffer_dict = {"50:F1:4A:CB:FE:EE": "",
                   "78:DB:2F:BF:2C:E2": "", "1C:BA:8C:1D:30:22": ""}
    position_buffer = {"50:F1:4A:CB:FE:EE": "",
                       "78:DB:2F:BF:2C:E2": "", "1C:BA:8C:1D:30:22": ""}
    incoming_data_flag = {"50:F1:4A:CB:FE:EE": False,
                          "78:DB:2F:BF:2C:E2": False, "1C:BA:8C:1D:30:22": False}
    relative_position_flag = {"50:F1:4A:CB:FE:EE": True,
                              "78:DB:2F:BF:2C:E2": True, "1C:BA:8C:1D:30:22": True}
    ground_truth = ""
    # data global variables
    num_datasets = 160
    beetle1_position_dict = {"50:F1:4A:CB:FE:EE": {}}
    beetle2_position_dict = {"78:DB:2F:BF:2C:E2": {}}
    beetle3_position_dict = {"1C:BA:8C:1D:30:22": {}}
    beetle1_data_dict = {"50:F1:4A:CB:FE:EE": {}}
    beetle2_data_dict = {"78:DB:2F:BF:2C:E2": {}}
    beetle3_data_dict = {"1C:BA:8C:1D:30:22": {}}
    datastring_dict = {"50:F1:4A:CB:FE:EE": "",
                       "78:DB:2F:BF:2C:E2": "", "1C:BA:8C:1D:30:22": ""}
    packet_count_dict = {"50:F1:4A:CB:FE:EE": 0,
                         "78:DB:2F:BF:2C:E2": 0, "1C:BA:8C:1D:30:22": 0}
    dataset_count_dict = {"50:F1:4A:CB:FE:EE": 0,
                          "78:DB:2F:BF:2C:E2": 0, "1C:BA:8C:1D:30:22": 0}
    float_flag_dict = {"50:F1:4A:CB:FE:EE": False,
                       "78:DB:2F:BF:2C:E2": False, "1C:BA:8C:1D:30:22": False}
    timestamp_flag_dict = {"50:F1:4A:CB:FE:EE": False,
                           "78:DB:2F:BF:2C:E2": False, "1C:BA:8C:1D:30:22": False}
    comma_count_dict = {"50:F1:4A:CB:FE:EE": 0,
                        "78:DB:2F:BF:2C:E2": 0, "1C:BA:8C:1D:30:22": 0}
    checksum_dict = {"50:F1:4A:CB:FE:EE": 0,
                     "78:DB:2F:BF:2C:E2": 0, "1C:BA:8C:1D:30:22": 0}
    start_flag = {"50:F1:4A:CB:FE:EE": False,
                  "78:DB:2F:BF:2C:E2": False, "1C:BA:8C:1D:30:22": False}
    end_flag = {"50:F1:4A:CB:FE:EE": False,
                "78:DB:2F:BF:2C:E2": False, "1C:BA:8C:1D:30:22": False}
    # clock synchronization global variables
    dance_count = 0
    clocksync_flag_dict = {"50:F1:4A:CB:FE:EE": False,
                           "78:DB:2F:BF:2C:E2": False, "1C:BA:8C:1D:30:22": False}
    timestamp_dict = {"50:F1:4A:CB:FE:EE": [],
                      "78:DB:2F:BF:2C:E2": [], "1C:BA:8C:1D:30:22": []}
    clock_offset_dict = {"50:F1:4A:CB:FE:EE": [],
                         "78:DB:2F:BF:2C:E2": [], "1C:BA:8C:1D:30:22": []}

    [global_delegate_obj.append(0) for idx in range(len(beetle_addresses))]
    [global_beetle.append(0) for idx in range(len(beetle_addresses))]
    """
    establish_connection("50:F1:4A:CC:01:C4")
    time.sleep(1)
    """
    establish_connection("50:F1:4A:CB:FE:EE")
    time.sleep(1)

    establish_connection("78:DB:2F:BF:2C:E2")
    time.sleep(1)

    establish_connection("1C:BA:8C:1D:30:22")
    time.sleep(1)

    
    try:
        eval_client = eval_client.Client(
            "192.168.43.248", 8080, 6, "cg40024002group6")
    except Exception as e:
        print(e)
    
    """
    try:
        board_client = dashBoardClient.Client(
            "192.168.42.14", 8080, 6, "cg40024002group6")
    except Exception as e:
        print(e)
    """
    """
    # start collecting data only after 1 min passed
    while True:
        elapsed_time = time.time() - start_time
        if int(elapsed_time) == 60:
            break
        else:
            print(elapsed_time)
            time.sleep(1)
    """
    # emg_thread = EMGThread(global_beetle[0])
    while True:
        """
        # do calibration once every 4 moves; change 4 to other values according to time calibration needs
        if dance_count == 4:
            print("Proceed to do time calibration...")
            # clear clock_offset_dict for next time calibration
            for address in clock_offset_dict.keys():
                clock_offset_dict[address].clear()
            for beetle in global_beetle:
                if beetle.addr != "50:F1:4A:CC:01:C4":
                    initHandshake(beetle)
        if dance_count == 4:
            dance_count = 0
        dance_count += 1
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=7) as data_executor:
            receive_data_futures = {data_executor.submit(
                getDanceData, beetle): beetle for beetle in global_beetle}
            data_executor.shutdown(wait=True)
        pool = multiprocessing.Pool()
        workers = [pool.apply_async(processData, args=(address, ))
                   for address in beetle_addresses]
        result = [worker.get() for worker in workers]
        pool.close()
        try:
            for idx in range(0, len(result)):
                for address in result[idx][1].keys():
                    if address == "50:F1:4A:CB:FE:EE":
                        beetle1_data_dict[address] = result[idx][1][address]
                    elif address == "78:DB:2F:BF:2C:E2":
                        beetle2_data_dict[address] = result[idx][1][address]
                    elif address == "1C:BA:8C:1D:30:22":
                        beetle3_data_dict[address] = result[idx][1][address]
        except Exception as e:
            pass
        # clear buffer for next move
        for address in buffer_dict.keys():
            buffer_dict[address] = ""
        print(beetle1_data_dict)
        print(beetle2_data_dict)
        print(beetle3_data_dict)

        with open(r'dance.txt', 'a') as file:
            file.write(json.dumps(beetle1_data_dict) + "\n")
            file.write(json.dumps(beetle2_data_dict) + "\n")
            file.write(json.dumps(beetle3_data_dict) + "\n")
            file.close()

        # synchronization delay
        try:
            beetle1_time_ultra96 = calculate_ultra96_time(
                beetle1_data_dict, clock_offset_dict["50:F1:4A:CB:FE:EE"][0])

            beetle2_time_ultra96 = calculate_ultra96_time(
                beetle2_data_dict, clock_offset_dict["78:DB:2F:BF:2C:E2"][0])

            beetle3_time_ultra96 = calculate_ultra96_time(
                beetle3_data_dict, clock_offset_dict["1C:BA:8C:1D:30:22"][0])

            sync_delay = max(beetle1_time_ultra96, beetle2_time_ultra96, beetle3_time_ultra96) - \
                min(beetle1_time_ultra96, beetle2_time_ultra96, beetle3_time_ultra96)
        except Exception as e:
            sync_delay = 4123

        # print("Beetle 1 ultra 96 time: ", beetle1_time_ultra96)
        # print("Beetle 2 ultra 96 time: ", beetle2_time_ultra96)
        # print("Beetle 3 ultra 96 time: ", beetle3_time_ultra96)
        print("Synchronization delay is: ", sync_delay)
        """
        # machine learning
        # ml_result = get_prediction(beetle1_data_dict)
        ml_pool = multiprocessing.Pool()
        workers = ml_pool.apply_async(get_prediction, args=(beetle1_data_dict))
        ml_result = workers.get()
        ml_pool.close()
        """
        ml_result = "shoutout"
        # send data to eval and dashboard server
        eval_pool = multiprocessing.Pool()
        workers = eval_pool.apply_async(
            eval_client.send_data, args=("1 2 3", ml_result, str(sync_delay)))
        eval_pool.close()
        ground_truth = eval_client.receive_dancer_position()
        print(ground_truth)
        # eval_client.send_data("1 2 3", ml_result, str(sync_delay))
        
        """
        board_pool = multiprocessing.Pool()
        workers = board_pool.apply_async(
            board_client.send_data_to_DB, args=("MLDancer1", ml_result))
        board_pool.close()
        # board_client.send_data_to_DB("MLDancer1", ml_result)
        """
        break
