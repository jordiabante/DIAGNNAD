# -*- coding: utf-8 -*-
"""Graph_creation_real_data.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1FablhUNzGTgmQ9e7hBDnjfhc9DtCpGNn
"""

from google.colab import drive
drive.mount('/content/drive')

### The required libraries and packages ###
import networkx as nx
import networkx.utils as nu
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from networkx.algorithms.assortativity import average_degree_connectivity
import pickle
import os
os.chdir('/content/drive/MyDrive/Colab Notebooks/GitHub')
from labelling import label_ADNI
from ppi_network import print_graph_info, plot_graph, PPI_network_creation_STRING
import json

# Percorso del file GZIP
file_path = '/content/drive/MyDrive/PROJECT/chr_19_no_NaN.csv.gz'

df = pd.read_csv(file_path, sep='\t', dtype=str)
df.set_index('Unnamed: 0', inplace=True)
df = df.T.astype(float)
df

# Percorso del file GZIP
file_path = '/content/drive/MyDrive/PROJECT/lookup_snpid_gene.csv.gz'

gene_snp = pd.read_csv(file_path, sep='\t', dtype=str)
gene_snp[gene_snp['gene_name'] == 'None'] = np.nan
gene_snp = gene_snp.set_index('snpid')
gene_snp = gene_snp.drop('Unnamed: 0', axis = 1)
gene_snp = gene_snp.dropna()
gene_snp

usefull_snps = df.index.tolist()[:-3]
gene_snp = gene_snp.loc[usefull_snps]
gene_snp

# lista degli indici delle colonne
id_list = df.columns
thresholds = [0, 0.5, 0.75]
D_list = []
# ciclo for per applicare la funzione PPI_network_creation ad ogni riga
column_gene = gene_snp['gene_name']
for i in thresholds:
    D_flag = []
    for idx in id_list:
          column = df[idx]
          patient_df = column.to_frame()
          D = PPI_network_creation_STRING(column_gene, patient_df, i)
          D['y'] = df[idx]['y']
          D['AGE'] = df[idx]['AGE']
          D['PTGENDER'] = df[idx]['PTGENDER']
          D_flag.append(D)
    D_list.append(D_flag)

print_graph_info(D_list[0][0]['Graph'])

print_graph_info(D_list[1][0]['Graph'])

print_graph_info(D_list[2][0]['Graph'])

plot_graph(D_list[0][0]['Graph'])

# cod to see wich genes were added dyrectly from string
node_list = [D_list[0][0]['Graph'].nodes, D_list[1][0]['Graph'].nodes, D_list[2][0]['Graph'].nodes]
list_of_genes = set(gene_snp['gene_name'].tolist())
elements_added_string = [list(node_list[0] - list_of_genes), list(node_list[1] - list_of_genes), list(node_list[2] - list_of_genes)]
elements_genes_not_nodes = [list(list_of_genes - node_list[0]), list(list_of_genes - node_list[1]), list(list_of_genes - node_list[2])]

k = 0
for i in D_list:
  for j in i:
    j['Graph'].remove_nodes_from(elements_added_string[k])
  k = k+1

print_graph_info(D_list[2][0]['Graph'])
#threshold = 0: edges = 1143
#threshold = 0.25: edges = 1143
#threshold = 0.50: edges = 798
#threshold = 0.75: edges = 302

nodes_to_add = []
for i in elements_genes_not_nodes:
    nodes_to_add_flag = [stringa for stringa in i if not stringa.startswith(("LOC", "MIR"))]
    nodes_to_add.append(nodes_to_add_flag)

genes_to_remove = ['HULC', 'CDKN2B-AS1', 'narK', 'cotD', 'clpP2', 'yihA', 'ppnN', 'rpsD', 'mtrA', 'ompR', 'pvdR', 'UCA1', 'prgK',  'gpmI', 'panM', 'fliW', 'argG', 'sigV', 'PCAT19', 'sctF', 'mgtR']
nodes_to_add = [(set(nodes_to_add[0]) - set(genes_to_remove)), (set(nodes_to_add[1]) - set(genes_to_remove)), (set(nodes_to_add[2]) - set(genes_to_remove))]
most_common_element = gene_snp['gene_name'].value_counts().idxmax()
lung_features = gene_snp['gene_name'].value_counts()[most_common_element]

# add all of theese nodes to the graphs:
n = 0
for i in D_list:
  for k in i:
    values = df[k['sample']]
    for j in nodes_to_add[n]:
      #extract the list of genes associated to the j gene
      snps_gene = gene_snp[gene_snp['gene_name']==j].index.tolist()
      features = values.loc[snps_gene].tolist()
      num_features = len(features)
      if num_features < lung_features:
          features += [0.0] * (lung_features - num_features)
      k['Graph'].add_node(j)
      k['Graph'].nodes[j]['features'] = features
  n = n + 1

print_graph_info(D_list[2][0]['Graph'])

# Genera la matrice di adiacenza
adj_matrix = nx.adjacency_matrix(D_list[2][0]['Graph']).todense()

# Visualizza la heatmap
plt.imshow(adj_matrix, cmap='hot', interpolation='nearest')
plt.colorbar()

# Aggiungi titoli e etichette
plt.title("Heatmap - Adjacency matrix")
plt.xlabel("Nodi")
plt.ylabel("Nodi")

# Mostra la heatmap
plt.show()

plot_graph(D_list[1][0]['Graph'])

indici_comuni = gene_snp.loc[gene_snp['gene_name'].isin(list(D_list[2][0]['Graph'].nodes))].index
dataset = df.loc[indici_comuni]
dataset = dataset.T
dataset = pd.concat([dataset, df.T[['PTGENDER','AGE','y']]], axis=1)
dataset

with open('/content/drive/MyDrive/PROJECT/NCBI_graph_PET.pickle', 'wb') as handle:
    pickle.dump(D_list, handle, protocol=pickle.HIGHEST_PROTOCOL)

dataset.to_csv('/content/drive/MyDrive/PROJECT/dataset_full_real_phenotype.csv.gz', sep='\t', compression='gzip')

with open('/content/drive/MyDrive/PROJECT/NCBI_graph_PET.pickle', 'rb') as handle:
    lista_dizionari = pickle.load(handle)

print_graph_info(lista_dizionari[2][0]['Graph'])