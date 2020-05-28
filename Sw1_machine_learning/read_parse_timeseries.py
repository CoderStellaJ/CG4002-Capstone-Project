import operator
import csv

MyCount = {"1": [], "2": [], "3": []}

int(max(MyCount, key=int))

length = 89
time_series = 5

while (length % time_series != 0):
    length -= 1

print(length)

window_size = 5


# GET DATA, LABEL ACCORDING TO DANCE
# EVERY 3 lines of position.txt for 1 label
# 3 beetles for 1 label
# each line of data is data for 1 beetle
def func(x):
    return int(x[0])

def parse_dance_data(filename, dance_labels):
    # collect beetle data
    data = []
    # every 3 lines evaluated, next dance label
    a = 1
    b = 0
    z = 0  # time series counter

    with open(filename, 'r') as inf:
        for line in inf:
            # evaluate 3 lines (beetles) for 1 label

            dic_file = eval(line)
            for k, v in dic_file.items():  # k = beetle address
                if v:  # dict is not empty
                    window_count = 0
                    ypr = []
                    for data_num, data_value in sorted(v.items(), key=func):
                        window_count += 1
                        for i in range(1, 7):
                            ypr.append(data_value[i])

                        if (window_count % window_size == 0):
                            dance_label = dance_labels[b]  # take current dance label
                            ypr.append(dance_label)
                            data.append(ypr)
                            ypr = []

            if a % 3 == 0:
                b += 1  # increment pointer

            a += 1
    return (data)


# TIMESERIES FOR MOVEMENT

window_size = 5


def func(x):
    return int(x[0])


def parse_move_data(filename, movement):
    # collect data
    data = []
    a = 1
    b = 0  # point to first movement
    z = 0  # time series counter

    with open(filename, 'r') as inf:
        for line in inf:

            dic_file = eval(line)
            for k, v in dic_file.items():  # addr = beetle address
                if v:  # not empty dict
                    window_count = 0
                    ypr = []

                    for data_num, data_value in sorted(v.items(), key=func):
                        window_count += 1
                        for i in range(1, 7):
                            ypr.append(data_value[i])

                        if (window_count % window_size == 0):
                            movement_label = movement[k][b]  # get label
                            ypr.append(movement_label)
                            data.append(ypr)
                            ypr = []

            if a % 3 == 0:
                b += 1
            a += 1

    return (data)


def parse_dataset_dance(data_filename, label_filename):
    dance_labels, movement_labels = parse_labels(label_filename)

    dance_file_data = parse_dance_data(data_filename, dance_labels)

    return (dance_file_data)


def parse_dataset_move(data_filename, label_filename):
    dance_labels, movement_labels = parse_labels(label_filename)

    movement = {}
    movement[beetle_1] = movement_labels['1']
    movement[beetle_2] = movement_labels['2']
    movement[beetle_3] = movement_labels['3']

    move_file_data = parse_move_data(data_filename, movement)

    return (move_file_data)

# Get headings
time_series = 5

headings = ['y_', 'p_', 'r_', 'accX_', 'accY_', 'accZ_']
header = []

for i in range(1, time_series + 1):
    for j in range(6):
        header.append(headings[j] + str(i))

header.append('Movement')

move_headings = header
print(move_headings)


#DANCE
final_move_data = []

final_move_data.append(move_headings)

move_data = parse_dataset_move('position.txt', 'labels.txt')

final_move_data.extend(move_data)

move_data = parse_dataset_move('position2.txt', 'labels2.txt')

final_move_data.extend(move_data)

move_data = parse_dataset_move('position3.txt', 'labels3.txt')

final_move_data.extend(move_data)

move_data = parse_dataset_move('position4.txt', 'labels4.txt')

final_move_data.extend(move_data)

print(final_move_data[:3])

#MOVEMENT
move_data = parse_dataset_move('position.txt', 'labels.txt')

final_move_data.extend(move_data)

move_data = parse_dataset_move('position2.txt', 'labels2.txt')

final_move_data.extend(move_data)

move_data = parse_dataset_move('position3.txt', 'labels3.txt')

final_move_data.extend(move_data)

move_data = parse_dataset_move('position4.txt', 'labels4.txt')

final_move_data.extend(move_data)




csv_filename = "move_data.csv"

with open(csv_filename, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(final_move_data)