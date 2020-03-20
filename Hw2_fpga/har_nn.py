import torch
import pandas
import torch.nn.functional as F
import numpy as np
from torch.autograd import Variable

"""
Human Activity neural network implementation (Non-quantization aware training)
"""

class HARnn(torch.nn.Module):
  def __init__(self):
    super(HARnn, self).__init__()
    self.linear1 = torch.nn.Linear(560, 800)
    self.linear2 = torch.nn.Linear(800, 400)
    self.linear3 = torch.nn.Linear(400, 200)
    self.linear4 = torch.nn.Linear(200, 100)
    self.linear5 = torch.nn.Linear(100, 50)
    self.linear6 = torch.nn.Linear(50, 6)

  def forward(self, x):
    x = F.relu(self.linear1(x))
    x = F.relu(self.linear2(x))
    x = F.relu(self.linear3(x))
    x = F.relu(self.linear4(x))
    x = F.relu(self.linear5(x))
    x = F.log_softmax(self.linear6(x))
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
        torch.save(model.state_dict(), './HARNN_MODEL')

    return accuracy
#Hard-coded parameters
epochs = 50
learning_rate = 0.01
accuracy = 0;
# Construct our model by instantiating the class defined above.
model = HARnn()
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
