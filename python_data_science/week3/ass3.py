import pandas as pd
import re

energy = pd.read_excel('energy_indicators.xls', skip_footer=38, skiprows=17)
energy = energy.drop(energy.columns[[0,1]], axis=1)
energy.columns = ['Country', 'Energy Supply', 'Energy Supply per Capita', '% Renewable']
energy['Energy Supply'] *= 10**6
replace = { "Republic of Korea": "South Korea",
            "United States of America": "United States",
            "United Kingdom of Great Britain and Northern Ireland": "United Kingdom",
            "China, Hong Kong Special Administrative Region": "Hong Kong"}
rgx = re.compile(r"\d+|\s?\(.+?\)")

energy.Country = energy.Country.apply(lambda x: rgx.sub('', x))
energy.Country = energy.Country.apply(lambda x: replace[x] if x in replace else x)

GDP = pd.read_csv('world_bank.csv', skiprows=4)
gdp_replace = { "Korea, Rep.": "South Korea", 
                "Iran, Islamic Rep.": "Iran",
                "Hong Kong SAR, China": "Hong Kong" }
GDP['Country Name'] = GDP['Country Name'].map(lambda x : gdp_replace[x] if x in gdp_replace else x)
GDP = GDP[['Country Name'] + list(GDP.columns[-10:])]
ScimEn = pd.read_excel('scimagojr-3.xlsx')

def q1():
    top_ScimEn = ScimEn[:15]
    df = pd.merge(top_ScimEn, energy, how='inner', left_on="Country", right_on='Country')
    df = pd.merge(df, GDP, how='inner', left_on="Country", right_on='Country Name')
    df = df.set_index('Country')
    df = df.drop('Country Name', axis=1)
    return df

def q2():
    sci = ScimEn.set_index("Country")
    en = energy.set_index("Country")
    gdp = GDP.set_index("Country Name")
    outer = sci.join(en.join(gdp, how='outer'), how='outer')
    inner = sci.join(en.join(gdp, how='inner'), how='inner')
    return outer.shape[0]-inner.shape[0]

def q3():
    top15 = q1()
    gdp = top15[top15.columns[-10:]]
    avg_gdp = gdp.mean(axis=1)
    avg_gdp.name = 'avgGDP'
    return avg_gdp.sort_values(ascending=False)
    
def q4():
    Top15 = q1()
    country = q3().index[5]
    gdps = Top15[Top15.index == country]
    gdps = gdps[gdps.columns[-10:]]
    return gdps.max(axis=1)-gdps.min(axis=1)

def q5():
    Top15 = q1()
    return Top15['Energy Supply per Capita'].mean()

def q6():
    Top15 = q1()
    ren = Top15['% Renewable']
    return (ren.idxmax(), ren.max())

def q7():
    Top15 = q1()
    ratio = Top15['Self-citations'] / Top15['Citations']
    return (ratio.idxmax(), ratio.max())

def q8():
    Top15 = q1()
    sup = Top15['Energy Supply']
    sup_cap = Top15['Energy Supply per Capita']
    pop = sup / sup_cap
    pop = pop.sort_values()
    return pop.index[-3]

def q9():
    Top15 = q1()
    es = Top15['Energy Supply per Capita'].astype(float)
    pop_est = Top15['Energy Supply'] / es

    citable_cap = Top15['Citable documents'] / pop_est
    citable_cap = citable_cap.astype(float)

    return citable_cap.corr(es)    
    

def q10():
    Top15 = q1()
    ren = Top15['% Renewable']
    med = ren.median()
    res = ren.apply(lambda x: int(x >= med))
    res.name = 'HighRenew'
    return res

ContinentDict  = {'China':'Asia', 
                  'United States':'North America', 
                  'Japan':'Asia', 
                  'United Kingdom':'Europe', 
                  'Russian Federation':'Europe', 
                  'Canada':'North America', 
                  'Germany':'Europe', 
                  'India':'Asia',
                  'France':'Europe', 
                  'South Korea':'Asia', 
                  'Italy':'Europe', 
                  'Spain':'Europe', 
                  'Iran':'Asia',
                  'Australia':'Australia', 
                  'Brazil':'South America'}

def q11():
    Top15 = q1()
    es = Top15['Energy Supply per Capita'].astype(float)
    pop = Top15['Energy Supply'] / es
    pop = pop.astype(float)
    continents = pop.index.map(lambda x: ContinentDict[x])
    df = pd.DataFrame()
    df['size'] = pop
    df['Continents'] = continents
    group = df.groupby('Continents')
    df = group.count()
    df['sum'] = group.sum()
    df['mean'] = group.mean()
    df['std'] = group.std()
    return df

def q12():
    Top15 = q1()
    Top15['Continent'] = Top15.index.map(lambda x: ContinentDict[x])
    Top15 = Top15.reset_index()
    df = Top15[['Continent', '% Renewable']]
    bins = pd.cut(df['% Renewable'], 5)
    df['bins'] = bins
    df = df.groupby(['Continent', 'bins']).count()
    df = df.dropna()
    return df['% Renewable']
