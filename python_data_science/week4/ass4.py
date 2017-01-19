import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
import re

states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}
gdplev = pd.read_excel('gdplev.xls', skiprows=219, parse_cols= [4, 6], names=['Quarter', 'GDP'])
gdplev['Diff'] = gdplev.GDP.diff()

def get_list_of_university_towns():
    data = []
    state_re = re.compile(r"(\w+)(\[edit\]$)")
    with open('university_towns.txt') as towns:
        for line in towns:
            if state_re.match(line):
                state = line[:-7]
            else:
                parenthesis = line.find('(')
                if parenthesis != -1:
                    line = line[:parenthesis]
                town = line.strip()
                data.append([state, town])
    return pd.DataFrame(data, columns=['State', 'RegionName'])


def get_recession_start():
    start = gdplev[(gdplev.Diff < 0) & (gdplev.Diff.shift(-1) < 0)].iloc[0].Quarter
    return start
    
def get_recession_end():
    start = gdplev[(gdplev.Diff < 0) & (gdplev.Diff.shift(-1) < 0)].index[0]
    end = (gdplev[start:].where(gdplev.Diff > 0).dropna().index[0]) - 1
    return gdplev.loc[end].Quarter

def get_recession_bottom():
    start = gdplev[(gdplev.Diff < 0) & (gdplev.Diff.shift(-1) < 0)].index[0]
    end = (gdplev[start:].where(gdplev.Diff > 0).dropna().index[0]) - 1
    recessions = gdplev[start:end+1]
    return gdplev.loc[recessions.GDP.idxmin()].Quarter

def convert_housing_data_to_quarters():
    house = pd.read_csv('City_Zhvi_AllHomes.csv')
    house = house[list(house.columns[[1,2]]) + list(house.columns[51:])]
    house.State = house.State.map(states)
    house = house.set_index(['State', 'RegionName'])
    house = house.sort_index()
    house = house[house.columns[:-2]]
    quarters = list(gdplev.Quarter) + ['2016q3']
    house.columns = range(house.shape[1])
    house.columns = house.columns.map(lambda x: quarters[x//3])
    return house.groupby(by=house.columns, axis=1).mean()

def run_ttest():
    p_req = 0.01
    
    universities = get_list_of_university_towns().set_index(['State', 'RegionName'])
    rstart = get_recession_start()
    rbottom = get_recession_bottom()
    hp = convert_housing_data_to_quarters()
    hp_ratio = (hp[rstart] / hp[rbottom])
    hp_ratio.name = 'PriceRatio'
    hp_ratio = hp_ratio.dropna()
    uni_ratio = universities.join(hp_ratio, how='inner')
    non_uni_ratio = hp_ratio.drop(hp_ratio.index[hp_ratio.index.isin(uni_ratio.index)])

    ur_mean = uni_ratio.mean()[0]
    nur_mean = non_uni_ratio.mean()
    return ttest_ind(non_uni_ratio, uni_ratio)
    t, p = ttest_ind(non_uni_ratio, uni_ratio)
    str_res = ['university town', 'non-university town']
    return (p[0] < p_req, p[0], str_res[ur_mean < nur_mean])
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

