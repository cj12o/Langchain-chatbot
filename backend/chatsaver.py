from pydantic import BaseModel
import os
from datetime import date,datetime
from fastapi import APIRouter,FastAPI,HTTPException
import json
from uuid import uuid4,uuid3
from pydantic import BaseModel
import asyncio
from fastapi.responses import StreamingResponse
from database import collection
# from bson import ObjectId,_encode_text
from typing import Optional
router=APIRouter()

class Chats(BaseModel):
    user:str
    ai:str
    sessionid:str

class get_chat(BaseModel):
    date_:Optional[str]=None
    sesh_id:Optional[str]=None

class del_chat(BaseModel):
    date_:Optional[str]=None
    id_:Optional[str]=None

class Model(BaseModel):
    user:str
    ai:str
    sessionid:str
    # id:int 



async def insert_in_db(chats):
    try:
        result=await collection.insert_one({
            "user":chats["user"],
            "AI":chats["ai"],
            "session_id":chats["session_id"],
            "Date":str(date.today()),
            "Unique_id":str(uuid4())
        })
        print(f"Success in inserting {result.inserted_id}")
    except Exception as e:
        print(f"Error {e}")

@router.post('/savechats')
async def SaveChat(content:Chats):
    chats={"user":content.user,"ai":content.ai,"session_id":content.sessionid}
    await insert_in_db(chats=chats)


# @router.post('/chat_retriever')
@router.post('/chat_retriever_date')
async def chatretriever_date(dateee:get_chat):
    #note no await with cusor
    cursor=collection.find({"Date":dateee.date_},{"user":1,"AI":1,"Unique_id":1})
    # print(cursor)
    lst=[]
    try:
        async for ele in cursor:
            # print(ele)
            ele.pop('_id')
            lst.append(ele)
    except Exception as e:
        # return {"Erorr":e}
        print(f"Error:{e}")
    return lst


@router.post('/chat_retriever_sesh')
async def chatretriever_sesh(dateee:get_chat):
    #note no await with cusor
    cursor=collection.find({"Date":dateee.date_,"session_id":dateee.sesh_id},{"user":1,"AI":1,"Unique_id":1})
    # print(cursor)
    lst=[]
    try:
        async for ele in cursor:
            # print(ele)
            ele.pop('_id')
            lst.append(ele)
    except Exception as e:
        # return {"Erorr":e}
        print(f"Error:{e}")
    return lst

@router.post('/chat_retriever_all')
async def chatretriever_all():
    #note no await with cusor
    cursor=collection.find({},{"user":1,"AI":1,"Unique_id":1})
    # print(cursor)
    lst=[]
    try:
        async for ele in cursor:
            # print(ele)
            ele.pop('_id')
            lst.append(ele)
    except Exception as e:
        # return {"Erorr":e}
        print(f"Error:{e}")
    return lst


@router.post('/del_chat')
async def delete_db(entry:del_chat):
    if not entry.date_:
        result=await collection.delete_one({"Unique_id":entry.id_})
    else:
        result=await collection.delete_one({"Date":entry.date_,"Unique_id":entry.id_})
    # print(result)
    if result.deleted_count>0:
        if result.deleted_count>1:
            return {"status":f"successfully deleted {result.deleted_count} records"}
        return {"status":f"successfully deleted {result.deleted_count} record."}
    else:
        return {"status":"no chats matched selection criteria"}

# asyncio.run(chatretriever(get_chat(date_="2025-06-24")))#TEST
        

@router.post('/export_chat')
async def export():
    cursor=collection.find()
    lst=[]
    #ObjectId to str for json serialization
    try:
        async for doc in cursor:
            doc['_id']=str(doc['_id'])
            lst.append(doc)
        return lst
    except Exception as e:
        raise HTTPException(status_code=404,detail=f"Error : {e}")
    
@router.post('/clear_db')
async def drop_collec():
    try:
        result=await collection.delete_many({})
        # raise HTTPException(status_code=402,detail="Success")
        return {"status":f"{result.deleted_count}"}
    except Exception as e:
        return {"status":"error"}

# asyncio.run(drop_collec()) #test


@router.post('/sesh_retriever_chat')
async def getsesh_chat(dateee:get_chat):
    cursor=await collection.distinct("session_id",{"Date":dateee.date_})
    return {"sessions":cursor}
