'''
This file contains scripts to build and pickle the model
'''
from __future__ import division
import pandas as pd
from pymongo import MongoClient
from sklearn.cross_validation import train_test_split
import numpy as np
import graphlab
from dataHygiene import buildGameFeatureDF

def buildUserRatingsSFrame(remove_expansions=True):
	'''
	SFrames are used by graphlab to create the model
	First split the user data into training and testing data
	Then create and return a training and a testing SFrame
	'''
	client = MongoClient()
	db = client['boardGameGeek']
	table = db['userData']

	df = pd.DataFrame(list(table.find()))
	columns = ['boardGameId','username','rating']

	if remove_expansions:
		expansionIds = db['expansions'].distinct('id')
		df = df[map(lambda x: x not in expansionIds, df['boardGameId'])]

	df_train, df_test = train_test_split(df[columns])
	sf_train = graphlab.SFrame(df_train)
	sf_test = graphlab.SFrame(df_test)

	return sf_train, sf_test

def dimensionalityReduction(df, n_components=100):
	'''
	Reduce the dimensions of a dataframe to only the n_components that explain the most variance
	Returns a reduced version of the df as well as explained variance
	'''
	model = PCA(n_components=n_components)
	return model.fit_transform(df.values)

def buildFactrizationModel(data, item_data=None, user_id='username', item_id='boardGameId', target='rating', **kwargs):
	model = graphlab.recommender.factorization_recommender.create(
			observation_data=data,
			user_id=user_id,
			item_id=item_id,
			target=target,
			item_data=item_data,
			**kwargs
		)

	return model

if __name__ == '__main__':
	sf_train, sf_test = buildUserRatingsSFrame()
	gameData = pd.read_csv('data/gameData.csv')
	gameData = graphlab.SFrame(gameData)
	model = buildFactrizationModel(sf_train, gameData, user_id='username', item_id='boardGameId', target='rating')