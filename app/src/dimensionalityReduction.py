'''
Functions in this file are built to help reduce dimensionality on our
board game meta data matrix
Before reduction, the file is 9gb and has 56k columns
'''
from __future__ import division
import pandas as pd
from sklearn.decomposition import NMF
import numpy as np

def reduceDimensionality(n_components=100):
	# import the csv into a pandas df
	df = pd.read_csv('data/gameData.csv')

	# Normalize the numeric columns to values in [0,1]
	numericColumns = ['maxPlayers','maxPlaytime','minAge','minPlayers','minPlaytime','playtime']
	colsToNormalize = []
	for col in numericColumns:
		if col in df.columns:
			colsToNormalize.append(col)

	df[colsToNormalize] = df[colsToNormalize].apply(lambda x: (x - x.min())/(x.max() - x.min())/2)

	# Drop string columns
	colsToDrop = ['artists','categories','designers','families','publishers','mechanics','boardGameId','yearPublished']

	# Convert df to an array for NMF and stor the board game id column to attach later
	boardGameIds = df['boardGameId']
	arr = df.as_matrix([col for col in df.columns if col not in colsToDrop])
	arr = np.nan_to_num(arr)

	# Perform NMF with n_dimensions
	model = NMF(n_components=n_components)
	W = model.fit_transform(arr)
	W = np.insert(W, 0, boardGameIds, axis=1)

	np.savetxt("data/reducedGameFeatures.csv", W, delimiter=",")
