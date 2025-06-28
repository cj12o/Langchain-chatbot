from fastapi import FastAPI, APIRouter
from fastapi.responses import StreamingResponse
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from datetime import date
from contextlib import asynccontextmanager
import subprocess
import uuid
import time
import gc
import os
from dotenv import load_dotenv

from Tokenizer import gettokencount
from llm_config import router as router_llmconfig, llm_configurator, llmval,llm
from chatsaver import router as router_chatsaver, SaveChat, Chats
from rag import router as router_rag,_vector_store,indexing
from session import router as router_session,contextbuilder,session_id,addtosession, sessionbuilder,sessionidbuilder,settime,gettime
from metricsaver import router as metric_router,metric_model,insert_metrics
from database import collection,collection_metrics,collection_ragdocs
from rag_func import summerize

##sesh id initialize
if not session_id:
    sessionidbuilder()
from session import session_id




# Initialize config
llm_configurator()

class Myexception(Exception):
    pass


class DataModel(BaseModel):
    query: str
    session_id: str = None
    
# --------------------------------------------------- LIFESPAN ---------------------------------------------------
@asynccontextmanager
async def lifespan(api: FastAPI):
    global llm
    global _vector_store
    ls=[]
    ollama_proc=None
    result=collection_ragdocs.find({})
    async for ele in result:
        ls.append(ele)
    try:
        ollama_proc = subprocess.Popen(["ollama", "serve"])
        print("Ollama server started.")
        if len(ls)>0:
            await indexing()
        else:
            print("No previous chats to form vector Db.")
        yield
    finally:
        await summerize()
        if ollama_proc and ollama_proc.poll() is None:
            ollama_proc.terminate()
            ollama_proc.wait()
            print("embedding_model (Ollama server) Closed")
        if llm:
            print("LLM server connection is halted but lm studio is running. Manual shutdown needed to free system resources.")
            llm = None
            gc.collect()



# --------------------------------------------------- API/Routing ---------------------------------------------------
#
api = FastAPI(lifespan=lifespan)

api.include_router(router=router_llmconfig)
api.include_router(router=router_chatsaver)
api.include_router(router=router_rag)
api.include_router(router=router_session)
api.include_router(router=metric_router)
# --------------------------------------------------- PROMPT TEMPLATE ---------------------------------------------------
prompt_template = ChatPromptTemplate.from_messages([
    ("system", """
You are a friendly and efficient AI chatbot.

Your name is virtual friend.

At the start of the conversation, ask the user for their name (if not already provided) and address them by name in your responses.

Keep responses short and direct unless detail is requested.

If asked to remember or refer to previous chats, use the provided **session_context**.

Always encourage engagement at the end by offering options like:
- "Would you like a more detailed explanation?"
- "Should I give more examples?"
- "Would you like a summary of what we’ve discussed?"
- "If you'd like, I can help you prepare for a test or interview."

Here is the session context:
{session_context}
"""),
    ("user", "{query}")
])

# --------------------------------------------------- CHAT ENDPOINT ---------------------------------------------------
@api.post("/chat")
async def getprompt(usermsg: DataModel):
    
    from llm_config import llm
    start = time.time()
    sessionbuilder()
    
    context = contextbuilder()
    prompt = prompt_template.format_messages(query=usermsg.query, session_context=context)

    # Get stream from LLM
    stream = llm.stream(prompt)

    async def token_generator():
        full_response = ""
        start=time.time()
        token_count=0
        first_token=None
        for chunk in stream:
            if not first_token:
                first_token=chunk.content
                end=time.time()-start
                settime(end)
        
            token = chunk.content
            full_response += token
            token_count+=1
            yield token
        # Save session + chat at end of stream
    
        addtosession(usermsg=usermsg.query, content=full_response)
        await SaveChat(Chats(user=usermsg.query, ai=full_response,sessionid=session_id))

        end_time = (time.time() - start)
        # ttft=gettime()
        input_tokens=gettokencount(usermsg.query)
        await insert_metrics(metric_model(date_=str(date.today()),session_id=session_id,input_Tokens=input_tokens,total_time=round(end_time,3),ttft=round(gettime(),3),totaltokens=token_count,tokens_per_second=round(float(token_count/end_time),3),temp=llm.temperature,context_="sessional"))
    
        yield f"\n\n[sesh_id:{session_id}]   [Total time:{end_time} sec][TTFT->{gettime()}]     [token qty{token_count}]   [Tok/sec:{token_count/end_time}]"

    return StreamingResponse(token_generator(), media_type="text/plain")

