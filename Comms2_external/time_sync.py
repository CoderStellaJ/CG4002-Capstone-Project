def calculate_clock_offset(beetle_timestamp_list):
    if(len(beetle_timestamp_list) == 4) :
        RTT = (beetle_timestamp_list[3] - beetle_timestamp_list[0]) \
              - (beetle_timestamp_list[2] - beetle_timestamp_list[1])
        clock_offset = (beetle_timestamp_list[1] - beetle_timestamp_list[0]) - RTT/2
        return clock_offset
    else:
        print("error in beetle timestamp")
        return None


def most_frequent(List):
    if len(List) == 0:
        print("Dance data is empty")
        return None
    else: 
        return max(set(List), key = List.count) 


def calculate_ultra96_time(beetle_data_dict, clock_offset):
    time_ultra96 = 0
    value_list = []  # keeps the first 5 values
    count = 0
    for address in beetle_data_dict:
        for key in beetle_data_dict[address]:
            value_list.append(beetle_data_dict[address][key])
            count += 1
            if count >= 5:
                break
    
    time_beetle = most_frequent(value_list)
    if time_beetle is None:
        return None
    else:
        time_ultra96 = time_beetle - clock_offset
        return time_ultra96


def calculate_sync_delay(beetle1_time_ultra96, beetle2_time_ultra96, beetle3_time_ultra96):
    sync_delay = 850
    if beetle1_time_ultra96 is not None and beetle2_time_ultra96 is not None and beetle3_time_ultra96 is not None:
        sync_delay = max(beetle1_time_ultra96, beetle2_time_ultra96, beetle3_time_ultra96) \
                     - min(beetle1_time_ultra96, beetle2_time_ultra96, beetle3_time_ultra96)
    elif beetle1_time_ultra96 is None:
        sync_delay = max(beetle2_time_ultra96, beetle3_time_ultra96) - min(beetle2_time_ultra96, beetle3_time_ultra96)
    elif beetle2_time_ultra96 is None:
        sync_delay = max(beetle1_time_ultra96, beetle3_time_ultra96) - min(beetle1_time_ultra96, beetle3_time_ultra96)
    elif beetle3_time_ultra96 is None:
        sync_delay = max(beetle1_time_ultra96, beetle2_time_ultra96) - min(beetle1_time_ultra96, beetle2_time_ultra96)
    return sync_delay





