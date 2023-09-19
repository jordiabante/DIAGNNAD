# -*- coding: utf-8 -*-
"""XGBoost_Classifier_PET_madeup_data_interactions.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ebQhVpHHMa7ICaxQ74YgJCEWYUeFmZon
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

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV

# checkejem que s'obri correctament:
with open('/content/drive/MyDrive/PROJECT/dataset_Age_Sex_madeup_pheno_interactions.pickle', 'rb') as handle:
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

# creem el model XBOOST per classificar
        xgb_model = XGBClassifier(random_state=42)

# Definir los hiperparámetros a ajustar
        param_grid = {
            'reg_alpha': [0, 0.01, 0.1], # this controls de l1 penalty, if = 0 -> no penalty applied.
            'n_estimators': [100, 200, 300],
            'max_depth': [None, 1, 5, 10],
            'learning_rate': [0.01, 0.1, 0.5]
        }

# Realizar la búsqueda de hiperparámetros con validación cruzada
        grid_search = GridSearchCV(xgb_model, param_grid, cv=5, scoring='balanced_accuracy')
        grid_search.fit(X_train, y_train)

# Seleccionar los mejores hiperparámetros encontrados por la búsqueda
        best_params = grid_search.best_params_

# Entrenar el modelo de XGBoost con los mejores hiperparámetros
        xgb_model = XGBClassifier(random_state=42, **best_params) #, objective='binary:logistic', tree_method='hist', eta=0.1, max_depth=3)
        xgb_model.fit(X_train, y_train)


        # podem calcular el pes de cada predictiu amb la funció següent:
        importances = xgb_model.feature_importances_
        max_idx = np.argmax(importances)
        print("The most important predictor is:", X_train.columns[max_idx])
# que el predictor amb més pes quasi sempre és la EDAT!!!! WHOT

# Imprime los mejores parámetros encontrados
        print("Best parameters found:", best_params)


# Make the prediction
        y_pred = xgb_model.predict(X_test)
        y_pred = y_pred.astype(float).round(1)
        y_proba = xgb_model.predict_proba(X_test)[:,1]

# Compute the metrics
        classes=['0.0', '1.0']
        cm, accuracy, balanced_accuracy, precision, recall, specificity, NPV, f1, roc_auc, thresholds = metrics(y_test, y_pred, y_proba, classes)
        print("Precisión del modelo: {:.2f}".format(accuracy))

# Compute the loss function
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
file_1 = open('./res_XGBoost_madeup_data_inter.json','w')
json.dump(result,file_1)
file_1.close()