import os
import json
import asyncio
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from database import collection,collection_ragdocs
from datetime import date

from langchain_core.prompts import ChatPromptTemplate,PromptTemplate
from session import contextbuilder,session_id
from llm_config import llm

async def function():
    document_list=[]
    lst_dates=await collection_ragdocs.distinct("Date")
    
    for dat in lst_dates:
       
        doc_text=""
        cursor=collection_ragdocs.find({"Date":dat})
        async for ele in cursor:
            doc_text+=ele['Summary']
        #converting to document obj
        doc=Document(page_content=doc_text,metadata={"Date":ele['Date'],"session_id":ele['session_id']})
        #appended to make List[Document]
        document_list.append(doc)
    print(document_list)
    return document_list


# asyncio.run(function()) #TEST

async def summerize():
    prompt_temp = ChatPromptTemplate([
    ("system", """
You are an AI assistant tasked with summarizing a conversation between a user and a chatbot.
Please follow these guidelines:
-If chats are empty no need to summarize.
- Retain any personal or identifying information shared by the user, such as name, address, interests, or preferences.
- Ignore generic or factual questions (e.g., "Where is the Taj Mahal?").
- Focus primarily on summarizing the **top 20 most relevant user-AI interactions**.
- The goal is to create a concise summary that captures key personal details and the overall intent of the user.

Here are the chats:
"""),
    ("user", "{chats}")
])

    from llm_config import llm
    from session import session_id
    prevchats=contextbuilder()
    if len(prevchats)<1:
        print("No previous chats to summarize")
        return
    print(prevchats)
    prompt=prompt_temp.format_messages(chats=prevchats)
    stream=llm.stream(prompt)
    async def token_gen():
        fullcontext=""
        for chnk in stream:
            token=chnk.content
            fullcontext+=token
            
        return fullcontext
    fullcntx=await token_gen()
    result=await collection_ragdocs.insert_one({"Summary":fullcntx,"session_id":str(session_id),"Date":str(date.today())})
