import streamlit as st
import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pylab as pl
import datetime
from dateutil.relativedelta import relativedelta
from google.cloud import firestore
from google.oauth2 import service_account
import json
import app_tools as tools
from variables import *
from styles import *
import uuid
import base64
import streamlit_authenticator as stauth
from google.cloud import storage
import io
import plotly.express as px
from st_aggrid import GridOptionsBuilder,AgGrid,GridUpdateMode,DataReturnMode
st.set_page_config(layout="wide")
import requests
import folium
from streamlit_folium import st_folium
import streamlit_toggle as tog

env='prod'
#env='dev'

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
zone_parquets_dir='zone_parquets/'
soil_data_dir='soil_lab_data/'

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
def get_gcp_geoparquet(_g_client,bucket_name,file_path):
    file_url=get_signed_url(_g_client,bucket_name,file_path)
    df=pd.read_parquet(file_url)
    gs=gpd.GeoSeries.from_wkb(df['geometry'])
    gdf=gpd.GeoDataFrame(df,geometry=gs,crs='EPSG:4326')
    return gdf

@st.experimental_memo(ttl=3600)
def get_gcp_text(_g_client,bucket_name,file_path):
    file_url=get_signed_url(_g_client,bucket_name,file_path)
    df=pd.read_table(file_url)
    return df

##Sets up main page
hide_streamlit_style="""
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style,unsafe_allow_html=True)

#set_png_as_page_bg('data/background3.jpg')

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
    #years=YEARS
    #fields=get_gcp_csv(gcp_client,bucket_name,field_file)
    #crops_variety=get_gcp_csv(gcp_client,bucket_name,crops_file)
    #inputs=get_gcp_csv(gcp_client,bucket_name,inputs_file)
    #fert_analysis=get_gcp_text(gcp_client,bucket_name,fert_analysis_file)
    zone_data_table=get_gcp_csv(gcp_client,bucket_name,zone_data_file)
    zone_data_table=zone_data_table[zone_data_table['active']=='yes']
    
    if username!='mgriffel':
        #fields=fields[fields['user_name']==username]
        zone_data_table=zone_data_table[zone_data_table['user_name']==username]
    elif username=='mgriffel':
        if st.sidebar.button('Clear All Cache'):
            st.experimental_memo.clear()

    st.sidebar.image('data/progro2.png',use_column_width=True)
    st.sidebar.write(f'Hello {name}')
    st.title('ProGro Data Management System')
    
    main_choice=st.sidebar.selectbox('Site Navigation Options',MAIN_MENU)
    if main_choice=='Welcome':
        choice='Welcome'
    #elif main_choice=='Planning Tools':
    #    choice=st.sidebar.selectbox('Planning Tools',PLANNING_OPTIONS)
    #elif main_choice=='Application Tools':
    #    choice=st.sidebar.selectbox('Application Tools',APPLICATION_OPTIONS)
    elif main_choice=='VRT Tools':
        choice=st.sidebar.selectbox('VRT Tools',VRT_OPTIONS)
    elif main_choice=='Agrimet Dashboards':
        choice=st.sidebar.selectbox('Agrimet Tools',AGRIMET_OPTIONS)
    
    authenticator.logout('Logout','sidebar')
    
    if choice=='Welcome':
        st.write(WELCOME)        
        st.markdown('<a href="mailto:agtech@progroagronomy.com">Contact us!</a>', unsafe_allow_html=True)
    
    elif choice=='Agrimet Daily Weather':
        st.subheader('Query daily Agrimet data by station ID, weather parameters, and date ranges.')
        params=list(AGRIMET_PARAMS)
        params=sorted(params)
        stations=list(AGRIMET_STATIONS)
        stations=sorted(stations)
        now=datetime.datetime.utcnow()-relativedelta(days=1)
        now_minus_1=datetime.datetime.utcnow()-relativedelta(days=7)
        
        col0,col1,col2,col3=st.columns(4)
        with col0:
            station=st.selectbox('Agrimet Station',stations)
            station_id=AGRIMET_STATIONS[station]
        with col1:
            param=st.selectbox('Weather Parameter',params)
            param_id=AGRIMET_PARAMS[param]
        with col2:
            start_date=st.date_input('Start Date',value=now_minus_1,max_value=now_minus_1)
            start=tools.get_date_string(start_date)
        with col3:
            end_date=st.date_input('End Date',value=now,min_value=start_date,max_value=now)
            end=tools.get_date_string(end_date)
        
        agrimet_address=tools.get_agrimet_daily_address(station_id,param_id,start,end)
        req=requests.get(agrimet_address)
        agrimet_df=pd.read_html(req.text,header=0)[0]
        agrimet_df=agrimet_df.dropna()
        
        start_date_prev=start_date-relativedelta(years=1)
        end_date_prev=end_date-relativedelta(years=1)
        #end_date_prev=end_date_prev-relativedelta(days=1)
        start_prev=tools.get_date_string(start_date_prev)
        end_prev=tools.get_date_string(end_date_prev)
        
        agrimet_address_prev=tools.get_agrimet_daily_address(station_id,param_id,start_prev,end_prev)
        req_prev=requests.get(agrimet_address_prev)
        agrimet_df_prev=pd.read_html(req_prev.text,header=0)[0]
        agrimet_df_prev=agrimet_df_prev.dropna()
        
        if len(agrimet_df)>1:
            agrimet_df['DateTime']=pd.to_datetime(agrimet_df['DateTime'])
            agrimet_df.set_index('DateTime',inplace=True)
            agrimet_df=agrimet_df.rename(columns={list(agrimet_df)[0]:param})
            agrimet_df['label']='Current Year'
            if param_id=='tg':
                total=agrimet_df[param].sum()
                st.write(f'Total accumulated growing degree days for the selected time period: {total:0.2f}')
            elif param_id=='pp':
                total=agrimet_df[param].sum()
                st.write(f'Total accumulated precipitation (inches) for the selected time period: {total:0.2f}')
            if len(agrimet_df_prev)>1:
                agrimet_df_prev['DateTime']=pd.to_datetime(agrimet_df_prev['DateTime'])
                agrimet_df_prev['DateTime']=agrimet_df_prev['DateTime']+pd.DateOffset(years=1)
                agrimet_df_prev.set_index('DateTime',inplace=True)
                agrimet_df_prev=agrimet_df_prev.rename(columns={list(agrimet_df_prev)[0]:param})
                agrimet_df_prev['label']='Previous Year'
                agrimet_df_final=pd.concat([agrimet_df,agrimet_df_prev])
            else:
                agrimet_df_final=agrimet_df
                
            fig=px.line(agrimet_df_final,x=agrimet_df_final.index,y=param,
                        color='label',
                        markers=True,
                        title=station)
            st.plotly_chart(fig)
            st.write('Data Source: https://www.usbr.gov/pn/agrimet/')

        else:
            st.write('No data are available')
            
    elif choice=='Agrimet Daily Crop ET':
        st.subheader('Query daily Agrimet evapotranspiration data by station ID and crop.')
        stations=list(AGRIMET_STATIONS)
        stations=sorted(stations)
        now=datetime.datetime.utcnow()
        if now.month>3:
            et_year=now.year
        else:
            et_year=now.year-1
        
        col0,col1,col2=st.columns(3)
        with col0:
            years=[]
            for i in range(5):
                years.append(et_year)
                et_year-=1
            selected_year=st.selectbox('Select Crop Year',years)
        with col1:
            station=st.selectbox('Agrimet Station',stations)
            station_id=AGRIMET_STATIONS[station]            
            agrimet_et_df=tools.get_et_table(station_id,selected_year)
            crops_df=tools.get_et_data(agrimet_et_df)
        with col2:
            crops=crops_df['crop_name'].to_list()
            crops=set(crops)
            crops=sorted(crops)
            crop=st.selectbox('Select Crop',crops)
            crop_df=crops_df[crops_df['crop_name']==crop]
            if len(crop_df)>1:
                start_dates=crop_df['start_date'].to_list()
                start_dates=sorted(start_dates)
                with col0:
                    start_date=st.selectbox('Select ET Vegetation Start Date',start_dates)
                    crop_df=crop_df[crop_df['start_date']==start_date]
            else:
                with col0:
                    st.write()
                    st.write('ET Vegetation Start Date')
                    st.write(crop_df.iloc[0]['start_date'].strftime('%m/%d/%Y'))
        with col1:
            et_df=pd.DataFrame({'Date':crop_df.iloc[0]['dates'],'ET (inches)':crop_df.iloc[0]['data']})
            et_df.sort_values(by='Date',inplace=True)
            start_et_date=et_df.iloc[0]['Date']
            end_et_date=et_df.iloc[-1]['Date']
            start_et=st.date_input('Start Date',value=start_et_date,min_value=start_et_date,max_value=end_et_date)
            
        with col2:
            end_et=st.date_input('End Date',value=end_et_date,min_value=start_et,max_value=end_et_date)
        
        if start_et!=end_et:
            et_df=et_df[(et_df['Date']>=start_et) & (et_df['Date']<=end_et)]
            st.write(f'Total ET (inches) for the selected time period: {et_df["ET (inches)"].sum():0.2f}')
            fig=px.line(et_df,x='Date',y='ET (inches)',
                        markers=True,
                        title=f'{station} - {crop}')
            st.plotly_chart(fig)
            st.write('Data Source: https://www.usbr.gov/pn/agrimet/')        
    
    elif choice=='Zone Fertilizer Dashboard':
        st.subheader('Zone Fertilizer Dashboard')
        col0,col_blank,col1,col2=st.columns([1,0.5,1,1])
        soil_lab_data_flag=False
        
        with col0:
            toggle_response=tog.st_toggle_switch(label='View Archive Data')
            if toggle_response:
                zone_data_table=zone_data_table[zone_data_table['archive']=='x']
            else:
                zone_data_table=zone_data_table[zone_data_table['archive']!='x']
                
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
            lab_code=vrt_fields_sub.iloc[0]['lab_code']
            short_name=vrt_fields_sub.iloc[0]['name']
            img_file_url=get_signed_url(gcp_client,bucket_name,f'zone_images/{zone_id}.png')
            
            bucket=gcp_client.bucket(bucket_name)
            
        with col1:
            st.write('Available PDF Downloads')
            file_path=f'zone_pdf_labels/{zone_id}.pdf'
            if bucket.blob(file_path).exists():
                pdf_file=bucket.blob(file_path).download_as_bytes(raw_download=True)
                st.download_button(label='Download Sample Labels',
                                   data=pdf_file,
                                   file_name=f'{short_name}_labels.pdf',
                                   mime='application/octet-stream')
            
            file_path=f'zone_pdf_samples/{zone_id}.pdf'
            if bucket.blob(file_path).exists():
                soil_lab_data_flag=True
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
            
        with col2:
            st.write('Available Prescription Downloads')
            file_path=f'zone_prescriptions/{zone_id}.zip'
            if bucket.blob(file_path).exists():
                zip_file_bytes=bucket.blob(file_path).download_as_bytes(raw_download=True)
                st.download_button(label='Download Prescription File',
                                   data=zip_file_bytes,
                                   file_name=f'{short_name}_prescription.zip',
                                   mime='application/zip')
        
        #with col1:
        
        col0,col1,col2=st.columns([0.75,0.2,0.75])
        geo_file_path=f'{zone_parquets_dir}{zone_id}.parquet'
        if bucket.blob(geo_file_path).exists():
            with col0:
                zone_gdf=get_gcp_geoparquet(gcp_client,bucket_name,geo_file_path)
                zone_gdf['Zone']=zone_gdf['Zone'].astype(str)
                zone_gdf['Acres']=zone_gdf['Acres'].round(decimals=1)
                zone_gdf_1=zone_gdf.copy()
                zones=zone_gdf['Zone'].to_list()
                zone_gdf.set_index('Zone',inplace=True)
                colors=pl.cm.viridis(np.linspace(0,1,len(zones)))
                color_map={}
                i=0
                for zone in zones:
                    color=colors[i]
                    color=color*255
                    color=color.astype(int)
                    color_map[zone]=f'rgb({color[0]},{color[1]},{color[2]})'
                    i+=1

                gdf_fig=px.choropleth(zone_gdf,geojson=zone_gdf['geometry'],
                                      locations=zone_gdf.index,
                                      color=zone_gdf.index,
                                      hover_data=[zone_gdf['Acres']],
                                      color_discrete_map=color_map,
                                      projection='natural earth',
                                      template='plotly_dark')
                gdf_fig.update_geos(fitbounds='geojson',visible=True)

                gdf_fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                                      paper_bgcolor="rgba(0,0,0,0)",
                                      legend=dict(y=0.85))
                st.plotly_chart(gdf_fig,use_container_width=True)
            
            file_path=f'zone_img_tables/{zone_id}.csv'
            if bucket.blob(file_path).exists():
                with col1:
                    zone_img_data=get_gcp_csv(gcp_client,bucket_name,file_path)
                    zone_img_data['dates']=pd.to_datetime(zone_img_data['dates'])
                    zone_img_data.sort_values(by='dates',inplace=True)
                    zone_img_data_1=zone_img_data.copy()
                    zone_gdf=tools.get_vigor_pos(zone_gdf_1,zone_img_data_1)
                    vigor_df=zone_gdf[['Zone','Acres','Vigor']]
                    vigor_df.set_index('Zone',inplace=True)
                    vigor_df['Vigor']=vigor_df['Vigor'].astype(float)
                    vigor_df['Vigor']=vigor_df['Vigor'].round(decimals=1)
                    #st.write(vigor_df)
                    st.dataframe(vigor_df.style.format(ZONE_STYLE),use_container_width=False)
                
            
        #file_path=f'zone_img_tables/{zone_id}.csv'
        #if bucket.blob(file_path).exists():
                with col2:
                    #zone_img_data=get_gcp_csv(gcp_client,bucket_name,file_path)
                    zones=list(zone_img_data)
                    colors=pl.cm.viridis(np.linspace(0,1,len(zones)))
                    color_map={}
                    i=0
                    for zone in zones:
                        color=colors[i]*255
                        color=color.astype(int)
                        color_map[zone]=f'rgb({color[0]},{color[1]},{color[2]})'
                        i+=1
                    #zone_img_data['dates']=pd.to_datetime(zone_img_data['dates'])
                    fig=px.line(zone_img_data,x='dates',y=zones,
                                color_discrete_map=color_map,
                                markers=True,
                                labels={'dates':'Date','value':'Zone Crop Vigor',
                                        'variable':'Zone'},
                                title='Zone Crop Vigor Curves')
                                
                    fig.update_layout(margin={"r":10,"t":50,"l":30,"b":10})
                    st.plotly_chart(fig)
            
        if soil_lab_data_flag:
            try:

                box_label=f'Soil Data Source: {SOIL_LAB_KEY[lab_code]}'
                soil_data_choices=st.multiselect(box_label,LAB_DATA_COLS[lab_code],
                                                 max_selections=4)

                soil_data_path=f'{soil_data_dir}{zone_id}.csv'
                soil_data=get_gcp_csv(gcp_client,bucket_name,soil_data_path)
                soil_data.rename(columns=LAB_DATA_MAPS[lab_code],inplace=True)
                soil_data.sort_values(by='Zone',inplace=True)
                soil_data['zone_int']=soil_data['Zone'].astype(int)
                soil_data['Zone']=soil_data['Zone'].astype(int).astype(str)
                zones=soil_data['zone_int'].to_list()
                colors=pl.cm.viridis(np.linspace(0,1,len(zones)))
                color_map={}
                i=0
                for zone in zones:
                    color=colors[i]*255
                    color=color.astype(int)
                    color_map[str(int(zone))]=f'rgb({color[0]},{color[1]},{color[2]})'
                    i+=1

                col0,col1,col2,col3=st.columns(4)
                if len(soil_data_choices)==1:
                    with col0:
                        bar_fig0=tools.get_soil_data_bar_chart(soil_data,color_map,soil_data_choices[0])
                        st.plotly_chart(bar_fig0,use_container_width=True)

                if len(soil_data_choices)==2:
                    with col0:  
                        bar_fig0=tools.get_soil_data_bar_chart(soil_data,color_map,soil_data_choices[0])
                        st.plotly_chart(bar_fig0,use_container_width=True)
                    with col1:
                        bar_fig1=tools.get_soil_data_bar_chart(soil_data,color_map,soil_data_choices[1])
                        st.plotly_chart(bar_fig1,use_container_width=True)

                if len(soil_data_choices)==3:
                    with col0:
                        bar_fig0=tools.get_soil_data_bar_chart(soil_data,color_map,soil_data_choices[0])
                        st.plotly_chart(bar_fig0,use_container_width=True)
                    with col1:
                        bar_fig1=tools.get_soil_data_bar_chart(soil_data,color_map,soil_data_choices[1])
                        st.plotly_chart(bar_fig1,use_container_width=True)
                    with col2:
                        bar_fig2=tools.get_soil_data_bar_chart(soil_data,color_map,soil_data_choices[2])
                        st.plotly_chart(bar_fig2,use_container_width=True)

                if len(soil_data_choices)==4:
                    with col0:
                        bar_fig0=tools.get_soil_data_bar_chart(soil_data,color_map,soil_data_choices[0])
                        st.plotly_chart(bar_fig0,use_container_width=True)
                    with col1:
                        bar_fig1=tools.get_soil_data_bar_chart(soil_data,color_map,soil_data_choices[1])
                        st.plotly_chart(bar_fig1,use_container_width=True)
                    with col2:
                        bar_fig2=tools.get_soil_data_bar_chart(soil_data,color_map,soil_data_choices[2])
                        st.plotly_chart(bar_fig2,use_container_width=True)
                    with col3:
                        bar_fig3=tools.get_soil_data_bar_chart(soil_data,color_map,soil_data_choices[3])
                        st.plotly_chart(bar_fig3,use_container_width=True)
                        
            except:
                st.write('Soil data are not available')
                
            

