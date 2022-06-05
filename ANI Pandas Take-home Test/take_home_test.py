# -*- coding: utf-8 -*- 
# Description:
# @Time : 2022-06-04 23:15 
# @Author : Tingjun Guo
# @File : take_home_test.py

import pandas as pd
import numpy as np

if __name__ == '__main__':
    example_data = pd.read_excel('./Example_Data.xlsx', sheet_name='Example_Data', header=1)
    example_DB = pd.read_excel('./Example_Data.xlsx', sheet_name='Example_DB')

    # check digit
    example_data['valid_fiscal_year'] = list(map(lambda x: str(x).isnumeric(), example_data['Fiscal Year']))
    example_data['valid_sic_code'] = list(map(lambda x: str(x).isnumeric(), example_data['SIC Code']))
    example_data = example_data[example_data['valid_fiscal_year'] == True].drop(columns=['valid_fiscal_year'])
    example_data = example_data[example_data['valid_sic_code'] == True].drop(columns=['valid_sic_code'])

    # valid years
    example_data['Fiscal Year'] = example_data['Fiscal Year'].astype('int64')
    example_data = example_data[(1999 <= example_data['Fiscal Year']) & (example_data['Fiscal Year'] <= 2021)]

    # valid sic code
    example_data['SIC Code'] = example_data['SIC Code'].astype('str')
    example_data = example_data[example_data['SIC Code'].str.len() == 4]
    example_data['SIC Code'] = example_data['SIC Code'].astype('int')

    # valid trading currency
    example_data = example_data[(example_data['Trading Currency'] == 'USD') | (example_data['Trading Currency'] == 'GBP')]

    # same id different name
    dulplicate_name = example_data.groupby(['Company ID'])['Company Name'].nunique().reset_index()
    dulplicate_name = dulplicate_name[dulplicate_name['Company Name'] != 1]['Company ID'].values

    # same name different id
    dulplicate_id = example_data.groupby(['Company Name'])['Company ID'].nunique().reset_index()
    dulplicate_id = dulplicate_id[dulplicate_id['Company ID'] != 1]['Company Name'].values

    # drop invalid duplicate
    for id in dulplicate_id:
        example_data = example_data[~(example_data['Company Name'] == id)]
    for name in dulplicate_name:
        example_data = example_data[~(example_data['Company ID'] == name)]

    # data processing
    example_data = pd.melt(example_data,
                  id_vars=['Company ID', 'Company Name', 'Fiscal Year', 'Industry', 'SIC Code', 'Trading Currency'],
                  var_name='Metric Name', value_name='Value')

    # data comparison
    example_data['source'] = ['Data in File'] * example_data.shape[0]
    example_DB['source'] = ['Data in DB'] * example_DB.shape[0]
    example_DB = example_DB.fillna('nan in DB')
    example_data = example_data.fillna('nan in data')

    example_answer = pd.concat([example_data, example_DB]).drop_duplicates(
        subset=['Company ID', 'Company Name', 'Fiscal Year', 'Industry', 'SIC Code', 'Trading Currency', 'Metric Name',
                'Value'], keep=False)

    example_answer = example_answer.pivot(
        index=['Company ID', 'Company Name', 'Fiscal Year', 'Industry', 'SIC Code', 'Trading Currency', 'Metric Name'],
        columns='source', values='Value').rename_axis(columns=None).reset_index()

    example_answer = example_answer[~((example_answer['Data in DB'] == 'nan in DB') & (example_answer['Data in File'] == 'nan in data'))]

    error_type = []
    for in_db, in_data in zip(example_answer['Data in DB'], example_answer['Data in File']):
        if pd.isna(in_db) and ~pd.isna(in_data):
            error_type.append('Not_in_DB')
        elif ~pd.isna(in_db) and pd.isna(in_data):
            error_type.append('Not_in_File')
        elif ~pd.isna(in_db) and ~pd.isna(in_data) and in_db != in_data:
            error_type.append('UnEqual')
    example_answer['Error Type'] = error_type

    nan_in_db = [np.nan if in_db == 'nan in DB'  else in_db for in_db in example_answer['Data in DB']]
    nan_in_data = [np.nan if in_data == 'nan in data'  else in_data for in_data in example_answer['Data in File']]

    example_answer['Data in DB'] = nan_in_db
    example_answer['Data in File'] = nan_in_data
    example_answer['Data in DB'] = example_answer['Data in DB'].astype('Int64')
    example_answer['Data in File'] = example_answer['Data in File'].astype('Int64')
    example_answer = example_answer.drop(columns=['Industry'])

    print(example_answer)