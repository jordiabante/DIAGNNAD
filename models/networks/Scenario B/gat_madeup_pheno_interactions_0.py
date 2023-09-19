# -*- coding: utf-8 -*-
"""GAT_madeup_pheno_interactions_0.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Rls7y0FKA5VY7vZHQv-e2HC4BLCk_CiP
"""

import os.path as osp
from math import ceil
import pickle
from sklearn.metrics import balanced_accuracy_score

import torch
import torch.nn.functional as F
from torch.nn import Linear

from torch_geometric.datasets import TUDataset
from torch_geometric.loader import DataLoader
from torch_geometric.nn import DenseGraphConv, DMoNPooling, GCNConv, TopKPooling, global_mean_pool
import torch.nn as nn
from torch_geometric.utils import to_dense_adj, to_dense_batch
import matplotlib.pyplot as plt
import os
import numpy as np
import math
import json
from torch.optim.lr_scheduler import OneCycleLR
from sklearn.model_selection import ParameterGrid
import time
import random
import sys


sys.path.append('/biofisica/home/creatio_student/project_gnn_ad/file_articolo/')
from metrics import metrics
from gnn_definitions import GAT, train, validation, test
os.chdir('/biofisica/home/creatio_student/project_gnn_ad/models/GAT_madeup_pheno_interactions_grid_0')

with open('/biofisica/home/creatio_student/project_gnn_ad/file_articolo/dataset_GNN_0_madeup_pheno_interactions.pickle', 'rb') as handle:
    dataset_list = pickle.load(handle)


file1 = open('./winner_params.json', 'r')
winner_params = json.load(file1)

# Set the number of epochs
num_epoch = 750
# set the batch size
batch_size = 16

start_time = time.time()
# Initialize lists to store the validation metrics for each trial
val_accuracy_list = []
val_loss_list = []
val_cm_list = []
val_balanced_accuracy_list = []
val_precision_list = []
val_recall_list = []
val_specificity_list = []
val_NPV_list = []
val_f1_list = []
val_roc_auc_list = []
val_thresholds_list = []


# Loop over the specified number of trials
flag = 0
for j in dataset_list:
    flag += 1
    n_elem = len(j)
    validation_list = []
    training_list = []

    #initialize the lists to store the result of each of the 5 folds of 5fold method
    val_accuracy_list_flag = []
    val_loss_list_flag = []
    val_cm_list_flag = []
    val_balanced_accuracy_list_flag = []
    val_precision_list_flag = []
    val_recall_list_flag = []
    val_specificity_list_flag = []
    val_NPV_list_flag = []
    val_f1_list_flag = []
    val_roc_auc_list_flag = []
    val_thresholds_list_flag = []
    # Create a directory for each trial to save model checkpoints
    if not os.path.exists('./PET_iteration_'+ str (flag)):
        os.mkdir('./PET_iteration_'+ str (flag))
        os.chdir('./PET_iteration_'+ str (flag))


    for i in range(5):
        if i == 4:
            tr = j[:int(n_elem/5*i)]
            vali = j[int(n_elem/5*i):]
        else:
            train1 = j[:int(n_elem/5*i)]
            train2 = j[int(n_elem/5*(i+1)):]
            tr = train1 + train2
            vali = j[int(n_elem/5*i):int(n_elem/5*(i+1))]

        validation_list.append(vali)
        training_list.append(tr)

        training_set = training_list[i]
        validation_set = validation_list[i]

        # Create a DataLoader object for the validation set with batch size 16 and shuffle the data
        val_loader = DataLoader(validation_set, batch_size, shuffle=True)

        # Create a DataLoader object for the training set with batch size 16 and shuffle the data
        train_loader = DataLoader(training_set, batch_size, shuffle=True)

        # Initialize variables and set device to use GPU if available, CPU otherwise
        max_balanced = 0
        train_loss_list_epoch = []
        val_loss_list_epoch = []
        balanced_accuracy_list_epoch_val = []
        balanced_accuracy_list_epoch_train = []
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = GAT(num_features=winner_params['num_features'],
                   hidden_channels=winner_params['hidden_channels'],
                   num_classes=winner_params['num_classes'],
                   out_channels=winner_params['out_channels'],
                   num_layer=winner_params['num_layer']).to(device)

        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        total_iterations = math.ceil(len(training_set) / batch_size)*num_epoch
        scheduler = OneCycleLR(optimizer, max_lr=0.01, total_steps=total_iterations)

        # Loop over the specified number of epochs
        for epoch in range(1, num_epoch+1):

            # Train the model
            train_loss = train(train_loader, model, device, optimizer, scheduler)

            # Calculate the training and validation loss and balanced accuracy
            train_loss_2, balanced_accuracy_train = validation(train_loader, model, device)
            val_loss,  balanced_accuracy = validation(val_loader, model, device)

            # Print the current epoch's metrics
            print(f'dataset: {flag} trial: {i+1} Epoch: {epoch:03d}, Train Loss: {train_loss:.3f}, '
                  f'Train Bal Acc: {balanced_accuracy_train:.3f}, Val Loss: {val_loss:.3f}, '
                  f'Val Bal Acc: {balanced_accuracy:.3f}')

                # Append the current epoch's metrics to the corresponding lists
            balanced_accuracy_list_epoch_val.append(balanced_accuracy)
            balanced_accuracy_list_epoch_train.append(balanced_accuracy_train)
            train_loss_list_epoch.append(train_loss)
            val_loss_list_epoch.append(val_loss)

            # If the current epoch's balanced accuracy is higher than the previous highest, save the current model checkpoint
            if balanced_accuracy > max_balanced:
                max_balanced = balanced_accuracy
                torch.save(model.state_dict(), "./modello_" + 'iteration_' + str(flag) + '_trial_' + str(i+1) + ".pt")
                print('model_saved at epoch ' + str(epoch) + ' with balanced_accuracy: ' + str(max_balanced))


        # Plot the loss and balanced accuracy for each epoch of the current trial
        plt.figure("train", (12, 6))
        plt.subplot(1, 2, 1)
        plt.title("Iteration Average Loss")
        x = [(i + 1) for i in range(len(train_loss_list_epoch))]
        y = train_loss_list_epoch
        y1 = val_loss_list_epoch
        plt.xlabel("Iteration")
        plt.plot(x, y,label="train BCE")
        plt.plot(x,y1,label="val BCE")
        plt.legend(loc="upper right")
        plt.subplot(1, 2, 2)
        plt.title("Val balanced Accuracy")
        x = [(i + 1) for i in range(len(balanced_accuracy_list_epoch_train))]
        y = balanced_accuracy_list_epoch_val
        y1 = balanced_accuracy_list_epoch_train
        plt.xlabel("Iteration")
        plt.plot(x, y,color='orange',label="val balanced Accuracy")
        plt.plot(x, y1,color='blue',label="train balanced Accuracy")
        plt.legend(loc="upper left")

        # Save the plot of the loss and balanced accuracy
        plt.savefig('./balanced_accuracy_loss ' + str(i+1) + '.png')

        plt.show()
        plt.close()

        # Load the state dictionary of the model saved during training
        model.load_state_dict(torch.load("./modello_" + 'iteration_' + str(flag) + '_trial_' + str(i+1) + ".pt"))

        # Test the model on the validation set
        val_loss, cm, accuracy, balanced_accuracy, precision, recall, specificity, NPV, f1, roc_auc, thresholds, _, _ = test(val_loader, model, device)

        # Append the evaluation metrics to their respective lists if they are not NaN
        val_cm_list_flag.append(cm)
        if not math.isnan(accuracy):
          val_accuracy_list_flag.append(accuracy)
        if not math.isnan(val_loss):
          val_loss_list_flag.append(val_loss)
        if not math.isnan(balanced_accuracy):
          val_balanced_accuracy_list_flag.append(balanced_accuracy)
        if not math.isnan(precision):
          val_precision_list_flag.append(precision)
        if not math.isnan(recall):
          val_recall_list_flag.append(recall)
        if not math.isnan(specificity):
          val_specificity_list_flag.append(specificity)
        if not math.isnan(NPV):
          val_NPV_list_flag.append(NPV)
        if not math.isnan(f1):
          val_f1_list_flag.append(f1)
        if not math.isnan(roc_auc):
          val_roc_auc_list_flag.append(roc_auc)


    # Change the current working directory back to the original directory
    os.chdir('/biofisica/home/creatio_student/project_gnn_ad/models/GAT_madeup_pheno_interactions_grid_0')
    val_cm_list.append(val_cm_list_flag)
    val_accuracy_list.append(val_accuracy_list_flag)
    val_loss_list.append(val_loss_list_flag)
    val_balanced_accuracy_list.append(val_balanced_accuracy_list_flag)
    val_precision_list.append(val_precision_list_flag)
    val_recall_list.append(val_recall_list_flag)
    val_specificity_list.append(val_specificity_list_flag)
    val_NPV_list.append(val_NPV_list_flag)
    val_f1_list.append(val_f1_list_flag)
    val_roc_auc_list.append(val_roc_auc_list_flag)
end_time = time.time()

result = {'accuracy': val_accuracy_list,
          'balanced_accuracy': val_balanced_accuracy_list,
          'recall' : val_recall_list,
          'precision': val_precision_list,
          'specificity': val_specificity_list,
          'NPV': val_NPV_list,
          'F1_score': val_f1_list,
          'AUC': val_roc_auc_list
}

os.chdir('/biofisica/home/creatio_student/project_gnn_ad/results')
file_1 = open('./risultati_GAT_madeup_pheno_interactions_0.json','w')
json.dump(result,file_1)
file_1.close()

# Calcola il tempo trascorso
elapsed_time = end_time - start_time

# Stampa il tempo trascorso
print(f"Tempo trascorso: {elapsed_time} secondi")