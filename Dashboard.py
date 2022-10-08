                                                                ### Preparation ###
# Import libraries
from PrepareData import *
from datetime import timedelta
import pandas as pd
import streamlit as st
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

# Set up wide mode 
st.set_page_config(page_title = 'EchoIT',
                  layout="wide")

# Function to get and prepare data
@st.experimental_memo
def data_for_dashboard():
        df = PrepareData().prepare_data()
        return df

# Function for exporting csv raw data
@st.experimental_memo
def df_to_csv(df):
        return df.to_csv().encode('utf-8')

                                                                ### Streamlit app ###

                                                                ## Intro ##

# try:
        # Create main df
df_main = data_for_dashboard()
# except:
#         st.info('Server does not respond. Please reload')

# Title
st.title('EchoIT')
st.markdown('''###### Welcome to EchoIT dashboard. Main purpose of this app is to have an overview of IT job marketplace in Poland as of now. Commercial reports are cool, however they share one disadvantage - they refer to the past (past year, usually). It's a bit late if you want to know, for example what are the current wages or most desired technologies and skills. An here it is, when EchoIT enters the stage. EchoIT is based on the latest, daily refreshed data provided from one of the most popular IT job marketplace in Poland - [justjoin.it](https://justjoin.it/?tab=with-salary)''')
st.markdown('#')
st.markdown('''##### Below you can find several plots that show aggregated data in various dimensions for a selected period. Check this out.''')


                                                                ## Global filters ##
# Create a filter date range
filter_date_range = st.date_input(label = 'Date range: ', 
                                value = (df_main['datestamp'].max() - timedelta(days = 30), df_main['datestamp'].max()),
                                min_value = df_main['datestamp'].min(),
                                max_value = df_main['datestamp'].max(),
                                help = 'Default period is 30 days back from the latest available day in dataset. Minimum date value is 27-jul-2022.',
                                key = 0)

st.markdown('#')

if len(filter_date_range) == 2:

                                                                        ## Main ## 
        ## First sector
        with st.container():
                col1, col2 = st.columns(2)

                with col1:

                        ## Technology area split chart ##
                        with st.container():

                                st.markdown('##### Technology area')
                                st.caption('Chart below shows distribution of offers per technology area for a given period and seniority level(s)')

                                # Create seniority level filter
                                list_seniority_level = df_main['experience_level'].drop_duplicates().to_list()
                                list_seniority_level.sort()
                                list_seniority_level = ['all'] + list_seniority_level
                                filter_seniority_level = st.selectbox('Seniority level:', 
                                                                list_seniority_level,
                                                                index = list_seniority_level.index('all'),
                                                                key = 1)

                                # Create filtered df
                                if filter_seniority_level == 'all':
                                        df_technology_popularity = df_main[(df_main.datestamp >= filter_date_range[0]) &
                                                                        (df_main.datestamp <= filter_date_range[1]) 
                                                                        ].reset_index()
                                else:
                                        df_technology_popularity = df_main[(df_main.datestamp >= filter_date_range[0]) &
                                                                        (df_main.datestamp <= filter_date_range[1]) &
                                                                        (df_main.experience_level == filter_seniority_level)
                                                                        ].reset_index()

                                # Create chart of technology split
                                df_counter_technology_popularity = df_technology_popularity[['technology_area', 'counter']].groupby(by = 'technology_area').count()
                                df_share_technology_popularity = df_counter_technology_popularity/df_technology_popularity['counter'].sum()*100
                                df_share_technology_popularity = df_share_technology_popularity.rename(columns = {'counter': 'percentage_share'})
                                df_share_technology_popularity['percentage_share'] = df_share_technology_popularity['percentage_share'].round(1).astype('str') + '%'
                                df_plot_technology_popularity = df_counter_technology_popularity.reset_index().merge(df_share_technology_popularity.reset_index(), how = 'left', on = 'technology_area').sort_values(by = 'counter', ascending = True)

                                plot_technology_popularity = px.bar(df_plot_technology_popularity,
                                                                y = 'technology_area',
                                                                x = 'counter',
                                                                orientation = 'h',
                                                                custom_data = ['percentage_share'],
                                                                labels = {'technology_area': 'technology area',
                                                                                'counter': 'number of offers',
                                                                                'percentage_share': 'percentage share'},
                                                                height = 700,
                                                                template = 'plotly_dark')
                                plot_technology_popularity.update_traces(hovertemplate = 'technology area: %{y} <br>number of offers: %{x} <br>percentage share: %{customdata[0]}')
                                plot_technology_popularity.update_xaxes(range = [0, df_plot_technology_popularity['counter'].max() + 100])
                                st.plotly_chart(plot_technology_popularity, use_container_width = True)

                with col2:

                        ## Seniority level split chart ##
                        with st.container():

                                st.markdown('##### Seniority level')
                                st.caption('Chart below shows distribution of offers per seniority level for a given period and technology area(s)')

                                # Create technology area filter
                                list_technology_area = df_main['technology_area'].drop_duplicates().to_list()
                                list_technology_area.sort()
                                list_technology_area = ['all'] + list_technology_area
                                filter_technology_area = st.selectbox('Technology area:', 
                                                                list_technology_area,
                                                                index = list_technology_area.index('all'),
                                                                key = 2)

                                # Create filtered df
                                if filter_technology_area == 'all':
                                        df_seniority_level = df_main[(df_main.datestamp >= filter_date_range[0]) &
                                                                (df_main.datestamp <= filter_date_range[1]) 
                                                                ].reset_index()
                                else:
                                        df_seniority_level = df_main[(df_main.datestamp >= filter_date_range[0]) &
                                                                (df_main.datestamp <= filter_date_range[1]) &
                                                                (df_main.technology_area == filter_technology_area)
                                                                ].reset_index()

                                # Create chart of seniority split
                                df_counter_seniority_level = df_seniority_level[['experience_level', 'counter']].groupby(by = 'experience_level').count()
                                df_share_seniority_level = df_counter_seniority_level/df_seniority_level['counter'].sum()
                                df_share_seniority_level = df_share_seniority_level.rename(columns = {'counter': 'percentage_share'})
                                df_share_seniority_level['percentage_share'] = df_share_seniority_level['percentage_share'].round(2)
                                df_plot_seniority_level = df_counter_seniority_level.reset_index().merge(df_share_seniority_level.reset_index(), how = 'left', on = 'experience_level').sort_values(by = 'experience_level', ascending = True)

                                plot_seniority_level = px.bar(df_plot_seniority_level,
                                                                y = 'percentage_share',
                                                                x = 'experience_level',
                                                                orientation = 'v',
                                                                custom_data = ['counter'],
                                                                labels = {'experience_level': 'seniority level',
                                                                                'counter': 'number of offers',
                                                                                'percentage_share': 'percentage share'},
                                                                height = 700,
                                                                template = 'plotly_dark')
                                plot_seniority_level.update_traces(hovertemplate = 'seniority level: %{x} <br>percentage share: %{y} <br>number of offers: %{customdata[0]}')
                                plot_seniority_level.update_yaxes(range = [0, df_plot_seniority_level['percentage_share'].max() + 0.1], tickformat = ',.1%')
                                st.plotly_chart(plot_seniority_level, use_container_width = True)

        st.markdown('###')

        ## Second sector
        with st.container():

                ## Sector filters
                # Create technology area filter
                list_technology_area = df_main['technology_area'].drop_duplicates().to_list()
                list_technology_area.sort()
                list_technology_area = ['all'] + list_technology_area
                filter_technology_area = st.selectbox('Technology area:', 
                                                list_technology_area,
                                                index = list_technology_area.index('all'),
                                                key = 3)

                # Create seniority level filter
                list_seniority_level = df_main['experience_level'].drop_duplicates().to_list()
                list_seniority_level.sort()
                list_seniority_level = ['all'] + list_seniority_level
                filter_seniority_level = st.selectbox('Seniority level:', 
                                                list_seniority_level,
                                                index = list_seniority_level.index('all'),
                                                key = 4)

                # Create filtered df
                if filter_technology_area == 'all' and filter_seniority_level == 'all':
                        df_second_sector = df_main[(df_main.datestamp >= filter_date_range[0]) &
                                                (df_main.datestamp <= filter_date_range[1]) 
                                                ].reset_index()
                elif filter_technology_area != 'all' and filter_seniority_level != 'all':
                        df_second_sector = df_main[(df_main.datestamp >= filter_date_range[0]) &
                                                (df_main.datestamp <= filter_date_range[1]) &
                                                (df_main.technology_area == filter_technology_area) &
                                                (df_main.experience_level == filter_seniority_level)
                                                ].reset_index()
                elif filter_technology_area == 'all' and filter_seniority_level != 'all':
                        df_second_sector = df_main[(df_main.datestamp >= filter_date_range[0]) &
                                                (df_main.datestamp <= filter_date_range[1]) &
                                                (df_main.experience_level == filter_seniority_level)
                                                ].reset_index()
                elif filter_technology_area != 'all' and filter_seniority_level == 'all':
                        df_second_sector = df_main[(df_main.datestamp >= filter_date_range[0]) &
                                                (df_main.datestamp <= filter_date_range[1]) &
                                                (df_main.technology_area == filter_technology_area)
                                                ].reset_index()

                st.markdown('###')

                col1, col2 = st.columns(2)

                with col1:
                        
                        ## Employment split chart ##
                        with st.container():

                                st.markdown('##### Employment type')
                                st.caption('Chart below shows distribution of offers per employment type for a given period, technology area(s) and seniority level(s)')
                                
                                # Create chart of employment type split
                                df_counter_employment_type = df_second_sector[['employment_type', 'counter']].groupby(by = 'employment_type').count()
                                df_share_employment_type = df_counter_employment_type/df_second_sector['counter'].sum()*100
                                df_share_employment_type = df_share_employment_type.rename(columns = {'counter': 'percentage_share'})
                                df_share_employment_type['percentage_share'] = df_share_employment_type['percentage_share'].round(1).astype('str') + '%'
                                df_plot_employment_type = df_counter_employment_type.reset_index().merge(df_share_employment_type.reset_index(), how = 'left', on = 'employment_type').sort_values(by = 'counter', ascending = True)

                                plot_employment_type = px.bar(df_plot_employment_type,
                                                                y = 'employment_type',
                                                                x = 'counter',
                                                                orientation = 'h',
                                                                custom_data = ['percentage_share'],
                                                                labels = {'employment_type': 'employment type',
                                                                                'counter': 'number of offers',
                                                                                'percentage_share': 'percentage share'},
                                                                height = 500,
                                                                template = 'plotly_dark')
                                plot_employment_type.update_traces(hovertemplate = 'employment type: %{y} <br>number of offers: %{x} <br>percentage share: %{customdata[0]}')
                                plot_employment_type.update_xaxes(range = [0, df_plot_employment_type['counter'].max() + 100])
                                st.plotly_chart(plot_employment_type, use_container_width = True)

                        ## Salary flag chart ##
                        with st.container():

                                st.markdown('##### Salary flag')
                                st.caption('Chart below shows distribution of offers with/without specified salary range for a given period, technology area(s) and seniority level(s)')
                                
                                # Create chart of salary flag split
                                df_plot_is_main_salary_flag = df_second_sector[['is_main_salary_flag', 'counter']].groupby(by = 'is_main_salary_flag').count().reset_index()

                                plot_is_main_salary_flag = px.pie(df_plot_is_main_salary_flag,
                                                                names = 'is_main_salary_flag',
                                                                values = 'counter',
                                                                labels = {'is_main_salary_flag': 'salary flag',
                                                                                'counter': 'number of offers'},
                                                                height = 500,
                                                                template = 'plotly_dark')
                                st.plotly_chart(plot_is_main_salary_flag, use_container_width = True)
                        
                with col2:

                        ## Workplace type chart ##
                        with st.container():

                                st.markdown('##### Workplace type')
                                st.caption('Chart below shows distribution of offers per workplace type for a given period, technology area(s) and seniority level(s)')

                                # Create chart of workplace type split
                                df_counter_workplace_type = df_second_sector[['workplace_type', 'counter']].groupby(by = 'workplace_type').count()
                                df_share_workplace_type = df_counter_workplace_type/df_second_sector['counter'].sum()
                                df_share_workplace_type = df_share_workplace_type.rename(columns = {'counter': 'percentage_share'})
                                df_share_workplace_type['percentage_share'] = df_share_workplace_type['percentage_share'].round(2)
                                df_plot_workplace_type = df_counter_workplace_type.reset_index().merge(df_share_workplace_type.reset_index(), how = 'left', on = 'workplace_type').sort_values(by = 'workplace_type', ascending = False)

                                plot_workplace_type = px.bar(df_plot_workplace_type,
                                                                y = 'percentage_share',
                                                                x = 'workplace_type',
                                                                orientation = 'v',
                                                                custom_data = ['counter'],
                                                                labels = {'workplace_type': 'workplace type',
                                                                                'counter': 'number of offers',
                                                                                'percentage_share': 'percentage share'},
                                                                height = 500,
                                                                template = 'plotly_dark')
                                plot_workplace_type.update_traces(hovertemplate = 'workplace type: %{x} <br>percentage share: %{y} <br>number of offers: %{customdata[0]}')
                                plot_workplace_type.update_yaxes(range = [0, df_plot_workplace_type['percentage_share'].max() + 0.1], tickformat = ',.1%')
                                st.plotly_chart(plot_workplace_type, use_container_width = True)

                        ## Currency split chart ##
                        with st.container():

                                st.markdown('##### Currency flag')
                                st.caption('Chart below shows distribution of offers per salary currency for a given period, technology area(s) and seniority level(s)')

                                # Create chart of currency split
                                df_plot_salary_currency = df_second_sector[['salary_currency', 'counter']].groupby(by = 'salary_currency').count().reset_index()

                                plot_salary_currency = px.pie(df_plot_salary_currency,
                                                                names = 'salary_currency',
                                                                values = 'counter',
                                                                labels = {'salary_currency': 'salary currency',
                                                                                'counter': 'number of offers'},
                                                                height = 500,
                                                                template = 'plotly_dark')
                                st.plotly_chart(plot_salary_currency, use_container_width = True)

        st.markdown('###')

#         ## Third sector
#         with st.container():

#                 st.markdown('##### Salary distribution')
#                 st.caption('Chart below shows distribution of salary range per technology area for a given period, seniority level, employment type and salary currency')

#                 df_third_sector = df_main[(df_main.is_main_salary_flag == 'Yes') &
#                                         (df_main.datestamp >= filter_date_range[0]) &
#                                         (df_main.datestamp <= filter_date_range[1])]

#                 ## Sector filters
#                 # Create seniority level filter
#                 list_seniority_level = df_third_sector['experience_level'].drop_duplicates().to_list()
#                 list_seniority_level.sort()
#                 filter_seniority_level = st.selectbox('Seniority level:', 
#                                                 list_seniority_level,
#                                                 index = list_seniority_level.index('mid'),
#                                                 key = 5)
                
#                 df_third_sector = df_third_sector[df_third_sector.experience_level == filter_seniority_level]

#                 # Create employment type filter
#                 list_employment_type = df_third_sector['employment_type'].drop_duplicates().to_list()
#                 list_employment_type = [x for x in list_employment_type if '&' not in x]
#                 list_employment_type.sort()
#                 filter_employment_type = st.selectbox('Employment type:', 
#                                                 list_employment_type,
#                                                 index = list_employment_type.index('b2b'),
#                                                 key = 6)
                
#                 df_third_sector = df_third_sector[df_third_sector.employment_type == filter_employment_type]

#                 # Create salary currency filter
#                 list_salary_currency = df_third_sector['salary_currency'].drop_duplicates().to_list()
#                 list_salary_currency.sort()
#                 filter_salary_currency = st.selectbox('Salary currency:', 
#                                                 list_salary_currency,
#                                                 index = list_salary_currency.index('pln'),
#                                                 key = 7)

#                 df_third_sector = df_third_sector[df_third_sector.salary_currency == filter_salary_currency]

#                 # Create box plot to visualise salary distribution per technology area
#                 with st.container():
#                         plot_salary_group = make_subplots(specs=[[{"secondary_y": True}]])
                        
#                         plot_salary_group_salary_from = px.box(
#                                                                 df_third_sector,
#                                                                 x = 'technology_area',
#                                                                 y = (filter_employment_type + '_salary_from'),
#                                                                 points = 'outliers',
#                                                                 template = 'plotly_dark'
#                                                         )

#                         plot_salary_group_salary_from.update_traces(hovertemplate = 'technology area: %{x} <br>bottom salary range: %{y}')

#                         plot_salary_group_salary_to = px.box(
#                                                                 df_third_sector,
#                                                                 x = 'technology_area',
#                                                                 y = (filter_employment_type + '_salary_to'),
#                                                                 points = 'outliers',
#                                                                 template = 'ggplot2'
#                                                         )

#                         plot_salary_group_salary_to.update_traces(yaxis = 'y2',
#                                                                         hovertemplate = 'technology area: %{x} <br>top salary range: %{y}')
                        
#                         # plot_salary_group_main_salary_to.update_traces(fillcolor = 'green') Quite useful when you want to setup color for a trace but I prefer setting up different templates for each plot/subplot
                        
#                         plot_salary_group.add_traces(plot_salary_group_salary_from.data + 
#                                                         plot_salary_group_salary_to.data)                                   
#                         plot_salary_group.update_layout(boxmode = 'group',
#                                                         height = 700,
#                                                         template = 'plotly_dark')
#                         plot_salary_group.layout.yaxis.title = 'bottom salary range'
#                         plot_salary_group.layout.yaxis2.title = 'top salary range'
#                         plot_salary_group.update_yaxes(range = [0, df_third_sector[(filter_employment_type + '_salary_to')].max() + 1000])
#                         plot_salary_group.update_xaxes(categoryorder = 'category ascending')

#                         st.plotly_chart(plot_salary_group, use_container_width = True)

#         st.markdown('###')

#         ## Fourth sector
#         with st.container():

#                 ## Sector filters
#                 # Create technology area filter
#                 list_technology_area = df_main['technology_area'].drop_duplicates().to_list()
#                 list_technology_area.sort()
#                 list_technology_area = ['all'] + list_technology_area
#                 filter_technology_area = st.selectbox('Technology area:', 
#                                                 list_technology_area,
#                                                 index = list_technology_area.index('all'),
#                                                 key = 8)

#                 # Create seniority level filter
#                 list_seniority_level = df_main['experience_level'].drop_duplicates().to_list()
#                 list_seniority_level.sort()
#                 list_seniority_level = ['all'] + list_seniority_level
#                 filter_seniority_level = st.selectbox('Seniority level:', 
#                                                 list_seniority_level,
#                                                 index = list_seniority_level.index('all'),
#                                                 key = 9)

#                 # Create filtered df
#                 if filter_technology_area == 'all' and filter_seniority_level == 'all':
#                         df_fourth_sector = df_main[(df_main.datestamp >= filter_date_range[0]) &
#                                                 (df_main.datestamp <= filter_date_range[1]) 
#                                                 ].reset_index()
#                 elif filter_technology_area != 'all' and filter_seniority_level != 'all':
#                         df_fourth_sector = df_main[(df_main.datestamp >= filter_date_range[0]) &
#                                                 (df_main.datestamp <= filter_date_range[1]) &
#                                                 (df_main.technology_area == filter_technology_area) &
#                                                 (df_main.experience_level == filter_seniority_level)
#                                                 ].reset_index()
#                 elif filter_technology_area == 'all' and filter_seniority_level != 'all':
#                         df_fourth_sector = df_main[(df_main.datestamp >= filter_date_range[0]) &
#                                                 (df_main.datestamp <= filter_date_range[1]) &
#                                                 (df_main.experience_level == filter_seniority_level)
#                                                 ].reset_index()
#                 elif filter_technology_area != 'all' and filter_seniority_level == 'all':
#                         df_fourth_sector = df_main[(df_main.datestamp >= filter_date_range[0]) &
#                                                 (df_main.datestamp <= filter_date_range[1]) &
#                                                 (df_main.technology_area == filter_technology_area)
#                                                 ].reset_index()

#                 st.markdown('###')

#                 col1, col2 = st.columns(2)
                
#                 with col1:
#                         ## Create a wordcloud for most frequent skills
#                         with st.container():

#                                 st.markdown('##### Top technologies')
#                                 st.caption('Wordcloud below shows 20 most frequent technologies for a given period, technology area(s) and seniority level(s)')

#                                 # List all skills
#                                 list_skills = df_fourth_sector.skills_0_name.tolist() + df_fourth_sector.skills_1_name.tolist() + df_fourth_sector.skills_2_name.tolist()

#                                 # Create a dictionary with a frequency per skill counted
#                                 dictionary_skills = {}
#                                 for element in list_skills:
#                                         if pd.isna(element) == True:
#                                                 continue
                                        
#                                         elif element in dictionary_skills:
#                                                 dictionary_skills[element] += 1
                                        
#                                         else:
#                                                 dictionary_skills.update({element: 1})
                                
#                                 # Sort values
#                                 dictionary_skills_sorted = dict(sorted(dictionary_skills.items(), key=lambda item: item[1], reverse = True))
#                                 # list_skills_sorted = sorted(dictionary_skills, key = dictionary_skills.get, reverse = True)

#                                 # Create wordcloud object
#                                 wordcloud = WordCloud(width = 1600, height = 800,
#                                                 background_color ='black',
#                                                 colormap = 'Blues',
#                                                 max_words = 20,
#                                                 min_font_size = 10).generate_from_frequencies(dictionary_skills_sorted)
                                
#                                 # Plot the WordCloud image                      
#                                 fig, ax = plt.subplots(figsize = (20, 10), facecolor = 'k')
#                                 ax.imshow(wordcloud)
#                                 plt.axis("off")
#                                 plt.tight_layout(pad = 0)
#                                 st.pyplot(fig)
                                
#                 with col2:
#                         ## Create a wordcloud for most frequent job titles
#                         with st.container():

#                                 st.markdown('##### Top job titles')
#                                 st.caption('Wordcloud below shows 20 most frequent job titles for a given period, technology area(s) and seniority level(s)')

#                                 # List all job titles
#                                 list_job_titles = df_fourth_sector.title.tolist()

#                                 # Create a dictionary with a frequency per title counted
#                                 dictionary_job_titles = {}
#                                 for element in list_job_titles:
#                                         if pd.isna(element) == True:
#                                                 continue
                                        
#                                         elif element in dictionary_job_titles:
#                                                 dictionary_job_titles[element] += 1
                                        
#                                         else:
#                                                 dictionary_job_titles.update({element: 1})
                                
#                                 # Sort values
#                                 dictionary_job_titles_sorted = dict(sorted(dictionary_job_titles.items(), key=lambda item: item[1], reverse = True))
#                                 # list_job_titles_sorted = sorted(dictionary_job_titles, key = dictionary_job_titles.get, reverse = True)

#                                 # Create wordcloud object
#                                 wordcloud = WordCloud(width = 1600, height = 800,
#                                                 background_color ='black',
#                                                 colormap = 'Blues',
#                                                 max_words = 20,
#                                                 min_font_size = 10).generate_from_frequencies(dictionary_job_titles_sorted)
                                
#                                 # Plot the WordCloud image                      
#                                 fig, ax = plt.subplots(figsize = (20, 10), facecolor = 'k')
#                                 ax.imshow(wordcloud)
#                                 plt.axis("off")
#                                 plt.tight_layout(pad = 0)
#                                 st.pyplot(fig)                      

#         st.markdown('#')

#         # Fifth sector
#         with st.container():

#                 st.markdown('##### Raw data')
#                 st.caption('Table below contains raw data for a given period')

#                 # Create and show raw data set filtered by data range
#                 df_raw_data = df_main[(df_main.datestamp >= filter_date_range[0]) &
#                                         (df_main.datestamp <= filter_date_range[1])
#                                         ].reset_index()

#                 df_raw_data

#                 # Export csv button
#                 df_raw_data_export = df_to_csv(df_raw_data)

#                 st.download_button(
#                 label = 'Download table as csv',
#                 data = df_raw_data_export,
#                 file_name = 'df.csv',
#                 mime = 'text/csv'
#                 )

# else:
#         st.info('Choose date range')




















