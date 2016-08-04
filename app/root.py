from flask import Flask, url_for, request, render_template, Markup, jsonify, session
import json
from json2html import json2html
import requests
import socket
import graphlab
from src.modeling import getRecommendations
from pymongo import MongoClient
import pandas as pd
from flask import jsonify
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

app = Flask(__name__)
app.secret_key = 'Shhh! It is a secret!'
PORT = 5353

@app.route('/')
@app.route('/index')
def api_root():
	recs = None
	newRecs = None

	# If a username is supplied, return recommendations for the user
	if 'username' in request.args.keys():
		recs = getRecommendations(model, request.args['username'])

	# Update the liked games session variable if necessary
	if 'likedGames' not in session:
		session['likedGames'] = []

	print session['likedGames']

	# If a user selects to get recommendations based on liked games, supply them
	if 'newRecs' in request.args.keys():
		# Build graphlab SFrame
		boardGameIds = []
		if 'likedGames' in session:
			games = boardGames.find({'name': {'$in': session['likedGames']}})
			for game in games:
				boardGameIds.append(game['id'])

		newData = None
		for i in range(len(boardGameIds)):
			if i ==	 0:
				newData = graphlab.SFrame({'username': ['this_is_a_fake_user_1234'], 'boardGameId': [boardGameIds[i]], 'rating': [10]})
			else:
				newerData = graphlab.SFrame({'username': ['this_is_a_fake_user_1234'], 'boardGameId': [boardGameIds[i]], 'rating': [10]})
				newData = newData.append(newerData)

		newRecs = getRecommendations(model, 'this_is_a_fake_user_1234', k=10, new_observation_data=newData)

	return render_template('index.html', recs=recs, newRecs=newRecs, likedGames=session['likedGames'])

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/contact')
def contact():
	return render_template('contact.html')

@app.route('/blog')
def blog():
	return render_template('blog.html')

@app.route('/autocomplete')
def autocomplete():
	search = request.args.get('q')
	names = [s for s in boardGameNames if search.lower() in s.lower()][:5]
	return jsonify(json_list=names)

@app.route('/addGame')
def addGame():
	gameName = request.args['gameName']

	if request.args['gameName'] not in session['likedGames']:
		session['likedGames'].append(request.args['gameName'])

	return jsonify(likedGames=session['likedGames'])

@app.route('/removeGame')
def removeGame():
	gameName = request.args['gameName']

	if request.args['gameName'] in session['likedGames']:
		session['likedGames'].remove(request.args['gameName'])

	return jsonify(likedGames=session['likedGames'])

if __name__ == '__main__':
	# Connect to the database
	client = MongoClient()
	db = client['boardGameGeek']
	boardGames = db['formattedGameData']
	boardGameNames = [x.encode('utf-8') for x in boardGames.distinct('name')]

	# Get the model
	model = graphlab.load_model('../model1.pkl')

	# Start Flask app
	app.run(host='0.0.0.0', port=PORT, debug=True)
