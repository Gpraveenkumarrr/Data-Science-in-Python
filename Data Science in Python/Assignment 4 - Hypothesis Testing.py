
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[166]:

import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[167]:

# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 
          'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 
          'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 
          'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 
          'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 
          'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 
          'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 
          'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 
          'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 
          'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 
          'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 
          'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[122]:

import re

def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''
    data_file = pd.read_table('university_towns.txt', header=None, dtype=str)
    university_towns = []
    state = []
    town = []
    for i in range(0, len(data_file)):
        if 'edit' in data_file.iloc[i, :][0]:
            state = data_file.iloc[i, :][0].strip('[edit]')
        else:
            town = data_file.iloc[i, :][0]
            town1 = re.sub(r'\s\([^)]*\)', '', town)
            town2 = re.sub(r'\[[^)]*\]', '', town1)
            university_towns.append([state, town2])
    u_towns = pd.DataFrame(university_towns, columns=["State", "RegionName"])   
    
    return u_towns

get_list_of_university_towns()


# In[168]:

def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    gdp = pd.read_excel('gdplev.xls', skiprows=5).drop([0,1], axis=0)
    start = gdp[gdp['Unnamed: 4'].str.contains('2000q1')].index[0]
    gdp = gdp.loc[start:, ['Unnamed: 4', 'GDP in billions of chained 2009 dollars.1']]
    gdp.reset_index(drop=True, inplace=True)
    gdp.columns = ['Quarters', 'GDP']
    
    recession_start = []
    for i in range(1, len(gdp)-1):
        if (gdp.iloc[i-1, 1] > gdp.iloc[i, 1]) & (gdp.iloc[i, 1] > gdp.iloc[i+1, 1]):
            recession_start.append(gdp.iloc[i, 0])
        
    return recession_start[0]

get_recession_start()


# In[169]:

def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
    gdp = pd.read_excel('gdplev.xls', skiprows=5).drop([0,1], axis=0)
    start = gdp[gdp['Unnamed: 4'].str.contains('2000q1')].index[0]
    gdp = gdp.loc[start:, ['Unnamed: 4', 'GDP in billions of chained 2009 dollars.1']]
    gdp.reset_index(drop=True, inplace=True)
    gdp.columns = ['Quarters', 'GDP']
    
    recession_end = []
    for i in range(3, len(gdp)-1):
        if ((gdp.iloc[i-3, 1] > gdp.iloc[i-2, 1]) & (gdp.iloc[i-2, 1] > gdp.iloc[i-1, 1]) 
            & (gdp.iloc[i-1, 1] < gdp.iloc[i, 1]) & (gdp.iloc[i, 1] < gdp.iloc[i+1, 1])):
                recession_end.append(gdp.iloc[i+1, 0])
    return recession_end[0]

get_recession_end()


# In[8]:

def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    gdp = pd.read_excel('gdplev.xls', skiprows=5).drop([0,1], axis=0)
    start = gdp[gdp['Unnamed: 4'].str.contains('2000q1')].index[0]
    gdp = gdp.loc[start:, ['Unnamed: 4', 'GDP in billions of chained 2009 dollars.1']]
    gdp.reset_index(drop=True, inplace=True)
    gdp.columns = ['Quarters', 'GDP']
    
    recession_bottom = []
    for i in range(3, len(gdp)-1):
        if ((gdp.iloc[i-3, 1] > gdp.iloc[i-2, 1]) & (gdp.iloc[i-2, 1] > gdp.iloc[i-1, 1]) 
            & (gdp.iloc[i-1, 1] < gdp.iloc[i, 1]) & (gdp.iloc[i, 1] < gdp.iloc[i+1, 1])):
                recession_bottom.append(gdp.iloc[i-1, 0])
    return recession_bottom[0]   
    
    
get_recession_bottom()


# In[170]:

def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    df = pd.read_csv('City_Zhvi_AllHomes.csv')
    df_date = df.loc[:, '2000-01':'2016-08']
    df_date.columns = pd.to_datetime(df_date.columns)
    df_date_res = df_date.resample('QS', axis=1).mean()
    
    year = df_date_res.columns.year.astype(str)
    year_q = []
    for i in year:
        year_plus_q = i + 'q'
        year_q.append(year_plus_q)
        
    cols = []
    count = 1
    for j in year_q:
        if count < 4:
            year_q_quarter = j + str(count)
            cols.append(year_q_quarter)
            count += 1
        else:
            year_q_quarter = j + str(count)
            cols.append(year_q_quarter)
            count = 1
    df_date_res.columns = cols
    
    #quarter = df_date_res.columns.quarter.astype(object)
    #df_date_res.columns = [df_date_res.columns.year]
    states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 
          'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 
          'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 
          'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 
          'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 
          'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 
          'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 
          'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 
          'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 
          'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 
          'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 
          'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}
    df['State'] = df['State'].replace(states)
    
    h_data = df[["State","RegionName"]].merge(df_date_res, left_index=True, right_index=True).set_index(["State","RegionName"])
    
    return h_data

convert_housing_data_to_quarters()


# In[165]:

def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    
    house_data = convert_housing_data_to_quarters()
    house_data['diff'] = house_data['2008q3'] - house_data['2009q2']
    towns = get_list_of_university_towns()
    all_recession_data = house_data.loc[:, ['2008q3', '2009q2', 'diff']].reset_index()
    
    hp = pd.merge(towns, all_recession_data, how='right', left_on=['State', 'RegionName'], 
                                right_on=['State', 'RegionName']).dropna()
    u_hp = pd.merge(towns, all_recession_data, how='left', left_on=['State', 'RegionName'], 
                                right_on=['State', 'RegionName']).dropna()
    def compare_better():
        if hp['diff'].mean() < u_hp['diff'].mean():
            better = 'non-university town'
        else:
            better ='university town'
        return better
    
    def test_different():
        if p < 0.01:
            different = True
        else: 
            different = False
        return different
    
    stat, p = ttest_ind(hp['diff'], u_hp['diff'])
    
    return (test_different(), p, compare_better())
run_ttest()


# In[ ]:



