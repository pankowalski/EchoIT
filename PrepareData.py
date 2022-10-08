import pandas as pd
import numpy as np
from pymongo import MongoClient
import streamlit as st
# https://medium.com/@amirziai/flatten-json-on-python-package-index-pypi-9e4951693a5a
# https://towardsdatascience.com/flattening-json-objects-in-python-f5343c794b10
from flatten_json import flatten

class PrepareData:
    def __init__(self):
        self.host = st.secrets["host"]
        self.port = st.secrets["port"]
        self.db_name = st.secrets["db_name"]
        self.collection_name = st.secrets["collection_name"]

        self.client = MongoClient(host = self.host, port = self.port)
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]
    
    def prepare_data(self):

        # Get data from the server
        self.list_of_offers = list(self.collection.find({}))
        self.dict_flattened_offers = [flatten(offer) for offer in self.list_of_offers]
        df = pd.DataFrame(self.dict_flattened_offers)

        # Adjust data types
        df = df.astype({'_id': str,
                        'employment_types_0_salary_from': 'Int64', # Only 'Int64' conversion works for n/a values which I want to keep
                        'employment_types_0_salary_to': 'Int64',
                        'employment_types_1_salary_from': 'Int64', # Only 'Int64' conversion works for n/a values which I want to keep
                        'employment_types_1_salary_to': 'Int64',
                        'skills_0_level': 'Int64',
                        'skills_1_level': 'Int64',
                        'skills_2_level': 'Int64'})

        # Only needed columns
        df = df[['published_at',
                'title', 
                'city', 
                'marker_icon', 
                'workplace_type',
                'experience_level',
                'employment_types_0_type',
                'employment_types_0_salary_from',
                'employment_types_0_salary_to',
                'employment_types_0_salary_currency',
                'employment_types_1_type',
                'employment_types_1_salary_from',
                'employment_types_1_salary_to',
                'employment_types_1_salary_currency',
                'skills_0_name',
                'skills_0_level',
                'skills_1_name',
                'skills_1_level',
                'skills_2_name',
                'skills_2_level']]

        # Rename columns
        df = df.rename(columns = {'employment_types_0_type': 'main_employment_type',
                                'employment_types_0_salary_from': 'main_salary_from',
                                'employment_types_0_salary_to': 'main_salary_to',
                                'employment_types_0_salary_currency': 'salary_currency',
                                'employment_types_1_type': 'secondary_employment_type',
                                'employment_types_1_salary_from': 'secondary_salary_from',
                                'employment_types_1_salary_to': 'secondary_salary_to',
                                'employment_types_1_salary_currency': 'secondary_salary_currency',
                                'marker_icon': 'technology_area'})

        # Create datestamp
        df['datestamp'] = (df['published_at'].str[0:10]).astype('datetime64').dt.date
        df['datestamp_temp'] = (df['published_at'].str[0:10]).astype('datetime64')

        # Calculate year, month, week
        df['datestamp_year'] = (df.datestamp_temp.dt.year).astype(str) + 'y'
        df['datestamp_month'] = df['datestamp_year'].astype(str) + '-' + (df.datestamp_temp.dt.month).astype(str) + 'm'
        df['datestamp_week'] = df['datestamp_year'].astype(str) + '-' + (df.datestamp_temp.dt.isocalendar().week).astype(str) + 'w'

        # Drop temporary columns
        df = df.drop(columns = ['published_at', 'datestamp_temp'])

        # Remove duplicates - multiplied locations and reposted offers. Unfortunately with reposted offers I came up how to clean this only for a month so far, therefore between months might be two, same offers but shouldn't impact results anyhow significantly
        list_column_names = df.columns.to_list()
        list_column_names.remove('city')
        list_column_names.remove('datestamp')
        list_column_names.remove('datestamp_year')
        list_column_names.remove('datestamp_week')
        df = df.drop_duplicates(subset = list_column_names, keep = 'first', ignore_index = True)

        # Remove completely outstanding salary outliers
        df = df[((pd.isnull(df.main_salary_from) == True) & (pd.isnull(df.main_salary_to) == True)) | ((df.main_salary_from < 150000) & (df.main_salary_to < 150000))]

        # Employment type
        df['employment_type'] = np.select(condlist = [pd.isnull(df['secondary_employment_type']) == True,
                                              (((df['secondary_employment_type'] == 'b2b') | (df['secondary_employment_type'] == 'permanent')) & ((df['main_employment_type'] == 'b2b') | (df['main_employment_type'] == 'permanent'))),
                                              (((df['secondary_employment_type'] == 'b2b') | (df['secondary_employment_type'] == 'mandate_contract')) & ((df['main_employment_type'] == 'b2b') | (df['main_employment_type'] == 'mandate_contract'))),
                                              (((df['secondary_employment_type'] == 'mandate_contract') | (df['secondary_employment_type'] == 'permanent')) & ((df['main_employment_type'] == 'mandate_contract') | (df['main_employment_type'] == 'permanent')))
                                             ],
                                  choicelist = [df['main_employment_type'],
                                               'b2b & permanent',
                                               'b2b & mandate_contract',
                                               'permanent & mandate_contract'
                                               ]
                                            
                                 )

        # Secondary employment flag
        df['is_secondary_employment_flag'] = df['secondary_employment_type'].apply(lambda x: 'Yes' if pd.isnull(x) == False else 'No')

        # Salary flags
        df['is_main_salary_flag'] = df['salary_currency'].apply(lambda x: 'Yes' if pd.isnull(x) == False else 'No')
        df['is_secondary_salary_flag'] = df['secondary_salary_currency'].apply(lambda x: 'Yes' if pd.isnull(x) == False else 'No')

        # b2b/permanent/mandate_contract column for proper calculations of salary ranges (want to include all offers, with two employment types for each type)
        df[['b2b_salary_from', 'b2b_salary_to', 'permanent_salary_from', 'permanent_salary_to', 'mandate_contract_salary_from', 'mandate_contract_salary_to']] = None
        df.loc[df.main_employment_type.str.contains('b2b', na = False), 'b2b_salary_from'] = df.main_salary_from
        df.loc[df.main_employment_type.str.contains('b2b', na = False), 'b2b_salary_to'] = df.main_salary_to
        df.loc[df.main_employment_type.str.contains('permanent', na = False), 'permanent_salary_from'] = df.main_salary_from
        df.loc[df.main_employment_type.str.contains('permanent', na = False), 'permanent_salary_to'] = df.main_salary_to
        df.loc[df.main_employment_type.str.contains('mandate contract', na = False), 'mandate_contract_salary_from'] = df.main_salary_from
        df.loc[df.main_employment_type.str.contains('mandate contract', na = False), 'mandate_contract_salary_to'] = df.main_salary_to

        df.loc[df.secondary_employment_type.str.contains('b2b', na = False), 'b2b_salary_from'] = df.secondary_salary_from
        df.loc[df.secondary_employment_type.str.contains('b2b', na = False), 'b2b_salary_to'] = df.secondary_salary_to
        df.loc[df.secondary_employment_type.str.contains('permanent', na = False), 'permanent_salary_from'] = df.secondary_salary_from
        df.loc[df.secondary_employment_type.str.contains('permanent', na = False), 'permanent_salary_to'] = df.secondary_salary_to
        df.loc[df.secondary_employment_type.str.contains('mandate contract', na = False), 'permanent_salary_from'] = df.secondary_salary_from
        df.loc[df.secondary_employment_type.str.contains('mandate contract', na = False), 'permanent_salary_to'] = df.secondary_salary_to

        # Add counter
        df['counter'] = 1

        # Final columns order 
        df = df[['datestamp',
                'datestamp_year',
                'datestamp_month',
                'datestamp_week', 
                'title',
                'technology_area', 
                'workplace_type',
                'experience_level',
                'employment_type',
                'main_employment_type',
                'is_main_salary_flag',
                'main_salary_from',
                'main_salary_to',
                'is_secondary_employment_flag',
                'secondary_employment_type',
                'is_secondary_salary_flag',
                'secondary_salary_from',
                'secondary_salary_to',
                'salary_currency',
                'b2b_salary_from', 
                'b2b_salary_to', 
                'permanent_salary_from', 
                'permanent_salary_to', 
                'mandate_contract_salary_from', 
                'mandate_contract_salary_to',
                'skills_0_name',
                'skills_0_level',
                'skills_1_name',
                'skills_1_level',
                'skills_2_name',
                'skills_2_level',
                'counter'
                ]]

        return df
