# -*- coding: utf-8 -*-
"""XLNET.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/186Gf1E7kldt8hn_es20fKr4SlGaXv5_b
"""

#We import all the dependencies
!pip install transformers # For Colab 
!pip install pytorch-transformers
!pip install torchvision
import torch
import pandas as pd
from pytorch_transformers import XLNetTokenizer
!pip install sentencepiece
from sklearn.model_selection import train_test_split
from transformers import AdamW
import matplotlib.pyplot as plt
from keras.preprocessing.sequence import pad_sequences
import torch
from torch.utils.data import TensorDataset,DataLoader,RandomSampler,SequentialSampler

#import data
from google.colab import drive
drive.mount('/content/drive')
dataframe = pd.read_csv('/content/drive/MyDrive/cleaned_data.csv', index_col = 0)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

dataframe.head

dataframe = dataframe[['cleaned_title','cleaned_content', 'label']]
print(dataframe.head)

dataframe["cleaned_content"] = dataframe["cleaned_title"] + dataframe["cleaned_content"]
dataframe.head
dataframe = dataframe[['cleaned_content', 'label']]

dataframe.columns = ['sentence','value']
dataframe.head

#XLNet need [SEP] [CLS] tags at the end of each sentence
#We add them by using following code
sentences  = []
for sentence in dataframe['sentence']:
  sentence = sentence+"[SEP] [CLS]"
  sentences.append(sentence)

sentences[0] ##To check if tags are added or not

#XLNet tokenizer is used to convert our text into tokens that correspond to XLNet’s vocabulary.
tokenizer  = XLNetTokenizer.from_pretrained('xlnet-base-cased',do_lower_case=True)
tokenized_text = [tokenizer.tokenize(sent) for sent in sentences]

tokenized_text[0]

#Use the XLNet tokenizer to convert the tokens to their index numbers in the XLNet vocabulary
ids = [tokenizer.convert_tokens_to_ids(x) for x in tokenized_text]

print(ids[0])
labels = dataframe['value'].values
print(labels[0])

#maximum length of our sentences so that we can pad the rest
MAX_LEN = 128

#We pad our sentences
input_ids2 = pad_sequences(ids,maxlen=MAX_LEN,dtype="long",truncating="post",padding="post")

#we split our data
xtrain,xtest,ytrain,ytest = train_test_split(input_ids2,labels,test_size=0.101)

#we make tensors
Xtrain = torch.tensor(xtrain)
Ytrain = torch.tensor(ytrain)
Xtest = torch.tensor(xtest)
Ytest = torch.tensor(ytest)

batch_size = 16

train_data = TensorDataset(Xtrain,Ytrain)
test_data = TensorDataset(Xtest,Ytest)
loader = DataLoader(train_data,batch_size=batch_size)
test_loader = DataLoader(test_data,batch_size=batch_size)

#we use xlnet model from transformers library
from transformers import XLNetForSequenceClassification

model = XLNetForSequenceClassification.from_pretrained("xlnet-base-cased",num_labels=2)
model.cuda()

#We use AdamW optimizer which is imported earlier
optimizer = AdamW(model.parameters(),lr=2e-5)# We pass model parameters

#For loss function we use Cross Entropy Loss
import torch.nn as nn
criterion = nn.CrossEntropyLoss()

#define accuracy, precision, recall and fscore
import numpy as np
def flat_accuracy(preds,labels):  # A function to predict Accuracy
  correct=0
  for i in range(0,len(labels)):
    if(preds[i]==labels[i]):
      correct+=1
  return (correct/len(labels))*100

from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import confusion_matrix

# Function to calculate the accuracy of our predictions vs labels
def flat_score(preds, labels):
    #pred_flat = np.argmax(preds, axis=0)
    #labels_flat = labels.flatten()
    score = precision_recall_fscore_support(labels, preds, average = None)
    return score[0][1], score[1][1], score[2][1]

"""### Here our training Begins"""

#training model
no_train = 0
epochs = 3
for epoch in range(epochs):
  model.train()
  loss1 = []
  steps = 0
  train_loss = []
  l = []
  for inputs,labels1 in loader :
    inputs.to(device)
    labels1.to(device)
    optimizer.zero_grad()
    outputs = model(inputs.to(device))
    loss = criterion(outputs[0],labels1.to(device)).to(device)
    logits = outputs[0]
    [train_loss.append(p.item()) for p in torch.argmax(outputs[0],axis=1).flatten() ]#our predicted 
    [l.append(z.item()) for z in labels1]# real labels
    loss.backward()
    optimizer.step()
    loss1.append(loss.item())
    no_train += inputs.size(0)
    steps += 1
  print("Current Loss is : {} and Accuracy is : {}".format(loss.item(),flat_accuracy(train_loss,l)))
  print("Current Precision, Recall and Fscore are : {}".format(flat_score(train_loss,l)))

#testing our model for test data
model.eval()
acc = []
lab = []
t = 0
for inp,lab1 in test_loader:
  inp.to(device)
  lab1.to(device)
  t+=lab1.size(0)
  outp1 = model(inp.to(device))
  [acc.append(p1.item()) for p1 in torch.argmax(outp1[0],axis=1).flatten() ]
  [lab.append(z1.item()) for z1 in lab1]

print("Accuracy is {}".format(flat_accuracy(acc,lab)))

print("Precision, Recall and Fscore are{}".format(flat_score(acc,lab)))