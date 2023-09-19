# -*- coding: utf-8 -*-
"""logistic_regression_adnimerge_PET_snps_GNN.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1WW6j6DnfABKBTjb45RFOtw_2leV7QNk0
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
from sklearn.linear_model import LogisticRegression
from metrics import metrics
from labelling import label_ADNI
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedKFold
import itertools
from sklearn.metrics import log_loss
import random
from sklearn.metrics import mean_squared_error
import pickle
import json

# https://realpython.com/logistic-regression-python/

# checkejem que s'obri correctament:
with open('/content/drive/MyDrive/PROJECT/training_set_Age_Sex.pickle', 'rb') as handle:
    training = pickle.load(handle)

# checkejem que s'obri correctament:
with open('/content/drive/MyDrive/PROJECT/validation_set_Age_Sex.pickle', 'rb') as handle:
    validation = pickle.load(handle)
validation[0]

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

for i in range(len(training)):
    df_train = training[i]
    df_test = validation[i]
    print("length del TRAINING set is ", len(df_train))
    print("length del VALIDATION set is ", len(df_test))

    X_train = df_train.drop(columns=['y'])
    y_train = df_train['y']
    y_train = y_train.astype(float).round(1)


    X_test = df_test.drop(columns=['y'])
    y_test = df_test['y']
    y_test = y_test.astype(float).round(1)

    model = LogisticRegression(penalty='l1',solver='liblinear', max_iter=1000)
# model = LogisticRegression(penalty='l1', solver='liblinear', max_iter=1000)

    # Train the model using our data sets
    model.fit(X_train, y_train)

    # Make the prediction
    y_pred = model.predict(X_test)
    y_pred = y_pred.astype(float).round(1)
    y_proba = model.predict_proba(X_test)[:,1]

    coefficients = model.coef_ # Get the coefficients
    maximum_index = np.unravel_index(np.argmax(coefficients), coefficients.shape)
    print(maximum_index)

    # obtain the best predictors
    coefficients = model.coef_[0]
    max_idx = np.argmax(np.abs(coefficients))  # Find the index of the highest absolute coefficient

    best_predictor = X_train.columns[max_idx]

    print("The best predictor is:", best_predictor)
    # Compute the metrics
    classes=['0.0', '1.0']
    cm, accuracy, balanced_accuracy, precision, recall, specificity, NPV, f1, roc_auc, thresholds = metrics(y_test, y_pred, y_proba, classes)

    # Compute the loss function
    loss = mean_squared_error(y_test.dropna(), y_pred[y_test.notna()])
# loss = log_loss(y_test, y_proba, normalize=True, sample_weight=None, labels=[0.0, 1.0])

    # Store the data in the lists
    cm_list.append(cm)
    accuracy_list.append(accuracy)
    balanced_accuracy_list.append(balanced_accuracy)
    precision_list.append(precision)
    recall_list.append(recall)
    specificity_list.append(specificity)
    NPV_list.append(NPV)
    f1_list.append(f1)
    roc_auc_list.append(roc_auc)
    loss_list.append(loss)

# definisci una lista con le tue 8 liste di dati
metric = [accuracy_list, balanced_accuracy_list, precision_list, recall_list, specificity_list, NPV_list, f1_list, roc_auc_list, loss_list]

# definisci i nomi dei boxplot
names = ['accuracy', 'balanced accuracy', 'precision', 'recall', 'specificity', 'NPV', 'F1 score', 'AUC', 'LOSS F']

# crea la figura e gli assi
fig, ax = plt.subplots(figsize=(15, 8))

# disegna i boxplot
bp = ax.boxplot(metric, labels=names, patch_artist=True)

# imposta i colori dei boxplot
colors = ['pink', 'lightblue', 'lightgreen', 'tan', 'lightgrey', 'lavender', 'beige', 'plum', 'cornsilk']
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)

# imposta il titolo e le etichette degli assi
ax.set_title('LOGISTIC REGRESSION PET')

# mostra la figura
plt.show()

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
file_1 = open('./res_logreg_l1_realdata.json','w')
json.dump(result,file_1)
file_1.close()