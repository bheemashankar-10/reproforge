import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
client = MongoClient(os.environ["MONGODB_URI"], serverSelectionTimeoutMS=5000)
client.admin.command("ping")
print("MongoDB connection OK")
