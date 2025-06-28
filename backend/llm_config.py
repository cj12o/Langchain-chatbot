from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
load_dotenv()
LLM_chat_endpt=os.getenv("LM_STUDIO_URL")#chatcompleteion edpt

router=APIRouter()

Maximum_token=225
temperature=0.5
llm=None

load_dotenv()
API_KEY=os.getenv("API_KEY")

class llmval(BaseModel):
    token_lim:int=Maximum_token
    temp:float=temperature

@router.post('/config')
def llm_configurator(conf:Optional[llmval]=None):
    global Maximum_token
    global temperature
    global llm
    if conf is None:
        conf=llmval()
  
    Maximum_token = conf.token_lim
    temperature=conf.temp
    
    llm=ChatOpenAI(
        base_url=LLM_chat_endpt,
        max_completion_tokens=Maximum_token,
        api_key=API_KEY,
        temperature=temperature,
        model="hermes-3-llama-3.2-3b",
        #model="gemma-2-9b-it",                         
        #model="deepseek/deepseek-r1-0528-qwen3-8b",
        streaming=True,
    )
    # return {"response":"success"}
    return {"token_lim":llm.max_tokens,"temp":llm.temperature}


