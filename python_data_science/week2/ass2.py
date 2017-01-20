import pandas as pd

df = pd.read_csv('olympics.csv', index_col=0, skiprows=1)

for col in df.columns:
    if col[:2] == '01':
        df.rename(columns={col: 'Gold' + col[4:]}, inplace=True)
    if col[:2] == '02':
        df.rename(columns={col: 'Silver' + col[4:]}, inplace=True)
    if col[:2] == '03':
        df.rename(columns={col: 'Bronze' + col[4:]}, inplace=True)
    if col[:1] == 'N':
        df.rename(columns={col: '#' + col[1:]}, inplace=True)

names_ids = df.index.str.split('\s\(')  # split the index by '('

df.index = names_ids.str[0]  # the [0] element is the country name (new index)
df['ID'] = names_ids.str[1].str[:3]  # the [1] element is the abbreviation or ID (take first 3 characters from that)

df = df.drop('Totals')
df.head()

# Country with most gold medals
def q1():
    return df['Gold'].idxmax()

#Biggest difference between Summer Gold and Winter Gold
def q2():
    g = df['Gold']
    g1 = df['Gold.1']
    return abs(g-g1).idxmax()

#q2 but relative to total gold
def q3():
    has_golds = df[(df['Gold'] > 0) & (df['Gold.1'] > 0)]
    g = has_golds['Gold']
    g1 = has_golds['Gold.1']
    return (abs(g-g1)/(g+g1)).idxmax()

def q4():  
    g2 = df['Gold.2']
    s2 = df['Silver.2']
    b2 = df['Bronze.2']
    return pd.Series(g2*3 + s2*2 + b2, name='Points')

census_df = pd.read_csv('census.csv',  skiprows=0)

def q5():
    counties = census_df[census_df.SUMLEV == 50]
    res = pd.value_counts(counties.STNAME.values, sort=True)
    return res.idxmax()

def q6():
    counties = census_df[census_df.SUMLEV == 50]
    counties = counties.groupby('STNAME')['CENSUS2010POP']
    counties = counties.nlargest(3).reset_index()
    counties = counties.groupby('STNAME')['CENSUS2010POP'].sum()
    return list(counties.nlargest(3).index)

def q7():
    counties = census_df[census_df.SUMLEV == 50]
    c = ['POPESTIMATE2010',
               'POPESTIMATE2011',
               'POPESTIMATE2012',
               'POPESTIMATE2013',
               'POPESTIMATE2014',
               'POPESTIMATE2015']
    cs = counties.ix[:, c]
    max_year = cs.idxmax(axis=1)
    min_year = cs.idxmin(axis=1)
    diff = cs.lookup(cs.index, max_year) - cs.lookup(cs.index, min_year)
    row = diff.argmax()
    return counties.iloc[row]['CTYNAME']

def q8():
    counties = census_df[census_df.SUMLEV == 50]
    washingtons = counties[(counties['REGION'] <= 2) &
                 (counties['CTYNAME'].str.startswith('Washington'))]
    washingtons = washingtons[washingtons.POPESTIMATE2015 > washingtons.POPESTIMATE2014]
    return pd.DataFrame([washingtons.STNAME, washingtons.CTYNAME]).T

g = df['Gold']
g1 = df['Gold.1']

g2 = df['Gold.2']
s2 = df['Silver.2']
b2 = df['Bronze.2']
