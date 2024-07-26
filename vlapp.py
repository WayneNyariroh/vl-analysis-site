#wayne_willis_omondi
import streamlit as st
import streamlit_shadcn_ui as ui
import pandas as pd
import numpy as np
import altair as alt
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta

#SECTION 1: THE PAGE
img = "assets\prescription.png"

def page_styling():
    st.set_page_config(
        page_title="wayne: facility viral load analyst",
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
#with st.container():
    pic, about = st.columns((1,3))
    with pic:
        ui.avatar(src="https://i.etsystatic.com/38806485/r/il/5fa54b/5521669591/il_570xN.5521669591_25tt.jpg")
    with about:
        st.markdown('''[wayne willis](https://www.linkedin.com/in/waynewillislink/)''')
        
    st.title('Viral Load Analyst `version 1.5` ')
    st.caption("Analyse your clients' :green[viral load indicators] with a just simple linelist upload")
    st.caption("- 0 t0 24 years as well as pmtct vl on 6 month-basis and 25+ on a 12 month-basis.")
    
#SECTION 2:THE DATA
    upload_linelist_csv = st.file_uploader("**Upload today's Active on ART Linelist below (csv only)** ", type=['csv'])
  
if upload_linelist_csv is not None:
    #@st.cache_data
    def load_csv():
        df = pd.read_csv(upload_linelist_csv, 
                        usecols=['MFL Code','CCC No', 'Sex', 'Age at reporting','Art Start Date','Last VL Result','Last VL Date', 'Active in PMTCT','Next Appointment Date'],
                        parse_dates=['Art Start Date','Last VL Date','Next Appointment Date']) 
        return df
    data = load_csv()
    
    data.columns = [x.lower().replace(" ","_") for x in data.columns]
#upload_pending_csv = st.file_uploader("**2. Upload today's Viral Load and CD4 Lab requests pending Report (csv only)** ", type=['csv'])
#ui.alert_dialog(show=upload_csv, title=" ", description="Upload Successfully", confirm_label="OK", key="alert_dialog_1")

    def prep_df(data):
        return (data
                .assign(ccc_no = data.ccc_no.astype(str),
                        art_start_date = pd.to_datetime(data.art_start_date),
                        last_vl_date = pd.to_datetime(data.last_vl_date),
                        next_appointment_date = pd.to_datetime(data.next_appointment_date))
                )
    linelist = prep_df(data)
    
#a part of section 1 to get the facility information
    st.write(" ")
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

    #SCETION 3: ANALYTICS
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
    
                        
    #SECTION 4: VISUALIZATIONS
    with st.container():
        metric1,metric2,metric3,metric4,metric5, downloads = st.columns(6)
        
        with metric1:
            ui.metric_card(title="TX_CURR",
                    content=(linelist.shape[0]),
                    description="adults and children currently on antiretroviral therapy")
        with metric2:
            ui.metric_card(title="Elligible for VL",
                    content=(elligible_df.shape[0]),
                    description="active clients on ART for a period more than 3 mnths")
        with metric4:
            ui.metric_card(title="TX_PVLS (N)",
                    content=(validtable.query('vl_category == "suppressed"').shape[0]),
                    description="valid documented viral loads below 200copies/ml")
        with metric3:
            ui.metric_card(title="TX_PVLS (D)",
                    content=(full_valid_df.shape[0]),
                    description="elligible clients with a valid documented viral result")
        with metric5:
            ui.metric_card(title="Due For Repeat VL",
                    content=(due_for_repeat.shape[0]),
                    description="high vl clients due for repeat vl i.e. 3 mnths since result") 
        with downloads:
            def df_to_csv(df):
                header = ["ccc_no", "sex", "age_at_reporting", "active_in_pmtct","elligibility_status", "validity", "vl_category", "last_vl_date", "next_appointment_date"]
                return df.to_csv(index=False, columns=header).encode("utf-8")
                    
            final_analysis_csv = df_to_csv(pivot_linelist)
            repeat_csv = df_to_csv(due_for_repeat)
            
            with st.container():
                st.write("Click to download results from the analysis")
                st.download_button(
                    label="**_VL Analysis Results_**",
                    data=final_analysis_csv,
                    file_name=f'{facility_name} VL_Analysis {date.today().strftime("%d-%m-%Y")}.csv', 
                    mime="text/csv")
                st.download_button(
                    label="**_Suppression Pivot Table_**",
                    data=(((pivot_linelist
                            .query('elligibility_status == "elligible"')
                            .query('validity == "valid"')
                            ).groupby(['age_category','active_in_pmtct','vl_category'])['vl_category'].count()).to_csv()),
                    file_name=f'{facility_name} Suppression Table {date.today().strftime("%d-%m-%Y")}.csv', 
                    mime="text/csv")
                st.download_button(
                label="**_Due for Repeat VL_**",
                    data=repeat_csv,
                    file_name=f'{facility_name} Unsuppressed_due_for_repeat_VL_as_at_{date.today().strftime("%d-%m-%Y")}.csv', 
                    mime="text/csv")
                
    valchart, vltable = st.columns((2,1))
    
    with valchart:
        with st.container(border=True):
            summary_chart = alt.Chart(pivot_linelist).mark_bar(cornerRadiusTopLeft=4,cornerRadiusTopRight=4).encode(
                x=alt.X('validity').title(""), 
                y=alt.Y('count()').title(""),
                color=alt.Color('sex:O').scale(scheme="viridis")).properties(
                    width=110, 
                    height=243).facet(column='age_category', 
                                    title=alt.Title("vl uptake summary based on defined age categories and sex",
                                                    color="green",
                                        subtitle="viral load status for all clients currently on antirhetroviral therapy. patients who have been on ART for less than 3 months considered 'not elligible'.",
                                        subtitleColor="grey")).configure_header(
                                            title=None
                                        )

            st.altair_chart(summary_chart, use_container_width=True)
            st.write(f'**:green[vl uptake:]** {(np.round(full_valid_df.shape[0]/elligible_df.shape[0], decimals=2)*100)}' + "%")
            
    with vltable:
        with st.container(border=True):
            #st.caption("**:green[suppression]** status (200 cp/ml cutt-off) for the **:green[valid]** documented viral loads")
            validsumtable = pivot_linelist[pivot_linelist.validity.eq('valid')]
            summarytable = validsumtable.groupby(
                ['age_category','vl_category']).agg(
                    total=('ccc_no','count'))
            summarytable.index.names = ['group','status']
            vlsum = summarytable.reset_index()
            ui.table(vlsum)
            st.write(f'**:green[suppression rate:]** {(np.round(suppressedtable.shape[0]/validtable.shape[0], decimals=2)*100)}' + "%")
            
    pmtct_valid = validtable.query('active_in_pmtct == "Yes"')
    pmtct_suppressed = pmtct_valid.query('vl_category == "suppressed"')
    
    
    
    
#wayne_willis_omondi
