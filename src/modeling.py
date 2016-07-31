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

if __name__ == '__main__':
	pass