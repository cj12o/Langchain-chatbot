from database import collection_metrics
from pydantic import BaseModel
from typing import Optional
import asyncio
from fastapi import HTTPException,APIRouter,FastAPI

router=APIRouter()

class metric_model(BaseModel):
    date_:str
    session_id:str
    input_Tokens:int
    total_time:float
    ttft:float
    totaltokens:int
    tokens_per_second:float
    temp:float
    context_:str

class filtermodel(BaseModel):
    date_:Optional[str]=None
    session_id:Optional[str]=None


async def insert_metrics(metrics:metric_model):
    try:
        result=await collection_metrics.insert_one({"Date":metrics.date_,
            "session_Id":metrics.session_id,
            "input_tok":metrics.input_Tokens,
            "total_Time":metrics.total_time,
            "ttft":metrics.ttft,
            "tokens_gen":metrics.totaltokens,
            "tok_per_sec":metrics.tokens_per_second,
            "temp":metrics.temp,
            "context":metrics.context_})
        if not result.acknowledged:
            raise HTTPException(status_code=500,detail=f"Error in metrics logging")
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error{e}")

@router.post('/sesh_retriever')
async def getsesh(filt:filtermodel):
    cursor=await collection_metrics.distinct("session_Id",{"Date":filt.date_})
   
    return {"sessions":cursor}

@router.post('/get_metrics')
async def getmetrics(criteria:filtermodel):
    try:
        lst=[]
        if criteria.date_ and criteria.session_id:
            cursor=collection_metrics.find({"Date":criteria.date_,"session_Id":criteria.session_id})
        elif criteria.date_:
            cursor=collection_metrics.find({"Date":criteria.date_})
        else:
            cursor=collection_metrics.find({})
        async for ele in cursor:
            ele.pop('_id')#for json serilaization
            lst.append(ele)
        return {"response":lst}
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error {e}")
    

# asyncio.run(getmetrics(filtermodel()))