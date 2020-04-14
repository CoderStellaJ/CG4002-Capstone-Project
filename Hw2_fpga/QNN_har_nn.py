import torch
import pandas
import torch.nn.functional as F
import numpy as np
import brevitas.nn as qnn
from brevitas.core.quant import QuantType

"""
Human Activity neural network implementation (quantization aware training)
"""

class QNN_HARnn(torch.nn.Module):
  def __init__(self):
    super(QNN_HARnn, self).__init__()
    self.linear1 = qnn.QuantLinear(560, 200, bias=True,
                                     weight_quant_type=QuantType.INT,
                                     weight_bit_width=8)
    self.relu1 = qnn.QuantReLU(quant_type=QuantType.INT, bit_width=8, max_val=6)
    self.linear2 = qnn.QuantLinear(200, 100, bias=True,
                                     weight_quant_type=QuantType.INT,
                                     weight_bit_width=8)
    self.relu2 = qnn.QuantReLU(quant_type=QuantType.INT, bit_width=8, max_val=6)
    self.linear3 = qnn.QuantLinear(100, 6, bias=True,
                                     weight_quant_type=QuantType.INT,
                                     weight_bit_width=8)
  def forward(self, x):
    x = self.relu1(self.linear1(x))
    x = self.relu2(self.linear2(x))
    x = F.log_softmax(self.linear3(x))
    return x

train_frame = pandas.read_csv('train.csv')
accelerometer_data = train_frame.iloc[1:, 1:561]
values = train_frame.iloc[1:, 562]

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
    test_accelerometer_data = test_frame.iloc[1:, 1:561]
    test_values = test_frame.iloc[1:, 562]
    correct_pred = 0;

    for x in range(len(test_values)):
        data = torch.tensor([test_accelerometer_data.iloc[x]])
        data.requires_grad = True;
        result_tensor = model(data)
        pred = np.argmax(result_tensor.data.numpy())
        if (labels[test_values.iloc[x]][0] == pred):
            correct_pred += 1;

    accuracy = 100. * correct_pred / len(test_values)
    print('Accuracy: {}'.format(accuracy))
    if (accuracy > prev_accuracy):
        torch.save(model.state_dict(), './QNN_HARNN_MODEL')

    return accuracy
#Hard-coded parameters
epochs = 50
learning_rate = 0.01
accuracy = 0;
# Construct our model by instantiating the class defined above.
model = QNN_HARnn()
loss_fn = torch.nn.CrossEntropyLoss()

optimizer = torch.optim.SGD(model.parameters(), lr = learning_rate,)
for epoch in range(epochs):
  # Forward pass: Compute predicted y by passing x to the model
  for x in range(len(values)):
    data = torch.tensor([accelerometer_data.iloc[x]])
    data.requires_grad = True;
    target = labels[values.iloc[x]]
    pred = model(data)
    loss = loss_fn(pred, target)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    if x % 2000 == 0 and x:
        print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(epoch, x, len(values), x / len(values) * 100., loss.data))

  accuracy = predict(model, accuracy)
