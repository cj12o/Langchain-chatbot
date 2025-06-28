from fastapi import FastAPI,APIRouter
from contextlib import asynccontextmanager
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from datetime import date
import os
import uuid
from dotenv import load_dotenv
import json
import uuid
import time
from dotenv import load_dotenv
from Tokenizer import gettokencount
from llm_config import router as router_llmconfig,llm_configurator,llmval

#Splitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
#vect db
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
import os
from typing import TypedDict,List,Dict
from pydantic import BaseModel
from llm_config import llm_configurator,llmval
from langchain_core.documents import Document
from chatsaver import Chats,SaveChat
from session import router as router_session,contextbuilder,session_id,addtosession, sessionbuilder,sessionidbuilder,settime,gettime
from fastapi.responses import StreamingResponse
from metricsaver import metric_model,insert_metrics
from rag_func import function#custom_docloader
from chroma_db import collection



_vector_store=None
embedding_model=None

if not session_id:
    sessionidbuilder()
from session import session_id

load_dotenv()
Chromadir=os.getenv("CHROMADB_PERDIR")

router=APIRouter()



#------------------------------------------RAG--------------------------------------------------------------------------------------
prompt_template_rag = ChatPromptTemplate.from_messages([
    ("system", """
    You are an RAG chatbot.
    Use the context provided to answer the query.
    {context}

    if answer not found use Sessional context
    {sessioncontext}
     
    give the best answer possible .
    """),
    ("user", "{query}")
])



llm_configurator(llmval(token_lim=1000,temp=0.75))
# from llm_config import llm

#-------------------------------------------------------------------###------------------------------------------------------------------



class datamodel(BaseModel):
    query:str
    session_id:str=None


class State(TypedDict):
    user_query:str
    context:List[Document]
    answer:str
    sessioncontext:str

class Myexception(Exception):
    pass
async def indexing():
    global _vector_store
    global embedding_model

    documents=await function()#gets doc
   
    #textsplitter
    splitter=RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    chunks=splitter.split_documents(documents)
    
    #vector_db+embedding
    embedding_model=OllamaEmbeddings(model="nomic-embed-text:v1.5")

    

    _vector_store = Chroma(
        collection_name="chat_history",
        embedding_function=embedding_model,
        persist_directory=Chromadir # Where to save data locally, remove if not necessary
    )


    #handle chunks
    i=1
    docs=[]
    for chunk in chunks: 
        doc=Document(
            page_content=chunk.page_content,
            metadata=chunk.metadata,
            id=i,
        )
        docs.append(doc)
        i=i+1

    uuids=[str(uuid.uuid4()) for x in range(len(docs))]
    _vector_store.add_documents(documents=docs,ids=uuids)


async def retriever(state:State):
    global _vector_store# it was built on startup
    if not _vector_store:
        raise Myexception("No chats to do rag")
        return
    #     await indexing()
    retrived_docs=_vector_store.similarity_search(state["user_query"])
    # print(retrived_docs)
    return {"context":retrived_docs}
    

@router.post('/rag_response')
async def run(usermsg:datamodel):
    #checking
    if not _vector_store:
        async def norag():
            msg=list("No previous chats were present in record,make a fresh start .from next time you can use previous chats")
            for token in msg:
                yield token 
        return StreamingResponse(norag(),media_type="plain/text")
    from llm_config import llm
    sessionbuilder()
    #--------------------------------------session context
    context=contextbuilder()

    #--------------------------------------------------------
    state=State(user_query=usermsg.query,context=[],answer="",sessioncontext=context)
    state.update(await retriever(state))
    

    doc_context='\n\n'.join(doc.page_content for doc in state["context"])
    start=time.time()

    prompt=prompt_template_rag.format_messages(query=usermsg.query,context=doc_context,sessioncontext=context)
    # print(doc_context)
    stream=llm.stream(prompt)
    async def tokengenerator(state,prompt,session_id):
        fullcontent=""
        start=time.time()
        first_token=None
        token_count=0
        # end=0
        for chunk in stream:
            if not first_token:
                first_token=chunk.content
                end=time.time()-start
                settime(end)

            token=chunk.content
            fullcontent+=token
            token_count+=1
            yield token
            #caching

        addtosession(usermsg=usermsg.query, content=fullcontent)
        await SaveChat(Chats(user=usermsg.query, ai=fullcontent,sessionid=session_id))

         ###streaming
        end_time=time.time()-start
        input_tokens=gettokencount(fullcontent)

        await insert_metrics(metric_model(date_=str(date.today()),session_id=session_id,input_Tokens=input_tokens,total_time=round(end_time,3),ttft=round(gettime(),3),totaltokens=token_count,tokens_per_second=round(float(token_count/end_time),3),temp=llm.temperature,context_="sessional+Know.Base"))
        yield f"\n\n[sesh_id:{session_id}]   [Total time:{end_time} sec][TTFT->{gettime()}]     [token qty{token_count}]   [Tok/sec:{token_count/end_time}]"
    return StreamingResponse(tokengenerator(state=state,prompt=prompt,session_id=session_id),media_type="text/plain")