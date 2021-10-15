from pymongo import MongoClient
from private.config import MongoDBPrivate


class MongoDB():
    def __init__(self):
        self.client = None
        self.db = None

    def __enter__(self):
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def insert(self, collection, document)->None:
        if self.db != None:
            try:
                result = self.db[collection].insert_one(document)
            except Exception as e:
                print(f"Error insert_one ticker:{e}")
                raise e
            print(f"insert result:{result.inserted_id}")

    def close(self):
        self.client.close()
        self.client = None
        self.db = None

    def connect(self):
        '''
        w setting: how many nodes should acknowledge the write before declaring it a success. 
        w=majority
        retryWrites=true retry certain write operations a single time if they fail.
        '''
        if MongoDBPrivate.atlas:
            uri = f"mongodb+srv://{MongoDBPrivate.user}:{MongoDBPrivate.password}@{MongoDBPrivate.host}/{MongoDBPrivate.database}?retryWrites=true&w=majority"
        else:
            uri = f"mongodb://{MongoDBPrivate.user}:{MongoDBPrivate.password}@{MongoDBPrivate.host}/{MongoDBPrivate.database}"
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        except Exception as e:
            print(f"MongoClient Connection ERROR:{e}")
            raise e

        db = client.get_database(MongoDBPrivate.database)
        try:
            response = db.command(
                {'connectionStatus': 1, 'showPrivileges': False})
            print(response)
        except Exception as e:
            print(
                f"MongoClient DataBase Connection ERROR:{e}")
            raise e
        else:
            if response['ok'] == 1.0:
                print(f"DB Connected OK:{response}")
                self.client = client
                self.db = db
            else:
                print(f"DB Connected ERROR:{response}")