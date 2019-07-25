import mysql.connector
from models import config
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import pairwise_distances

def total_users():
    """
    :return: total users count rated for the movies
    """
    mydb = mysql.connector.connect(**config.db_credentials)
    mycursor = mydb.cursor()
    mycursor.execute("Select count(DISTINCT user_id) from ratings")
    for i in mycursor:
        user_count = i[0]
    mydb.close()
    return user_count

def movie_count():
    """
    :return: total movies count for which user has rated
    """
    mydb = mysql.connector.connect(**config.db_credentials)
    mycursor = mydb.cursor()
    mycursor.execute("Select count(DISTINCT movie_id) from ratings")
    for i in mycursor:
        movie_count = i[0]
    mydb.close()
    return movie_count



def user_movie_rating_matrix(user_count, movie_count):
    """
    The user-movie rating matrix is being calculated and stored in the
    outputs folder for the reference as well as returned for further usage.
    :param User_count: total number of user count who rated the movies
    :param Movie_count: total number of movies present
    :return: It will return the user-movie rating matrix as numpy 2D array
    """
    mydb = mysql.connector.connect(**config.db_credentials)
    mycursor = mydb.cursor()
    data_matrix = np.zeros((user_count, movie_count))
    mycursor.execute("Select * from ratings")

    #creating a user-movie rating matrix
    for each in mycursor:
        data_matrix[each[0] - 1, each[1] - 1] = each[2]

    # print(data_matrix)
    # storing the user movie rating matrix
    user_movie = pd.DataFrame(data_matrix)
    user_movie.index = ["user_"+str(i) for i in range(1, user_count+1)]
    user_movie.columns = ["movie_"+str(i) for i in range(1, movie_count+1)]
    user_movie.to_csv("../outputs/User_movie_rating.csv")

    mydb.close()
    return data_matrix

def similarity(data_matrix, user_count, movie_count):
    """
    calculating the similarity of users and items, storing in outputs folder and returning
    :param data_matrix: it is the user-movie rating data matrix.
    :return: user_similarity matrix and item_similarity matrix in form of numpy matrix
    """
    mydb = mysql.connector.connect(**config.db_credentials)
    mycursor = mydb.cursor()

    user_similarity = pairwise_distances(data_matrix, metric='cosine')
    item_similarity = pairwise_distances(data_matrix.T, metric='cosine')

    user_similarity_matrix = pd.DataFrame(user_similarity)
    user_similarity_matrix.index = ["user_" + str(i) for i in range(1, user_count + 1)]
    user_similarity_matrix.columns = ["user_" + str(i) for i in range(1, user_count + 1)]
    user_similarity_matrix.to_csv("../outputs/User_similarity.csv")

    mycursor.execute("Select movie_title from items")
    movie_title = list(mycursor)
    item_similarity_matrix = pd.DataFrame(item_similarity)
    item_similarity_matrix.index = [movie_title[i][0] for i in range(0, movie_count)]
    item_similarity_matrix.columns = [movie_title[i][0] for i in range(0, movie_count)]
    item_similarity_matrix.to_csv("../outputs/Movie_similarity.csv")
    mydb.close()
    return user_similarity, item_similarity

def predict(ratings, similarity, type='user'):
    """
    The prediction is calculated here on the basis of similarity and the prediction is
    based on the fundamentals of collaborative filtering.
    :param ratings: it is the user-movie data matrix
    :param similarity: either user similarity or item similarity
    :param type: user or item
    :return: it will return the prediction matrix with the weights.
    """
    if type == 'user':
        mean_user_rating = ratings.mean(axis=1)
        #We use np.newaxis so that mean_user_rating has same format as ratings
        ratings_diff = (ratings - mean_user_rating[:, np.newaxis])
        pred = mean_user_rating[:, np.newaxis] + similarity.dot(ratings_diff) / np.array([np.abs(similarity).sum(axis=1)]).T
    elif type == 'item':
        pred = ratings.dot(similarity) / np.array([np.abs(similarity).sum(axis=1)])
    return pred




def movies_to_predict(user_prediction, top = 5 ):
    """
    :param user_prediction: the user prediction matrix
    :param top: Number of movies to predict
    :return: a list of top movies
    """
    mydb = mysql.connector.connect(**config.db_credentials)
    mycursor = mydb.cursor()

    ranked_movie_index = user_prediction.argsort()[:, ::-1] + 1

    mycursor.execute("select movie_id from ratings where user_id =" + str(user_id))
    watched_movie = list(list(zip(*list(mycursor.fetchall())))[0])
    top_movie_id_list = list(set(list(ranked_movie_index[user_id - 1])) - set(watched_movie))

    movie_list = []
    for i in range(top):
        mycursor.execute("select movie_title from items where movie_id =" + str(top_movie_id_list[i]))
        for each in mycursor:
            movie_list.append(each)

    mydb.close()
    return movie_list

user_count = total_users()
movie_count = movie_count()
data_matrix = user_movie_rating_matrix(user_count, movie_count)
user_similarity, item_similarity = similarity(data_matrix, user_count, movie_count)
user_prediction = predict(data_matrix, user_similarity, type='user')
item_prediction = predict(data_matrix, item_similarity, type='item')


while(True):
    user_id = int(input("input user_id for movie prediction"))
    if user_id == 0:
        break
    top = int(input("input how many movies to suggest"))

    predicted_movie_list = movies_to_predict(user_prediction = user_prediction, top = top)
    for i in predicted_movie_list:
        print(i[0])



