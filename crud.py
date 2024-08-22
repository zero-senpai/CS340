# Jake Brunton 2024

from pymongo import MongoClient
import bson

class CRUD:
    def __init__(self, username, password, host, port, database, col):
        USER = username
        PASS = password
        HOST = host
        PORT = port
        DB = database
        COL = col

        #Init connection
        self.client = MongoClient('mongodb://%s:%s@%s:%d' % (USER,PASS,HOST,PORT))
        self.database = self.client['%s' % (DB)]
        self.collection = self.database['%s' % (COL)]

    # Find and validate data set
    def findData(self, data):
        if data is not None:
            if (self.collection.find_one(data)):
                return True
            else:
                return False
        else:
            raise Exception("Parameter empty. Could not search for data")

    # Create method
    def create(self, data):
        if data is not None:
            # @data: dictionary value
            return self.collection.insert_one(data)
        else:
            raise Exception("Parameter empty. Did not save.")

    # Read method
    def read(self, data):
        if data is not None:
            return self.collection.find(data)
        else:
            raise Exception("Parameter empty. Could not find anything.")

    # Update a record
    def update(self, query, data):
        if query and data:
            if(self.findData(query)):
                return self.collection.update_one(query, {'$set': data})
            else:
                raise Exception("Could not locate passed data as record.")
        else:
            raise Exception("Parameter empty. Could not update.")
            
    def delete(self, data):
        if data is not None:
            if(self.findData(data)):
                return self.collection.delete_one(data)
            else:
                raise Exception("Could not locate passed data as record.")
        else:
            raise Exception("Parameter empty. Could not delete.")
