"""
TODO
"""

from pymongo import MongoClient
from pymongo import errors
from private.config import MongoDBPrivate


class MongoDB:
    """
    TODO
    """

    def __init__(self):
        self.client = None
        self.data_base = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def insert(self, collection: str, document: str) -> bool:
        """
        TODO
        """
        if self.data_base is not None:
            try:
                self.data_base[collection].insert_one(document)
                return True
            except errors.WriteError as error:
                print(f"Error insert_one ticker:{error}")
            except errors.WriteConcernError as error:
                print(f"Error insert_one ticker:{error}")
        return False

    def read_collection(self, collection: str) -> list:
        """
        TODO
        """
        if self.data_base is not None:
            try:
                return list(self.data_base[collection].find())
            except errors.OperationFailure as error:
                print(f"Exception reading collection:{error}")
        return []

    def close(self):
        """
        TODO
        """
        self.client.close()
        self.client = None
        self.data_base = None

    def connect(self):
        """
        w setting: how many nodes should acknowledge the write before declaring it a success.
        w=majority
        retryWrites=true retry certain write operations a single time if they fail.
        """
        if MongoDBPrivate.atlas:
            uri = f"mongodb+srv://{MongoDBPrivate.user}:{MongoDBPrivate.password}"
            uri += f"@{MongoDBPrivate.host}/{MongoDBPrivate.database}"
            uri += "?retryWrites=true&w=majority"
        else:
            uri = f"mongodb://{MongoDBPrivate.user}:{MongoDBPrivate.password}"
            uri += f"@{MongoDBPrivate.host}/{MongoDBPrivate.database}"
        try:
            print(uri)
            client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        except errors.ConnectionFailure as error:
            print(f"MongoClient Connection ERROR:{error}")
            raise error

        data_base = client.get_database(MongoDBPrivate.database)
        try:
            response = data_base.command(
                {"connectionStatus": 1, "showPrivileges": False}
            )
            print(response)
        except errors.ConnectionFailure as error:
            print(f"MongoClient DataBase Connection ERROR:{error}")
            raise error
        except errors.OperationFailure as error:
            print(f"MongoClient DataBase Operation ERROR:{error}")
            raise error
        else:
            if response["ok"] == 1.0:
                print(f"DB Connected OK:{response}")
                self.client = client
                self.data_base = data_base
            else:
                print(f"DB Connected ERROR:{response}")
