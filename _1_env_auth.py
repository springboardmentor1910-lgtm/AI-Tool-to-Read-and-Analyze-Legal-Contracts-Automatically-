import os
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

PINECONE_KEY = os.getenv("PINECONE_API_KEY")

os.environ["HUGGINGFACEHUB_API_KEY"] = HF_TOKEN


