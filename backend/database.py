import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import asyncio


load_dotenv()

mongo_url=os.getenv("MONGO_URL")
main_db=os.getenv("MAIN_DB")
history_db=os.getenv("CHAT_HISTDB")
metric_db=os.getenv("METRIC_DB")
rag_db=os.getenv("RAG_DOCS_DB")


client = AsyncIOMotorClient(mongo_url)
db = client.get_database(main_db)
collection=db.get_collection(history_db)
collection_metrics=db.get_collection(metric_db)
collection_ragdocs=db.get_collection(rag_db)

