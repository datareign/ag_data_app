import streamlit as st
import pandas as pd
import numpy as np
import datetime
from google.cloud import firestore
from google.oauth2 import service_account
import json
import app_tools as tools
from styles import *
import uuid
import base64

fields=pd.read_csv('data/fields.csv')
crops_variety=pd.read_csv('data/crops_variety.csv')
inputs=pd.read_csv('data/inputs.csv')
fert_analysis=pd.read_table('data/fert_analysis.txt')

key_dict=json.loads(st.secrets['textkey'])
creds=service_account.Credentials.from_service_account_info(key_dict)
db=firestore.Client(credentials=creds,project='agdata-f5a79')

@st.cache(allow_output_mutation=True)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    .stApp {
      background-image: url("data:image/png;base64,%s");
      background-size: cover;
    }
    </style>
    ''' % bin_str
    
    st.markdown(page_bg_img, unsafe_allow_html=True)
    return


@st.experimental_memo
def get_crop_data(_dbase,collection):
    df_list=[]
    crop_refs=_dbase.collection(collection)
    for doc in crop_refs.stream():
        df_list.append(pd.DataFrame(doc.to_dict(),index=[0]))
    df=pd.concat(df_list)
    return df

@st.experimental_memo
def get_input_data(_dbase,collection):
    df_list=[]
    crop_refs=_dbase.collection(collection)
    for doc in crop_refs.stream():
        df_list.append(pd.DataFrame(doc.to_dict(),index=[0]))
    df=pd.concat(df_list)
    return df

set_png_as_page_bg('data/background3.jpg')

years=[2022,2023]

st.title('ProGro Data Management System')
menu=['View Crop Assignments','View Input Assignments',
      'View Applied Nutrients',
      'Assign Crops','Assign Inputs']
st.sidebar.image('data/progro1.png',use_column_width=True)
choice=st.sidebar.selectbox('Options',menu)

if choice=='View Crop Assignments':
    st.subheader('View Crop Assignments')
    st.write('Select by Grower')
    col0,col1=st.columns(2) 
    with col0:
        year=st.selectbox('Crop Year',years)
        clients=np.sort(fields['Client'].unique())
    with col1:
        client=st.selectbox('Client',clients)    
        
    df=get_crop_data(db,'crop_assignments')
    
    df=df[df['crop_year']==int(year)]
    df['crop_year']=df['crop_year'].astype(int)
    df=df[df['client']==client]
    
    if len(df)>0:
        df.sort_values(by=['field','farm','client'],inplace=True)
        df.reset_index(drop=True,inplace=True)
        df=df[['client','farm','field','crop_year',
               'acres','crop','variety','uuid']]
        #st.table(df.style.format(CROP_STYLE))
        st.dataframe(df.style.format(CROP_STYLE))
        st.write('If you wish to delete a record, copy the UUID and paste into the input cell below.')
        doc_del=st.text_input('Delete Record',key=0)
        if len(doc_del)>0:
            db.collection('crop_assignments').document(doc_del).delete()
            st.button('Click to Delete',on_click=tools.clear_text)
        
        csv=df.to_csv().encode('utf-8')
        if st.download_button(label='Download Data',data=csv,
                              file_name='Crop_Assignments.csv',
                              mime='text/csv'):
            st.write('Your dataset has downloaded.')
        
    else:
        st.write('There are no crop assignments for this grower.')
    
    
if choice=='View Input Assignments':
    st.subheader('View Input Assignments')
    st.write('Select by Grower')
    col0,col1=st.columns(2)    
    with col0:
        year=st.selectbox('Crop Year',years)
        clients=np.sort(fields['Client'].unique())
    with col1:
        client=st.selectbox('Client',clients)
    
    df=get_input_data(db,'crop_inputs_prod')
    
    df=df[df['crop_year']==int(year)]
    df['crop_year']=df['crop_year'].astype(int)
    df=df[df['client']==client]
    
    if len(df)>0:
        df.sort_values(by=['field','farm','client'],inplace=True)
        df.reset_index(drop=True,inplace=True)
        df=df[['client','farm','field','crop_year','acres',
               'product','type','formulation','rate','units',
               'uuid','notes']]
        #st.table(df.style.format(INPUT_STYLE))
        st.dataframe(df.style.format(INPUT_STYLE))
        
        st.write('If you wish to delete a record, copy the UUID and paste into the input cell below.')
        doc_del=st.text_input('Delete Record',key=0)
        if len(doc_del)>0:
            db.collection('crop_inputs').document(doc_del).delete()
            st.button('Click to Delete',on_click=tools.clear_text)
        csv=df.to_csv().encode('utf-8')
        if st.download_button(label='Download Data',data=csv,
                              file_name='Input_Assignments.csv',
                              mime='text/csv'):
            st.write('Your dataset has downloaded.')
    else:
        st.write('There are no inputs for this client')
    
if choice=='View Applied Nutrients':
    st.subheader('View Applied Nutrients')
    col0,col1=st.columns(2)
    with col0:
        year=st.selectbox('Crop Year',years)
        clients=np.sort(fields['Client'].unique())
        client=st.selectbox('Client',clients)
    with col1:
        farms=np.sort(fields[fields['Client']==client]['Farm'].unique())
        farm=st.selectbox('Farm',farms)
        fields_sub=fields[fields['Client']==client]
        fields_sub=fields_sub[fields_sub['Farm']==farm]
        fields_list=np.sort(fields_sub['Field'].unique())
        field=st.selectbox('Field',fields_list)

    df=get_input_data(db,'crop_inputs_prod')

    df=df[df['crop_year']==int(year)]
    df['crop_year']=df['crop_year'].astype(int)
    df=df[df['client']==client]
    df=df[df['farm']==farm]
    df=df[df['field']==field]
    df=df[df['type']=='fertilizer']
        
    if len(df)>0:    
        nutrient_dfs=[]
        for index,row in df.iterrows():
            nutrient_dfs.append(tools.add_nutrients(fert_analysis,
                                                    row['product'],
                                                    row['rate'],
                                                    row['units'],
                                                    int(year)))
        nutrient_df=pd.concat(nutrient_dfs)
        #nutrient_df['Crop Year']=nutrient_df['Crop Year'].astype(int)
        nutrient_df.reset_index(drop=True,inplace=True)
        
        nutrients=['N','P','K','S','Mg','Ca','B','Cl','Mn','Fe','Cu','Zn','Mo']
        if len(nutrient_df)>1:
            nutrient_df.loc[len(nutrient_df),nutrients]=nutrient_df.sum(axis=0)
            nutrient_df.loc[len(nutrient_df)-1,'Product']='Totals'
            #nutrient_df.loc[len(nutrient_df)-1,'Rate']=0
            #nutrient_df.loc[len(nutrient_df)-1,'App Units']=''
        
        #st.table(nutrient_df.style.format(NUTRIENT_STYLE))
        st.dataframe(nutrient_df.style.format(NUTRIENT_STYLE))
        csv=nutrient_df.to_csv().encode('utf-8')
        if st.download_button(label='Download Data',data=csv,
                              file_name='Applied_Nutrients.csv',
                              mime='text/csv'):
            st.write('Your dataset has downloaded.')     
    else:
        st.write('There are no fertilizer records for this field')
    
elif choice=='Assign Crops':
    st.subheader('Assign Crops')
    now=datetime.datetime.utcnow()
    clients=np.sort(fields['Client'].unique())
    crops=np.sort(crops_variety['crop'].unique())
    
    col0,col1=st.columns(2)
    with col0:
        crop=st.selectbox('Crop',crops,0)
        varieties=np.sort(crops_variety[crops_variety['crop']==crop]['variety'].unique())
        variety=st.selectbox('Variety',varieties)    
        year=st.selectbox('Crop Year',years)
        
    with col1:
        client=st.selectbox('Client',clients)
        farms=np.sort(fields[fields['Client']==client]['Farm'].unique())
        farm=st.selectbox('Farm',farms)
        fields_sub=fields[fields['Client']==client]
        fields_sub=fields_sub[fields_sub['Farm']==farm]
        fields_list=np.sort(fields_sub['Field'].unique())
        fields_list=st.multiselect('Fields',fields_list)
        notes=st.text_area('Notes')
    
        if st.button('SUBMIT'):
            for field in fields_list:
                field_row=fields_sub[fields_sub['Field']==field]
                assert len(field_row)==1, 'There is a duplicate field name for this farm'
                unq_fldid=field_row.iloc[0]['unq_fldid']
                acres=field_row.iloc[0]['acres']
                uid=str(uuid.uuid1())
                doc_ref=db.collection('crop_assignments').document(f'{uid}')
                doc_ref.set({'log_datetime':now,
                             'uuid':uid,
                             'unq_fldid':int(unq_fldid),
                             'crop_year':int(year),
                             'client':client,
                             'farm':farm,
                             'field':field,
                             'acres':float(acres),
                             'crop':crop,
                             'variety':variety,
                             'notes':notes})
            st.write('You have successfully submitted your data.')
            #st.experimental_memo.clear()
            get_crop_data.clear()
            
elif choice=='Assign Inputs':
    st.subheader('Assign Inputs')
    
    now=datetime.datetime.utcnow()
    
    dry_units=['lbs/acre','oz/acre','tons/acre']
    liquid_units=['qt/acre','gal/acre','pt/acre','oz/acre']
    
    col0,col1=st.columns(2)
    
    with col0:
        st.subheader('Enter Product Information')
        input_forms=inputs['form'].unique()            
        input_form=st.selectbox('Product Formulation',input_forms)
        
        inputs_sub_form=inputs[inputs['form']==input_form]
        input_types=inputs_sub_form['input_type'].unique()
        if input_form=='liquid':
            units=st.selectbox('Application Units',liquid_units)
        elif input_form=='dry':
            units=st.selectbox('Application Units',dry_units)
        
        input_type=st.selectbox('Product Type',input_types)
        inputs_sub_type=inputs_sub_form[inputs_sub_form['input_type']==input_type]
        products=inputs_sub_type['input'].unique()
        
        product=st.selectbox('Product',products)
        rate=st.number_input('Application Rate')
    
    with col1:
        st.subheader('Assign Fields')
        clients=np.sort(fields['Client'].unique())        
        
        year=st.selectbox('Crop Year',years)
        client=st.selectbox('Client',clients)
        farms=np.sort(fields[fields['Client']==client]['Farm'].unique())
        farm=st.selectbox('Farm',farms)
        fields_sub=fields[fields['Client']==client]
        fields_sub=fields_sub[fields_sub['Farm']==farm]
        fields_list=np.sort(fields_sub['Field'].unique())
        fields_list=st.multiselect('Fields',fields_list)
        notes=st.text_area('Notes')

        if st.button('SUBMIT'):
            for field in fields_list:
                field_row=fields_sub[fields_sub['Field']==field]
                assert len(field_row)==1, 'There is a duplicate field name for this farm'
                unq_fldid=field_row.iloc[0]['unq_fldid']
                acres=field_row.iloc[0]['acres']
                uid=str(uuid.uuid1())
                doc_ref=db.collection('crop_inputs').document(f'{uid}')
                doc_ref.set({'log_datetime':now,
                             'uuid':uid,
                             'unq_fldid':int(unq_fldid),
                             'crop_year':int(year),
                             'client':client,
                             'farm':farm,
                             'field':field,
                             'acres':float(acres),
                             'product':product,
                             'type':input_type,
                             'formulation':input_form,
                             'rate':float(rate),
                             'units':units,
                             'notes':notes})
            st.write('You have successfully submitted your data.')
            #st.experimental_memo.clear()
            get_input_data.clear()
    
    
