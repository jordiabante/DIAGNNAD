# -*- coding: utf-8 -*-
"""Random_Grid_search_0.75.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1n_Pv3mqyHIdbHBWaxVIHN35T-FMpseio
"""

import os.path as osp
from math import ceil
import pickle
from sklearn.metrics import balanced_accuracy_score
from sklearn.manifold import TSNE

import torch
import torch.nn.functional as F
from torch.nn import Linear

from torch_geometric.datasets import TUDataset
from torch_geometric.loader import DataLoader
from torch_geometric.nn import DenseGraphConv, DMoNPooling, GCNConv, GATv2Conv, TopKPooling, global_mean_pool
import torch.nn as nn
from torch_geometric.utils import to_dense_adj, to_dense_batch
import matplotlib.pyplot as plt
import os
import numpy as np
import math
import json
from torch.optim.lr_scheduler import OneCycleLR
import torch.nn.functional as F
from sklearn.model_selection import ParameterGrid
import time
from torch_geometric.explain import Explainer, GNNExplainer
import random
import sys



sys.path.append('/biofisica/home/creatio_student/project_gnn_ad/file_articolo/')
from metrics import metrics
from gnn_definitions import train, validation, test, GCNNet
os.chdir('/biofisica/home/creatio_student/project_gnn_ad/models/Random_grid_0.75')

with open('/biofisica/home/creatio_student/project_gnn_ad/file_articolo/training_0.75_GNN_PET.pickle', 'rb') as handle:
    training_list = pickle.load(handle)

with open('/biofisica/home/creatio_student/project_gnn_ad/file_articolo/validation_0.75_GNN_PET.pickle', 'rb') as handle:
    validation_list = pickle.load(handle)

# Set the number of epochs for the grid search
num_epoch_grid = 2000
# set the batch size
batch_size = 16

# Define a list of values to search for each hyperparameter
start_time = time.time()
param_grid = {
    'num_features': [15],
    'hidden_channels': [8, 16, 32],
    'num_classes': [2],
    'out_channels': [1],
    'num_layer': [1, 2, 3], # Test different numbers of ConvGNN layers
}
max_balanced_step = []
# Generate all possible combinations of hyperparameters
param_list = list(ParameterGrid(param_grid))
j = 0
n = random.randint(0, 9)

edge_index = training_list[0][0].edge_index
num_nodes = training_list[0][0].num_nodes

src_nodes = edge_index[0]
dst_nodes = edge_index[1]

edge_list = list(zip(src_nodes.tolist(), dst_nodes.tolist()))
random.shuffle(edge_list)

num_edges = len(edge_list)

new_src_nodes = []
new_dst_nodes = []
new_edge_index = []

for k in range(int(num_edges/2)):

    new_src = random.randint(0, num_nodes - 1)
    new_dst = random.randint(0, num_nodes - 1)

    new_edge_index.append([new_src,new_dst])
    new_edge_index.append([new_dst,new_src])

new_edge_index = torch.tensor(new_edge_index, dtype=torch.long).t().contiguous()

adj_matrix = torch.sparse_coo_tensor(new_edge_index, torch.ones(num_edges), size=(num_nodes, num_nodes))
adj_matrix_dense = adj_matrix.to_dense()
adj_matrix_dense[adj_matrix_dense != 0] = 1

plt.imshow(adj_matrix_dense, cmap='hot', interpolation='nearest')
plt.colorbar()
plt.show()

for k in training_list[n]:
  k.edge_index = new_edge_index
for k in validation_list[n]:
  k.edge_index = new_edge_index

# Create a DataLoader object for the validation set with batch size 16 and shuffle the data
val_loader = DataLoader(validation_list[n], batch_size, shuffle=True)

# Create a DataLoader object for the training set with batch size 16 and shuffle the data
train_loader = DataLoader(training_list[n], batch_size, shuffle=True)
# Loop through each combination of hyperparameters
for params in param_list:
        print(str(j+1) + ' parameters set')
        # Initialize the model with the current set of hyperparameters
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = GCNNet(**params).to(device)


        # Define your optimizer (e.g., Adam optimizer with a specific learning rate)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        total_iterations = math.ceil(len(training_list[n]) / batch_size)*num_epoch_grid
        scheduler = OneCycleLR(optimizer, max_lr=0.01, total_steps=total_iterations)

        # Define your loss function (e.g., binary cross-entropy loss for binary classification)
        loss_function = torch.nn.BCEWithLogitsLoss()
        max_balanced = 0
        for epoch in range(1, num_epoch_grid+1):

                # Train the model
                train_loss = train(train_loader, model, device, optimizer, scheduler)

                # Calculate the training and validation loss and balanced accuracy
                train_loss_2, balanced_accuracy_train = validation(train_loader, model, device)
                val_loss,  balanced_accuracy = validation(val_loader, model ,device)

                # Print the current epoch's metrics
                print(f'Epoch: {epoch:03d}, Train Loss: {train_loss:.3f}, '
                      f'Train Bal Acc: {balanced_accuracy_train:.3f}, Val Loss: {val_loss:.3f}, '
                      f'Val Bal Acc: {balanced_accuracy:.3f}')



                # If the current epoch's balanced accuracy is higher than the previous highest, save the current model checkpoint
                if balanced_accuracy > max_balanced:
                    max_balanced = balanced_accuracy
                    print('new max with balanced accuracy = ' + str(max_balanced))
        j += 1
        max_balanced_step.append(max_balanced)

# Record and compare the model performance (e.g., validation accuracy) for each set of hyperparameters
# and select the best set of hyperparameters based on the performance metric of interest.
indice_massimo = max_balanced_step.index(max(max_balanced_step))
winner_params = param_list[indice_massimo]
print('the winner parameters are: ')
print(winner_params)

file_1 = open('./winner_params.json','w')
json.dump(winner_params,file_1)
file_1.close()