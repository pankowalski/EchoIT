# EchoIT
Main purpose of this app is to have an overview of IT job marketplace in Poland as of now - what are the current wages or most desired technologies, skills, etc.

Link to dashboard: https://echoit.streamlit.app/

Dashboard is fully automated and deployed (using this repo) on streamlit cloud. Data is refreshed on a daily basis. 

dashboard_vXX.py - defines dashboard class and its methods (DB connection, elements such filters, charts, etc.)

main_dashboard_vXX.py - main file where app is written

ETL folder contains files used in ETL process on server side. Documentation purposes. 
