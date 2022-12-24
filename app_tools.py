import pandas as pd
import streamlit as st
from variables import *

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

def get_data(db,collection):
    ##TODO need to filter 'out aaaaaa_template'
    df_list=[]
    crop_refs=db.collection(collection)
    for doc in crop_refs.stream():
        df_list.append(pd.DataFrame(doc.to_dict(),index=[0]))
    df=pd.concat(df_list)
    return df

def add_nutrients(fert_analysis,fert_name,fert_rate,rate_units,crop_year):
    nutrients=['N','P','K','S','Mg','Ca','B','Cl','Mn','Fe','Cu','Zn','Mo']
    cols=['Product','Rate','App Units','Crop Year','N','P','K','S','Mg',
          'Ca','B','Cl','Mn','Fe','Cu','Zn','Mo']
    df=pd.DataFrame(columns=cols)
    df.loc[0,'Crop Year']=crop_year
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

def get_prod_summaries(i_df,i_client,i_year):
    i_df['total_prod']=i_df['rate'].astype(float)*i_df['acres'].astype(float)
    prod_df_cols=['client','farm','year','product','type',
                  'formulation','amount','units']
    prod_df=pd.DataFrame(columns=prod_df_cols)
    i=0
    for farm_name,farm_group in i_df.groupby(by='farm'):
        for form_name,form_group in farm_group.groupby(by='formulation'):
            for prod_name,prod_group in form_group.groupby(by='product'):
                for type_name,type_group in prod_group.groupby(by='type'):
                    for units_name,units_group in type_group.groupby(by='units'):
                        total_prod=units_group['total_prod'].sum()
                        if form_name=='dry':
                            units='pounds'
                            if units_name=='tons/acre':                                
                                total_prod=total_prod*2000
                            elif units_name=='oz/acre':
                                total_prod=total_prod/16
                        elif form_name=='liquid':
                            units='gallons'
                            if units_name=='pt/acre':
                                total_prod=total_prod/8
                            elif units_name=='qt/acre':
                                total_prod=total_prod/4
                            elif units_name=='oz/acre':
                                total_prod=total_prod/128
                        prod_df.loc[i,'client']=i_client
                        prod_df.loc[i,'farm']=farm_name
                        prod_df.loc[i,'year']=i_year
                        prod_df.loc[i,'product']=prod_name
                        prod_df.loc[i,'type']=type_name
                        prod_df.loc[i,'formulation']=form_name
                        prod_df.loc[i,'amount']=total_prod
                        prod_df.loc[i,'units']=units
                        i+=1
    prod_df.sort_values(by=['product','farm'],inplace=True)
    prod_df.reset_index(drop=True,inplace=True)
    return prod_df

def get_crop_summaries(c_df,c_client,c_year):
    crop_df_cols=['client','farm','year','crop','variety',
                  'acres']
    crop_df=pd.DataFrame(columns=crop_df_cols)
    i=0
    for farm_name,farm_group in c_df.groupby(by='farm'):
        for crop_name,crop_group in farm_group.groupby(by='crop'):
            for variety_name,variety_group in crop_group.groupby(by='variety'):
                crop_df.loc[i,'client']=c_client
                crop_df.loc[i,'farm']=farm_name
                crop_df.loc[i,'year']=c_year
                crop_df.loc[i,'crop']=crop_name
                crop_df.loc[i,'variety']=variety_name
                crop_df.loc[i,'acres']=variety_group['acres'].astype(float).sum()
                i+=1
                
    crop_df.sort_values(by=['farm','crop'],inplace=True)
    crop_df.reset_index(drop=True,inplace=True)
    return crop_df

def get_agrimet_daily_address(station,param,start,end):
    return f'{AGRIMET_BASE_DAILY_ADDRESS}{station} {param}&start={start}&end={end}&format=html'