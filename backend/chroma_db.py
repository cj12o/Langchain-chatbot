import chromadb
import numpy as np
from chromadb.config import Settings
from dotenv import load_dotenv
import os

load_dotenv()
chromadb_dir=os.getenv("CHROMADB_PERDIR")

client=chromadb.Client(Settings(
    persist_directory=chromadb_dir
))

collection=client.get_or_create_collection(name="Chat_history")
