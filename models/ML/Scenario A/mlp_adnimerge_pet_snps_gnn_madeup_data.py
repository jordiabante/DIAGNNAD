# -*- coding: utf-8 -*-
"""MLP_adnimerge_PET_snps_GNN_madeup_data.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1vUA1HylNn_Hn4Av1TSaTVgNzE1p1crRG
"""

from google.colab import drive
drive.mount('/content/drive')

##import library
import gc
import os
os.chdir('/content/drive/MyDrive/Colab Notebooks/GitHub')
import numpy as np
import networkx
import csv
import pandas as pd
from tqdm import tqdm
import gzip
import re
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Sequential
from metrics import metrics
from labelling import label_ADNI
from sklearn.model_selection import train_test_split
from keras import backend as K
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import StratifiedKFold
import itertools
import math
import pickle
import json

from sklearn.metrics import log_loss
from sklearn.model_selection import GridSearchCV
from sklearn.neural_network import MLPClassifier

# https://realpython.com/logistic-regression-python/

with open('/content/drive/MyDrive/PROJECT/dataset_Age_Sex_madeup_pheno.pickle', 'rb') as handle:
    dataset_list = pickle.load(handle)
dataset_list

# Crea las listas vacías para las métricas
cm_list = []
accuracy_list = []
balanced_accuracy_list = []
precision_list = []
recall_list = []
specificity_list = []
NPV_list = []
f1_list = []
roc_auc_list = []
loss_list = []

for j in dataset_list:
    rows, columns = j.shape
    validation_list = []
    training_list = []

    cm_list_f = []
    accuracy_list_f = []
    balanced_accuracy_list_f = []
    precision_list_f = []
    recall_list_f = []
    specificity_list_f = []
    NPV_list_f = []
    f1_list_f = []
    roc_auc_list_f = []
    loss_list_f = []

    for i in range(5):
        if i == 4:
            train = j.iloc[:int(rows/5*i), :]
            validation = j.iloc[int(rows/5*i):, :]
        else:
            train1 = j.iloc[:int(rows/5*i), :]
            train2 = j.iloc[int(rows/5*(i+1)):, :]
            train = pd.concat([train1, train2], axis=0)
            validation = j.iloc[int(rows/5*i):int(rows/5*(i+1)), :]
        validation_list.append(validation)
        training_list.append(train)

        df_train = training_list[i]
        df_test = validation_list[i]
        print(i, "test SET", len(df_test))

        X_train = df_train.drop(columns=['y'])
        y_train = df_train['y']
        y_train = y_train.astype(float).round(1)

        X_test = df_test.drop(columns=['y'])
        y_test = df_test['y']
        y_test = y_test.astype(float).round(1)

   # Create model object --> https://machinelearninggeek.com/multi-layer-perceptron-neural-network-using-python/
    # Define los parámetros para la grid search
        parameters = {
            'hidden_layer_sizes': [
            (20,15), (20,20), (20,25),
            (30,15), (30,20), (30,25),
            (40,10), (40,15), (40,20), (40,25),
            (50,15), (50,20), (50,25)],  # Prueba diferentes combinaciones de números de neuronas
            'random_state': [None],  # Deja el random_state sin cambios
            'verbose': [False],  # Deja el verbose sin cambios, no volem info a cada iteració
            'learning_rate_init': [0.01]  # Deja la tasa de aprendizaje sin cambios
        }

    # Crea el modelo base
    # asume que el número de inputs se deriva automáticamente del tamaño de los datos de entrenamiento proporcionados durante el ajuste del modelo.
        base_model = MLPClassifier() #This model optimizes the log-loss function using LBFGS or stochastic gradient descent.

    # Realiza la grid search
        grid_search = GridSearchCV(base_model, parameters, cv=5, scoring='accuracy', n_jobs=-1)
        grid_search.fit(X_train, y_train)

    # Obtiene los mejores parámetros y el mejor modelo
        best_params = grid_search.best_params_
        best_model = grid_search.best_estimator_

    # Imprime los mejores parámetros encontrados
        print("Mejores parámetros encontrados:")
        print(best_params)

    # Make the prediction
        y_pred = best_model.predict(X_test)
        y_pred = y_pred.astype(float).round(1)
        y_proba = best_model.predict_proba(X_test)[:,1]

    # Compute the metrics
        classes=['0.0', '1.0']
        cm, accuracy, balanced_accuracy, precision, recall, specificity, NPV, f1, roc_auc, thresholds = metrics(y_test, y_pred, y_proba, classes)

    # Compute the loss function
    # loss = mean_squared_error(y_test.dropna(), y_pred[y_test.notna()])
        loss = log_loss(y_test, y_proba, normalize=True, sample_weight=None, labels=[0.0, 1.0])

    # Store the data in the lists
        cm_list_f.append(cm)
        accuracy_list_f.append(accuracy)
        balanced_accuracy_list_f.append(balanced_accuracy)
        precision_list_f.append(precision)
        recall_list_f.append(recall)
        specificity_list_f.append(specificity)
        NPV_list_f.append(NPV)
        f1_list_f.append(f1)
        roc_auc_list_f.append(roc_auc)
        loss_list_f.append(loss)

# Store the data in the lists
    cm_list.append(cm_list_f)
    accuracy_list.append(accuracy_list_f)
    balanced_accuracy_list.append(balanced_accuracy_list_f)
    precision_list.append(precision_list_f)
    recall_list.append(recall_list_f)
    specificity_list.append(specificity_list_f)
    NPV_list.append(NPV_list_f)
    f1_list.append(f1_list_f)
    roc_auc_list.append(roc_auc_list_f)
    loss_list.append(loss_list_f)

print(str(round(np.mean(roc_auc_list),4)) + ' +- ' + str(round(np.std(roc_auc_list),4)))

result = {'accuracy': accuracy_list,
          'balanced_accuracy': balanced_accuracy_list,
          'recall' : recall_list,
          'precision': precision_list,
          'specificity': specificity_list,
          'NPV': NPV_list,
          'F1_score': f1_list,
          'AUC': roc_auc_list
}
os.chdir('/content/drive/MyDrive/Colab Notebooks/GitHub/results')
file_1 = open('./res_MLP_madeup_data.json','w')
json.dump(result,file_1)
file_1.close()