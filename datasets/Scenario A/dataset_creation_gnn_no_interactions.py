# -*- coding: utf-8 -*-
"""dataset_creation_GNN_no_interactions.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Bc-8dpUMMiSBpzUp3zyEee4at4mvPZtw
"""

import networkx as nx
import networkx.utils as nu
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from networkx.algorithms.assortativity import average_degree_connectivity
import pickle
import torch
!pip install torch_geometric
import torch_geometric.data as pyg_data
import torch_geometric.utils
import ast
import torch
import torch.nn.functional as F
import random
from torch.nn import Linear

from torch_geometric.datasets import TUDataset
from torch_geometric.loader import DataLoader
from torch_geometric.nn import DenseGraphConv, DMoNPooling, GCNConv
from torch_geometric.utils import to_dense_adj, to_dense_batch


from google.colab import drive
drive.mount('/content/drive')
import os
os.chdir('/content/drive/MyDrive/Colab Notebooks/GitHub')
from ppi_network import print_graph_info, plot_graph

#load training and validation madeup graphs
with open('/content/drive/MyDrive/PROJECT/dataset_NCBI_graph_madeup_pheno.pickle', 'rb') as handle:
    dataset_dict = pickle.load(handle)

dataset_list = []

for j in dataset_dict:
  dataset_list_flag = []
  for k in j:
    data_flag = []
    for i in k:
      node_names = list(i['Graph'].nodes)
      node_dict = {node_names[i]: i for i in range(len(node_names))}
      node_features = [i['Graph'].nodes[n]['features'] for n in node_names]
      x = torch.tensor(node_features, dtype=torch.float)
      edge_index = []
      for e in i['Graph'].edges:
          u, v = e[0], e[1]
          u_idx, v_idx = node_dict[u], node_dict[v]
          edge_index.append([u_idx, v_idx])
          edge_index.append([v_idx, u_idx])
      edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()
      y = torch.tensor(i['y'], dtype = torch.float)
      AGE = torch.tensor(i['AGE'], dtype = torch.float)
      PTGENDER = torch.tensor(i['PTGENDER'], dtype = torch.float)
      data = pyg_data.Data(x=x, edge_index=edge_index, y=y, AGE = AGE, PTGENDER = PTGENDER)
      data_flag.append(data)
    dataset_list_flag.append(data_flag)
  dataset_list.append(dataset_list_flag)

print(dataset_list[2][3][0].num_nodes)
print(dataset_list[2][3][0].num_edges)
len(dataset_list[2])

graph = nx.Graph()
graph.add_nodes_from(range(dataset_list[2][0][0].num_nodes))
graph.add_edges_from(dataset_list[2][0][0].edge_index.t().tolist())
plot_graph(graph)

print_graph_info(graph)

thresholds = [0, 0.5, 0.75]
for i in range(len(dataset_list)):
  with open('/content/drive/MyDrive/PROJECT/dataset_GNN_' + str(thresholds[i]) + '_madeup_pheno.pickle', 'wb') as handle:
      pickle.dump(dataset_list[i], handle, protocol=pickle.HIGHEST_PROTOCOL)