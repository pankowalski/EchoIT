# Import libraries
import requests as rq
from pymongo import MongoClient
from sqlalchemy import create_engine
from datetime import date, timedelta
import pandas as pd
import numpy as np
from flatten_json import flatten

class ETL:
    def __init__(self, url, host, port, db_name, collection_name, mysql_user, mysql_password, mysql_port, staging_table_name, final_table_name):
        # Set up variables
        self.url = url
        self.yesterday_date = date.today() - timedelta(days = 1)
        
        self.host = host
        self.port = port
        self.db_name = db_name
        self.collection_name = collection_name

        self.client = MongoClient(host = self.host, port = self.port)
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]

        self.user = mysql_user
        self.password = mysql_password
        self.mysql_port = mysql_port

        self.engine = create_engine(f'mysql+mysqldb://{self.user}:{self.password}@{self.host}:{self.mysql_port}/{self.db_name}')
        
        self.mysql_connection = self.engine.connect()
        self.staging_table_name = staging_table_name
        self.final_table_name = final_table_name
    
    def close_db_connections(self):
        # Close mongo connection
        self.client.close()

        # CLose mysql connection
        self.mysql_connection.close()
        self.engine.dispose()

    def extract_data(self):
        # Get data from justjoin API
        url_content = rq.get(self.url)
        data = url_content.json()

        # Filter out yesterday's offers
        list_of_offers_from_yesterday = []
        for offer in data:
            if offer['published_at'][:10] == str(self.yesterday_date):
                list_of_offers_from_yesterday.append(offer)
            else:
                pass
        
        # Update mongodb database
        self.collection.insert_many(list_of_offers_from_yesterday)
    
    def update_staging_table(self):
        # Get data from mongodb database
        filter_query = {'published_at': {'$regex': str(self.yesterday_date)}}
        filter_columns = {
                    '_id': 0,
                    'street': 0,
                    'city': 0,
                    'country_code': 0,
                    'address_text': 0,
                    'company_name': 0,
                    'company_url': 0,
                    'company_size': 0,
                    'latitude': 0,
                    'longitude': 0,
                    'remote_interview': 0,
                    'open_to_hire_ukrainians': 0,
                    'id': 0,
                    'display_offer': 0,
                    'company_logo_url': 0,
                    'remote': 0,
                    'multilocation': 0,
                    'way_of_apply': 0
                    }
        list_of_offers = list(self.collection.find(filter_query, filter_columns))

        # Makes json flat
        dict_flattened_offers = [flatten(offer) for offer in list_of_offers]

        # Flattened df
        df = pd.DataFrame(dict_flattened_offers)

        # Only needed columns (Just to make sure and in case some new column I don't need would appear in the future)
        df = df[['published_at',
                'title', 
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

        # Load data to staging table
        df.to_sql(name = self.staging_table_name, if_exists = 'append', index = False, con = self.mysql_connection)

        # Remove duplicates
        self.mysql_connection.execute('SET SQL_SAFE_UPDATES = 0')
        self.mysql_connection.execute(f"""
                                        DELETE FROM {self.db_name}.{self.staging_table_name}
                                        WHERE ID NOT IN (
                                                SELECT IDtoDel FROM (
                                                        SELECT MIN(ID) as IDtoDel
                                                                FROM {self.db_name}.{self.staging_table_name}
                                                                GROUP BY title,
                                                                technology_area,
                                                                workplace_type,
                                                                experience_level,
                                                                main_employment_type,
                                                                main_salary_from,
                                                                main_salary_to,
                                                                salary_currency,
                                                                secondary_employment_type,
                                                                secondary_salary_from,
                                                                secondary_salary_to,
                                                                secondary_salary_currency,
                                                                skills_0_name,
                                                                skills_0_level,
                                                                skills_1_name,
                                                                skills_1_level,
                                                                skills_2_name,
                                                                skills_2_level
                                                    ) as t
                                                )
        """)

    def update_final_table(self):
        df = pd.read_sql(f"""
                            select * from {self.db_name}.{self.staging_table_name}
                            where datestamp = '{self.yesterday_date}'
        """, con = self.mysql_connection)

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

        # Load data to final table
        df.to_sql(name = self.final_table_name, if_exists = 'append', index = False, con = self.mysql_connection)
