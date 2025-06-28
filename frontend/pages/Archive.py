import os
import streamlit as st
import json
from datetime import date,datetime
import pandas as pd
import matplotlib.pyplot as plt
import requests
# import asyncio #testing purpose


def call_container():
    st.sidebar.title("Stored Chats")
    
    
def clear():
    resp_del=resp_exp=requests.post("http://127.0.0.1:8000/clear_db")
    if resp_del.status_code==200:
        count=int(resp_del.json()["status"])
        if count>0:
            st.sidebar.success(f"All records deleted->total  {count} deleted")
        else:
            st.sidebar.error("No previous chats to delete")
    else:
        st.sidebar.error("Oops Error kindly retry")

def chat_exporter():
    resp_exp=requests.post("http://127.0.0.1:8000/export_chat")

    st.download_button(
        label="📥 Download All Chats",
        data=json.dumps(resp_exp.json(), indent=2),
        file_name=f"complete_data_date_{date.today()}.json",
        mime="application/json"
    )





# Buttons
clear_hist = st.sidebar.button("Clear Complete history")
chat_log_export = st.sidebar.button("Export Complete chats")




if clear_hist:
    clear()

if chat_log_export:
    chat_exporter()


#--------------------------------------------------------------------------------------------------
st.title("Chat history ..")

st.header("🗃️   Filter By")
option = st.selectbox(
    "",
    ("No Filters","Date","Session_Id"),
)

st.write("You selected:", option)
if option=="Date":
    chat_date=st.date_input(label="Date")
    delete_tgl=st.toggle("Delete chat")
    btn=st.button(label="Submit Date")
    if btn:
        resp=requests.post("http://127.0.0.1:8000/chat_retriever_date",json={"date_":str(chat_date)})
        data=resp.json()
        if len(data)==0:
            st.error("No Chat history")
        else:
            for dct in data:
                for k,v in dct.items():
                    if k=="Unique_id":
                        st.markdown(f"Unique_id  : {v}")
                        continue
                    with st.chat_message(k):
                        st.markdown(v)
            st.download_button(
                label=f"📥 Download Chats on {str(chat_date)}",
                data=json.dumps(data),
                file_name=f"complete_data_date_{str(chat_date)}.json",
                mime="application/json"
            )
            st.button(f"🗑️ Clear All Chats on {str(chat_date)}")
            if delete_tgl:
                st.warning("""Note...\n\n
                        press submit date first in order to get unique id of chats,
                    which you can paste in the unique_id box to delete a particular chat.""")
                uid=st.text_input(label="Unique Id",placeholder="Enter Unique id give below each chat")
                btn1=st.button("submit Unique_id")
                if btn1:
                    res_del=requests.post("http://127.0.0.1:8000/del_chat",json={"date_":str(chat_date),"id_":str(uid)})
                    if res_del.json()["status"]=="no chats matched selection criteria":
                        st.error(res_del.json()["status"])
                    else:
                        st.success(res_del.json()["status"])
    
elif option=="Session_Id":
    date_=st.date_input(label="Date")
    delete_tgl=st.toggle("Delete chat")
    date_=str(date_)
    st.sidebar.header(f"Sessions on {date_[8:]}-{date_[5:7]}-{date_[:4]}")
    if date:
        resp=requests.post("http://127.0.0.1:8000/sesh_retriever_chat",json={"date_":date_})
        sesh_list=resp.json()["sessions"]
        if len(sesh_list)==0:
            st.error("No chat history")
        else:
            for sesh in sesh_list:
                st.sidebar.markdown(sesh)
        sesh_id=st.text_input(label="Session_Id",placeholder="Paste session id")
        submit=st.button("Submit")
        if submit:
            if not sesh_id:
                st.error("Kindly paste valid session_id from sidebar")
            else:
                resp=requests.post("http://127.0.0.1:8000/chat_retriever_sesh",json={"date_":date_,"sesh_id":str(sesh_id)})
                data=resp.json()
                if len(data)==0:
                    st.error("No Chat history")
                else:
                    for dct in data:
                        for k,v in dct.items():
                            if k=="Unique_id":
                                st.markdown(f"Unique_id  : {v}")
                                continue
                            with st.chat_message(k):
                                st.markdown(v)
                    st.download_button(
                        label=f"📥 Download Chats in session:{sesh_id}",
                        data=json.dumps(data),
                        file_name=f"complete_data_date_{sesh_id}.json",
                        mime="application/json"
                    )
                    st.button(f"🗑️ Clear All Chats in session: {str(sesh_id)}")
                    if delete_tgl:
                        st.warning("""Note...\n\n
                                press submit date first in order to get unique id of chats,
                            which you can paste in the unique_id box to delete a particular chat.""")
                        uid=st.text_input(label="Unique Id",placeholder="Enter Unique id give below each chat")
                        btn1=st.button("submit Unique_id")
                        if btn1:
                            res_del=requests.post("http://127.0.0.1:8000/del_chat",json={"date_":str(date_),"id_":str(uid)})
                            if res_del.json()["status"]=="no chats matched selection criteria":
                                st.error(res_del.json()["status"])
                            else:
                                st.success(res_del.json()["status"])


elif option=="No Filters":
    delete_tgl=st.toggle("Delete chat")
    btn=st.button(label="Submit")
    if btn:
        resp=requests.post("http://127.0.0.1:8000/chat_retriever_all",json={})
        data=resp.json()
        if len(data)==0:
            st.error("No Chat history")
        else:   
            for dct in data:
                for k,v in dct.items():
                    if k=="Unique_id":
                        st.markdown(f"Unique_id  : {v}")
                        continue
                    with st.chat_message(k):
                        st.markdown(v)
            if delete_tgl:
                st.warning("""Note...\n\n
                        press submit date first in order to get unique id of chats,
                    which you can paste in the unique_id box to delete a particular chat.""")
                uid=st.text_input(label="Unique Id",placeholder="Enter Unique id give below each chat")
                btn1=st.button("submit Unique_id")
                if btn1:
                    res_del=requests.post("http://127.0.0.1:8000/del_chat",json={"id_":str(uid)})
                    if res_del.json()["status"]=="no chats matched selection criteria":
                        st.error(res_del.json()["status"])
                    else:
                        st.success(res_del.json()["status"])