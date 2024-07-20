import streamlit as st
import pandas as pd
import altair as alt
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
import time

from streamlit_extras.metric_cards import style_metric_cards

#function to style the page - remove menu, footer and top spacing; set web title, layout
def page_styling():
    st.set_page_config(
        page_title="Facility Viral Load Analysis",
        page_icon="assets\prescription.png",
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
    
#call the function
page_styling()

#sidebar
with st.sidebar:
    cal_watch = datetime.datetime.now()
    st.button(f'{cal_watch.strftime("%d/%m/%Y")}', disabled=True)
    
    st.subheader('Facility Viral Load Analysis `version 2.0` ')
    st.caption("Analyse your facility's client :green[viral loads] within a few seconds with a simple upload")
 
    upload_csv = st.file_uploader("Upload Recent Active on ART Linelist (CSV only)", type=['csv'])
    
    st.markdown('''Made by [Wayne Omondi](https://www.linkedin.com/in/waynewillislink/)
                    ''')
if upload_csv is not None:
    @st.cache
    def load_csv():
        csv = pd.read_csv(upload_csv, 
                            usecols=['CCC No', 'Sex', 'Age at reporting','Art Start Date','Last VL Result','Last VL Date', 'Active in PMTCT', 'Self Visit Date','Next Appointment Date'],
                            parse_dates=['Art Start Date','Last VL Date','Self Visit Date','Next Appointment Date'])
        return csv
    
    data = load_csv()
else:
    #what displays while upload hasnt been done yet
    st.info("Awaiting **_Active on ART Linelist_** upload for analysis") 

#st.write(data)

#st.write(data.dtypes)
    
    #st.divider()
data.columns = [x.lower().replace(" ","_") for x in data.columns]

def prep_df(data):
    return (data
            .assign(art_start_date = pd.to_datetime(data.art_start_date),
                    last_vl_date = pd.to_datetime(data.last_vl_date),
                    self_visit_date = pd.to_datetime(data.self_visit_date),
                    next_appointment_date = pd.to_datetime(data.next_appointment_date))
                    )
df = prep_df(data)

#the various analysis needed
#elligible for vl means clients who have been active on an ART regimen 
#validity of vl - 0-24 years and pmtct vl is valid if done in the last 6 months
#elligible df to be used for all other analysis
elligible_df = df[(df.art_start_date < pd.to_datetime(date.today() + relativedelta(months=-3)))]

#place all components within a container
with st.container():
    metric1,metric2,metric3 = st.columns(3)
    
    with metric1:
        st.metric(label="TX_Curr",
                  value=(df.shape[0])
                  )
    with metric3:
        st.metric(label="Active in PMTCT",
                value=(df[df['active_in_pmtct'].eq('Yes')].shape[0]))

    with metric2:
            st.metric(label="Clients Elligible for VL Uptake",
                    value=(elligible_df.shape[0]))

    st.write(elligible_df)