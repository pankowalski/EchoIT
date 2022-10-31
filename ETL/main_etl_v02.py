from ETL_v01 import *

etl = ETL()

etl.extract_data()

etl.update_staging_table()

etl.update_final_table()

etl.close_db_connections()
