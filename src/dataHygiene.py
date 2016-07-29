'''
This file contains scripts to prepare the data for modeling
'''
from __future__ import division
import pandas as pd
from pymongo import MongoClient
import numpy as np
from sklearn.decomposition import PCA

def splitListsIntoDummyColumns(df, column):
	# Get set of unique values in column
	uniqueVals = uniqueValues(df[column])

	# Add a column to the dataframe for each unique value
	for value in uniqueVals:
		df[value] = map(lambda x: 1 if value in x else 0, df[column])

	df.drop(column, axis=1, inplace=True)
	return df

def uniqueValues(series):
	# Return the unique values from a series of lists
	values = set()
	for l in series:
		for value in l:
			values.add(value)
	return values

def buildGameFeatureDF(columns='all'):
	'''
	Features:
	 	id, artists, categories, designers, minPlaytime, name, mechanics
	 	families, maxPlayers, maxPlaytime, minAge, minPlayers
	 	playtime, publishers, yearPublished
	'''
	client = MongoClient()
	db = client['boardGameGeek']
	table = db['formattedGameData']

	df = pd.DataFrame(list(table.find()))
	df['boardGameId'] = df['id']

	# Drop unecessary columns
	unecessaryColumns = ['_id','id','name','description','avgRating','bayesAverage','rank']
	df.drop(unecessaryColumns, axis=1, inplace=True)
	columns = [c for c in columns if c not in unecessaryColumns]

	if columns != 'all':
		if 'boardGameId' not in columns:
			columns.append('boardGameId')
		df = df[columns]

	# Build dummy columns
	columnsOfLists = ['artists','categories','designers','families','publishers', 'mechanics','expansions']
	for column in columnsOfLists:
		if column in columns or columns == 'all':
			df = splitListsIntoDummyColumns(df, column)

	# Change necessary columns to numeric
	columnsToNumeric = ['maxPlayers','maxPlaytime','minAge','minPlayers','minPlaytime']
	for column in columnsToNumeric:
		if column in columns or columns == 'all':
			df[column] = pd.to_numeric(df[column])

	# This process takes a while, so save the final df to a csv file
	df.to_csv('data/gameData.csv')
	return df

def dimensionalityReduction(df, n_components=100):
	'''
	Reduce the dimensions of a dataframe to only the n_components that explain the most variance
	Returns a reduced version of the df as well as explained variance
	'''
	model = PCA(n_components=n_components)
	return model.fit_transform(df.values)


if __name__ == '__main__':
	pass