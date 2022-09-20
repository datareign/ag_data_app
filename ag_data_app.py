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
import streamlit_authenticator as stauth
from google.cloud import storage
import io
import plotly.express as px

env='prod'

#fields=pd.read_csv('data/fields.csv')
#crops_variety=pd.read_csv('data/crops_variety.csv')
#inputs=pd.read_csv('data/inputs.csv')
#fert_analysis=pd.read_table('data/fert_analysis.txt')

key_dict=json.loads(st.secrets['textkey'])
creds=service_account.Credentials.from_service_account_info(key_dict)
db=firestore.Client(credentials=creds,project='agdata-f5a79')

gcp_client=storage.Client(credentials=creds)
main_dir='https://storage.cloud.google.com/agdata-f5a79.appspot.com/'
bucket_name='agdata-f5a79.appspot.com'

field_file='gen_tables/fields.csv'
crops_file='gen_tables/crops_variety.csv'
inputs_file='gen_tables/inputs.csv'
fert_analysis_file='gen_tables/fert_analysis.txt'
zone_data_file='zone_tables/zone_data_table.csv'

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

def get_data(dbase,collection):
    df_list=[]
    crop_refs=dbase.collection(collection)
    for doc in crop_refs.stream():
        df_list.append(pd.DataFrame(doc.to_dict(),index=[0]))
    df=pd.concat(df_list)
    return df


def get_signed_url(g_client,bucket_name, file_path,mins=1):
    bucket = g_client.bucket(bucket_name)
    #content = bucket.blob(file_path).download_as_string().decode("utf-8")
    url = bucket.blob(file_path).generate_signed_url(version='v4',
                                                         expiration=datetime.timedelta(minutes=mins),
                                                         method='GET')
    return url

@st.experimental_memo(ttl=3600)
def get_gcp_csv(_g_client,bucket_name,file_path):
    file_url=get_signed_url(_g_client,bucket_name,file_path)
    df=pd.read_csv(file_url)
    return df

@st.experimental_memo(ttl=3600)
def get_gcp_text(_g_client,bucket_name,file_path):
    file_url=get_signed_url(_g_client,bucket_name,file_path)
    df=pd.read_table(file_url)
    return df

set_png_as_page_bg('data/background3.jpg')

users=get_data(db,'users')
names=users['user'].to_list()
user_names=users['user_name'].to_list()
hashed_passwords=users['hash_password'].to_list()

credentials={'usernames':{}}

for un,name,pw in zip(user_names,names,hashed_passwords):
    user_dict={'name':name,'password':pw}
    credentials['usernames'].update({un:user_dict})

authenticator=stauth.Authenticate(credentials,'data_portal','abcdef',cookie_expiry_days=30)

name,authentication_status,username=authenticator.login('Login','main')

if authentication_status==False:
    st.error('Username/password is incorrect')
if authentication_status==None:
    st.warning('Please enter your username and password.')
if authentication_status:
    
    fields=get_gcp_csv(gcp_client,bucket_name,field_file)
    crops_variety=get_gcp_csv(gcp_client,bucket_name,crops_file)
    inputs=get_gcp_csv(gcp_client,bucket_name,inputs_file)
    fert_analysis=get_gcp_text(gcp_client,bucket_name,fert_analysis_file)
    zone_data_table=get_gcp_csv(gcp_client,bucket_name,zone_data_file)
    zone_data_table=zone_data_table[zone_data_table['active']=='yes']
    
    if username!='mgriffel':
        fields=fields[fields['user_name']==username]
        zone_data_table=zone_data_table[zone_data_table['user_name']==username]
    elif username=='mgriffel':
        if st.sidebar.button('Clear All Cache'):
            st.experimental_memo.clear()
            

    years=[2022,2023]

    st.title('ProGro Data Management System')
    menu=['Welcome',
          'Assign Crops','Assign Inputs',
          'View Crop Assignments',
          'View Input Recommendations',
          'View Nutrient Recommendations',
          'VRT Zone Dashboard']
    st.sidebar.image('data/progro1.png',use_column_width=True)
    st.sidebar.write(f'Hello {name}')
    choice=st.sidebar.selectbox('Options',menu)
    authenticator.logout('Logout','sidebar')
    
    if choice=='Welcome':
        st.write('''Welcome to the ProGro Data Management System.
                 This interface is designed to allow users to develop 
                 detailed crop plans including planned field assignments, 
                 varieties/hybrids, and inputs. To make this process
                 as efficient as possible, almost all entries are
                 restricted to drop-down selection boxes.
                 This application is connected to a secure and 
                 private cloud database. You also have the option 
                 to download CSVs to maintain your own copies and 
                 use as you wish. If you have any questions or need
                 additional input options for products, crop types, and/or
                 varieties, please use the link below to contact the 
                 site administrator. Be sure to include detailed
                 information. Thanks and Happy Farming!''')        
        
        st.markdown('<a href="mailto:agtech@progroagronomy.com">Contact us!</a>', unsafe_allow_html=True)
        

    if choice=='View Crop Assignments':
        st.subheader('View Crop Assignments')
        st.write('Select by Grower')
        col0,col1=st.columns(2) 
        with col0:
            ca_year=st.selectbox('Crop Year',years)
            ca_clients=np.sort(fields['Client'].unique())
        with col1:
            ca_client=st.selectbox('Client',ca_clients)

        ca_df=get_crop_data(db,f'crop_assignments_{env}')
        
        #ca_df=ca_df[ca_df['user_name']==username]
        ca_df=ca_df[ca_df['crop_year']==int(ca_year)]
        ca_df['crop_year']=ca_df['crop_year'].astype(int)
        ca_df=ca_df[ca_df['client']==ca_client]

        if len(ca_df)>0:
            ca_df.sort_values(by=['field','farm','client'],inplace=True)
            ca_df.reset_index(drop=True,inplace=True)
            ca_df=ca_df[['client','farm','field','crop_year',
                         'acres','crop','variety','uuid']]
            with st.expander('Results Table'):
                st.dataframe(ca_df.style.format(CROP_STYLE))
            st.write('If you wish to delete a record, copy the UUID and paste into the input cell below.')
            doc_del=st.text_input('Delete Record',key=0)
            if len(doc_del)>0:
                db.collection(f'crop_assignments_{env}').document(doc_del).delete()
                get_crop_data.clear()
                st.button('Click to Delete',on_click=tools.clear_text)
                #st.success('The data have been deleted.')

            csv=ca_df.to_csv().encode('utf-8')
            if st.download_button(label='Download Data',data=csv,
                                  file_name='Crop_Assignments.csv',
                                  mime='text/csv'):
                st.success('Your dataset has downloaded.')

        else:
            st.write('There are no crop assignments for this grower.')


    if choice=='View Input Recommendations':
        st.subheader('View Input Assignments')
        st.write('Select by Grower')
        col0,col1=st.columns(2)    
        with col0:
            i_year=st.selectbox('Crop Year',years)
            i_clients=np.sort(fields['Client'].unique())
        with col1:
            i_client=st.selectbox('Client',i_clients)

        i_df=get_input_data(db,f'crop_inputs_{env}')
        
        #i_df=i_df[i_df['user_name']==username]
        i_df=i_df[i_df['crop_year']==int(i_year)]
        i_df['crop_year']=i_df['crop_year'].astype(int)
        i_df=i_df[i_df['client']==i_client]

        if len(i_df)>0:
            i_df.sort_values(by=['field','farm','client'],inplace=True)
            i_df.reset_index(drop=True,inplace=True)
            i_df=i_df[['client','farm','field','crop_year','acres',
                       'product','type','formulation','rate','units',
                       'uuid','notes']]
            #st.table(df.style.format(INPUT_STYLE))
            with st.expander('Results Table'):
                st.dataframe(i_df.style.format(INPUT_STYLE))

            st.write('If you wish to delete a record, copy the UUID and paste into the input cell below.')
            doc_del=st.text_input('Delete Record',key=0)
            if len(doc_del)>0:
                db.collection(f'crop_inputs_{env}').document(doc_del).delete()
                get_input_data.clear()
                st.button('Click to Delete',on_click=tools.clear_text)
                #st.write('The data have been deleted.')
                
            csv=i_df.to_csv().encode('utf-8')
            if st.download_button(label='Download Data',data=csv,
                                  file_name='Input_Assignments.csv',
                                  mime='text/csv'):
                st.success('Your dataset has downloaded.')
        else:
            st.write('There are no inputs for this client')

    if choice=='View Nutrient Recommendations':
        st.subheader('View Applied Nutrients')
        col0,col1=st.columns(2)
        with col0:
            vn_year=st.selectbox('Crop Year',years)
            vn_clients=np.sort(fields['Client'].unique())
            vn_client=st.selectbox('Client',vn_clients)
        with col1:
            vn_farms=np.sort(fields[fields['Client']==vn_client]['Farm'].unique())
            vn_farm=st.selectbox('Farm',vn_farms)
            vn_fields_sub=fields[fields['Client']==vn_client]
            vn_fields_sub=vn_fields_sub[vn_fields_sub['Farm']==vn_farm]
            vn_fields_list=np.sort(vn_fields_sub['Field'].unique())
            vn_field=st.selectbox('Field',vn_fields_list)

        n_df=get_input_data(db,f'crop_inputs_{env}')
        
        #n_df=n_df[n_df['user_name']==username]
        n_df=n_df[n_df['crop_year']==int(vn_year)]
        n_df['crop_year']=n_df['crop_year'].astype(int)
        n_df=n_df[n_df['client']==vn_client]
        n_df=n_df[n_df['farm']==vn_farm]
        n_df=n_df[n_df['field']==vn_field]
        n_df=n_df[n_df['type']=='fertilizer']

        if len(n_df)>0:    
            nutrient_dfs=[]
            for index,row in n_df.iterrows():
                nutrient_dfs.append(tools.add_nutrients(fert_analysis,
                                                        row['product'],
                                                        row['rate'],
                                                        row['units'],
                                                        int(vn_year)))
            nutrient_df=pd.concat(nutrient_dfs)
            #nutrient_df['Crop Year']=nutrient_df['Crop Year'].astype(int)
            nutrient_df.reset_index(drop=True,inplace=True)

            nutrients=['N','P','K','S','Mg','Ca','B','Cl','Mn','Fe','Cu','Zn','Mo']
            if len(nutrient_df)>1:
                nutrient_df.loc[len(nutrient_df),nutrients]=nutrient_df.sum(axis=0)
                nutrient_df.loc[len(nutrient_df)-1,'Product']='Totals'

            with st.expander('Results Table'):
                st.dataframe(nutrient_df.style.format(NUTRIENT_STYLE))
            csv=nutrient_df.to_csv().encode('utf-8')
            if st.download_button(label='Download Data',data=csv,
                                  file_name='Applied_Nutrients.csv',
                                  mime='text/csv'):
                st.success('Your dataset has downloaded.')     
        else:
            st.write('There are no fertilizer records for this field')

    elif choice=='Assign Crops':
        st.subheader('Assign Crops')
        now=datetime.datetime.utcnow()
        ac_clients=np.sort(fields['Client'].unique())
        ac_crops=np.sort(crops_variety['crop'].unique())

        col0,col1=st.columns(2)
        with col0:
            ac_crop=st.selectbox('Crop',ac_crops,0)
            ac_varieties=np.sort(crops_variety[crops_variety['crop']==ac_crop]['variety'].unique())
            ac_variety=st.selectbox('Variety',ac_varieties)    
            ac_year=st.selectbox('Crop Year',years)

        with col1:
            ac_client=st.selectbox('Client',ac_clients)
            ac_farms=np.sort(fields[fields['Client']==ac_client]['Farm'].unique())
            ac_farm=st.selectbox('Farm',ac_farms)
            ac_fields_sub=fields[fields['Client']==ac_client]
            ac_fields_sub=ac_fields_sub[ac_fields_sub['Farm']==ac_farm]
            ac_fields_list=np.sort(ac_fields_sub['Field'].unique())
            ac_fields_list=st.multiselect('Fields',ac_fields_list)
            ac_notes=st.text_area('Notes')

            if st.button('SUBMIT'):
                for field in ac_fields_list:
                    field_row=ac_fields_sub[ac_fields_sub['Field']==field]
                    assert len(field_row)==1, 'There is a duplicate field name for this farm'
                    unq_fldid=field_row.iloc[0]['unq_fldid']
                    acres=field_row.iloc[0]['acres']
                    uid=str(uuid.uuid1())
                    doc_ref=db.collection(f'crop_assignments_{env}').document(f'{uid}')
                    doc_ref.set({'log_datetime':now,
                                 'uuid':uid,
                                 'unq_fldid':int(unq_fldid),
                                 'crop_year':int(ac_year),
                                 'client':ac_client,
                                 'farm':ac_farm,
                                 'field':field,
                                 'acres':float(acres),
                                 'crop':ac_crop,
                                 'variety':ac_variety,
                                 'notes':ac_notes,
                                 'user_name':username})
                st.success('You have successfully submitted your data.')
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
            ai_clients=np.sort(fields['Client'].unique())

            ai_year=st.selectbox('Crop Year',years)
            ai_client=st.selectbox('Client',ai_clients)
            ai_farms=np.sort(fields[fields['Client']==ai_client]['Farm'].unique())
            ai_farm=st.selectbox('Farm',ai_farms)
            ai_fields_sub=fields[fields['Client']==ai_client]
            ai_fields_sub=ai_fields_sub[ai_fields_sub['Farm']==ai_farm]
            ai_fields_list=np.sort(ai_fields_sub['Field'].unique())
            ai_fields_list=st.multiselect('Fields',ai_fields_list)
            ai_notes=st.text_area('Notes')

            if st.button('SUBMIT'):
                for field in ai_fields_list:
                    field_row=ai_fields_sub[ai_fields_sub['Field']==field]
                    assert len(field_row)==1, 'There is a duplicate field name for this farm'
                    unq_fldid=field_row.iloc[0]['unq_fldid']
                    acres=field_row.iloc[0]['acres']
                    uid=str(uuid.uuid1())
                    doc_ref=db.collection(f'crop_inputs_{env}').document(f'{uid}')
                    doc_ref.set({'log_datetime':now,
                                 'uuid':uid,
                                 'unq_fldid':int(unq_fldid),
                                 'crop_year':int(ai_year),
                                 'client':ai_client,
                                 'farm':ai_farm,
                                 'field':field,
                                 'acres':float(acres),
                                 'product':product,
                                 'type':input_type,
                                 'formulation':input_form,
                                 'rate':float(rate),
                                 'units':units,
                                 'notes':ai_notes,
                                 'user_name':username})
                st.success('You have successfully submitted your data.')
                get_input_data.clear()
                
    elif choice=='VRT Zone Dashboard':
        st.subheader('VRT Zone Dashboard')
        col0,col1=st.columns([1,2])
        with col0:
            vrt_clients=np.sort(zone_data_table['client'].unique())
            vrt_client=st.selectbox('Client',vrt_clients)
            vrt_farms=np.sort(zone_data_table[zone_data_table['client']==vrt_client]['farm'].unique())
            vrt_farm=st.selectbox('Farm',vrt_farms)
            vrt_fields_sub=zone_data_table[zone_data_table['client']==vrt_client]
            vrt_fields_sub=vrt_fields_sub[vrt_fields_sub['farm']==vrt_farm]
            vrt_fields_list=np.sort(vrt_fields_sub['field'].unique())
            vrt_field=st.selectbox('Field',vrt_fields_list)
            vrt_fields_sub=vrt_fields_sub[vrt_fields_sub['field']==vrt_field]
            assert len(vrt_fields_sub)==1, 'There is a duplicate field name for this farm'
            zone_id=vrt_fields_sub.iloc[0]['zones_id']
            short_name=vrt_fields_sub.iloc[0]['name']
            img_file_url=get_signed_url(gcp_client,bucket_name,f'zone_images/{zone_id}.png')
            
            bucket=gcp_client.bucket(bucket_name)
            file_path=f'zone_pdf_labels/{zone_id}.pdf'
            if bucket.blob(file_path).exists():
                #pdf_file=bucket.blob(file_path).open()
                pdf_file=bucket.blob(file_path).download_as_bytes(raw_download=True)
                st.download_button(label='Download Sample Labels',
                                   data=pdf_file,
                                   file_name=f'{short_name}_labels.pdf',
                                   mime='application/octet-stream')
            
            file_path=f'zone_pdf_samples/{zone_id}.pdf'
            if bucket.blob(file_path).exists():
                #pdf_file=bucket.blob(file_path).open()
                pdf_file=bucket.blob(file_path).download_as_bytes(raw_download=True)
                st.download_button(label='Download Soil Data',
                                   data=pdf_file,
                                   file_name=f'{short_name}_soil_data.pdf',
                                   mime='application/octet-stream')
                
            file_path=f'zone_prescriptions/{zone_id}.zip'
            if bucket.blob(file_path).exists():
                zip_file_bytes=bucket.blob(file_path).download_as_bytes(raw_download=True)
                st.download_button(label='Download Prescription File',
                                   data=zip_file_bytes,
                                   file_name=f'{short_name}_prescription.zip',
                                   mime='application/zip')
        
        with col1:
            st.image(img_file_url)            
        
        file_path=f'zone_img_tables/{zone_id}.csv'
        if bucket.blob(file_path).exists():
            zone_img_data=get_gcp_csv(gcp_client,bucket_name,file_path)
            zones=list(zone_img_data)
            zone_img_data['dates']=pd.to_datetime(zone_img_data['dates'])
            fig=px.line(zone_img_data,x='dates',y=zones,
                        #color_discrete_sequence=px.colors.sequential.Viridis,
                        markers=True,
                        labels={'dates':'Dates','value':'Biomass Index Value',
                                'variable':'Zone'},
                        title='Zone Biomass Curves')
            st.plotly_chart(fig)
