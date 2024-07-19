import streamlit as st
import pandas as pd
import altair as alt
import datetime
import time

from streamlit_extras.metric_cards import style_metric_cards

st.set_page_config(
    page_title="KCCB-ACTs Facility Viral Load Analysis",
    page_icon="assets\prescription.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """<style>
    #MainMenu {visibility:hidden;}
    footer {visibility:hidden;}
    </style>""", unsafe_allow_html=True)

st.markdown(
    """<style>
    .block-container {
        padding-top: 0.5rem;}</style>""", unsafe_allow_html=True)

with st.sidebar:
    cal_watch = datetime.datetime.now()
    st.button(f':calendar: {cal_watch.strftime("%d/%m/%Y")}', disabled=True)
    st.subheader('KCCB-ACTs Facility Viral Load Analysis `version 2.0` ')
    st.caption("mapping of sites supported by ***KCCB-ACTS*** with additional visualizations. "
                "First tab - :orange[Site Locations] - maps all the facilities, grouping them into proximity clusters depending on zoom level. ")
 
    upload_csv = st.file_uploader("Upload Recent Active on ART Linelist (CSV only)")
    if upload_csv is not None:
        df = pd.read_csv(upload_csv)
        
    st.divider()
    st.markdown('''Made by [Wayne Omondi](https://www.linkedin.com/in/waynewillislink/)
                    ''')
with st.container:
    metric1,metric2,metric3 = st.columns(3)
    
    with metric1:
        st.metric(label="TX_Curr",
                  value=(df.shape[0].astype(str))
                  )
    with metric2:
        st.metric(label="Active in PMTCT",
                value=(df['Active in PMTCT'].eq('Yes').astype(str)))


    st.write(df)
    