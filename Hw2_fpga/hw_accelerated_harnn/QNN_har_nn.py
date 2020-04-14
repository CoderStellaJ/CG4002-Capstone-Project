import torch
import pandas
import torch.nn.functional as F
import numpy as np
import brevitas.nn as qnn
from brevitas.core.quant import QuantType
from brevitas.core.stats import StatsOp
from brevitas.core.restrict_val import RestrictValueType
from brevitas.core.bit_width import BitWidthImplType
from brevitas.core.scaling import ScalingImplType
import brevitas.onnx as bo

"""
Human Activity neural network implementation (quantization aware training)
"""

DROPOUT = 0.2

class QNN_HARnn(torch.nn.Module):
  def __init__(self):
    super(QNN_HARnn, self).__init__()
    self.hardtanh0 = qnn.QuantHardTanh(quant_type=QuantType.INT, bit_width=2, narrow_range=True, bit_width_impl_type=BitWidthImplType.CONST, min_val = -1.0, max_val = 1.0, restrict_scaling_type=RestrictValueType.LOG_FP, scaling_per_channel=False, scaling_impl_type=ScalingImplType.PARAMETER)
    self.dropout0 = torch.nn.Dropout(p = DROPOUT)
    self.linear1 = qnn.QuantLinear(256, 64, bias=False, weight_quant_type=QuantType.BINARY, weight_bit_width=1, weight_scaling_stats_op = StatsOp.AVE, weight_scaling_stats_sigma=0.001, weight_scaling_per_output_channel = True, weight_narrow_range = True, weight_bit_width_impl_type=BitWidthImplType.CONST)
    self.hardtanh1 = qnn.QuantHardTanh(quant_type=QuantType.INT, bit_width=2, narrow_range=True, bit_width_impl_type=BitWidthImplType.CONST, min_val = -1.0, max_val = 1.0, restrict_scaling_type=RestrictValueType.LOG_FP, scaling_per_channel=False, scaling_impl_type=ScalingImplType.PARAMETER)
    self.dropout1 = torch.nn.Dropout(p = DROPOUT)
    self.linear2 = qnn.QuantLinear(64, 64, bias=False, weight_quant_type=QuantType.BINARY, weight_bit_width=1, weight_scaling_stats_op = StatsOp.AVE, weight_scaling_stats_sigma=0.001, weight_scaling_per_output_channel = True, weight_narrow_range = True, weight_bit_width_impl_type=BitWidthImplType.CONST)
    self.hardtanh2 = qnn.QuantHardTanh(quant_type=QuantType.INT, bit_width=2, narrow_range=True, bit_width_impl_type=BitWidthImplType.CONST, min_val = -1.0, max_val = 1.0, restrict_scaling_type=RestrictValueType.LOG_FP, scaling_per_channel=False, scaling_impl_type=ScalingImplType.PARAMETER)
    self.dropout2 = torch.nn.Dropout(p = DROPOUT)
    self.linear3 = qnn.QuantLinear(64, 6, bias=False, weight_quant_type=QuantType.BINARY, weight_bit_width=1, weight_scaling_stats_op = StatsOp.AVE, weight_scaling_stats_sigma=0.001, weight_scaling_per_output_channel = False, weight_narrow_range = True, weight_bit_width_impl_type=BitWidthImplType.CONST)


  def forward(self, x):
    x = self.hardtanh0(x)
    x = self.dropout0(x)
    x = self.linear1(x)
    x = self.hardtanh1(x)
    x = self.dropout1(x)
    x = self.linear2(x)
    x = self.hardtanh2(x)
    x = self.dropout2(x)
    x = self.linear3(x)
    return x

train_frame = pandas.read_csv('train.csv')
train_data_array = train_frame.values

labels = {
  "STANDING": torch.tensor([0]),
  "SITTING": torch.tensor([1]),
  "LAYING": torch.tensor([2]),
  "WALKING": torch.tensor([3]),
  "WALKING_DOWNSTAIRS": torch.tensor([4]),
  "WALKING_UPSTAIRS": torch.tensor([5])
}

def predict(model, prev_accuracy):
    test_frame = pandas.read_csv('test.csv')
    test_data_array = test_frame.values
    correct_pred = 0;

    for x in range(len(test_data_array)):
        data = np.asarray(test_data_array[x, 0:256], dtype = np.float32)
        data = torch.tensor([data])
        data.requires_grad = True;
        result_tensor = model(data)
        pred = np.argmax(result_tensor.data.numpy())
        if (labels[test_data_array[x, -1]] == pred):
            correct_pred += 1;

    accuracy = 100. * correct_pred / len(test_data_array)
    print('Accuracy: {}'.format(accuracy))
    if (accuracy > prev_accuracy):
        bo.export_finn_onnx(model, (1, 256), './qnn_harnn_model.onnx')

    return accuracy
#Hard-coded parameters
epochs = 500
learning_rate = 0.075
accuracy = 0;
default_momentum = 0.5
# Construct our model by instantiating the class defined above.
model = QNN_HARnn()
loss_fn = torch.nn.CrossEntropyLoss()

optimizer = torch.optim.SGD(model.parameters(), lr = learning_rate)
for epoch in range(epochs):
  # Forward pass: Compute predicted y by passing x to the model
  for x in range(len(train_data_array)):
    data = np.asarray(train_data_array[x, 0:256], dtype = np.float32)
    data = torch.tensor([data])
    data.requires_grad = True;
    target = labels[train_data_array[x, -1]]
    pred = model(data)
    loss = loss_fn(pred, target)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    if x % 1000 == 0 and x:
        print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(epoch, x, len(train_data_array), x / len(train_data_array) * 100., loss.data))

  accuracy = predict(model, accuracy)
