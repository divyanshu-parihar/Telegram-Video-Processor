import sqlite3
from sqlite3 import Error



# from peewee import *
import datetime
def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")







# db = SqliteDatabase('my_database.db')

# class BaseModel(Model):
#     class Meta:
#         database = db

# class User(BaseModel):
#     username = CharField(unique=True)

# class Tweet(BaseModel):
#     user = ForeignKeyField(User, backref='tweets')
#     message = TextField()
#     created_date = DateTimeField(default=datetime.datetime.now)
#     is_published = BooleanField(default=True)