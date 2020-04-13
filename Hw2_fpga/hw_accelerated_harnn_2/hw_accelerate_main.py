from finn.custom_op.registry import getCustomOp
from finn.core.modelwrapper import ModelWrapper
from custom_onnx_exec import  execute_hw_accelerated_onnx
import numpy as np
import pandas
import time

from fpga import FPGA

BASE_DIR = '/home/xilinx/jupyter_notebooks/hw2_fpga_finn/'

TEST_CSV_DIR = BASE_DIR + 'test.csv'
BITFILE_PATH = BASE_DIR + "resizer.bit"
PARENT_ONNX_MODEL_DIR = BASE_DIR + 'qnn_harnn_model_dataflow_parent.onnx'
REMOTE_EXEC_MODEL_DIR = BASE_DIR + 'qnn_harnn_model_pynq_deploy.onnx'
PARENT_REMOTE_BITFILE_EXEC_MODEL_DIR = BASE_DIR + 'qnn_harnn_model_dataflow_parent_with_remote_bitfile_exec.onnx'

labels = {
  "STANDING": 0,
  "SITTING": 1,
  "LAYING": 2,
  "WALKING": 3,
  "WALKING_DOWNSTAIRS": 4,
  "WALKING_UPSTAIRS": 5
}

def fpga_setup(bitfile_path):
    #bitfile and hwh file have to be in the same directory
    start = time.time()
    fpga = FPGA(bitfile_path)
    print ("Bitfile Loading Time: " + str(time.time() - start) + "s")
    return fpga

def hw_accelerate_data_setup():
    start = time.time()
    test_frame = pandas.read_csv(TEST_CSV_DIR)
    test_data_array = test_frame.values
    print ("CSV Loading Time: " + str(time.time() - start) + "s")
    return test_data_array

def hw_accelerate_parent_model_setup(parent_onnx_model_dir, remote_exec_model_dir):
    parent_model = ModelWrapper(parent_onnx_model_dir)
    sdp_node = parent_model.graph.node[1]#Need to look into parent model to customize the value
    getCustomOp(sdp_node).set_nodeattr("model", REMOTE_EXEC_MODEL_DIR)
    parent_model.save(BASE_DIR+"/qnn_harnn_model_dataflow_parent_with_remote_bitfile_exec.onnx")
    return parent_model

def hw_accelerate_parent_remote_bitfile_setup(parent_model_remote_bitfile_dir):
    #Requires pynq deploy model to be in the same directory
    parent_remote_bitfile_model = ModelWrapper(parent_model_remote_bitfile_dir)
    return parent_remote_bitfile_model

def hw_accelerate_parent_model_eval(parent_model, fpga, input_np_arr):
    iname = parent_model.graph.input[0].name
    oname = parent_model.graph.output[0].name
    ishape = parent_model.get_tensor_shape(iname)
    input_dict = {iname: input_np_arr.reshape(ishape)}

    ret = execute_hw_accelerated_onnx(parent_model, fpga, input_dict, True)
    return ret[oname].flatten()

if __name__ == "__main__":
    correct_pred = 0;
    test_data_array = hw_accelerate_data_setup()
    parent_remote_bitfile_model = hw_accelerate_parent_remote_bitfile_setup(PARENT_REMOTE_BITFILE_EXEC_MODEL_DIR)
    fpga = fpga_setup(BITFILE_PATH)
    start = time.time()
    for i in range(len(test_data_array)):
        x = np.asarray(test_data_array[i, 0:256], dtype=np.float32)
        output = hw_accelerate_parent_model_eval(parent_remote_bitfile_model, fpga, x)
        if labels[test_data_array[i][-1]] == np.argmax(output):
            correct_pred += 1;

    print ("Process time: " + str(time.time() - start) + "s")
    print('Accuracy: {}'.format(100. * correct_pred / len(test_data_array)))
