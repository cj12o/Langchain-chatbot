import pandas as pd 
import datetime
from datetime import date
from typing import Optional
from pydantic import BaseModel
import streamlit as st
import csv
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests

DIR="C:/Users/BIT/Desktop/GPT Wrapper/llm_log"


import altair as alt

def plotter(colx, coly):
    df_rag =st.session_state.df[st.session_state.df["Context"] =="sessional"]
    df_chat = st.session_state.df[st.session_state.df["Context"] =="sessional+Know.Base"]
    

    df_rag=df_rag[[colx,coly,"Context"]]
    df_chat=df_chat[[colx,coly,"Context"]]

    #concat
    concaat=pd.concat([df_rag,df_chat],ignore_index=True)

    # Plot with Altair
    chart = alt.Chart(concaat).mark_line(point=True).encode(
        x=alt.X(colx, title=colx),
        y=alt.Y(coly, title=coly),
        color="Context"
    ).properties(
        width=600,
        height=400,
        title=f"{colx} vs {coly}"
    )
    st.altair_chart(chart, use_container_width=True)


dct={"Date":[],"Session_Id":[],"Input_Tokens":[],"Total_Time":[],"TTFT(time_to_get_first_token)":[],"Tokens_Generated":[],"Tokens_per_sec":[],"Temperature":[],"Context":[]}
if "df" not in st.session_state:
    st.session_state.df=pd.DataFrame(dct)


st.header("🗃️   Filter By")
option = st.selectbox(
    "",
    ("No Filters","Date","Session_Id"),
)

st.write("You selected:", option)
if option=="Date":
    date_=st.date_input(label="Select Date")
    btn1=st.button("submit")
    if btn1:
        resp=requests.post("http://127.0.0.1:8000/get_metrics",json={"date_":str(date_)})
        data=resp.json()["response"]
        st.session_state.df=pd.DataFrame(dct)
        for dct in data:
            newrow={"Date":[dct["Date"]],"Session_Id":[dct["session_Id"]],"Input_Tokens":[dct["input_tok"]],"Total_Time":[dct["total_Time"]],"TTFT(time_to_get_first_token)":[dct["ttft"]],"Tokens_Generated":[dct["tokens_gen"]],"Tokens_per_sec":[dct["tok_per_sec"]],"Temperature":[dct["temp"]],"Context":[dct["context"]]}
            newrow_df=pd.DataFrame(newrow)
            st.session_state.df=pd.concat([st.session_state.df,newrow_df])
        st.dataframe(st.session_state.df)

    viewcharts=st.button("View Analytics")
    if viewcharts:
        plotter("Total_Time","Tokens_Generated")
        plotter("Tokens_Generated","Temperature")
        plotter("Tokens_per_sec","Temperature")
        plotter("TTFT(time_to_get_first_token)","Temperature")




elif option=="Session_Id":
    date_=st.date_input(label="Select Date")
    date_=str(date_)
    st.sidebar.header(f"Sessions on {date_[8:]}-{date_[5:7]}-{date_[:4]}")
    if date:
        resp=requests.post("http://127.0.0.1:8000/sesh_retriever",json={"date_":date_})
        sesh_list=resp.json()["sessions"]
        for sesh in sesh_list:
            st.sidebar.markdown(sesh)
    sesh_id=st.text_input(label="Session_Id",placeholder="Paste session id")
    submit=st.button("Submit")
    if submit:
        if not sesh_id:
           st.error("Kindly paste valid session_id from sidebar")

        else:
            resp=requests.post("http://127.0.0.1:8000/get_metrics",json={"date_":date_,"session_id":str(sesh_id)})
            data=resp.json()["response"]
            st.session_state.df=pd.DataFrame(dct)
            for dct in data:
                newrow={"Date":[dct["Date"]],"Session_Id":[dct["session_Id"]],"Input_Tokens":[dct["input_tok"]],"Total_Time":[dct["total_Time"]],"TTFT(time_to_get_first_token)":[dct["ttft"]],"Tokens_Generated":[dct["tokens_gen"]],"Tokens_per_sec":[dct["tok_per_sec"]],"Temperature":[dct["temp"]],"Context":[dct["context"]]}
                newrow_df=pd.DataFrame(newrow)
                st.session_state.df=pd.concat([st.session_state.df,newrow_df])
            st.dataframe(st.session_state.df)

        viewcharts=st.button("View Analytics")
        if viewcharts and sesh_id:
            plotter("Total_Time","Tokens_Generated")
            plotter("Tokens_Generated","Temperature")
            plotter("Tokens_per_sec","Temperature")
            plotter("TTFT(time_to_get_first_token)","Temperature")






elif option=="No Filters":
    btn1=st.button("submit")
    if btn1:
        resp=requests.post("http://127.0.0.1:8000/get_metrics",json={})
        data=resp.json()["response"]
        st.session_state.df=pd.DataFrame(dct)
        for dct in data:
            newrow={"Date":[dct["Date"]],"Session_Id":[dct["session_Id"]],"Input_Tokens":[dct["input_tok"]],"Total_Time":[dct["total_Time"]],"TTFT(time_to_get_first_token)":[dct["ttft"]],"Tokens_Generated":[dct["tokens_gen"]],"Tokens_per_sec":[dct["tok_per_sec"]],"Temperature":[dct["temp"]],"Context":[dct["context"]]}
            newrow_df=pd.DataFrame(newrow)

            st.session_state.df=pd.concat([st.session_state.df,newrow_df])
        st.dataframe(st.session_state.df)

    viewcharts=st.button("View Analytics")
    if viewcharts:
        plotter("Total_Time","Tokens_Generated")
        plotter("Tokens_Generated","Temperature")
        plotter("Tokens_per_sec","Temperature")
        plotter("TTFT(time_to_get_first_token)","Temperature")
