from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from typing import Any

class MongoDBOptions:
    def __init__(self):
        self.client: MongoClient[dict[str, Any]] | None = None
        self.db: Database[dict[str, Any]] | None = None
        self.mongo_uri: str = ""
        self.db_name: str = ""

    def init_app(self, app):
        self.mongo_uri = app.config.get('MONGODB_URI', '')
        self.db_name = app.config.get('MONGODB_DB', '')
        
        try:
            if not self.mongo_uri or not self.db_name:
                self.client = None
                self.db = None
                return

            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command("ping")
            self.db = self.client[self.db_name]
            print(" * Connected to MongoDB successfully")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f" * Failed to connect to MongoDB: {e}")
            self.client = None
            self.db = None

    def disconnect(self):
        if self.client:
            self.client.close()
            print(" * Disconnected from MongoDB")

mongo = MongoDBOptions()
