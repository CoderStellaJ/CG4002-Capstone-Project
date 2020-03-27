from bluepy import btle
import concurrent
from concurrent import futures
import threading
import multiprocessing
import time
from time_sync import *
import eval_client
import dashBoardClient
import pickle
import numpy  # to count labels and store in dict
import operator  # to get most predicted label


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
                if incoming_data_flag[beetle_addresses[idx]] is True and relative_position_flag[beetle_addresses[idx]] is True:
                    position_buffer[beetle_addresses[idx]
                                    ] += data.decode('ISO-8859-1')
                    print("storing position dataset")
                    if '>' in data.decode('ISO-8859-1'):
                        packet_count_dict[beetle_addresses[idx]] += 1
                elif incoming_data_flag[beetle_addresses[idx]] is True and relative_position_flag[beetle_addresses[idx]] is False:
                    if handshake_flag_dict[beetle_addresses[idx]] is True:
                        buffer_dict[beetle_addresses[idx]
                                    ] += data.decode('ISO-8859-1')
                        if '>' not in data.decode('ISO-8859-1'):
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
                        if '>' in data.decode('ISO-8859-1'):
                            buffer_dict[beetle_addresses[idx]
                                        ] += data.decode('ISO-8859-1')
                            print("storing dance dataset")
                            packet_count_dict[beetle_addresses[idx]] += 1
                        else:
                            buffer_dict[beetle_addresses[idx]
                                        ] += data.decode('ISO-8859-1')
                        # send data to dashboard once every 10 datasets
                        if packet_count_dict[beetle_addresses[idx]] % 10 == 0 and '>' in data.decode('ISO-8859-1'):
                            print("sending data to dashboard")
                            arr = buffer_dict[beetle_addresses[idx]].split("|")[
                                0]
                            final_arr = arr.split(",")
                            """
                            board_client.send_data_to_DB(
                                beetle_addresses[idx], final_arr)
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
            characteristic.write(
                bytes('T', 'UTF-8'), withResponse=False)
            characteristic.write(
                bytes('H', 'UTF-8'), withResponse=False)
            while True:
                try:
                    if beetle.waitForNotifications(2):
                        if clocksync_flag_dict[beetle.addr] is True:
                            clock_offset_dict[beetle.addr].clear()
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
                            "Failed to receive timestamp, sending 'T', 'H', and 'R' packet")
                        for characteristic in beetle.getCharacteristics():
                            if characteristic.uuid == UUIDS.SERIAL_COMMS:
                                characteristic.write(
                                    bytes('T', 'UTF-8'), withResponse=False)
                                characteristic.write(
                                    bytes('H', 'UTF-8'), withResponse=False)
                                characteristic.write(
                                    bytes('R', 'UTF-8'), withResponse=False)
                                break
                except Exception as e:
                    reestablish_connection(beetle)
                    # if timestamp data already received from beetle
                    if clock_offset_dict[beetle.addr]:
                        incoming_data_flag[beetle.addr] = False
                        return


def establish_connection(address):
    while True:
        try:
            for idx in range(len(beetle_addresses)):
                # for initial connections or when any beetle is disconnected
                if beetle_addresses[idx] == address:
                    print("connecting with %s" % (address))
                    beetle = btle.Peripheral(address)
                    global_beetle[idx] = beetle
                    beetle_delegate = Delegate(address)
                    global_delegate_obj[idx] = beetle_delegate
                    beetle.withDelegate(beetle_delegate)
                    initHandshake(beetle)
                    print("Connected to %s" % (address))
                    return
        except Exception as e:
            print(e)
            time.sleep(1)
            continue


def reestablish_connection(beetle):
    while True:
        try:
            if beetle.waitForNotifications(2):
                return
            print("reconnecting to %s" % (beetle.addr))
            beetle.connect(beetle.addr)
            print("re-connected to %s" % (beetle.addr))
            return
        except:
            continue


def getPositionData(beetle):
    relative_position_flag[beetle.addr] = True
    if relative_position_flag[beetle.addr] is True:
        print("start moving to new positions in ")
        for i in range(3, 0, -1):
            time.sleep(1)
            print(i)
        for characteristic in beetle.getCharacteristics():
            if characteristic.uuid == UUIDS.SERIAL_COMMS:
                print("sending 'A' to beetle to kickstart beetle sensor collection")
                characteristic.write(
                    bytes('A', 'UTF-8'), withResponse=False)
                print("sending 'A' to beetle to collect relative position movement data")
                characteristic.write(
                    bytes('A', 'UTF-8'), withResponse=False)
                incoming_data_flag[beetle.addr] = True
                break
        while True:
            try:
                if beetle.waitForNotifications(3):
                    print("getting relative position data...")
                    if packet_count_dict[beetle.addr] >= 59:
                        relative_position_flag[beetle.addr] = False
                        incoming_data_flag[beetle.addr] = False
                        packet_count_dict[beetle.addr] = 0
                        for characteristic in beetle.getCharacteristics():
                            if characteristic.uuid == UUIDS.SERIAL_COMMS:
                                characteristic.write(
                                    bytes('P', 'UTF-8'), withResponse=False)
                                print("stop moving")
                                return
                    continue
                elif packet_count_dict[beetle.addr] >= 30:
                    relative_position_flag[beetle.addr] = False
                    incoming_data_flag[beetle.addr] = False
                    packet_count_dict[beetle.addr] = 0
                    for characteristic in beetle.getCharacteristics():
                        if characteristic.uuid == UUIDS.SERIAL_COMMS:
                            characteristic.write(
                                bytes('P', 'UTF-8'), withResponse=False)
                            print("stop moving")
                            return
                else:
                    for characteristic in beetle.getCharacteristics():
                        if characteristic.uuid == UUIDS.SERIAL_COMMS:
                            print(
                                "Failed to receive position data, sending 'A' packet")
                            characteristic.write(
                                bytes('A', 'UTF-8'), withResponse=False)
                            break
                    print("start moving again")
                    relative_position_flag[beetle.addr] = True
                    incoming_data_flag[beetle.addr] = True
            except Exception as e:
                reestablish_connection(beetle)
                if position_buffer[beetle.addr]:
                    relative_position_flag[beetle.addr] = False
                    incoming_data_flag[beetle.addr] = False
                    for characteristic in beetle.getCharacteristics():
                        if characteristic.uuid == UUIDS.SERIAL_COMMS:
                            characteristic.write(
                                bytes('P', 'UTF-8'), withResponse=False)
                            print("stop moving")
                            return
    else:
        return


def processData(address):
    position_dict = {address: {}}
    data_dict = {address: {}}

    def deserialize(buffer_dict, result_dict, address):
        for char in buffer_dict[address]:
            if char == 'D' or end_flag[address] is True:  # start of new dataset
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
                if comma_count_dict[address] == 1:  # already past timestamp value
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
                            int(int(datastring_dict[address]) / 100))
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
                    print("error in processData in line 334")
            elif char == '|' or (float_flag_dict[address] is False and timestamp_flag_dict[address] is False):
                if float_flag_dict[address] is True:
                    try:
                        result_dict[address][dataset_count_dict[address]].append(
                            int(int(datastring_dict[address]) / 100))
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
            print("error in processData in line 356")
    for character in "\r\n":
        position_buffer[address] = position_buffer[address].replace(
            character, "")
    deserialize(position_buffer, position_dict, address)
    dataset_count_dict[address] = 0
    data_tuple = (position_dict, data_dict)
    return data_tuple


def parse_hand_data(dic_data):

    # collect hand data
    data = []

    for k, v in dic_data[hand].items():  # k = data point no, v = data collected
        ypr = []  # yaw, pitch, roll
        for i in range(1, 4):
            ypr.append(v[i])
        data.append(ypr)

    return(data)


def get_prediction(dic_data):
    print(dic_data)
    ypr_data = parse_hand_data(dic_data)
    with open("knn_dance.pkl", 'rb') as file:
        knn = pickle.load(file)
    # knn = load('knn_dance.pkl')
    y_pred = knn.predict(ypr_data)
    unique, counts = numpy.unique(y_pred, return_counts=True)
    y_pred_count = dict(zip(unique, counts))
    prediction = max(y_pred_count.items(), key=operator.itemgetter(1))[0]
    return prediction

# add dummy datasets to data dict if less than num_datasets, delete otherwise


def clean_up_dict(data_dict, address):
    if len(data_dict[address]) < num_datasets:
        count = num_datasets - len(data_dict[address])
        for num in range(len(data_dict[address])+1, len(data_dict[address])+count+1):
            data_dict[address][num] = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    elif len(data_dict[address]) > num_datasets:
        count = len(data_dict[address]) - num_datasets
        for num in range(0, count):
            del data_dict[address][list(data_dict[address].keys())[-1]]


if __name__ == '__main__':
    leg = "50:F1:4A:CB:FE:EE"
    hand = "78:DB:2F:BF:3B:54"
    # global variables
    # beetle_addresses = ["78:DB:2F:BF:3F:63", "78:DB:2F:BF:3F:23", "78:DB:2F:BF:3B:54", "1C:BA:8C:1D:30:22", "50:F1:4A:CB:FE:EE", "78:DB:2F:BF:3F:63"]
    # change this depending on number of decimal places needed; get original float from beetle sensors
    divide_get_float = 100.0
    beetle_addresses = ["78:DB:2F:BF:3F:23"]
    global_delegate_obj = []
    global_beetle = []
    handshake_flag_dict = {"1C:BA:8C:1D:30:22": True, "50:F1:4A:CB:FE:EE": True, "78:DB:2F:BF:3F:63": True,
                           "78:DB:2F:BF:3F:23": True, "78:DB:2F:BF:3B:54": True, "78:DB:2F:BF:2C:E2": True}
    buffer_dict = {"1C:BA:8C:1D:30:22": "", "50:F1:4A:CB:FE:EE": "", "78:DB:2F:BF:3F:63": "", "78:DB:2F:BF:3F:23": "",
                   "78:DB:2F:BF:3B:54": "", "78:DB:2F:BF:2C:E2": ""}
    position_buffer = {"1C:BA:8C:1D:30:22": "", "50:F1:4A:CB:FE:EE": "", "78:DB:2F:BF:3F:63": "", "78:DB:2F:BF:3F:23": "",
                       "78:DB:2F:BF:3B:54": "", "78:DB:2F:BF:2C:E2": ""}
    incoming_data_flag = {"1C:BA:8C:1D:30:22": False, "50:F1:4A:CB:FE:EE": False, "78:DB:2F:BF:3F:63": False,
                          "78:DB:2F:BF:3F:23": False, "78:DB:2F:BF:3B:54": False, "78:DB:2F:BF:2C:E2": False}
    relative_position_flag = {"1C:BA:8C:1D:30:22": False, "50:F1:4A:CB:FE:EE": False, "78:DB:2F:BF:3F:63": False,
                              "78:DB:2F:BF:3F:23": False, "78:DB:2F:BF:3B:54": False, "78:DB:2F:BF:2C:E2": False}
    # data global variables
    num_datasets = 60
    # {"78:DB:2F:BF:3F:23": {1: [100, 12.23, 14.45, 15.67]}, {2: [100, 14.56, -23.24, -16.78]}}
    beetle1_data_dict = {"1C:BA:8C:1D:30:22": {}}
    beetle2_data_dict = {"50:F1:4A:CB:FE:EE": {}}
    beetle3_data_dict = {"78:DB:2F:BF:3F:63": {}}
    beetle4_data_dict = {"78:DB:2F:BF:3F:23": {}}
    beetle5_data_dict = {"78:DB:2F:BF:3B:54": {}}
    beetle6_data_dict = {"78:DB:2F:BF:2C:E2": {}}
    beetle1_position_dict = {"1C:BA:8C:1D:30:22": {}}
    beetle2_position_dict = {"50:F1:4A:CB:FE:EE": {}}
    beetle3_position_dict = {"78:DB:2F:BF:3F:63": {}}
    beetle4_position_dict = {"78:DB:2F:BF:3F:23": {}}
    beetle5_position_dict = {"78:DB:2F:BF:3B:54": {}}
    beetle6_position_dict = {"78:DB:2F:BF:2C:E2": {}}
    datastring_dict = {"1C:BA:8C:1D:30:22": "", "50:F1:4A:CB:FE:EE": "", "78:DB:2F:BF:3F:63": "", "78:DB:2F:BF:3F:23": "",
                       "78:DB:2F:BF:3B:54": "", "78:DB:2F:BF:2C:E2": ""}
    packet_count_dict = {"1C:BA:8C:1D:30:22": 0, "50:F1:4A:CB:FE:EE": 0, "78:DB:2F:BF:3F:63": 0, "78:DB:2F:BF:3F:23": 0,
                         "78:DB:2F:BF:3B:54": 0, "78:DB:2F:BF:2C:E2": 0}
    dataset_count_dict = {"1C:BA:8C:1D:30:22": 0, "50:F1:4A:CB:FE:EE": 0, "78:DB:2F:BF:3F:63": 0, "78:DB:2F:BF:3F:23": 0,
                          "78:DB:2F:BF:3B:54": 0, "78:DB:2F:BF:2C:E2": 0}
    float_flag_dict = {"1C:BA:8C:1D:30:22": False, "50:F1:4A:CB:FE:EE": False, "78:DB:2F:BF:3F:63": False, "78:DB:2F:BF:3F:23": False,
                       "78:DB:2F:BF:3B:54": False, "78:DB:2F:BF:2C:E2": False}
    timestamp_flag_dict = {"1C:BA:8C:1D:30:22": False, "50:F1:4A:CB:FE:EE": False, "78:DB:2F:BF:3F:63": False, "78:DB:2F:BF:3F:23": False,
                           "78:DB:2F:BF:3B:54": False, "78:DB:2F:BF:2C:E2": False}
    comma_count_dict = {"1C:BA:8C:1D:30:22": 0, "50:F1:4A:CB:FE:EE": 0, "78:DB:2F:BF:3F:63": 0, "78:DB:2F:BF:3F:23": 0,
                        "78:DB:2F:BF:3B:54": 0, "78:DB:2F:BF:2C:E2": 0}
    checksum_dict = {"1C:BA:8C:1D:30:22": 0, "50:F1:4A:CB:FE:EE": 0, "78:DB:2F:BF:3F:63": 0, "78:DB:2F:BF:3F:23": 0,
                     "78:DB:2F:BF:3B:54": 0, "78:DB:2F:BF:2C:E2": 0}
    start_flag = {"1C:BA:8C:1D:30:22": False, "50:F1:4A:CB:FE:EE": False, "78:DB:2F:BF:3F:63": False, "78:DB:2F:BF:3F:23": False,
                  "78:DB:2F:BF:3B:54": False, "78:DB:2F:BF:2C:E2": False}
    end_flag = {"1C:BA:8C:1D:30:22": False, "50:F1:4A:CB:FE:EE": False, "78:DB:2F:BF:3F:63": False, "78:DB:2F:BF:3F:23": False,
                "78:DB:2F:BF:3B:54": False, "78:DB:2F:BF:2C:E2": False}
    # clock synchronization global variables
    dance_count = 0
    clocksync_flag_dict = {"1C:BA:8C:1D:30:22": False, "50:F1:4A:CB:FE:EE": False, "78:DB:2F:BF:3F:63": False, "78:DB:2F:BF:3F:23": False,
                           "78:DB:2F:BF:3B:54": False, "78:DB:2F:BF:2C:E2": False}
    timestamp_dict = {"1C:BA:8C:1D:30:22": [], "50:F1:4A:CB:FE:EE": [], "78:DB:2F:BF:3F:63": [], "78:DB:2F:BF:3F:23": [],
                      "78:DB:2F:BF:3B:54": [], "78:DB:2F:BF:2C:E2": []}
    clock_offset_dict = {"1C:BA:8C:1D:30:22": [], "50:F1:4A:CB:FE:EE": [], "78:DB:2F:BF:3F:63": [], "78:DB:2F:BF:3F:23": [],
                         "78:DB:2F:BF:3B:54": [], "78:DB:2F:BF:2C:E2": []}

    [global_delegate_obj.append(0) for idx in range(len(beetle_addresses))]
    [global_beetle.append(0) for idx in range(len(beetle_addresses))]

    """
    try:
        eval_client = eval_client.Client(
            "137.132.92.80", 4000, 6, "cg40024002group6")
    except Exception as e:
        print(e)
    """
    """
    try:
        board_client = dashBoardClient.Client(
            "192.168.43.248", 8080, 6, "cg40024002group6")
    except Exception as e:
        print(e)

    print("connected to both servers")
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=7) as connection_executor:
        connection_futures = {connection_executor.submit(
            establish_connection, address): address for address in beetle_addresses}
    connection_executor.shutdown(wait=True)
    while True:
        with concurrent.futures.ThreadPoolExecutor(max_workers=7) as data_executor:
            receive_data_futures = {data_executor.submit(
                getPositionData, beetle): beetle for beetle in global_beetle}
            for future in concurrent.futures.as_completed(receive_data_futures):
                pass
            data_executor.shutdown(wait=True)
        pool = multiprocessing.Pool()
        workers = [pool.apply_async(processData, args=(address, ))
                   for address in beetle_addresses]
        result = [worker.get() for worker in workers]
        for idx in range(0, len(result)):
            for address in result[idx][0].keys():
                if address == "1C:BA:8C:1D:30:22":
                    beetle1_position_dict[address] = result[idx][0][address]
                elif address == "50:F1:4A:CB:FE:EE":
                    beetle2_position_dict[address] = result[idx][0][address]
                elif address == "78:DB:2F:BF:3F:63":
                    beetle3_position_dict[address] = result[idx][0][address]
                elif address == "78:DB:2F:BF:3F:23":
                    beetle4_position_dict[address] = result[idx][0][address]
                elif address == "78:DB:2F:BF:3B:54":
                    beetle5_position_dict[address] = result[idx][0][address]
                elif address == "78:DB:2F:BF:2C:E2":
                    beetle6_position_dict[address] = result[idx][0][address]
        # clear buffer for next move
        for address in position_buffer.keys():
            position_buffer[address] = ""
        print(beetle1_position_dict)
        print(beetle2_position_dict)
        print(beetle3_position_dict)
        print(beetle4_position_dict)
        print(beetle5_position_dict)
        print(beetle6_position_dict)

        # synchronization delay
        """
        beetle1_time_ultra96 = calculate_ultra96_time(
            beetle1_data_dict, clock_offset_dict["1C:BA:8C:1D:30:22"][0])
        """
        """
        beetle2_time_ultra96 = calculate_ultra96_time(
            beetle2_data_dict, clock_offset_dict["50:F1:4A:CB:FE:EE"][0])
        """
        """
        beetle3_time_ultra96 = calculate_ultra96_time(
            beetle3_data_dict, clock_offset_dict["78:DB:2F:BF:3F:63"][0])
        """

        beetle4_time_ultra96 = calculate_ultra96_time(
            beetle4_data_dict, clock_offset_dict["78:DB:2F:BF:3F:23"][0])

        """
        beetle5_time_ultra96 = calculate_ultra96_time(
            beetle5_data_dict, clock_offset_dict["78:DB:2F:BF:3B:54"][0])
        """
        """
        beetle6_time_ultra96 = calculate_ultra96_time(
            beetle6_data_dict, clock_offset_dict["78:DB:2F:BF:2C:E2"][0])
        """
        """
        # max(beetle3_time_ultra96, ...) - min(beetle1_time_ultra96, ...)
        sync_delay = max(beetle5_time_ultra96, beetle6_time_ultra96) - \
            min(beetle5_time_ultra96, beetle6_time_ultra96)
        """
        # print("Beetle 1 ultra 96 time: ", beetle1_time_ultra96)
        # print("Beetle 2 ultra 96 time: ", beetle2_time_ultra96)
        # print("Beetle 3 ultra 96 time: ", beetle3_time_ultra96)
        # print("Beetle 4 ultra 96 time: ", beetle4_time_ultra96)
        # print("Beetle 5 ultra 96 time: ", beetle5_time_ultra96)
        # print("Beetle 6 ultra 96 time: ", beetle6_time_ultra96)
        print("Synchronization delay is: ", beetle4_time_ultra96)

        # machine learning
        """
        ml_result = get_prediction(beetle5_data_dict)
        """
        """
        workers = pool.apply_async(predict_dance.get_prediction, args=(beetle5_data_dict))
        ml_result = workers.get()
        """

        ml_result = "dumbbelldumbbell"
        # send data to eval server
        # send data to dashboard server
        """
        eval_client.send_data("1 2 3", ml_result, str(sync_delay))
        """
        """
        board_client.send_data_to_DB("ML1Dancer1234567", ml_result)
        """

        # clear the data dictionaries for next dance move
        beetle1_position_dict = {"1C:BA:8C:1D:30:22": {}}
        beetle2_position_dict = {"50:F1:4A:CB:FE:EE": {}}
        beetle3_position_dict = {"78:DB:2F:BF:3F:63": {}}
        beetle4_position_dict = {"78:DB:2F:BF:3F:23": {}}
        beetle5_position_dict = {"78:DB:2F:BF:3B:54": {}}
        beetle6_position_dict = {"78:DB:2F:BF:2C:E2": {}}
