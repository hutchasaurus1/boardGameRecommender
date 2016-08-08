'''
This file runs all relevant functions in src to gather the data, create the model, and start the web app
'''
from src.gatherData import getBoardGameIds, getUsernames, getUserDataParallel, getBoardGameData
from src.dataCleaning import formatGameDataParallel
from src.dataHygiene import buildGameFeatureDF, generateExpansions, buildUserRatingsSFrame
from src.dimensionalityReduction import reduceDimensionality
from src.modeling import buildFactorizationModel, getRecommendations
import pandas as pd
import graphlab

if __name__ == '__main__':
	# Gather and clean the data
	getBoardGameIds()
	getUsernames(16)
	getUserDataParallel(16)
	getBoardGameData()
	formatGameDataParallel(16)

	# Prepare the data for the model
	columns = ['mechanics','categories','families','maxPlayers','maxPlaytime','minAge','minPlayers','minPlaytime']
	buildGameFeatureDF(columns)
	generateExpansions()
	sf_train, sf_test = buildUserRatingsSFrame(remove_expansions=False, split_train_test=True)

	# Get best parameters for ranking factorization model
	grid_search = graphlab.toolkits.model_parameter_search.grid_search.create(
		(sf_train, sf_test),
		graphlab.recommender.ranking_factorization_recommender.create,
		{
			'user_id': 'username',
			'item_id': 'boardGameId',
			'target': 'rating',
			'ranking_regularization': 0,
			'regularization': [1e-1, 1e-3, 1e-5, 1e-7, 1e-10, 1e-12],
			'linear_regularization': [1e-1, 1e-3, 1e-5, 1e-7, 1e-10, 1e-12]
		},
		perform_trial_run=True
	)

	# Generate and save the model
	gameData = graphlab.SFrame.read_csv('data/reducedGameFeatures.csv', header=False)
	gameData.rename('X1': 'boardGameId')
	gameData['boardGameId'] = gameData['boardGameId'].apply(lambda x: str(int(x)))
	recommender = buildFactorizationModel(
		sf_train,
		item_data=gameData,
		user_id='username',
		# Column name of board games is X1 by default
		item_id='X1',
		target='rating',
		num_factors=10,
		num_sampled_negative_examples=4,
		ranking_regularization=0,
		regularization=1e-05,
		linear_regularization=1e-05
	)
	recommender.save('model')

	'''
	new_data = graphlab.SFrame({'username':['new_user_123321312'], 'boardGameId': ['891'], 'rating': [10]})

	recommender1, Has the card drafting mechanic present
	training rmse: 1.12
	test rmse: 1.27

	recommender2, does not
	training rmse: 1.01
	test rmse: 1.297

	recommender3, Has all the mechanics categories
	training rmse: 1.12
	test rmse: 1.25

	'''