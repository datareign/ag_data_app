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

key_dict=json.loads(st.secrets['textkey'])
creds=service_account.Credentials.from_service_account_info(key_dict)
db=firestore.Client(credentials=creds,project='agdata-f5a79')

#doc_ref=db.collection('crop_assignments').document('test0')
#doc=doc_ref.get()
#st.write(doc.id)
#st.write(doc.to_dict())


years=[2022,2023]

st.title('ProGro Data Management System')
menu=['View Crop Assignments','Assign Crops','Inputs Logging']
choice=st.sidebar.selectbox('Menu',menu)

if choice=='View Crop Assignments':
    year=st.selectbox('Crop Year',years)
    df_list=[]
    crop_refs=db.collection('crop_assignments')
    for doc in crop_refs.stream():
        df_list.append(pd.DataFrame(doc.to_dict(),index=[0]))
    df=pd.concat(df_list)
    df=df[df['crop_year']==int(year)]
    st.write(df[['client','farm','field','crop_year','acres','crop','variety']])

elif choice=='Assign Crops':
    now=datetime.datetime.utcnow()
    clients=np.sort(fields['Client'].unique())
    crops=np.sort(crops_variety['crop'].unique())
    
    st.subheader('Crop and Variety Assignment')
    crop=st.selectbox('Crop',crops,0)
    varieties=np.sort(crops_variety[crops_variety['crop']==crop]['variety'].unique())
    variety=st.selectbox('Variety',varieties)
    
    year=st.selectbox('Crop Year',years)
    client=st.selectbox('Client',clients)
    farms=np.sort(fields[fields['Client']==client]['Farm'].unique())
    farm=st.selectbox('Farm',farms)

    fields_sub=fields[fields['Client']==client]
    fields_sub=fields_sub[fields_sub['Farm']==farm]
    fields_list=np.sort(fields_sub['Field'].unique())
    fields_list=st.multiselect('Fields',fields_list)
    
    if st.button('SUBMIT'):
        for field in fields_list:
            field_row=fields_sub[fields_sub['Field']==field]
            assert len(field_row)==1, 'There is a duplicate field name for this farm'
            unq_fldid=field_row.iloc[0]['unq_fldid']
            acres=field_row.iloc[0]['acres']
            doc_ref=db.collection('crop_assignments').document(f'{int(unq_fldid)}_{int(year)}')
            doc_ref.set({'log_datetime':now,
                         'unq_fldid':int(unq_fldid),
                         'crop_year':int(year),
                         'client':client,
                         'farm':farm,
                         'field':field,
                         'acres':float(acres),
                         'crop':crop,
                         'variety':variety})
            
    
elif choice=='Inputs Logging':
    st.subheader('Inputs Logging')
    
