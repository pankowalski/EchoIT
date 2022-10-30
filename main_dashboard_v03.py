                                                                ### Preparation ###
# Import libraries
from dashboard_v03 import *

# Set up wide mode 
st.set_page_config(page_title = 'EchoIT',
                  layout="wide")

                                                                ### Streamlit app ###

                                                                ## Intro ##
        
# Title
st.title('EchoIT')
st.markdown('''###### Welcome to EchoIT dashboard. Main purpose of this app is to have an overview of IT job marketplace in Poland as of now. Commercial reports are cool, however they share one disadvantage - they refer to the past (past year, usually). It's a bit late if you want to know, for example what are the current wages or most desired technologies and skills. An that's where EchoIT enters the stage. EchoIT is based on the latest, daily refreshed data provided by one of the most popular IT job marketplace in Poland - [justjoin.it](https://justjoin.it/?tab=with-salary)''')
st.markdown('#')
st.markdown('''##### Below you can find several plots that show aggregated data in various dimensions for a selected period. Check this out.''')


                                                                ## Global ##

# Create an instance of class dashboard
dashboard = dashboard()

# Create a filter date range
filter_date_range = dashboard.create_data_range_filter(key = 0)

st.markdown('#')

if len(filter_date_range) == 2:

        df_main = dashboard.load_data_to_dashboard(filter_date_range[0],
                                                   filter_date_range[1])

                                                                ## Main ## 
        ## First sector
        with st.container():
                col1, col2 = st.columns(2)

                with col1:

                        ## Technology area split chart ##
                        with st.container():

                                list_column_names = ['technology_area', 
                                                     'experience_level', 
                                                     'counter']
                                
                                # Chart title
                                technology_area_split_chart_title = dashboard.create_chart_description(title = 'Technology area',
                                                                                                       description = 'Chart below shows distribution of offers per technology area for a given period and seniority level(s)')

                                # Create seniority level filter
                                filter_seniority_level = dashboard.create_chart_filter(key = 1,
                                                                                       dataframe = df_main,
                                                                                       column_name = list_column_names[1],
                                                                                       filter_name = 'Seniority level:',
                                                                                       all = True,
                                                                                       index = 'all')

                                # Create filtered df
                                if filter_seniority_level == 'all':
                                        df_technology_popularity = df_main[list_column_names]
                                else:
                                        df_technology_popularity = df_main[df_main.experience_level == filter_seniority_level].reset_index()

                                # Create chart of technology area split
                                technology_area_split_chart = dashboard.create_bar_chart(dataframe = df_technology_popularity,
                                                                                         column_name = list_column_names[0],
                                                                                         counter = list_column_names[2],
                                                                                         orientation = 'h',
                                                                                         column_label = 'technology area',
                                                                                         counter_label = 'number of offers')

                with col2:

                        ## Seniority level split chart ##
                        with st.container():

                                # Chart title
                                seniority_level_split_chart_title = dashboard.create_chart_description(title = 'Seniority level',
                                                                                                       description = 'Chart below shows distribution of offers per seniority level for a given period and technology area(s)')

                                # Create technology area filter
                                filter_technology_area = dashboard.create_chart_filter(key = 2,
                                                                                       dataframe = df_main,
                                                                                       column_name = list_column_names[0],
                                                                                       filter_name = 'Technology area:',
                                                                                       all = True,
                                                                                       index = 'all')

                                # Create filtered df
                                if filter_technology_area == 'all':
                                        df_seniority_level = df_main[list_column_names]
                                else:
                                        df_seniority_level = df_main[df_main.technology_area == filter_technology_area].reset_index()

                                # Create chart of seniority level split
                                seniority_level_split_chart = dashboard.create_bar_chart(dataframe = df_seniority_level,
                                                                                         column_name = list_column_names[1],
                                                                                         counter = list_column_names[2],
                                                                                         orientation = 'v',
                                                                                         column_label = 'seniority level',
                                                                                         counter_label = 'number of offers')

        st.markdown('###')

        ## Second sector
        with st.container():

                list_column_names = ['technology_area', 
                                     'experience_level', 
                                     'employment_type',
                                     'workplace_type', 
                                     'is_main_salary_flag',
                                     'salary_currency', 
                                     'counter']

                ## Sector filters
                # Create technology area filter
                filter_technology_area = dashboard.create_chart_filter(key = 3,
                                                                       dataframe = df_main,
                                                                       column_name = list_column_names[0],
                                                                       filter_name = 'Technology area:',
                                                                       all = True,
                                                                       index = 'all')

                # Create seniority level filter
                filter_seniority_level = dashboard.create_chart_filter(key = 4,
                                                                       dataframe = df_main,
                                                                       column_name = list_column_names[1],
                                                                       filter_name = 'Seniority level:',
                                                                       all = True,
                                                                       index = 'all')

                # Create filtered df
                if filter_technology_area == 'all' and filter_seniority_level == 'all':
                        df_second_sector = df_main[list_column_names]
                
                elif filter_technology_area != 'all' and filter_seniority_level != 'all':
                        df_second_sector = (df_main[list_column_names])[((df_main[list_column_names]).technology_area == filter_technology_area) &
                                                                          ((df_main[list_column_names]).experience_level == filter_seniority_level)].reset_index()
                
                elif filter_technology_area == 'all' and filter_seniority_level != 'all':
                        df_second_sector = (df_main[list_column_names])[((df_main[list_column_names]).experience_level == filter_seniority_level)].reset_index()
                
                elif filter_technology_area != 'all' and filter_seniority_level == 'all':
                        df_second_sector = (df_main[list_column_names])[((df_main[list_column_names]).technology_area == filter_technology_area)].reset_index()

                st.markdown('###')

                col1, col2 = st.columns(2)

                with col1:
                        
                        ## Employment split chart ##
                        with st.container():

                                # Chart title
                                employment_type_split_chart_title = dashboard.create_chart_description(title = 'Employment type',
                                                                                                       description = 'Chart below shows distribution of offers per employment type for a given period, technology area(s) and seniority level(s)')
                        
                                # Create chart of employment type split
                                employment_type_split_chart = dashboard.create_bar_chart(dataframe = df_second_sector,
                                                                                         column_name = list_column_names[2],
                                                                                         counter = list_column_names[6],
                                                                                         orientation = 'h',
                                                                                         column_label = 'employment type',
                                                                                         counter_label = 'number of offers',
                                                                                         height = 500)

                        ## Salary flag chart ##
                        with st.container():

                                # Chart title
                                salary_flag_split_chart_title = dashboard.create_chart_description(title = 'Salary flag',
                                                                                                   description = 'Chart below shows distribution of offers with/without specified salary range for a given period, technology area(s) and seniority level(s)')
    
                                # Create chart of salary flag split
                                salary_flag_split_chart = dashboard.create_pie_chart(dataframe = df_second_sector,
                                                                                     column_name = list_column_names[4],
                                                                                     counter = list_column_names[6],
                                                                                     column_label = 'salary flag',
                                                                                     counter_label = 'number of offers',
                                                                                     height = 500)
                        
                with col2:

                        ## Workplace type chart ##
                        with st.container():

                                # Chart title
                                workplace_type_split_chart_title = dashboard.create_chart_description(title = 'Workplace type',
                                                                                                      description = 'Chart below shows distribution of offers per workplace type for a given period, technology area(s) and seniority level(s)')

                                # Create chart of workplace type split
                                workplace_type_split_chart = dashboard.create_bar_chart(dataframe = df_second_sector,
                                                                                        column_name = list_column_names[3],
                                                                                        counter = list_column_names[6],
                                                                                        orientation = 'v',
                                                                                        column_label = 'workplace type',
                                                                                        counter_label = 'number of offers',
                                                                                        height = 500,
                                                                                        ascending = False)                                

                        ## Currency split chart ##
                        with st.container():

                                # Chart title
                                currency_split_chart_title = dashboard.create_chart_description(title = 'Currency flag',
                                                                                                description = 'Chart below shows distribution of offers per salary currency for a given period, technology area(s) and seniority level(s)')

                                # Create chart of currency split
                                currency_split_chart = dashboard.create_pie_chart(dataframe = df_second_sector,
                                                                                  column_name = list_column_names[5],
                                                                                  counter = list_column_names[6],
                                                                                  column_label = 'salary flag',
                                                                                  counter_label = 'number of offers',
                                                                                  height = 500)

        st.markdown('###')

        ## Third sector
        with st.container():

                list_column_names = ['technology_area',
                                     'experience_level',
                                     'employment_type',
                                     'is_main_salary_flag',
                                     'salary_currency',
                                     'permanent_salary_from',
                                     'permanent_salary_to',
                                     'b2b_salary_from',
                                     'b2b_salary_to',
                                     'mandate_contract_salary_from',
                                     'mandate_contract_salary_to']

                # Chart title
                salary_distribution_chart_title = dashboard.create_chart_description(title = 'Salary distribution',
                                                                                     description = 'Chart below shows distribution of salary range per technology area for a given period, seniority level, employment type and salary currency')

                df_third_sector = (df_main[list_column_names])[((df_main[list_column_names])[list_column_names[3]] == 'Yes')]

                ## Sector filters
                # Create seniority level filter
                filter_seniority_level = dashboard.create_chart_filter(key = 5,
                                                                        dataframe = df_third_sector,
                                                                        column_name = list_column_names[1],
                                                                        filter_name = 'Seniority level:',
                                                                        all = False,
                                                                        index = 'mid')
                
                filter_employment_type = dashboard.create_chart_filter(key = 6,
                                                                        dataframe = df_third_sector,
                                                                        column_name = list_column_names[2],
                                                                        filter_name = 'Employment type:',
                                                                        all = False,
                                                                        index = 'permanent',
                                                                        drop = True,
                                                                        drop_value = '&')

                filter_salary_currency = dashboard.create_chart_filter(key = 7,
                                                                        dataframe = df_third_sector,
                                                                        column_name = list_column_names[4],
                                                                        filter_name = 'Salary currency:',
                                                                        all = False,
                                                                        index = 'pln')                
     
                df_third_sector = (df_main[list_column_names])[((df_main[list_column_names])[list_column_names[1]] == filter_seniority_level) &
                                                               ((df_main[list_column_names])[list_column_names[2]] == filter_employment_type) &
                                                               ((df_main[list_column_names])[list_column_names[4]] == filter_salary_currency)]

                # Create box plot to visualise salary distribution per technology area
                with st.container():

                        # Chart title
                        salary_distribution_chart = dashboard.create_advanced_box_plot(dataframe = df_third_sector,
                                                                                        box1_column_name = list_column_names[0],
                                                                                        box1_counter = filter_employment_type + '_salary_from',
                                                                                        box1_column_label = 'technology area',
                                                                                        box1_counter_label = 'bottom salary range',
                                                                                        box2_column_name = list_column_names[0],
                                                                                        box2_counter = filter_employment_type + '_salary_to',
                                                                                        box2_column_label = 'technology area',
                                                                                        box2_counter_label = 'top salary range')

        st.markdown('###')

        ## Fourth sector
        with st.container():

                list_column_names = ['title',
                                     'technology_area', 
                                     'experience_level',
                                     'skills_0_name',
                                     'skills_1_name',
                                     'skills_2_name']

                ## Sector filters
                # Create technology area filter
                filter_technology_area = dashboard.create_chart_filter(key = 8,
                                                                       dataframe = df_main,
                                                                       column_name = list_column_names[1],
                                                                       filter_name = 'Technology area:',
                                                                       all = True,
                                                                       index = 'all')

                # Create seniority level filter
                filter_seniority_level = dashboard.create_chart_filter(key = 9,
                                                                       dataframe = df_main,
                                                                       column_name = list_column_names[2],
                                                                       filter_name = 'Seniority level:',
                                                                       all = True,
                                                                       index = 'all')

                # Create filtered df
                if filter_technology_area == 'all' and filter_seniority_level == 'all':
                        df_fourth_sector = df_main[list_column_names]

                elif filter_technology_area != 'all' and filter_seniority_level != 'all':
                        df_fourth_sector = (df_main[list_column_names])[((df_main[list_column_names])[list_column_names[1]] == filter_technology_area) &
                                                                        ((df_main[list_column_names])[list_column_names[2]] == filter_seniority_level)].reset_index()

                elif filter_technology_area == 'all' and filter_seniority_level != 'all':
                        df_fourth_sector = (df_main[list_column_names])[((df_main[list_column_names])[list_column_names[2]] == filter_seniority_level)].reset_index()

                elif filter_technology_area != 'all' and filter_seniority_level == 'all':
                        df_fourth_sector = (df_main[list_column_names])[((df_main[list_column_names])[list_column_names[1]] == filter_technology_area)].reset_index()

                st.markdown('###')

                col1, col2 = st.columns(2)
                
                with col1:
                        ## Create a wordcloud for most frequent skills
                        with st.container():

                                # Chart title
                                wordcloud_skills_chart_title = dashboard.create_chart_description(title = 'Top technologies',
                                                                                                  description = 'Wordcloud below shows 20 most frequent technologies for a given period, technology area(s) and seniority level(s)')
                                
                                wordcloud_skills = dashboard.create_wordcloud(dataframe = df_fourth_sector,
                                                                              column_names = list_column_names[3:6])
                                
                                wordcloud_skills_chart = dashboard.create_wordcloud_plot(wordcloud = wordcloud_skills) 

                                
                with col2:
                        ## Create a wordcloud for most frequent job titles
                        with st.container():

                                # Chart title
                                wordcloud_job_titles_chart_title = dashboard.create_chart_description(title = 'Top job titles',
                                                                                                      description = 'Wordcloud below shows 20 most frequent job titles for a given period, technology area(s) and seniority level(s)')

                                wordcloud_job_titles = dashboard.create_wordcloud(dataframe = df_fourth_sector,
                                                                                  column_names = [list_column_names[0]])

                                wordcloud_job_titles_chart = dashboard.create_wordcloud_plot(wordcloud = wordcloud_job_titles) 

        st.markdown('#')

        # Fifth sector
        with st.container():

                # Chart title
                raw_data_title = dashboard.create_chart_description(title = 'Raw data',
                                                                    description = 'Table below contains raw data for a given period')
                
                df_main

                # Export csv button
                df_export = dashboard.df_to_csv(df_main)
                button_export = dashboard.export_csv_button(dataframe = df_export)

else:
        st.info('Choose date range')

st.markdown('#')
st.markdown('''###### Author: [Patryk Kowalski](https://www.linkedin.com/in/patryk-kowalski-81a648103/)''')




















