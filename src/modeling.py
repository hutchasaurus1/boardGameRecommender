'''
This file contains scripts to build and pickle the model
'''
from __future__ import division
import graphlab
import cPickle as pickle

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

def pickleModel(model):
	with open("model.pkl") as f:
		pickle.dump(model, f)

def getRecommendations(model, username):
	recs = model.recommend([username])
	recs = list(recs['boardGameId'])
	recs_list = boardGames.find({'id': {'$in': recs}})

	ranked_recs_with_name =  []
	for rec in recs_list:
		rec['rank'] = recs.index(rec['id']) + 1
		ranked_recs_with_name.append([rec['id'], rec['name'], rec['rank']])

	return ranked_recs_with_name

if __name__ == '__main__':
	pass