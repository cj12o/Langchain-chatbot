import requests
import streamlit as st
import pyttsx3
import threading
import sys
import os
import time

import psutil#for ram usage

# Add parent path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from backend.llm_config import Maximum_token, temperature


# ------------------ Session Setup ------------------ #
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "tts_on" not in st.session_state:
    st.session_state.tts_on = False

if "slider" not in st.session_state:
    st.session_state.slider = Maximum_token

if "slider2" not in st.session_state:
    st.session_state.slider2 = temperature

if "use_history" not in st.session_state:
    st.session_state.use_history=False

if "rating" not in st.session_state:
    st.session_state.rating=-1

if "prev_metadata" not in st.session_state:
    st.session_state.prev_metadata=None

if "prev_resp" not in st.session_state:
    st.session_state.prev_resp=None
    
if "type" not in st.session_state:
    st.session_state.type=None

if "llm_status" not in st.session_state:
    st.session_state.llm_status=False


# ------------------ Display Messages ------------------ #
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ------------------ Sidebar ------------------ #
with st.sidebar:
    st.title("Settings ⚙️")
    slider_newval = st.slider("MAX TOKENS", min_value=0, max_value=800, value=st.session_state.slider)
    slider_newval2 = st.slider("TEMPERATURE", min_value=0.0, max_value=1.0, value=st.session_state.slider2, step=0.01)
    st.session_state.use_history=st.toggle(label="Use Previous Chats(Not in  this session)")
    texttospeech = st.toggle("Text To Speech 🗣️")
    st.session_state.tts_on = texttospeech
  
    if slider_newval != st.session_state.slider or slider_newval2 != st.session_state.slider2:
        try:
            resp = requests.post("http://127.0.0.1:8000/config", json={
                "token_lim": slider_newval,
                "temp": slider_newval2
            })
            if resp.status_code == 200:
                data = resp.json()
                st.session_state.slider = data["token_lim"]
                st.session_state.slider2 = data["temp"]
                st.success("Config updated successfully.")
            else:
                st.error("Error updating config.")
        except Exception as e:
            st.error(f"Config error: {e}")

    if st.button("Reset Sessional Context"):
        st.session_state.messages = []
        # st.session_state.session_id = None
        resp_reset=requests.post("http://127.0.0.1:8000/set_seshid")
        st.success("Session context reset.")


# ------------------ Chat Input & Response ------------------ #
with st.container():
    msg = st.chat_input("Enter your message")
    if st.session_state.tts_on==False:
        stop = st.button("🛑 Stop Generation")
        if stop:
            st.stop()


    if msg:

        with st.spinner("Generating response..."):
            try:
                request_payload = {"query": msg}
                
                response=None
                if st.session_state.use_history==True:
                    response = requests.post("http://127.0.0.1:8000/rag_response", json=request_payload,stream=True)
                else:
                    response = requests.post("http://127.0.0.1:8000/chat", json=request_payload,stream=True)
                full_content=""
                container=st.empty()
                st.sidebar.header("System Resource Usage..")
                cnin_ram1=st.sidebar.empty()
                cnin_ram2=st.sidebar.empty()
                contq=st.sidebar.empty()
                cntr=1
                for chunk in response.iter_content(chunk_size=None,decode_unicode=True):
                    full_content+=chunk
                    container.markdown(full_content)
                    try:
                        if cntr %10==0:
                            tupl=psutil.virtual_memory()
                            cnin_ram1.markdown(f"RAM Commited : {round(tupl.used/2**30,2)} Gb")
                            cnin_ram2.markdown(f"RAM Free : {round(tupl.free/2**30,2)} Gb")
                            # contq.markdown(f"LLM STATUS: {st.session_state.llm_status}")
                    except Exception as e:
                        st.error(e)
                    cntr+=1
            
                resp_session_id=requests.post("http://127.0.0.1:8000/sesh_id")
                


                
                st.session_state.messages.append({"role": "user", "content": msg})
                st.session_state.messages.append({"role": "assistant", "content": full_content})
                

                # Speak response if enabled
                if st.session_state.tts_on and full_content:
                    engine = pyttsx3.init()
                    engine.say(full_content)
                    engine.runAndWait()
                    engine.stop()
                    st.session_state.tts_on=False
            except Exception as e:
                st.error(f"Chat error: {e}")
