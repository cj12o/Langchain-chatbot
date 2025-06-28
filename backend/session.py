import uuid
from fastapi import APIRouter


#cache
session={}
ttft=None
session_id=None

router=APIRouter()

from pydantic import BaseModel
from chatsaver import Chats


@router.post('/set_seshid')
def sessionidbuilder():
    global session_id
    session_id=str(uuid.uuid4())

def sessionbuilder():
    global session_id
    global session
    if session_id:
        if session_id not in session:
            session[session_id]=[]
    
def contextbuilder()->str:#sessional context
    global session_id
    global session
    context=""
    
    if len(session)>0 and session_id:
        for msg in session[session_id]:

            context+="\n\n".join([f'{msg["role"]}:{msg["content"]}'])
            
    return context

def addtosession(usermsg,content):
    global session_id
    global session
    if session_id:
        session[session_id].append({"role":"user","content":usermsg})
        session[session_id].append({"role":"AI","content":content})

def settime(time):
    global ttft
    ttft=time

@router.post('/ttft')#TTFT
def gettime():
    global ttft
    return ttft

@router.post('/sesh_id')
def getsessionid():
    global session_id
    return {"id":session_id}