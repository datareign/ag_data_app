import streamlit as st
import pandas as pd
import numpy as np
import datetime
from google.cloud import firestore
from google.oauth2 import service_account
import json

fields=pd.read_csv('data/fields.csv')
crops_variety=pd.read_csv('data/crops_variety.csv')
inputs=pd.read_csv('data/inputs.csv')
#crop_assignments=pd.read_csv('data/crop_assignments.csv')
#ca_i=len(crop_assignments)

key_dict=json.loads(st.secrets['textkey'])
creds=service_account.Credentials.from_service_account_info(key_dict)
db=firestore.Client(credentials=creds,project='agdata-f5a79')

doc_ref=db.collection('crop_assignments').document('test0')
doc=doc_ref.get()
st.write(doc.id)
st.write(doc.to_dict())


years=[2022,2023]

st.title('ProGro Data Management System')
menu=['Crop Assignment','Inputs Logging']
choice=st.sidebar.selectbox('Menu',menu)

if choice=='Crop Assignment':
    st.session_state.counter=0
    now=datetime.datetime.utcnow()
    clients=np.sort(fields['Client'].unique())
    crops=np.sort(crops_variety['crop'].unique())
    
    st.subheader('Crop and Variety Assignment')
    #with st.form(key='form0'):
    crop=st.selectbox('Crop',crops,0)
    varieties=np.sort(crops_variety[crops_variety['crop']==crop]['variety'].unique())
    variety=st.selectbox('Variety',varieties)
    
    year=st.selectbox('Crop Year',years)
    client=st.selectbox('Client',clients)
    farms=np.sort(fields[fields['Client']==client]['Farm'].unique())
    farm=st.selectbox('Farm',farms)
    #submit_button1=st.form_submit_button()

#with st.form(key='form2'):
    fields_sub=fields[fields['Client']==client]
    fields_sub=fields_sub[fields_sub['Farm']==farm]
    fields_list=np.sort(fields_sub['Field'].unique())
    fields_list=st.multiselect('Fields',fields_list)
    #submit_button2=st.form_submit_button()
    
    #if st.button('SUBMIT'):
        #for field in fields_list:
        #    field_row=fields_sub[fields_sub['Field']==field]
        #    assert len(field_row)==1, 'There is a duplicate field name for this farm'
        #    crop_assignments.loc[ca_i,'log_datetime']=now
        #    crop_assignments.loc[ca_i,'unq_fldid']=field_row.iloc[0]['unq_fldid']
        #    crop_assignments.loc[ca_i,'year']=year
        #    crop_assignments.loc[ca_i,'client']=client
        #    crop_assignments.loc[ca_i,'farm']=farm
        #    crop_assignments.loc[ca_i,'field']=field
        #    crop_assignments.loc[ca_i,'crop']=crop
        #    crop_assignments.loc[ca_i,'variety']=variety
        #    ca_i+=1
        
        #crop_assignments['year']=crop_assignments['year'].astype(int)
        #crop_assignments['unq_fldid']=crop_assignments['unq_fldid'].astype(int)
        #crop_assignments.to_csv('data/crop_assignments.csv',index=False)
        #st.write('The crop was assigned to the fields')
        #st.write(st.session_state.keys())
        #st.write(crop_assignments[['log_datetime','client','farm'
        #                           ,'field','crop','variety']])
        #st.session_state.counter=0
        #st.experimental_rerun() 
        
        

    
elif choice=='Inputs Logging':
    st.subheader('Inputs Logging')
    
