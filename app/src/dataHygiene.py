'''
This file contains scripts to prepare the data for modeling
'''
from __future__ import division
import pandas as pd
from pymongo import MongoClient
import numpy as np
from sklearn.cross_validation import train_test_split
import graphlab
import csv
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def getDummyColumnNames(series, columnName):
	# Return the unique values from a series of lists
	values = set()
	for l in series:
		for value in l:
			values.add(columnName + '_' + value)

	return values

def buildGameFeatureDF(columns='all', remove_expansions=False):
	'''
	This function builds the game features dataframe
	'''
	client = MongoClient()
	db = client['boardGameGeek']
	table = db['formattedGameData']

	df = pd.DataFrame(list(table.find()))
	df['boardGameId'] = df['id']

	# Drop unecessary columns
	unecessaryColumns = ['_id','id','name','description','avgRating','bayesAverage','rank','expansions']
	df.drop(unecessaryColumns, axis=1, inplace=True)

	if remove_expansions:
		expansionIds = set(db['expansions'].distinct('id'))
		df = df[map(lambda x: x not in expansionIds, df['boardGameId'])]

	if columns != 'all':
		columns = [c for c in columns if c not in unecessaryColumns]
		if 'boardGameId' not in columns:
			columns.append('boardGameId')
		df = df[columns]
	else:
		columns = df.columns

	# Change necessary columns to numeric
	columnsToNumeric = ['maxPlayers','maxPlaytime','minAge','minPlayers','minPlaytime']
	for column in columnsToNumeric:
		if column in df.columns:
			df[column] = pd.to_numeric(df[column])

	# Grab list of columns for dummy columns
	dummyColumns = []
	columnsOfLists = ['artists','categories','designers','families','publishers','mechanics']
	for column in columnsOfLists:
		if column in df.columns:
			dummyColumns.extend(getDummyColumnNames(df[column], column))

	allColumns = list(df.columns) + dummyColumns

	# Write to the csv one line at a time
	with open('data/gameData.csv', 'w') as csvFile:
		writer = csv.writer(csvFile)
		writer.writerow(allColumns)

		for _, row in df.iterrows():
			# Build row to write into csv by generating all dummy column data
			new_row = []
			i = 0
			for column in allColumns:
				c = column.split("_", 1)
				if len(c) == 1:
					new_row.append(row[column])
				else:
					# Calculate dummy column values
					if c[1] in row[c[0]]:
						new_row.append(1)
					else:
						new_row.append(0)

			writer.writerow(new_row)

def generateExpansions():
	'''
	Saves expansion game ids into the database so that they may be ignored in the predictor
	'''
	client = MongoClient()
	db = client['boardGameGeek']
	table = db['expansions']
	gameData = db['formattedGameData']
	expansionNames = gameData.distinct('expansions')

	for expansionName in expansionNames:
		expansionData = gameData.find_one({'name': expansionName})
		if expansionData != None:
			table.insert_one(expansionData)

def buildUserRatingsSFrame(remove_expansions=True, split_train_test=True):
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
		expansionIds = set(db['expansions'].distinct('id'))
		df = df[map(lambda x: x not in expansionIds, df['boardGameId'])]

	if split_train_test:
		df_train, df_test = train_test_split(df[columns])
		sf_train = graphlab.SFrame(df_train)
		sf_test = graphlab.SFrame(df_test)

		return sf_train, sf_test
	else:
		return graphlab.SFrame(df[columns])


if __name__ == '__main__':
	pass