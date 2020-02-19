def calculate_clock_offset(beetle_timestamp_list):
    if(len(beetle_timestamp_list) == 4) :
        RTT = (beetle_timestamp_list[3] - beetle_timestamp_list[0]) - (beetle_timestamp_list[2] - beetle_timestamp_list[1])
        clock_offset = (beetle_timestamp_list[1] - beetle_timestamp_list[0]) - RTT/2
        return clock_offset
    else:
        print("error in beetle timestamp")


