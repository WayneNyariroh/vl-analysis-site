#wayne_willis_omondi

import streamlit as st
import streamlit_shadcn_ui as ui
import pandas as pd
import numpy as np
import openpyxl
import xlrd
import altair as alt
import plotly.express as px
import datetime
import time
from datetime import date
from dateutil.relativedelta import relativedelta

#SECTION 1: THE PAGE
img = "assets\prescription.png"

def page_styling():
    st.set_page_config(
        page_title="wynlabs: facility viral load analyst",
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
            padding-top: 3rem;}</style>""", unsafe_allow_html=True)
    
page_styling()

with st.sidebar:      
    st.title(' :bar_chart: VL_Analyst `v2.0` ')
    st.subheader("Analyse facility's :green[viral load indicators] with a just simple linelist upload.")
    st.caption("> :memo: **Note:** Those on ART for a period less than 3 months considered 'not elligible' for vl uptake. For 0 t0 24 yrs as well as pmtct; vl validity on 6 month-basis; and 25+ on a 12 month-basis.")
    
#SECTION 2:THE DATA
    upload_linelist_csv = st.file_uploader("**1. Upload _Active on ART Patients Linelist_ CSV** ", type=['csv'])
    
    upload_pending_csv = st.file_uploader("**2. Upload _Viral Load and CD4 Lab requests pending Results_ CSV**", type=['csv'])
    pic, about = st.columns((1,3))
    with pic:
        ui.avatar(src="https://www.centreofexcellence.com/media/image/c4/7a/de69537298bc64a96585a0df223c.jpeg")
    with about:
        st.markdown('''made by [wayne willis](https://www.linkedin.com/in/waynewillislink/)''')
    
if upload_linelist_csv is not None:
    df = pd.read_csv(upload_linelist_csv,
                    usecols=['MFL Code','CCC No', 'Sex', 'Age at reporting','Art Start Date','Last VL Result','Last VL Date', 'Active in PMTCT','Next Appointment Date'],
                    parse_dates=['Art Start Date','Last VL Date','Next Appointment Date'], 
                    dayfirst=True)
    data = df
    
    data.columns = [x.lower().replace(" ","_") for x in data.columns]

    def prep_df(data):
        return (data
                .assign(ccc_no = data.ccc_no.astype(str),
                        art_start_date = pd.to_datetime(data.art_start_date),
                        last_vl_date = pd.to_datetime(data.last_vl_date),
                        next_appointment_date = pd.to_datetime(data.next_appointment_date))
                )
    linelist = prep_df(data)

if upload_pending_csv is not None:
    pendingdf = (pd
                 .read_csv(upload_pending_csv,
                            usecols=['Unique Patient Number','Age', 'Sex', 'VL Order Date'],
                            parse_dates=['VL Order Date'],
                            dayfirst=True)
                 .rename(columns=str.lower)
                 .rename(columns = {"unique patient number":"ccc_no",
                                    "vl order date":"vl_order_date"}))
    def prepdf(pendingdf):
        return (pendingdf
                .assign(vl_order_date = pd.to_datetime(pendingdf.vl_order_date),
                        ccc_no = pendingdf.ccc_no.astype(str)))
        
    pendingdf = prepdf(pendingdf)
            
    pendingresults = pendingdf[(pendingdf.vl_order_date >= pd.to_datetime(date.today() + relativedelta(months=-3)))]
    pendingresults = pendingresults.assign(order_status = "pending results")

    with st.spinner(':wink: Hesabu mingi is happening kwa jikoni. Rit matin...'):
        time.sleep(6)
    success = st.success(":heavy_check_mark: Analysis Completed. Loading Results...")
    time.sleep(6)
    success.empty()
    msg = st.toast(':blush: Here you go...')
    time.sleep(3)
    msg.empty()
    
#a part of section 1 to get the facility information
    st.write(" ")
    with st.container():
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

        facility_county = (pd.merge(facility_meta, linelist,
                        on=['mfl_code'],
                        how='right')).county[0]

        facility_sc = (pd.merge(facility_meta, linelist,
                        on=['mfl_code'],
                        how='right')).sub_county[0]

    with st.container():
        info1,info2,info4,info5,info6 = st.columns(5)
        
        with info1:
            st.write(":green[**_Facility:_**] " + facility_name)
        with info2:
            st.write(":green[**_MFL Code:_**] " + facility_code)
        with info4:
            st.write(":green[**_County:_**] " + facility_county)
        with info5:
            st.write(":green[**_Sub County:_**] " + facility_sc)
        with info6:
            page_calendar = datetime.datetime.now()
            st.write(f':green[**_Date:_**]{datetime.datetime.now().strftime("  %a ")}'+ f'{page_calendar.strftime("    %Y, %b %d   ")}')

    #SCETION 3: FEATURE ENGINEERING AND ANALYTICS
    linelist.drop(['mfl_code'], axis=1, inplace=True)
    linelist_copy = linelist.copy()
    
    columns_to_use = ('ccc_no','sex', 'age_at_reporting', 'art_start_date', 'last_vl_result', 'last_vl_date',
        'active_in_pmtct', 'next_appointment_date')
    
    linelist_copy.columns = columns_to_use
    
    pmtct_df = linelist_copy[linelist_copy['active_in_pmtct'].eq('Yes')]
    
    elligible_df = linelist_copy[(linelist_copy.art_start_date <= pd.to_datetime(date.today() + relativedelta(months=-3)))]
    not_elligible = linelist_copy[(linelist_copy.art_start_date >= pd.to_datetime(date.today() + relativedelta(months=-3)))]
    
    elligible_pmtct = elligible_df[elligible_df['active_in_pmtct'].eq('Yes')]
    elligible_no_pmtct = elligible_df[elligible_df['active_in_pmtct'].eq('No')]
    
    valid_pmtct = (elligible_pmtct[(elligible_pmtct.last_vl_date >= pd.to_datetime(date.today() + relativedelta(months=-6)))])
    invalid_pmtct = (elligible_pmtct[(elligible_pmtct.last_vl_date < pd.to_datetime(date.today() + relativedelta(months=-6)))])
    
    elligible_no_vl = elligible_no_pmtct[elligible_no_pmtct.last_vl_result.isnull()]
    elligible_no_vl_pmtct = elligible_pmtct[elligible_pmtct.last_vl_result.isnull()]
    
    invalid_below_25 = (elligible_no_pmtct[(elligible_no_pmtct.last_vl_date < pd.to_datetime(date.today() + relativedelta(months=-6)))]
                        .query('age_at_reporting <=24'))
    valid_below_25 = (elligible_no_pmtct[(elligible_no_pmtct.last_vl_date >= pd.to_datetime(date.today() + relativedelta(months=-6)))]
                        .query('age_at_reporting <=24'))
    
    invalid_above_25 = (elligible_no_pmtct[(elligible_no_pmtct.last_vl_date < pd.to_datetime(date.today() + relativedelta(months=-12)))]
                        .query('age_at_reporting>=25'))
    valid_above_25 = (elligible_no_pmtct[(elligible_no_pmtct.last_vl_date >= pd.to_datetime(date.today() + relativedelta(months=-12)))]
                        .query('age_at_reporting>=25'))
    
    full_valid_df = pd.concat([valid_above_25, valid_below_25, valid_pmtct], ignore_index=True)
    full_invalid_df = pd.concat([elligible_no_vl, elligible_no_vl_pmtct , invalid_pmtct, invalid_below_25, invalid_above_25], ignore_index=True)
    
    full_valid_df = full_valid_df.assign(validity = 'valid')
    full_invalid_df = full_invalid_df.assign(validity = 'invalid')
    not_elligible = not_elligible.assign(validity = 'not_elligible')
    
    final_linelist = pd.concat([not_elligible, full_invalid_df, full_valid_df], ignore_index=True)
    
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
        if val >=15 and val <=19:
            return '15-19 years'
        if val >=20 and val <=24:
            return '20-24 years'
        return '25+ years'
    pivot_linelist = pivot_linelist.assign(age_category=pivot_linelist.age_at_reporting.apply(age_grouping))
    
    high_vl = pivot_linelist[pivot_linelist.vl_category.eq('unsuppressed')]
    due_for_repeat = high_vl[(high_vl.last_vl_date < pd.to_datetime(date.today() + relativedelta(months=-3)))]
    
    validtable = pivot_linelist.query('validity == "valid"')
    suppressedtable = validtable.query('vl_category == "suppressed"')
    
    pmtct_valid = validtable.query('active_in_pmtct == "Yes"')
    pmtct_suppressed = pmtct_valid.query('vl_category == "suppressed"')
    
    pivot_linelist = pivot_linelist.replace(0, "LDL")
    
    vl_status = pivot_linelist.merge(pendingresults[["ccc_no","order_status"]], on=["ccc_no"], how='left')
                        
    #SECTION 4: VISUALIZATIONS
    with st.container():
        metric1,metric2,metric3,metric4,metric5,metric6 = st.columns(6)
        
        with metric1:
            ui.metric_card(title="Active on ART",
                    content=(linelist.shape[0]),
                    description="adults & children active on antiretroviral therapy")
        with metric2:
            ui.metric_card(title="Elligible for VL",
                    content=(elligible_df.shape[0]),
                    description="active clients on ART for a period more than 3 mnths")
        with metric3:
            ui.metric_card(title="TX_PVLS (D)",
                    content=(full_valid_df.shape[0]),
                    description="elligible clients with a valid documented vl result")
        with metric4:
            ui.metric_card(title="Invalid VLs",
                    content=(pivot_linelist.query('validity == "invalid"').shape[0]),
                    description="elligible clients with no valid documented vl result") 
        with metric5:
            ui.metric_card(title="Pending Results",
                    content=(vl_status.query('validity == "invalid"').query('order_status == "pending results"').shape[0]),
                    description="Invalid but with an active sample collected in EMR")
        with metric6:
            ui.metric_card(title="TX_PVLS (N)",
                    content=(validtable.query('vl_category == "suppressed"').shape[0]),
                    description="valid documented viral loads below 200copies/ml")
            
    with st.container(border=True):
        def df_to_csv(df):
            header = ["ccc_no", "sex", "age_at_reporting", "active_in_pmtct",
                        "elligibility_status", "validity", "vl_category","last_vl_date", "next_appointment_date", "order_status"]
            return df.to_csv(index=False, columns=header).encode("utf-8")
                
        final_analysis_csv = df_to_csv(vl_status)
        invalids = vl_status[vl_status.validity.eq("invalid")]
        invalids_to_bled = invalids[invalids.order_status.isnull()]
        dwnldtext, dwnld1, dwnld2, dwnld3, dwnld4, dwnld5 = st.columns(6)
        with dwnldtext:
            st.write(":green[**Download Analytics Results :**]")
        with dwnld1:
            st.download_button(
                label="**_Full VL Indicator Analysis Linelist_**",
                data=final_analysis_csv,
                file_name=f'{facility_name} VL_Analysis {date.today().strftime("%d-%m-%Y")}.csv', 
                mime="text/csv")
        with dwnld2:
            st.download_button(
                label="**_Suppression Pivot Table_**",
                data=(((pivot_linelist
                        .query('elligibility_status == "elligible"')
                        .query('validity == "valid"')
                        ).groupby(['age_category','active_in_pmtct','vl_category'])['vl_category'].count()).to_csv(index=False)),
                file_name=f'{facility_name} Suppression Table {date.today().strftime("%d-%m-%Y")}.csv', 
                mime="text/csv")
        with dwnld3:
            st.download_button(
                label="**_PMTCT Client VL Indicators_**",
                data=(vl_status.query('active_in_pmtct == "Yes"').to_csv(index=False)),
                file_name=f'{facility_name} PMTCT Client VL Status {date.today().strftime("%d-%m-%Y")}.csv', 
                mime="text/csv")
        with dwnld4:
            st.download_button(
                label="**_Invalid with Pending Results_**",
                data=(vl_status.query('validity == "invalid"').query('order_status == "pending results"')).to_csv(index=False),
                file_name=f'{facility_name} Invalid Pending Results {date.today().strftime("%d-%m-%Y")}.csv',
                mime="text/csv")      
        with dwnld5:
            st.download_button(
                label="**_Invalid with No Pending Results_**",
                data=invalids_to_bled.to_csv(index=False),
                file_name=f'{facility_name} Invalid to be bled {date.today().strftime("%d-%m-%Y")}.csv',
                mime="text/csv")
            
    valchart, vltable = st.columns((2,1))
    
    with valchart:
        with st.container(border=True):
            summary_chart = alt.Chart(pivot_linelist).mark_bar(cornerRadiusTopLeft=4,cornerRadiusTopRight=4).encode(
                alt.X('validity', title=""), 
                alt.Y('count()', title=""),
                alt.Color('sex:O', scale=alt.Scale(scheme='greens'),legend=alt.Legend(orient="top", title=""))).properties(width=110, height=250)
            
            text_chart = alt.Chart(pivot_linelist).mark_text(
                align="center", baseline="middle",dx=1, dy=-7,
                fontSize=10).encode(text="count()", x='validity', y='count()')
            
            chart = (summary_chart + text_chart).facet(
                column='age_category', title=alt.Title("vl uptake summary based on defined age categories and sex", color="green",
                subtitle="viral load status for all clients currently on antirhetroviral therapy.",
                subtitleColor="grey")).configure_header(title=None)
            
            st.altair_chart(chart, use_container_width=True)
            st.write(f'**:green[vl uptake:]** {(np.round(full_valid_df.shape[0]/elligible_df.shape[0], decimals=2)*100)}' + "%")
            
    with vltable:
        with st.container(border=True):
            validsumtable = pivot_linelist[pivot_linelist.validity.eq('valid')]
            summarytable = validsumtable.groupby(
                ['age_category','vl_category']).agg(
                    total=('ccc_no','count'))
            summarytable.index.names = ['group','status']
            vlsum = summarytable.reset_index()
            st.caption("**suppression status for all valid clients based on 200copies/ml cuttoff grouped based on age categories.**")
            ui.table(vlsum)
            st.write(f'**:green[suppression rate:]** {(np.round(suppressedtable.shape[0]/validtable.shape[0], decimals=2)*100)}' + "%")
            
    pmtct_valid = validtable.query('active_in_pmtct == "Yes"')
    pmtct_suppressed = pmtct_valid.query('vl_category == "suppressed"')
    
    with st.container(border=True):
        age_at_reporting = vl_status['age_at_reporting'].unique().tolist()
        genders = vl_status['sex'].unique().tolist()
        pmtct_status = vl_status['active_in_pmtct'].unique().tolist()
        
        age_range = st.slider('**move sliders to select desired age range:**',
                              min_value=min(age_at_reporting),
                              max_value=max(age_at_reporting),
                              value=(min(age_at_reporting),max(age_at_reporting)))
        
        selections, dataframe = st.columns((1,3))
        
        with selections:
            gender_selection = st.multiselect('**Sex:**', genders, default=genders)
            pmtct_selection = st.multiselect('**Enrolled in PMTCT:**', pmtct_status, default=pmtct_status)
        
            selection = ((vl_status['age_at_reporting'].between(*age_range)) & (vl_status['sex'].isin(gender_selection)) & (vl_status['active_in_pmtct'].isin(pmtct_selection)))
            data_display = vl_status[selection]
            
            records_found = data_display.shape[0]
            elligible_found = (data_display.query('elligibility_status == "elligible"')).shape[0]
            valid_found = (data_display.query('validity == "valid"')).shape[0]
            invalid_found = (data_display.query('validity == "invalid"')).shape[0]
            pending_found = (data_display.query('validity == "invalid"').query('order_status == "pending results"')).shape[0]
            suppressed_found = (data_display.query('validity == "valid"').query('vl_category == "suppressed"')).shape[0]
            unsuppressed_found = (data_display.query('validity == "valid"').query('vl_category == "unsuppressed"')).shape[0]

            st.write(f'{records_found} clients found within selection.')
            st.write(f'{elligible_found} are elligible for vl')
            st.write(f'{valid_found} with valid vls')
            st.write(f'{invalid_found} invalid with {pending_found} pending results')
            st.write(f'{suppressed_found} suppressed; and {unsuppressed_found} unsuppressed')
        
            selection_csv = df_to_csv(data_display)
            
            st.download_button(
                label="**_download selected data_**",
                data=selection_csv,
                file_name=f'{facility_name} age selection data {date.today().strftime("%d-%m-%Y")}.csv', 
                mime="text/csv")
            
        with dataframe:
            st.dataframe(data_display[['ccc_no','sex','age_at_reporting','art_start_date', 'elligibility_status','last_vl_result','last_vl_date','validity','vl_category','order_status']],
                     hide_index=True, use_container_width=True, height=400)
        
    with st.container(border=True):
        pivot_linelist['art_cohort_year']= pivot_linelist.art_start_date.dt.year
        pivot_linelist['art_cohort_month']= pivot_linelist.art_start_date.dt.month_name()
        
        validtable = pivot_linelist[pivot_linelist.validity.eq('valid')]
        suppressedtable = (pivot_linelist.query('validity=="valid"').query('vl_category=="suppressed"'))

        cohortvalid = validtable.pivot_table(index='art_cohort_year',
                                            columns='art_cohort_month', aggfunc={'vl_category':'count'})

        cohortsuppressed = suppressedtable.pivot_table(index='art_cohort_year',
                                                    columns='art_cohort_month', aggfunc={'vl_category':'count'})

        cohortsuppression = cohortsuppressed.div(cohortvalid)
        cohortsuppression.columns = cohortsuppression.columns.droplevel(0)
        cohortsuppression.columns.name = None
        
        cohortperc = cohortsuppression.apply(lambda x: x * 100)
        cohortperc = cohortperc.round(2)
        artcohort = cohortperc[['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']]
        
        fig = px.imshow(artcohort, 
                        text_auto=True, color_continuous_scale='greens', 
                        contrast_rescaling='infer', aspect='auto')
        
        fig.update_layout(coloraxis_showscale=False)
        fig.update_xaxes(side="top")
        fig.update_yaxes(nticks=25)
        fig.update_layout(yaxis_title=None)
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)
        fig.update_traces(xgap=1)
        fig.update_traces(ygap=1)
        
        st.write("**:green[ART cohort suppression rates (%)]**")
        st.caption("A **cohort** is a group of subjects that share a defining characteristic and a cohort has three main attributes: **_time_**, **_size_** and **_behaviour_**. This heatmap represents clients, actively on care, who started antiretroviral therapy on the same month of the same year. Values represented in terms of percentages of those suppressed i.e., **_the percentage of ART patients within the cohort with a valid documented viral load (VL) result that is below <200 copies/ml._**")
        st.plotly_chart(fig, use_container_width=True)
        
#wayne_willis_omondi
