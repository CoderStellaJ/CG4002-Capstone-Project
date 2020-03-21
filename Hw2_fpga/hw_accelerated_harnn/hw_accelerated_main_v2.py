from finn.custom_op.registry import getCustomOp
from finn.core.modelwrapper import ModelWrapper
from custom_onnx_exec import  execute_hw_accelerated_onnx
import numpy as np
import pandas
import time

from fpga import FPGA
from fpga_v2 import FPGA_V2
BASE_DIR = '/home/xilinx/jupyter_notebooks/hw2_fpga_finn/'

TEST_CSV_DIR = BASE_DIR + 'test.csv'
BITFILE_PATH = BASE_DIR + "resizer.bit"

labels = {
  "STANDING": 0,
  "SITTING": 1,
  "LAYING": 2,
  "WALKING": 3,
  "WALKING_DOWNSTAIRS": 4,
  "WALKING_UPSTAIRS": 5
}

def fpga_v2_setup(bitfile_path):
    #bitfile and hwh file have to be in the same directory
    start = time.time()
    fpga = FPGA_V2(bitfile_path)
    print ("Bitfile Loading Time: " + str(time.time() - start) + "s")
    return fpga

def hw_accelerate_data_setup():
    start = time.time()
    test_frame = pandas.read_csv(TEST_CSV_DIR)
    test_data_array = test_frame.values
    print ("CSV Loading Time: " + str(time.time() - start) + "s")
    return test_data_array

if __name__ == "__main__":
    correct_pred = 0;
    test_data_array = hw_accelerate_data_setup()
    fpga = fpga_v2_setup(BITFILE_PATH)
    start = time.time()
    for i in range(len(test_data_array)):
        x = np.asarray(test_data_array[i, 0:256], dtype=np.float32)
        output = fpga.fpga_single_run(x);
        if labels[test_data_array[i][-1]] == np.argmax(output):
            correct_pred += 1;

    print("Process time: " + str(time.time() - start) + "s")
    print('Accuracy: {}'.format(100. * correct_pred / len(test_data_array)))
