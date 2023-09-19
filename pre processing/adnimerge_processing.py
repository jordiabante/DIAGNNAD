# -*- coding: utf-8 -*-
"""ADNIMERGE_processing.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1mnuCmcY4yXpB5dps2Tmdvlr4nihjIe1r
"""

'''
processing of ADNIMERGE matrix
'''
import os
import numpy as np
import pandas as pd

import datetime as dt
from scipy import stats

def select_genetic_cohort(input_filename, output_filename):

    '''
    in this function are replaced the values containing mathematical symbols and then are converted in float in all of those column
    the NaN are also replaced
    '''

    samples_filename = 'drive/MyDrive/PROJECT/field_names.txt'

    # Get samples names
    samples_file = open(samples_filename, 'r')
    samples_names = samples_file.read().split('\n')
    samples_file.close()
    del samples_names[0:79]
    samples_names = [i.upper() for i in samples_names]

    # Load original ADNIMERGE data
    adnimerge = pd.read_csv(input_filename, index_col='PTID', low_memory=False)

    # Select genetics cohort samples
    adnimerge_genetics = adnimerge.loc[samples_names]
    adnimerge_genetics.index = adnimerge_genetics.index.str.upper()

    # Preprocessing some data
    adnimerge_genetics['ABETA'].replace('>1700', 1700, inplace=True)
    adnimerge_genetics['PTAU'].replace('<8', 8, inplace=True)
    adnimerge_genetics['PTAU'].replace('>120', 120, inplace=True)
    adnimerge_genetics['ABETA'].replace('<200', 200, inplace=True)
    adnimerge_genetics['TAU'].replace('<80', 80, inplace=True)
    adnimerge_genetics['TAU'].replace('>1300', 1300, inplace=True)
    adnimerge_genetics['ABETA'] = adnimerge_genetics['ABETA'].astype('float64')
    adnimerge_genetics['PTAU'] = adnimerge_genetics['PTAU'].astype('float64')
    adnimerge_genetics['TAU'] = adnimerge_genetics['TAU'].astype('float64')

    # Replace NaN values
    adnimerge_genetics.replace('-4', np.nan, inplace=True)
    adnimerge_genetics.replace(r'(\d\:\d[0-9])|(\d[0-99]\:\d[0-99])|(\d[0-9]\:\d)|(\d\:\d)', np.nan, inplace=True, regex=True)

    #print()
    #print(adnimerge_genetics)
    adnimerge_genetics.to_csv(output_filename)

    return adnimerge_genetics

def biomarkers_processing(data):

    '''
    Process dataset. in particular where extracted data of last visit for the patients
    '''

    result = pd.DataFrame([])

    samples = list(set(data.index))
    # print(len(samples))

    columns = ['EXAMDATE', 'AGE', 'DX', 'PTGENDER', 'PTEDUCAT', 'PTETHCAT',
                'APOE4', 'AV45', 'PIB', 'ABETA', 'TAU', 'PTAU', 'FDG']
    
    data = data[columns]

    for sample in samples:

        sample_rows = data.loc[sample]

        if type(sample_rows['EXAMDATE']) == str:
            most_recent_row = sample_rows.to_frame().T

            
        else:
            sample_rows = sample_rows.sort_values(by='EXAMDATE', ascending=True)

            sample_rows = sample_rows.replace({'AV45': {0: np.nan}}).ffill()
            sample_rows = sample_rows.replace({'PIB': {0: np.nan}}).ffill()
            sample_rows = sample_rows.replace({'ABETA': {0: np.nan}}).ffill()
            sample_rows = sample_rows.replace({'TAU': {0: np.nan}}).ffill()
            sample_rows = sample_rows.replace({'PTAU': {0: np.nan}}).ffill()
            sample_rows = sample_rows.replace({'FDG': {0: np.nan}}).ffill()

            sample_rows.loc[:,'EXAMDATE'] = pd.to_datetime(sample_rows.loc[:, 'EXAMDATE'], format='%Y-%m-%d')
            most_recent_exam = sample_rows['EXAMDATE'].max()
            most_recent_row = sample_rows[sample_rows['EXAMDATE'] == most_recent_exam]

        result = result.append(most_recent_row)
    
    result = result.drop(columns=['EXAMDATE'])
    
    return result

def create_positive_columns(data):

    '''
    add a column with 1 if the specific data are above a specific treshold and 0 otherwise
    '''


    data.loc[:, 'AV45+'] = np.where(
    data['AV45'] >= 1.11, 1, np.where(
    data['AV45'] <  1.11, 0, np.nan))

    data.loc[:, 'PIB+'] = np.where(
        data['PIB'] >= 1.27, 1, np.where(
        data['PIB'] <  1.27, 0, np.nan))

    data.loc[:, 'ABETA+'] = np.where(
        data['ABETA'] >= 192, 1, np.where(
        data['ABETA'] <  192, 0, np.nan))

    data.loc[:, 'TAU+'] = np.where(
        data['TAU'] >= 93, 1, np.where(
        data['TAU'] <  93, 0, np.nan))

    data.loc[:, 'PTAU+'] = np.where(
        data['PTAU'] >= 23, 1, np.where(
        data['PTAU'] <  23, 0, np.nan))

    data.loc[:, 'APOE4+'] = np.where(
        data['APOE4'] > 0, 1, np.where(
        data['APOE4'] == 0, 0, np.nan))

    return data

def timeseries_processing(data, biomarker):

    '''
    perform a linear regression on the data tau ptu e fdg using the month from the baseline as a time
    '''

    # print(biomarker)

    notna_biomarker = data[data[biomarker].notna()]
    samples = list(set(notna_biomarker.index))

    rows_biomarker = []
    counter = 0
    for s in samples:
        
        sample_data = notna_biomarker.loc[s, :]
       
        if sample_data.shape != (112,):
            
            counter += 1
            if type(sample_data) == pd.DataFrame:
              sample_data = sample_data.sort_values('Month', ascending=True)
            
              slope, intercept, r_value, p_value, std_err = stats.linregress(sample_data['Month'],
                                                                            sample_data[biomarker])
            
              rows_biomarker.append([s, slope, r_value])
            
    # print(f'Number of subjects with >= 2 {biomarker} measurements: {counter} out of {len(samples)}')

    biomarker_progression = pd.DataFrame(rows_biomarker,
                                            columns=['sample',
                                                    f'{biomarker}_slope',
                                                    f'{biomarker}_rvalue'])

    biomarker_progression.set_index(['sample'], inplace=True)
    
    return biomarker_progression

def biomarkers_score(data):

    '''
    calculate the score of each patient for AV45 and PIB as a linear combination of that column and other
    '''

    av45_cohort = data[['AV45', 'APOE4', 'TAU', 'PTAU', 'ABETA']]
    av45_cohort = av45_cohort.dropna(thresh=5)
    # print(av45_cohort)

    pib_cohort = data[['PIB', 'APOE4', 'TAU', 'PTAU', 'ABETA']]
    pib_cohort = pib_cohort.dropna(thresh=5)
    # print(pib_cohort)

    # print('Number of patients with APOE4-AV45-ABETA-TAU-PTAU measurements:', av45_cohort.shape[0])
    # print('Number of patients with APOE4-PIB-ABETA-TAU-PTAU measurements:', pib_cohort.shape[0])

    av45_cohort['AV45_scoring'] = (av45_cohort['AV45']/av45_cohort['AV45'].mean()
                                    + av45_cohort['ABETA']/av45_cohort['ABETA'].mean()
                                    + av45_cohort['TAU']/av45_cohort['TAU'].mean()
                                    + av45_cohort['PTAU']/av45_cohort['PTAU'].mean())/4

    pib_cohort['PIB_scoring'] = (pib_cohort['PIB']/pib_cohort['PIB'].mean()
                                    + pib_cohort['ABETA']/pib_cohort['ABETA'].mean()
                                    + pib_cohort['TAU']/pib_cohort['ABETA'].mean()
                                    + pib_cohort['PTAU']/pib_cohort['ABETA'].mean())/4

    # print(av45_cohort)
    # print(pib_cohort)

    scoring = pd.concat([av45_cohort, pib_cohort], axis=1, sort=False)
    scoring.drop(columns=['AV45', 'PIB', 'APOE4', 'TAU', 'PTAU', 'ABETA'], inplace=True)
    
    return scoring


def main(input_filename, genetics_filename, output_filename):

    from google.colab import drive
    drive.mount('/content/drive')


    adnimerge_genetics = select_genetic_cohort(input_filename, genetics_filename)

    adnimerge_processed = biomarkers_processing(adnimerge_genetics)
    adnimerge_processed = create_positive_columns(adnimerge_processed)
    adnimerge_scoring = biomarkers_score(adnimerge_processed)

    tau_progression = timeseries_processing(adnimerge_genetics, 'TAU')
    ptau_progression = timeseries_processing(adnimerge_genetics, 'PTAU')
    fdg_progression = timeseries_processing(adnimerge_genetics, 'FDG')

    adnimerge_all = adnimerge_processed.merge(adnimerge_scoring, how='outer', left_index=True, right_index=True)
    adnimerge_all = adnimerge_all.merge(tau_progression, how='outer', left_index=True, right_index=True)
    adnimerge_all = adnimerge_all.merge(ptau_progression, how='outer', left_index=True, right_index=True)
    adnimerge_all = adnimerge_all.merge(fdg_progression, how='outer', left_index=True, right_index=True)

    print()
    print(adnimerge_all)
    adnimerge_all.to_csv(output_filename)


if __name__ == '__main__':

    main('drive/MyDrive/PROJECT/ADNIMERGE.csv','drive/MyDrive/PROJECT/genetics.csv','drive/MyDrive/PROJECT/output_adnimerge.csv')