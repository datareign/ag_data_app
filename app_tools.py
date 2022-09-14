import pandas as pd
import streamlit as st

def clear_text():
    st.session_state[0]=""
    
def mutate_string(s):
    s_last=s[-1]
    s_mutated=s.rstrip(s[-1])
    if s_last!='z':
        s_mutated=s_mutated+'z'
    else:
        s_mutated=s_mutated+'y'
    return s_mutated,s_last

def unmutate_string(s,s_last):
    s_unmutated=s.rstrip(s[-1])
    s_unmutated=s_unmutated+s_last
    return s_unmutated
    

def add_nutrients(fert_analysis,fert_name,fert_rate,rate_units):
    nutrients=['N','P','K','S','Mg','Ca','B','Cl','Mn','Fe','Cu','Zn','Mo']
    cols=['Product','Rate','App Units','N','P','K','S','Mg',
          'Ca','B','Cl','Mn','Fe','Cu','Zn','Mo']
    df=pd.DataFrame(columns=cols)
    df.loc[0,'Product']=fert_name
    df.loc[0,'Rate']=fert_rate
    df.loc[0,'App Units']=rate_units
    fert_analysis_row=fert_analysis[fert_analysis['fert_prod']==fert_name]
    assert len(fert_analysis_row)==1, 'There is a problem with fert analysis'
    #print(fert_analysis_row[0])
    if fert_analysis_row.iloc[0]['form']=='dry':
        if rate_units=='tons/acre':
            fert_rate=fert_rate*2000
        elif rate_units=='oz/acre':
            fert_rate=fert_rate/16
            
    if fert_analysis_row.iloc[0]['form']=='liquid':
        if rate_units=='pt/acre':
            fert_rate=fert_rate/8
        elif rate_units=='qt/acre':
            fert_rate=fert_rate/4
        elif rate_units=='oz/acre':
            fert_rate=fert_rate/128
    
    nutrient_dict={}
    for nutrient in nutrients:
        if fert_analysis_row.iloc[0]['form']=='dry':
            if fert_analysis_row.iloc[0][nutrient]!=None:
                nutrient_dict[nutrient]=fert_analysis_row.iloc[0][nutrient]*(fert_rate/100)
        if fert_analysis_row.iloc[0]['form']=='liquid':
            if fert_analysis_row.iloc[0][nutrient]!=None:
                density=fert_analysis_row.iloc[0]['liqDensity(lbs/gal)']
                fert_rate_1=fert_rate*density
                nutrient_dict[nutrient]=fert_analysis_row.iloc[0][nutrient]*(fert_rate_1/100)
        
    for k,v in nutrient_dict.items():
        if v>0:
            df.loc[0,k]=v
        else:
            df.loc[0,k]=0
    return df