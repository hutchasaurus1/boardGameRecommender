'''
This file contains scripts to build and pickle the model
'''
from __future__ import division
import graphlab
from pymongo import MongoClient
import cPickle as pickle
from operator import itemgetter

def buildFactorizationModel(data, item_data=None, user_id='username', item_id='boardGameId', target='rating', num_factors=None, num_sampled_negative_examples=4, ranking_regularization=None, regularization=1e-10, linear_regularization=1e-10):
	model = graphlab.recommender.ranking_factorization_recommender.create(
			observation_data=data,
			user_id=user_id,
			item_id=item_id,
			target=target,
			item_data=item_data,
			num_factors=10,
			num_sampled_negative_examples=num_sampled_negative_examples,
			ranking_regularization=ranking_regularization,
			regularization=regularization,
			linear_regularization=linear_regularization
		)

	return model

def getRecommendations(model, username, k=10, new_observation_data=None):
	client = MongoClient()
	db = client['boardGameGeek']
	boardGames = db['formattedGameData']

	recs = model.recommend([username], k=k, new_observation_data=new_observation_data)
	recs = list(recs['boardGameId'])
	recs_list = boardGames.find({'id': {'$in': recs}})

	ranked_recs_with_name =  []
	for rec in recs_list:
		rec['rank'] = recs.index(rec['id']) + 1
		url = 'http://www.boardgamegeek.com/boardgame/' + rec['id']
		ranked_recs_with_name.append([rec['id'], rec['name'], rec['rank'], url])

	return sorted(ranked_recs_with_name, key=itemgetter(2))

if __name__ == '__main__':
	pass