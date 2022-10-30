# from sqlalchemy import create_engine
import mysql.connector
import pandas as pd
import streamlit as st
import plotly.express as px
from plotly.subplots import make_subplots
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

class dashboard:
    @st.experimental_memo
    def __init__(_self):
        # _self.user = st.secrets['user']
        # _self.password = st.secrets['password']
        # _self.host = st.secrets['host']
        # _self.port = st.secrets['port']
        _self.db_name = st.secrets['db_name']        
        _self.final_table_name = st.secrets['final_table']
        _self.datestamp_column_name = 'datestamp'
        # _self.engine = create_engine(f'mysql+mysqldb://{_self.user}:{_self.password}@{_self.host}:{_self.port}/{_self.db_name}')
        # _self.mysql_connection = _self.engine.connect()
        _self.mysql_connection = mysql.connector.connect(**st.secrets['mysql'])
    
    # Get date range for dataset
    @st.experimental_memo
    def get_date_range(_self, 
                       range = 90):
        result = _self.mysql_connection.execute(f"""
                                            SELECT DATE_ADD(MAX({_self.datestamp_column_name}), INTERVAL -{str(range)} DAY) AS min_date,
                                                   MAX({_self.datestamp_column_name}) AS max_date
                                            FROM {_self.db_name}.{_self.final_table_name}
                                            """)
        date_range = result.fetchall()
        date_range = date_range[0].values()

        return date_range

    # Get max date range for dataset
    @st.experimental_memo
    def get_max_date_range(_self):
        result = _self.mysql_connection.execute(f"""
                                            SELECT MIN({_self.datestamp_column_name}) AS min_date,
                                                   MAX({_self.datestamp_column_name}) AS max_date
                                            FROM {_self.db_name}.{_self.final_table_name}
                                            """)
        date_range = result.fetchall()
        date_range = date_range[0].values()

        return date_range

    # Create data range filter
    def create_data_range_filter(_self,
                                 key, 
                                 range = 90, 
                                 label = 'Data range: '):
        date_range = _self.get_date_range(range = range)
        max_date_range = _self.get_max_date_range()
        help_message = f'Default period is {str(range)} days back from the latest available day in dataset. Minimum date value is ' + max_date_range[0].strftime('%d %b %Y')

        filter_date_range = st.date_input(label = label, 
                                value = date_range,
                                min_value = max_date_range[0],
                                max_value = max_date_range[1],
                                help = help_message,
                                key = key)

        return filter_date_range

    # Load data to dashboard
    @st.experimental_memo
    def load_data_to_dashboard(_self, 
                               start_date, 
                               end_date):
        df = pd.read_sql(f"""
                            SELECT * FROM {_self.db_name}.{_self.final_table_name}
                            WHERE {_self.datestamp_column_name} >= '{start_date}'
                            AND {_self.datestamp_column_name} <= '{end_date}'
                            """, con = _self.mysql_connection)
        
        return df
    
    # Create chart description
    @st.experimental_memo
    def create_chart_description(_self,
                                 title,
                                 description,
                                 title_format = '#####'):
        title = title_format + ' ' + title
        title_to_return = st.markdown(title)
        description_to_return = st.caption(description)

        return None

    # Create chart filter
    def create_chart_filter(_self,
                            key,
                            dataframe,
                            column_name,
                            filter_name,
                            all,
                            index,
                            drop = False,
                            drop_value = None):
        list = dataframe[f'{column_name}'].drop_duplicates().to_list()
        list.sort()

        if all == True:
            list = ['all'] + list
        
        if drop == True:
            list = [x for x in list if drop_value not in x]
            list.sort()

        filter = st.selectbox(label = filter_name,
                              options = list,
                              index = list.index(f'{index}'),
                              key = key)

        return filter

    # Create bar chart
    @st.experimental_memo
    def create_bar_chart(_self,
                         dataframe,
                         column_name,
                         counter,
                         orientation,
                         column_label,
                         counter_label,
                         ascending = True,
                         height = 700,
                         template = 'plotly_dark'
                         ):
        list_of_variables = [column_name, counter]
        
        if orientation == 'h':
            df_counter = dataframe[list_of_variables].groupby(by = list_of_variables[0]).count()
            df_share = df_counter/dataframe[list_of_variables[1]].sum()*100
            df_share = df_share.rename(columns = {list_of_variables[1]: 'percentage_share'})
            df_share['percentage_share'] = df_share['percentage_share'].round(1).astype('str') + '%'
            df_plot = df_counter.reset_index().merge(df_share.reset_index(), how = 'left', on = list_of_variables[0]).sort_values(by = list_of_variables[1], ascending = ascending)

            plot = px.bar(df_plot,
                        y = list_of_variables[0],
                        x = list_of_variables[1],
                        orientation = orientation,
                        custom_data = ['percentage_share'],
                        labels = {list_of_variables[0]: f'{column_label}',
                                  list_of_variables[1]: f'{counter_label}',
                                  'percentage_share': 'percentage share'},
                        height = height,
                        template = template)
            plot.update_traces(hovertemplate = f'{column_label}' + ': %{y} <br>' + f'{counter_label}' + ': %{x} <br>percentage share: %{customdata[0]}')
            plot.update_xaxes(range = [0, df_plot[list_of_variables[1]].max() + 100])

            plot_to_return = st.plotly_chart(plot, use_container_width = True)
        
        elif orientation == 'v':
            df_counter = dataframe[list_of_variables].groupby(by = list_of_variables[0]).count()
            df_share = df_counter/dataframe[list_of_variables[1]].sum()
            df_share = df_share.rename(columns = {list_of_variables[1]: 'percentage_share'})
            df_share['percentage_share'] = df_share['percentage_share'].round(2)
            df_plot = df_counter.reset_index().merge(df_share.reset_index(), how = 'left', on = list_of_variables[0]).sort_values(by = list_of_variables[0], ascending = ascending)

            plot = px.bar(df_plot,
                        y = 'percentage_share',
                        x = list_of_variables[0],
                        orientation = orientation,
                        custom_data = [list_of_variables[1]],
                        labels = {list_of_variables[0]: f'{column_label}',
                                  list_of_variables[1]: f'{counter_label}',
                                  'percentage_share': 'percentage share'},
                        height = height,
                        template = template)
            plot.update_traces(hovertemplate = f'{column_label}' + ': %{y} <br>' + f'{counter_label}' + ': %{x} <br>percentage share: %{customdata[0]}')
            plot.update_yaxes(range = [0, df_plot['percentage_share'].max() + 0.1], tickformat = ',.1%')

            plot_to_return = st.plotly_chart(plot, use_container_width = True)
        
        return None

    # Create pie chart
    @st.experimental_memo
    def create_pie_chart(_self,
                         dataframe,
                         column_name,
                         counter,
                         column_label,
                         counter_label,
                         height = 700,
                         template = 'plotly_dark'
                         ):
        list_of_variables = [column_name, counter]
        df_plot = dataframe[list_of_variables].groupby(by = list_of_variables[0]).count().reset_index()

        plot = px.pie(df_plot,
                      names = list_of_variables[0],
                      values = list_of_variables[1],
                      labels = {list_of_variables[0]: f'{column_label}',
                                list_of_variables[1]: f'{counter_label}'},
                      height = height,
                      template = template)
        plot_to_return = st.plotly_chart(plot, use_container_width = True)

        return None

    # Create an advanced box plot with two boxes per category
    @st.experimental_memo
    def create_advanced_box_plot(_self,
                                 dataframe,
                                 box1_column_name,
                                 box1_counter,
                                 box1_column_label,
                                 box1_counter_label,
                                 box2_column_name,
                                 box2_counter,
                                 box2_column_label,
                                 box2_counter_label,
                                 box1_points = 'outliers',
                                 box2_points = 'outliers',
                                 box1_template = 'plotly_dark',
                                 box2_template = 'ggplot2',
                                 plot_boxmode = 'group',
                                 plot_height = 700,
                                 plot_template = 'plotly_dark',
                                 plot_category_order = 'category ascending'                                 
                                 ):
        list_of_variables = [box1_column_name, box1_counter, box2_column_name, box2_counter]               
        plot = make_subplots(specs=[[{"secondary_y": True}]])
        
        box1 = px.box(dataframe,
                        x = list_of_variables[0],
                        y = list_of_variables[1],
                        points = box1_points,
                        template = box1_template)

        box1.update_traces(hovertemplate = f'{box1_column_label}' + ': %{x} <br>' + f'{box1_counter_label}' + ': %{y}')

        box2 = px.box(dataframe,
                        x = list_of_variables[2],
                        y = list_of_variables[3],
                        points = box2_points,
                        template = box2_template)

        box2.update_traces(yaxis = 'y2', hovertemplate = f'{box2_column_label}' + ': %{x} <br>' + f'{box2_counter_label}' + ': %{y}')

        plot.add_traces(box1.data + box2.data)

        plot.update_layout(boxmode = plot_boxmode,
                                        height = plot_height,
                                        template = plot_template)
        plot.layout.yaxis.title = f'{box1_counter_label}'
        plot.layout.yaxis2.title = f'{box2_counter_label}'
        plot.update_yaxes(range = [0, dataframe[(box2_counter)].max() + 1000])
        plot.update_xaxes(categoryorder = plot_category_order)

        plot_to_return = st.plotly_chart(plot, use_container_width = True)

        return None

    # Create a wordcloud
    @st.experimental_memo
    def create_wordcloud(_self,
                         dataframe,
                         column_names,
                         width = 1600,
                         height = 800,
                         background_color = 'black',
                         colormap = 'Blues',
                         max_words = 20,
                         min_font_size = 10):
        list = []
        for index in range(len(column_names)):
            list = list + dataframe[column_names[index]].tolist()
        
        dictionary = {}
        for element in list:
                if pd.isna(element) == True:
                        continue
                
                elif element in dictionary:
                        dictionary[element] += 1
                
                else:
                        dictionary.update({element: 1})

        dictionary_sorted = dict(sorted(dictionary.items(), key=lambda item: item[1], reverse = True))

        wordcloud = WordCloud(width = width, height = height,
                        background_color = background_color,
                        colormap = colormap,
                        max_words = max_words,
                        min_font_size = min_font_size).generate_from_frequencies(dictionary_sorted)
        
        return wordcloud

    # Plot a wordcloud
    def create_wordcloud_plot(_self,
                              wordcloud,
                              figsize = (20, 10),
                              facecolor = 'k'):
        fig, ax = plt.subplots(figsize = figsize, facecolor = facecolor)
        ax.imshow(wordcloud)
        plt.axis("off")
        plt.tight_layout(pad = 0)
        
        st.pyplot(fig)        

    # Function to export dataset as csv
    @st.experimental_memo
    def df_to_csv(_self, 
                  dataframe):
        
        return dataframe.to_csv().encode('utf-8')

    # Create a button to export dataset
    def export_csv_button(_self,
                          dataframe, 
                          label = 'Download table as csv',
                          file_name = 'job_offers.csv',
                          mime = 'text/csv'
                          ):
        button = st.download_button(
                        label = label,
                        data = dataframe,
                        file_name = file_name,
                        mime = mime
                        )
        
        return button
