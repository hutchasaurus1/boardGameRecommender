from __future__ import division
import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup
import multiprocessing
from functools import partial
import time

# Functions to get board game ids
def getBoardGameIds():
	'''
	Query boardgamegeek.com for all board game ids
	'''
	url = 'https://boardgamegeek.com/browse/boardgame/page/'

	# 850 pages of board games
	# Set up parallel processing to get them all
	pool = multiprocessing.Pool(processes=4)
	page_range = xrange(0,860)
	outputs = pool.map(func=partial(getBoardGamesFromPageN, url=url), iterable=page_range)

def getBoardGamesFromPageN(n, url):
	print n
	r = requests.get(url + str(n))
	if r.status_code == 200:
		html = r.content
		soup = BeautifulSoup(html, 'html.parser')
		page_ids = [tag.attrs['href'].split('/')[2] for tag in soup.select('td.collection_objectname a')]
		saveBoardGameIds(page_ids)

def saveBoardGameIds(ids):
	client = MongoClient()
	db = client['boardGameGeek']
	boardGames = db['boardGames']
	for boardGameId in ids:
		db.boardGames.insert({'id': boardGameId})

# Functions to get usernames
def getUsernames():
	'''
	Get the usernames for each user in the United States from BGG
	'''
	baseUrl = 'https://boardgamegeek.com/users/page/'
	page = 1
	parameters = '?country=United+States&state=&city='

	# There are over 13000 pages of users
	# Set up parallel processing to get them all
	pool = multiprocessing.Pool(processes=4)
	page_range = xrange(0,13500)
	outputs = pool.map(
		func=partial(getUsernamesFromPageN, baseUrl=baseUrl, parameters=parameters),
		iterable=page_range
	)

def getUsernamesFromPageN(n, baseUrl, parameters):
	print n
	r = requests.get(baseUrl + str(n) + parameters)
	if r.status_code == 200:
		html = r.content
		soup = BeautifulSoup(html, 'html.parser')
		page_ids = [tag.get_text() for tag in soup.select('div.username a')]
		saveUsernames(page_ids)

def saveUsernames(usernames):
	'''
	Saves the usernames to MongoDB
	'''
	client = MongoClient()
	db = client['boardGameGeek']
	users = db['users']
	for username in usernames:
		db.users.insert({'username': username})

def getUsersData():
	'''
	Gets the game ratings from each user based on username
	'''
	# Get a list of iterable usernames
	client = MongoClient()
	db = client['boardGameGeek']
	users = db['users']
	userData = db['userData']
	usernames = users.distinct('username')
	userDataNames = set(userData.distinct('username'))
	usernames = [username for username in usernames if username not in userDataNames]
	iterable = enumerate(usernames)

	# There are over 300000 users
	# Set up parallel processing to get all of their game data
	pool = multiprocessing.Pool(processes=4)
	outputs = pool.map(func=getUserData, iterable=iterable)

def getUserData(username):
	print username
	url = 'http://www.boardgamegeek.com/collection/user/' + username[1]
	r = requests.get(url)
	if r.status_code == 200:
		html = r.content
		saveUserData(username[1], html)
	else:
		print r.status_code


def saveUserData(username, html):
	client = MongoClient()
	db = client['boardGameGeek']
	userData = db['userData']
	db.userData.insert({'username': username, 'html': html})

def getBoardGamesMetaData():
	'''
	Get the board game meta data for each game based on game id
	'''
	# Get a list of iterable board game ids
	client = MongoClient()
	db = client['boardGameGeek']
	boardGames = db['boardGames']
	boardGameData = db['boardGameData']
	boardGameIds = boardGames.distinct('id')
	boardGameDataIds = set(boardGameData.distinct('id'))
	boardGameIds = [boardGameId for boardGameId in boardGameIds if boardGameId not in boardGameDataIds]
	iterable = enumerate(boardGameIds)

	# Set up parallel processing to get all of the meta game data
	pool = multiprocessing.Pool(processes=4)
	outputs = pool.map(func=getBoardGameMetaData, iterable=iterable)

def getBoardGameMetaData(boardGameId):
	print boardGameId
	url = 'http://www.boardgamegeek.com/boardgame/' + boardGameId[1]
	r = requests.get(url)
	if r.status_code == 200:
		html = r.content
		saveBoardGameMetaData(boardGameId[1], html)
	else:
		print r.status_code

def saveBoardGameMetaData(boardGameId, html):
	client = MongoClient()
	db = client['boardGameGeek']
	boardGameData = db['boardGameData']
	db.boardGameData.insert({'id': boardGameId, 'html': html})

if __name__ == '__main__':
	getBoardGamesMetaData()

