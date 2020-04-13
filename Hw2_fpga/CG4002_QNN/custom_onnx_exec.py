import copy
import os
import subprocess

import numpy as np
import onnx.helper as helper
import onnxruntime as rt

import finn.core.execute_custom_node as ex_cu_node
from finn.core.modelwrapper import ModelWrapper
from finn.core.rtlsim_exec import rtlsim_exec
from finn.custom_op.registry import getCustomOp
from finn.custom_op.multithreshold import MultiThreshold

def fpga_exec(fpga, model, execution_context):
    inp = execution_context[model.graph.input[0].name]
    outp = fpga.fpga_single_run(inp)
    execution_context[model.graph.output[0].name] = outp

def execute_node(node, fpga, context, graph):
    """Executes a single node by using onnxruntime, with custom function or
    if dataflow partition by using remote execution or rtlsim.
    Input/output provided via context."""

    if node.op_type == "StreamingDataflowPartition":
        sdp_node = getCustomOp(node)
        model = ModelWrapper(sdp_node.get_nodeattr("model"))
        ret = execute_hw_accelerated_onnx(model, fpga, context, True)
        context.update(ret)
    else:
        if node.domain == "finn":
            ex_cu_node.execute_custom_node(node, context, graph)
        else:
            # onnxruntime unfortunately does not implement run_node as defined by ONNX,
            # it can only execute entire models -- so we create a model which solely
            # consists of our current node.
            node_inputs = list(filter(lambda x: x.name in node.input, graph.input))
            node_inputs += list(
                filter(lambda x: x.name in node.input, graph.value_info)
            )
            node_outputs = list(filter(lambda x: x.name in node.output, graph.output))
            node_outputs += list(
                filter(lambda x: x.name in node.output, graph.value_info)
            )
            node_graph = helper.make_graph(
                nodes=[node],
                name="single-node-exec",
                inputs=node_inputs,
                outputs=node_outputs,
            )
            node_model = helper.make_model(node_graph)
            input_dict = dict()
            for inp in node.input:
                input_dict[inp] = context[inp]

            sess = rt.InferenceSession(node_model.SerializeToString())
            output_list = sess.run(None, input_dict)

            for output_ind in range(len(node.output)):
                outp = node.output[output_ind]
                if output_list[output_ind].shape != context[outp].shape:
                    raise Exception(
                        """Output shapes disagree after node execution:
                        found %s vs expected %s"""
                        % (
                            str(output_list[output_ind].shape.shape),
                            str(context[outp].shape),
                        )
                    )
                context[outp] = output_list[output_ind]

def execute_hw_accelerated_onnx(model, fpga, input_dict, return_full_exec_context=False):
    """Executes given ONNX ModelWrapper with given named inputs.
    If return_full_exec_context is False, a dict of named outputs is returned
    as indicated by the model.graph.output.
    If return return_full_exec_context is True, the full set of tensors used by
    the execution (including inputs, weights, activations and final outputs)
    will be returned as a dict."""

    if not model.check_all_tensor_shapes_specified():
        raise Exception("Found unspecified tensor shapes, try infer_shapes")

    graph = model.graph
    # first, we need to make sure that every variable required by the graph has
    # some buffer associated with it. this includes graph inputs (which includes
    # the input data as well as the trained parameters) and the graph ValueInfo
    # (intermediate tensors between layers)
    # this is provided by the execution_context, which is a dict of np.ndarray
    execution_context = model.make_empty_exec_context()
    # fill in any inputs provided to this function
    for inp_name in input_dict.keys():
        if inp_name in execution_context:
            if execution_context[inp_name].shape == input_dict[inp_name].shape:
                execution_context[inp_name] = input_dict[inp_name]
            else:
                raise Exception(
                    "Shape mismatch for provided input %s: found %s expected %s "
                    % (
                        inp_name,
                        str(execution_context[inp_name].shape),
                        str(input_dict[inp_name].shape),
                    )
                )
        # else:
        # raise Exception("Provided input not found in graph context: %s" % inp_name)

    # check if model has an execution mode set
    # if None, execute model node by node using execute_node()
    # if set to "remote_pynq" execute model on PYNQ board
    # if set to "rtlsim" execute model using pyverilator
    model_exec_mode = model.get_metadata_prop("exec_mode")
    if (model_exec_mode is None) or (model_exec_mode == ""):
        # execute the model node by node
        # we can simply walk down the list since the ONNX spec guarantees that it is
        # topologically sorted
        for node in graph.node:
            execute_node(node, fpga, execution_context, graph)
    elif model_exec_mode == "remote_pynq":
        # use custom remote exec metadata built into model to execute on a 'remote' PYNQ
        fpga_exec(fpga, model, execution_context)
    elif model_exec_mode == "rtlsim":
        # use stitched IP for rtlsim
        raise Exception("""Impossible exec value rtlsim""")
        rtlsim_exec(model, execution_context)
    else:
        raise Exception(
            """Metadata property "exec_mode" is set to an unknown value.
        Can be left unset or has to be set to "remote_pynq" for remote execution
        on PYNQ board or "rtlsim" for execution using pyverilator!"""
        )

    if return_full_exec_context:
        return execution_context
    else:
        # provide outputs as dict
        output_dict = dict()
        for out_tensor in graph.output:
            out_name = out_tensor.name
            output_dict[out_name] = execution_context[out_name]
        return output_dict
