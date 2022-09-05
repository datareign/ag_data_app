import streamlit as st
import pandas as pd
import numpy as np
import datetime

fields=pd.read_csv('data/fields.csv')
crops_variety=pd.read_csv('data/crops_variety.csv')
inputs=pd.read_csv('data/inputs.csv')
crop_assignments=pd.read_csv('data/crop_assignments.csv')
ca_i=len(crop_assignments)
years=[2022,2023]

st.title('ProGro Data Management System')
menu=['Crop Assignment','Inputs Logging']
choice=st.sidebar.selectbox('Menu',menu)

if choice=='Crop Assignment':
    now=datetime.datetime.utcnow()
    clients=np.sort(fields['Client'].unique())
    crops=np.sort(crops_variety['crop'].unique())
    
    st.subheader('Crop and Variety Assignment')
    with st.form(key='form0'):
        crop=st.selectbox('Crop',crops)
        client=st.selectbox('Client',clients)
        year=st.selectbox('Crop Year',years)
        submit_button=st.form_submit_button()
    
    with st.form(key='form1'):
        varieties=np.sort(crops_variety[crops_variety['crop']==crop]['variety'].unique())
        farms=np.sort(fields[fields['Client']==client]['Farm'].unique())

        variety=st.selectbox('Variety',varieties)
        farm=st.selectbox('Farm',farms)
        submit_button1=st.form_submit_button()
    
    with st.form(key='form2'):
        fields_sub=fields[fields['Client']==client]
        fields_sub=fields_sub[fields_sub['Farm']==farm]
        fields_list=np.sort(fields_sub['Field'].unique())
        fields_list=st.multiselect('Fields',fields_list)
        submit_button2=st.form_submit_button()
        
        for field in fields_list:
            field_row=fields_sub[fields_sub['Field']==field]
            assert len(field_row)==1, 'There is a duplicate field name for this farm'
            crop_assignments.loc[ca_i,'log_datetime']=now
            crop_assignments.loc[ca_i,'unq_fldid']=field_row.iloc[0]['unq_fldid']
            crop_assignments.loc[ca_i,'year']=year
            crop_assignments.loc[ca_i,'client']=client
            crop_assignments.loc[ca_i,'farm']=farm
            crop_assignments.loc[ca_i,'field']=field
            crop_assignments.loc[ca_i,'crop']=crop
            crop_assignments.loc[ca_i,'variety']=variety
            ca_i+=1
        
        crop_assignments.to_csv('data/crop_assignments.csv',index=False)
            
            
            
        
    
    
        
        
        
        
        
    
elif choice=='Inputs Logging':
    st.subheader('Inputs Logging')
    
