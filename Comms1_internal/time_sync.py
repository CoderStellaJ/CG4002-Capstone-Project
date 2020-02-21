def calculate_clock_offset(beetle_timestamp_list):
    if(len(beetle_timestamp_list) == 5) :
        RTT = (beetle_timestamp_list[4] - beetle_timestamp_list[1]) - (beetle_timestamp_list[3] - beetle_timestamp_list[2])
        clock_offset = (beetle_timestamp_list[2] - beetle_timestamp_list[1]) - RTT/2
        return clock_offset
    else:
        print("error in beetle timestamp")

def calculate_ultra96_time(beetle_data_dict, clock_offset):
    time_ultra96 = 0
    for key in beetle_data_dict:
        data_list = beetle_data_dict[key]
        time_beetle = data_list[0]
        if(time_beetle != 0):
            time_ultra96 = time_beetle - clock_offset
            return time_ultra96




