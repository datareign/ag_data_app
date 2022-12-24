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
from st_aggrid import GridOptionsBuilder,AgGrid,GridUpdateMode,DataReturnMode
st.set_page_config(layout="wide")

#env='prod'
env='dev'

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

## helpful data management functions
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

def get_data_query(_dbase,collection,crop_year,client_name):
    docs_refs=_dbase.collection(collection)
    docs=docs_refs.where('crop_year','==',crop_year).where('client','==',client_name).stream()
    df_list=[]
    for doc in docs:
        df_list.append(pd.DataFrame(doc.to_dict(),index=[0]))
    if len(df_list)>0:
        df=pd.concat(df_list)
        return df
    else:
        return None
    
def get_data_query_farm(_dbase,collection,crop_year,client_name,farm_name):
    docs_refs=_dbase.collection(collection)
    docs=docs_refs.where('crop_year','==',crop_year).where('client','==',client_name).where('farm','==',farm_name).stream()
    df_list=[]
    for doc in docs:
        df_list.append(pd.DataFrame(doc.to_dict(),index=[0]))
    if len(df_list)>0:
        df=pd.concat(df_list)
        return df
    else:
        return None
    
def get_data_query_field(_dbase,collection,crop_year,client_name,farm_name,field_name,i_type):
    docs_refs=_dbase.collection(collection)
    docs=docs_refs.where('crop_year','==',crop_year).where('client','==',client_name).where('farm','==',farm_name).where('field','==',field_name).where('type','==',i_type).stream()
    df_list=[]
    for doc in docs:
        df_list.append(pd.DataFrame(doc.to_dict(),index=[0]))
    if len(df_list)>0:
        df=pd.concat(df_list)
        return df
    else:
        return None

def get_data(dbase,collection):
    df_list=[]
    doc_refs=dbase.collection(collection)
    for doc in doc_refs.stream():
        df_list.append(pd.DataFrame(doc.to_dict(),index=[0]))
    df=pd.concat(df_list)
    return df

def get_document(_dbase,collection,uid):
    doc_ref=_dbase.collection(collection).document(uid)
    doc=doc_ref.get()
    if doc.exists:
        doc=doc.to_dict()
        return doc
    else:
        return None

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

##Sets up main page
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
    years=[2022,2023,2024,2025]
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

    st.sidebar.image('data/progro2.png',use_column_width=True)
    st.sidebar.write(f'Hello {name}')
    st.title('ProGro Data Management System')
    main_menu=['Welcome',
               'Planning Tools',
               'Application Tools',
               'VRT Tools']
    planning_options=['Assign Crops','Assign Inputs',
                      'Delete Assignment',
                      'View Crop Plan',
                      'View Input Plan',
                      'View Nutrient Plan']
    application_options=['Log Input Application',
                         'Delete Application']
    vrt_options=['Zone Fertilizer Dashboard']
    
    main_choice=st.sidebar.selectbox('Site Navigation Option',main_menu)
    if main_choice=='Welcome':
        choice='Welcome'
    elif main_choice=='Planning Tools':
        choice=st.sidebar.selectbox('Planning Tools',planning_options)
    elif main_choice=='Application Tools':
        choice=st.sidebar.selectbox('Application Tools',application_options)
    elif main_choice=='VRT Tools':
        choice=st.sidebar.selectbox('VRT Tools',vrt_options)
    
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
                 to download your data to maintain your own copies and 
                 use as you wish. If you have any questions or need
                 additional input options for products, crop types, and/or
                 varieties, please use the link below to contact the 
                 site administrator. Be sure to include detailed
                 information. Thanks and Happy Farming!''')
        
        st.markdown('<a href="mailto:agtech@progroagronomy.com">Contact us!</a>', unsafe_allow_html=True)

    if choice=='View Crop Plan':
        st.subheader('View Crop Plan Assignments')
        st.write('Select by crop year and grower.')
        col0,col1=st.columns(2)
        with col0:
            ca_year=st.selectbox('Crop Year',years)
            ca_clients=np.sort(fields['Client'].unique())
        with col1:
            ca_client=st.selectbox('Client',ca_clients)
                
        ca_df=get_data_query(db,f'crop_assignments_{env}',ca_year,ca_client)
        if ca_df is not None:
            st.write(f'There are {len(ca_df)} records in the table below.')
            ca_df['crop_year']=ca_df['crop_year'].astype(int)
            ca_df.sort_values(by=['farm','field','crop'],inplace=True)
            ca_df.reset_index(drop=True,inplace=True)
            ca_df=ca_df[['client','farm','field','crop_year',
                         'acres','crop','variety','notes']]
            
            with st.expander('Results Table'):
                st.dataframe(ca_df.style.format(CROP_STYLE))
                
            csv=ca_df.to_csv().encode('utf-8')
            if st.download_button(label='Download Planned Crop Data',data=csv,
                                  file_name='Crop_Assignments_Plan.csv',
                                  mime='text/csv'):
                st.success('Your dataset has downloaded.')
            
            crop_df=tools.get_crop_summaries(ca_df,ca_client,ca_year)            
                                
            with st.expander('Crop Summary Table'):
                st.dataframe(crop_df.style.format(CROP_STYLE))
                            
            crop_csv=crop_df.to_csv().encode('utf-8')
            if st.download_button(label='Download Planned Crop Summary Data',data=crop_csv,
                                  file_name=f'Crop_Summary_Plan_{ca_client}_{ca_year}.csv',
                                  mime='text/csv'):
                st.success('Your crop summaries have downloaded.')
        else:
            st.write('There are no planned crop assignements in the system for this year and client.')

    if choice=='View Input Plan':
        st.subheader('View Input Plan Assignments')
        st.write('Select by crop year and grower.')
        col0,col1=st.columns(2)    
        with col0:
            i_year=st.selectbox('Crop Year',years)
            i_clients=np.sort(fields['Client'].unique())
        with col1:
            i_client=st.selectbox('Client',i_clients)

        i_df=get_data_query(db,f'crop_inputs_{env}',i_year,i_client)
        if i_df is not None:
            st.write(f'There are {len(i_df)} records in the table below.')
            i_df['crop_year']=i_df['crop_year'].astype(int)
            i_df.sort_values(by=['farm','field'],inplace=True)
            i_df.reset_index(drop=True,inplace=True)
            i_df=i_df[['client','farm','field','crop_year','acres',
                       'product','type','formulation','rate','units',
                       'notes']]
            with st.expander('Results Table'):
                st.dataframe(i_df.style.format(INPUT_STYLE))
                
            csv=i_df.to_csv().encode('utf-8')
            if st.download_button(label='Download Planned Input Data',data=csv,
                                  file_name=f'Input_Assignments_Plan_{i_client}_{i_year}.csv',
                                  mime='text/csv'):
                st.success('Your input dataset has downloaded.')
                
            ##This builds the product summary table
            prod_df=tools.get_prod_summaries(i_df,i_client,i_year)            
                                
            with st.expander('Product Summary Table'):
                st.dataframe(prod_df.style.format(PROD_STYLE))
                            
            prod_csv=prod_df.to_csv().encode('utf-8')
            if st.download_button(label='Download Planned Product Summary Data',data=prod_csv,
                                  file_name=f'Product_Summary_Plan_{i_client}_{i_year}.csv',
                                  mime='text/csv'):
                st.success('Your product summaries have downloaded.')
        else:
            st.write('There are no planned inputs for this year and client')
            
    if choice=='Delete Assignment':
        input_types=inputs['input_type'].unique()
        
        st.subheader('Delete Planned Crop or Input Assignments')
        
        assignment=st.selectbox('Crop or Input',['Crop','Input'])
        if assignment=='Input':
            st.write('Select by crop year and field.')
            col0,col1=st.columns(2)    
            with col0:
                e_year=st.selectbox('Crop Year',years)
                e_type=st.selectbox('Input Type',input_types)
                e_clients=np.sort(fields['Client'].unique())
            with col1:
                e_client=st.selectbox('Client',e_clients)
                e_farms=np.sort(fields[fields['Client']==e_client]['Farm'].unique())
                e_farm=st.selectbox('Farm',e_farms)
                e_fields_sub=fields[fields['Client']==e_client]
                e_fields_sub=e_fields_sub[e_fields_sub['Farm']==e_farm]
                e_fields_list=np.sort(e_fields_sub['Field'].unique())
                e_field=st.selectbox('Field',e_fields_list)

            e_df=get_data_query_field(db,f'crop_inputs_{env}',e_year,e_client,e_farm,e_field,e_type)
            if e_df is not None:
                st.write(f'There are {len(e_df)} records in the table below.')
                e_df['crop_year']=e_df['crop_year'].astype(int)
                e_df.sort_values(by='product',inplace=True)
                e_df.reset_index(drop=True,inplace=True)
                e_df=e_df[['client','farm','field','crop_year','acres',
                           'product','type','formulation','rate','units',
                           'uuid','notes']]
                gb=GridOptionsBuilder.from_dataframe(e_df)
                gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
                #gb.configure_side_bar() #Add a sidebar
                gb.configure_selection('multiple',use_checkbox=True)
                gb.configure_column('acres',type=['numericColumn','numberColumnFilter','customNumericFormat'],
                                    precision=1)
                grid_options=gb.build()
                grid_response=AgGrid(e_df,
                                     gridOptions=grid_options,
                                     data_return_mode='AS_INPUT', 
                                     update_mode='MODEL_CHANGED', 
                                     fit_columns_on_grid_load=False,
                                     theme='alpine',
                                     enable_enterprise_modules=True,
                                     height=550, 
                                     width='100%',
                                     reload_data=False)
                selected=grid_response['selected_rows']
                if len(selected)>0:
                    if st.button('Click to Delete'):
                        for row in selected:
                            uid=row['uuid']
                            db.collection(f'crop_inputs_{env}').document(uid).delete()
                        st.success('The data have been deleted.')
                        st.experimental_rerun()
            else:
                st.write('There are no planned inputs for this year, field, and type.')
                    
        if assignment=='Crop':
            st.write('Select by crop year, grower, and farm.')
            col0,col1=st.columns(2)    
            with col0:
                d_year=st.selectbox('Crop Year',years)
                d_clients=np.sort(fields['Client'].unique())
            with col1:
                d_client=st.selectbox('Client',d_clients)
                d_farms=np.sort(fields[fields['Client']==d_client]['Farm'].unique())
                d_farm=st.selectbox('Farm',d_farms)

            d_df=get_data_query_farm(db,f'crop_assignments_{env}',d_year,d_client,d_farm)
            if d_df is not None:
                st.write(f'There are {len(d_df)} records in the table below.')
                d_df['crop_year']=d_df['crop_year'].astype(int)
                d_df.sort_values(by=['farm','field','crop'],inplace=True)
                d_df.reset_index(drop=True,inplace=True)
                d_df=d_df[['client','farm','field','crop_year','acres',
                           'crop','variety','uuid','notes']]
                gb=GridOptionsBuilder.from_dataframe(d_df)
                gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
                #gb.configure_side_bar() #Add a sidebar
                gb.configure_selection('multiple',use_checkbox=True)
                gb.configure_column('acres',type=['numericColumn','numberColumnFilter','customNumericFormat'],
                                    precision=1)
                grid_options=gb.build()
                grid_response=AgGrid(d_df,
                                     gridOptions=grid_options,
                                     data_return_mode='AS_INPUT', 
                                     update_mode='MODEL_CHANGED', 
                                     fit_columns_on_grid_load=False,
                                     theme='alpine',
                                     enable_enterprise_modules=True,
                                     height=550, 
                                     width='100%',
                                     reload_data=False)
                selected=grid_response['selected_rows']
                if len(selected)>0:
                    if st.button('Click to Delete'):
                        for row in selected:
                            uid=row['uuid']
                            db.collection(f'crop_assignments_{env}').document(uid).delete()
                        st.success('The data have been deleted.')
                        st.experimental_rerun()
            else:
                st.write('There are no planned crops for this year and field.')

    if choice=='View Nutrient Plan':
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

        n_df=get_data_query_field(db,f'crop_inputs_{env}',vn_year,vn_client,vn_farm,vn_field,'fertilizer')

        if n_df is not None:
            n_df['crop_year']=n_df['crop_year'].astype(int)
            nutrient_dfs=[]
            for index,row in n_df.iterrows():
                nutrient_dfs.append(tools.add_nutrients(fert_analysis,
                                                        row['product'],
                                                        row['rate'],
                                                        row['units'],
                                                        int(vn_year)))
            nutrient_df=pd.concat(nutrient_dfs)
            nutrient_df['Crop Year']=nutrient_df['Crop Year'].astype(int)
            nutrient_df.reset_index(drop=True,inplace=True)

            nutrients=['N','P','K','S','Mg','Ca','B','Cl','Mn','Fe','Cu','Zn','Mo']
            if len(nutrient_df)>1:
                nutrient_df.loc[len(nutrient_df),nutrients]=nutrient_df.sum(axis=0)
                nutrient_df.loc[len(nutrient_df)-1,'Product']='Totals'                
                st.write(f'There are {len(nutrient_df)-1} records in the table below.')
            else:
                st.write(f'There are {len(nutrient_df)} records in the table below.')
                
            with st.expander('Results Table'):
                st.dataframe(nutrient_df.style.format(NUTRIENT_STYLE))
            csv=nutrient_df.to_csv().encode('utf-8')
            if st.download_button(label='Download Data',data=csv,
                                  file_name='Applied_Nutrients.csv',
                                  mime='text/csv'):
                st.success('Your dataset has downloaded.')     
        else:
            st.write('There are no planned fertilizer records for this year and field')

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
            ac_client=st.selectbox('Client',ac_clients)

        with col1:            
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
                    uid=str(uuid.uuid4())
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

    elif choice=='Assign Inputs':
        st.subheader('Assign Inputs')

        now=datetime.datetime.utcnow()

        dry_units=['lbs/acre','oz/acre','tons/acre']
        liquid_units=['qt/acre','gal/acre','pt/acre','oz/acre']

        col0,col1=st.columns(2)

        with col0:
            st.subheader('Enter Product Information')
            input_forms=inputs['form'].unique().tolist()
            input_forms.insert(0,'<select>')
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
                    uid=str(uuid.uuid4())
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
                
    elif choice=='Zone Fertilizer Dashboard':
        st.subheader('Zone Fertilizer Dashboard')
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
                pdf_file=bucket.blob(file_path).download_as_bytes(raw_download=True)
                st.download_button(label='Download Sample Labels',
                                   data=pdf_file,
                                   file_name=f'{short_name}_labels.pdf',
                                   mime='application/octet-stream')
            
            file_path=f'zone_pdf_samples/{zone_id}.pdf'
            if bucket.blob(file_path).exists():
                pdf_file=bucket.blob(file_path).download_as_bytes(raw_download=True)
                st.download_button(label='Download Soil Data',
                                   data=pdf_file,
                                   file_name=f'{short_name}_soil_data.pdf',
                                   mime='application/octet-stream')
                
            file_path=f'zone_load_sheets/{zone_id}.pdf'
            if bucket.blob(file_path).exists():
                pdf_file=bucket.blob(file_path).download_as_bytes(raw_download=True)
                st.download_button(label='Download Load Sheet',
                                   data=pdf_file,
                                   file_name=f'{short_name}_prescription_load_sheet.pdf',
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
                        labels={'dates':'Dates','value':'Crop Vigor',
                                'variable':'Zone'},
                        title='Zone Crop Vigor Curves')
            st.plotly_chart(fig)
