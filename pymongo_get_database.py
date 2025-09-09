from pymongo import MongoClient #pymongo exists in the venv, no need to import.

import urllib3

def get_database():
    #Provide the mongodb atlas url to connect PYTHON to MongoDB using PYMongo
    CONNECTION_STRING = 'mongodb+srv://chazzycisneros:Toontown1001@grosherry.nsy0iio.mongodb.net/'

    # Create a connection using MongoClient.
    client = MongoClient(CONNECTION_STRING)

    # Create the database for the user's pantry.
    return client['user_pantry_list']

# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":   
  
   # Get the database
   dbname = get_database()