import streamlit as st
import streamlit_shadcn_ui as ui
import pandas as pd
import numpy as np
import altair as alt
import xlsxwriter
import os
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
import time

#SECTION 1: THE PAGE
#function to style the page
img = "assets\prescription.png"

def page_styling():
    st.set_page_config(
        page_title="Facility Viral Load Analysis",
        page_icon=img,
        layout="wide",
        initial_sidebar_state="expanded")
    st.markdown(
        """<style>
        #MainMenu {visibility:hidden;}
        footer {visibility:hidden;}
        </style>""", unsafe_allow_html=True)
    st.markdown(
        """<style>
        .block-container {
            padding-top: 0.5rem;}</style>""", unsafe_allow_html=True)
    
page_styling()

with st.sidebar:
   # ui.avatar(src=img)
    st.title('Facility Viral Load Analysis `version 2.0` ')
    st.caption("Analyse your facility's clients' :green[viral load indicators] within seconds with a just simple linelist upload")
 
#SECTION 2:THE DATA
    upload_csv = st.file_uploader(" **_upload recent active on ART Linelist below (csv only)_** ", type=['csv'])
    
    st.markdown('''Made by [Wayne Omondi](https://www.linkedin.com/in/waynewillislink/)
                    ''')

try:   
    if upload_csv is not None:
        @st.cache_data
        def load_csv():
            return (pd.read_csv(upload_csv, 
                                usecols=['MFL Code','CCC No', 'Sex', 'Age at reporting','Art Start Date','Last VL Result','Last VL Date', 'Active in PMTCT','Next Appointment Date'],
                                parse_dates=['Art Start Date','Last VL Date','Next Appointment Date'])
            )
except:
    st.info("Awaiting **_Active on ART Linelist_** upload for analysis") 
    
data = load_csv()

data.columns = [x.lower().replace(" ","_") for x in data.columns]

def prep_df(data):
    return (data
            .assign(ccc_no = data.ccc_no.astype(str),
                    art_start_date = pd.to_datetime(data.art_start_date),
                    last_vl_date = pd.to_datetime(data.last_vl_date),
                    next_appointment_date = pd.to_datetime(data.next_appointment_date))
            )
linelist = prep_df(data)

#a part of section 1 to get the facility information
facility_data = 'facilitydata.xlsx'
facility_meta = pd.read_excel(facility_data)

facility_name = (pd.merge(facility_meta, linelist,
                on=['mfl_code'],
                how='right')).facility_name[0]

facility_code = (pd.merge(facility_meta, linelist,
                on=['mfl_code'],
                how='right')).mfl_code[0].astype('str')

facility_region = (pd.merge(facility_meta, linelist,
                on=['mfl_code'],
                how='right')).region[0]

facility_sc = (pd.merge(facility_meta, linelist,
                on=['mfl_code'],
                how='right')).sub_county[0]

with st.container():
    info1,info2,info3,info4,info5 = st.columns(5)
    
    with info1:
        st.write(":green[**_Facility:_**] " + facility_name)
    with info2:
        st.write(":green[**_MFL Code:_**] " + facility_code)
    with info3:
        st.write(":green[**_Region:_**] " + facility_region)
    with info4:
        st.write(":green[**_Sub County:_**] " + facility_sc)
    with info5:
        page_calendar = datetime.datetime.now()
        st.write(f':green[**_Date:_**] {page_calendar.strftime("    %Y, %B %d   ")}')
        
#SCETION 3: ANALYTICS
linelist.drop(['mfl_code'], axis=1, inplace=True)

linelist_copy = linelist.copy()

columns_to_use = ('ccc_no','sex', 'age_at_reporting', 'art_start_date', 'last_vl_result', 'last_vl_date',
       'active_in_pmtct', 'next_appointment_date')

linelist_copy.columns = columns_to_use

pmtct_df = linelist_copy[linelist_copy['active_in_pmtct'].eq('Yes')]

elligible_df = linelist_copy[(linelist_copy.art_start_date < pd.to_datetime(date.today() + relativedelta(months=-3)))]
not_elligible = linelist_copy[(linelist_copy.art_start_date > pd.to_datetime(date.today() + relativedelta(months=-3)))]

elligible_pmtct = elligible_df[elligible_df['active_in_pmtct'].eq('Yes')]
elligible_no_pmtct = elligible_df[elligible_df['active_in_pmtct'].eq('No')]

valid_pmtct = (elligible_pmtct[(elligible_pmtct.last_vl_date > pd.to_datetime(date.today() + relativedelta(months=-6)))])
invalid_pmtct = (elligible_pmtct[(elligible_pmtct.last_vl_date < pd.to_datetime(date.today() + relativedelta(months=-6)))])

elligible_no_vl = elligible_no_pmtct[elligible_no_pmtct.last_vl_result.isnull()]
elligible_no_vl_pmtct = elligible_pmtct[elligible_pmtct.last_vl_result.isnull()]

invalid_below_25 = (elligible_no_pmtct[(elligible_no_pmtct.last_vl_date < pd.to_datetime(date.today() + relativedelta(months=-6)))]
                    .query('age_at_reporting <=24'))
valid_below_25 = (elligible_no_pmtct[(elligible_no_pmtct.last_vl_date > pd.to_datetime(date.today() + relativedelta(months=-6)))]
                    .query('age_at_reporting <=24'))

invalid_above_25 = (elligible_no_pmtct[(elligible_no_pmtct.last_vl_date < pd.to_datetime(date.today() + relativedelta(months=-12)))]
                    .query('age_at_reporting>=25'))
valid_above_25 = (elligible_no_pmtct[(elligible_no_pmtct.last_vl_date > pd.to_datetime(date.today() + relativedelta(months=-12)))]
                    .query('age_at_reporting>=25'))

full_valid_df = pd.concat([valid_above_25, valid_below_25, valid_pmtct], ignore_index=True)
full_invalid_df = pd.concat([elligible_no_vl, elligible_no_vl_pmtct , invalid_pmtct, invalid_below_25, invalid_above_25], ignore_index=True)

full_valid_df = full_valid_df.assign(validity = 'valid')
full_invalid_df = full_invalid_df.assign(validity = 'invalid')
not_elligible = not_elligible.assign(validity = 'not_elligible')

final_linelist = pd.concat([not_elligible, full_valid_df, full_invalid_df], ignore_index=True)

def elligibility_category(val):
    if val == "not_elligible":
        return 'not_elligible'
    return 'elligible'

final_vl_status = (final_linelist.assign(elligibility_status=final_linelist.validity.apply(elligibility_category)))

pivot_linelist = final_vl_status.copy()

def vl_category(val):
    if val >= 0 and val <200:
        return 'suppressed'
    if val >=200:
        return 'unsuppressed'
    
pivot_linelist = pivot_linelist.replace('LDL',0)
pivot_linelist.last_vl_result = pd.to_numeric(pivot_linelist.last_vl_result)

pivot_linelist = pivot_linelist.assign(vl_category=pivot_linelist.last_vl_result.apply(vl_category))

#assigning age groups
def age_grouping(val):
    if val >=0 and val <10:
        return '0-9 years'
    if val >=10 and val <=14:
        return '10-14 years'
    if val >15 and val <=19:
        return '15-19 years'
    if val >=20 and val <=24:
        return '20-24 years'
    return '25+ years'
pivot_linelist = pivot_linelist.assign(age_category=pivot_linelist.age_at_reporting.apply(age_grouping))

high_vl = pivot_linelist[pivot_linelist.vl_category.eq('unsuppressed')]

due_for_repeat = high_vl[(high_vl.last_vl_date < pd.to_datetime(date.today() + relativedelta(months=-3)))]

#SECTION 4: VISUALIZATIONS

with st.container():
    metric1,metric2,metric3,metric4,metric5 = st.columns(5)
    
    with metric1:
        ui.metric_card(title="Active on ART",
                  content=(linelist.shape[0]),
                  description="adults and children currently receiving ART")
    with metric2:
        ui.metric_card(title="Elligible for VL Uptake",
                content=(elligible_df.shape[0]),
                description="HIV positive clients on ART for more than 3 mnths")
    with metric3:
        ui.metric_card(title="Active in PMTCT",
                content=(pmtct_df.shape[0]),
                description="active on ART clients currently enrolled in MCH")
    with metric4:
        ui.metric_card(title="Valid VLs",
                content=(full_valid_df.shape[0]),
                description="elligible clients with a valid documented viral result")
    with metric5:
            ui.metric_card(title="Due For Repeat VL",
                    content=(due_for_repeat.shape[0]),
                    description="high vl clients due for repeat vl i.e. 3 mnths since result")

valid_table, invalid_table = st.columns(2)

with valid_table:
    with st.container():
        st.subheader("valid viral loads", divider='grey')
        st.caption("clients elligible for VL uptake with a valid documented viral load, includes: 0 - 24 years and pmtct filtered out based on 6 months vl guideline; and 12 months for 25 years+")
        st.dataframe(full_valid_df, use_container_width=True, height=200, hide_index=True)
'''        
@st.cache_data
def df_to_csv(df):
    return df.to_csv(index=False).encode("utf-8")

df_csv = df_to_csv(my_large_df)

st.download_button(
    label="Download valid data",
    data=df_csv,
    file_name=f"{}"+".csv", 
    mime="text/csv")
    
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    # Write each dataframe to a different worksheet.
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    
    writer.save()

    download2 = st.download_button(
        label="Download data as Excel",
        data=buffer,
        file_name='large_df.xlsx',
        mime='application/vnd.ms-excel'
    '''

with invalid_table:
    with st.container():
        st.subheader("invalid viral loads", divider='grey')
        st.caption("clients elligible for VL uptake without a valid documented viral load, includes: 0 - 24 years and pmtct filtered out based on 6 months vl guideline; high vl clients after 3 months since their vl")
        st.dataframe(full_invalid_df, use_container_width=True, height=200, hide_index=True)
    
#full_invalid_df.to_csv(f'Invalid_VL_as_at_{date.today().strftime("%d-%m-%Y")}.csv')
#st.dataframe(final_vl_status, use_container_width=True, hide_index=True)

with st.container():
    min_age = full_valid_df.age_at_reporting.min()
    max_age = full_valid_df.age_at_reporting.max()
    '''age_filter = ui.slider(default_value=[min_age, max_age],
                        #key=full_invalid_df.age_at_reporting, 
                        min_value=min_age, max_value=max_age, step=1)
'''
    #filtered = full_valid_df.loc[(full_valid_df.age_at_reporting >= full_valid_df.age_at_reporting.min()) & (full_valid_df.age_at_reporting <= full_valid_df.age_at_reporting.max())]

    #filter_view = full_invalid_df.query('age_at_reporting == @start_age')
    #st.dataframe(filtered)
    

st.dataframe(pivot_linelist)