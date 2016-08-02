'''
This file runs all relevant functions in src to gather the data, create the model, and start the web app
'''
from src.gatherData import getBoardGameIds, getUsernames, getUserDataParallel, getBoardGameData
from src.dataCleaning import formatGameDataParallel
from src.dataHygiene import buildGameFeatureDF, generateExpansions, buildUserRatingsSFrame
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
	columns = ['minPlaytime','mechanics','maxPlayers','maxPlaytime','minAge','minPlayers','playtime','yearPublished']
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
			'num_factors': [10, 50, 100],
			'num_sampled_negative_examples': [4, 7, 10]
		},
		perform_trial_run=True
	)

	# Generate and save the model
	gameData = pd.read_csv('data/gameData.csv')
	gameData.drop(['Unnamed: 0', 'maxPlayers', 'maxPlaytime', 'minAge', 'minPlayers', 'minPlaytime', 'yearPublished'], axis=1, inplace=True)
	gameData = graphlab.SFrame(gameData)
	recommender = buildFactorizationModel(
		sf_train,
		item_data=gameData,
		user_id='username',
		item_id='boardGameId',
		target='rating',
		num_factors=10,
		num_sampled_negative_examples=4,
		ranking_regularization=0,
		regularization=1e-05,
		linear_regularization=1e-05
	)
	recommender.save('model.pkl')