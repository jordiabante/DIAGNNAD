# -*- coding: utf-8 -*-
"""Random_forest_PET.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1B7CF402hFbCTRt3pSpPwJtVV44CS5LPI
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

# Data Processing
import pandas as pd
import numpy as np

# Modelling
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, ConfusionMatrixDisplay
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from scipy.stats import randint
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import log_loss

# Tree Visualisation
from sklearn.tree import export_graphviz
from IPython.display import Image
import graphviz

# checkejem que s'obri correctament:
with open('/content/drive/MyDrive/PROJECT/training_set_Age_Sex.pickle', 'rb') as handle:
    training = pickle.load(handle)

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
    print(i, "test SET", len(df_test))

    X_train = df_train.drop(columns=['y'])
    y_train = df_train['y']
    y_train = y_train.astype(float).round(1)

    X_test = df_test.drop(columns=['y'])
    y_test = df_test['y']
    y_test = y_test.astype(float).round(1)
    # Define the parameter grid for grid search
    param_grid = {
            'n_estimators': [100, 200, 300],
            'max_depth': [None, 1, 5, 10],
            'min_samples_split': [2, 5, 10]
        }

# Initialize the random forest classifier
    rfc = RandomForestClassifier(random_state=42)

# Create the grid search object
    grid_search = GridSearchCV(rfc, param_grid, cv=5, scoring='balanced_accuracy')

# Perform grid search to find the best hyperparameters
    grid_search.fit(X_train, y_train)

    # Get the best estimator from the grid search
    best_estimator = grid_search.best_estimator_

# podem calcular el pes de cada predictiu amb la funció següent:
    importances = best_estimator.feature_importances_
    indices = np.argsort(importances)[::-1]  # Ordenar los índices en orden descendente
    top5_indices = indices[:5]  # Obtener los primeros cinco índices

    print("Los cinco predictores más importantes son:")
    for idx in top5_indices:
        print(X_train.columns[idx])
# que el predictor amb més pes quasi sempre és rs429358 - APOE!!!!!!!!!!

    # Make the prediction
    y_pred = best_estimator.predict(X_test)
    y_pred = y_pred.astype(float).round(1)
    y_proba = best_estimator.predict_proba(X_test)[:,1]

    # Compute the metrics
    classes=['0.0', '1.0']
    cm, accuracy, balanced_accuracy, precision, recall, specificity, NPV, f1, roc_auc, thresholds = metrics(y_test, y_pred, y_proba, classes)
    print("Precisión del modelo: {:.2f}".format(accuracy))

    # Compute the loss function
    loss = log_loss(y_test, y_proba, normalize=True, sample_weight=None, labels=[0.0, 1.0])



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

print(str(round(np.mean(balanced_accuracy_list),4)) + ' +- ' + str(round(np.std(balanced_accuracy_list),4)))

import json
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
file_1 = open('./res_RF_realdata.json','w')
json.dump(result,file_1)
file_1.close()