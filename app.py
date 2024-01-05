import streamlit as st
from interaction import generateInteractionPoints
from tqdm import tqdm
import random
import datetime
import pandas as pd
import plotly.express as px
import os
st.set_page_config(layout="wide")

def get_chart(df, col):
    fig = px.line(df, x="Mu (kN.m)", y="Pu (kN)", color="Pt (%)",height=580, width=400)
    fig.update_traces(textposition="bottom right")
    fig.update_layout(autosize=True)
    col.plotly_chart(fig, theme="streamlit", use_container_width=True)




st.header("Column Interaction Plot Generator 📈")
col1, col2, col3 = st.columns([1,1,1])
col1.subheader("Required Inputs")
col2.subheader("Interaction Curve")
col3.subheader("Interaction Points")

form = col1.form("Input Form")
d = form.number_input("Depth (mm)",min_value=0, )
b = form.number_input("Width (mm)",min_value=0)
cc = form.number_input("Clear Cover (mm)",min_value=0)
fck = form.number_input("Characteristic Strength of Concrete (MPa)",min_value=0)
fy = form.number_input("Characteristic Strength of Steel (MPa)",min_value=0)
rd = form.selectbox(
    'Reinforcement Distribution',
    ('Equally Distributed in Each Four Sides', 'Equally Distributed in Two Sides'))
btn = form.form_submit_button("Generate Plot")
# oldfileid = ""
# fileid = ""

st.write('''Disclaimer:
1. This charts are prepared by following the SP 16 : 1980.
2. This tables are based on purely canculative basis.
3. No lab testing has being performed while calculating these data points.
4. The risk of using these are on the user.''')
st.write("©️ Copyright - All Rights Reserved Avishek Das 2024")
if btn:
    if not d:
        form.warning("Please Enter Depth of Column More Than Zero")
    if not b:
        form.warning("Please Enter Width of Column More Than Zero")
    if not cc:
        form.warning("Please Enter Clear Cover of Column More Than Zero")
    if not fck:
        form.warning("Please Enter Characteristic Strength of Concrete More Than Zero")
    if not fy:
        form.warning("Please Enter Characteristic Strength of Steel More Than Zero")
    rd = 1 if rd=="Equally Distributed in Each Four Sides" else 0
    # if oldfileid!="":
    #     os.remove(oldfileid)
    psByFck = [0.02,0.04,0.06,0.08,0.1,0.12,0.14,0.16,0.18,0.2,0.22,0.24]
    res_dicts = []
    dfs =[]
    for p in tqdm(psByFck):
        df = generateInteractionPoints(D = d, b=b, cc=cc, fck=fck, fy = fy, p = p*fck, reinforcement_dist=rd)
        dict_ = df.to_dict()
        dict_['xu/D'] = [dict_['xu/D'][i] for i in sorted(dict_['xu/D'].keys())]
        dict_['Pu'] = [dict_['Pu'][i] for i in sorted(dict_['Pu'].keys())]
        dict_['Mu'] = [dict_['Mu'][i] for i in sorted(dict_['Mu'].keys())]
        dict_['pt'] = round(p*fck,5)
        res_dicts.append(dict_)
        df['Pt (%)'] = round(p*fck,5)
        dfs.append(df[['Pt (%)', "Pu", 'Mu']])
    dfc = pd.concat(dfs, ignore_index=False)
    dfc.columns = ['Pt (%)', "Pu (kN)", 'Mu (kN.m)']
    dfc['Pt (%)'] = dfc['Pt (%)'].apply(str)
    col3.dataframe(dfc, hide_index=True, height=580,width=400)
    # col2.line_chart(dfc, x="Mu (kN.m)", y="Pu (kN)", color="Pt (%)")
    get_chart(dfc, col2)
    # fileid = "outputs/"+str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))+str(random.randint(100000,999999))+".xlsx"
    # oldfileid=fileid
    # dfc.to_excel(fileid, index=False)
    # with open(fileid, "rb") as f:
    #     download1 = st.download_button(
    #     label="Download data as XLSX",
    #     data=f,
    #     file_name='interaction_points.xlsx',)