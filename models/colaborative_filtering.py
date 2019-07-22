import mysql.connector
from models import config
import numpy as np


mydb = mysql.connector.connect(**config.db_credentials)
mycursor = mydb.cursor()

mycursor.execute("Select count(DISTINCT user_id) from ratings")
for i in mycursor:
    user_count = i[0]

mycursor.execute("Select count(DISTINCT movie_id) from ratings")
for i in mycursor:
    movie_count = i[0]

# print(user_count,movie_count)

data_matrix = np.zeros((user_count, movie_count))
mycursor.execute("Select * from ratings")

#creating a user-movie rating matrix
for each in mycursor:
    data_matrix[each[1] - 1, each[2] - 1] = each[3]

# print(data_matrix)


from sklearn.metrics.pairwise import pairwise_distances
user_similarity = pairwise_distances(data_matrix, metric='cosine')
item_similarity = pairwise_distances(data_matrix.T, metric='cosine')

def predict(ratings, similarity, type='user'):
    if type == 'user':
        mean_user_rating = ratings.mean(axis=1)
        #We use np.newaxis so that mean_user_rating has same format as ratings
        ratings_diff = (ratings - mean_user_rating[:, np.newaxis])
        pred = mean_user_rating[:, np.newaxis] + similarity.dot(ratings_diff) / np.array([np.abs(similarity).sum(axis=1)]).T
    elif type == 'item':
        pred = ratings.dot(similarity) / np.array([np.abs(similarity).sum(axis=1)])
    return pred


user_prediction = predict(data_matrix, user_similarity, type='user')
item_prediction = predict(data_matrix, item_similarity, type='item')
