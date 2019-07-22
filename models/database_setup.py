'''
Setting up database named movie_data as the recommendation system will be based on movie data set.
'''

import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="1234",
)

print(mydb)
mycursor = mydb.cursor()
mycursor.execute("create database movie_data")
mydb.close()

'''
After this move to setting up database both ways in notebook folder.
'''