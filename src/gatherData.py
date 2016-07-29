from __future__ import division
import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup
import multiprocessing
from functools import partial
import time
import math

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
		formatAndSaveUserData(username[1], html)
	else:
		print r.status_code

def formatAndSaveUserData(username, html):
	'''
	Format the html before saving it in the database
	'''
	soup = BeautifulSoup(html, 'html.parser')
	client = MongoClient()
	db = client['boardGameGeek']
	table = db['userData']

	rows = soup.select('table.collection_table tr')
	for row in rows:
		tds = row.find_all('td')
		if len(tds) > 0:
			boardGameLink = '' if tds[0].find('a') == None else tds[0].find('a')['href'].split('/')
			boardGameId = boardGameLink[2] if boardGameLink != '' else ''
			boardGameName = boardGameLink[3] if boardGameLink != '' else ''
			ratingText = row.find('div', class_='ratingtext')
			rating = 0 if ratingText == None else float(ratingText.get_text())
			owned = 0 if row.find('div', class_='owned') == None else 1
			commentText = row.find('td', class_='collection_comment')
			comment = '' if commentText == None else commentText.get_text()
			if rating != 0:
				table.insert_one({
					'username': username, 
					'boardGameId': boardGameId, 
					'boardGameName': boardGameName, 
					'rating': rating, 
					'owned': owned, 
					'comment': comment
				})

def getBoardGamesMetaData():
	'''
	Get the board game meta data for each game based on game id
	'''
	# Get a list of iterable board game ids
	client = MongoClient()
	db = client['boardGameGeek']
	boardGames = db['boardGames']
	metaData = db['boardGameMetaData']
	boardGameIds = boardGames.distinct('id')
	boardGameDataIds = set(metaData.distinct('id'))
	boardGameIds = [boardGameId for boardGameId in boardGameIds if boardGameId not in boardGameDataIds]
	l = len(boardGameIds)

	for i in range(int(math.ceil(l / 100))):
		time.sleep(5)
		boardGameIdsString = ','.join(boardGameIds[i * 100: min(l - 1,(i + 1) * 100)])
		getBoardGameMetaData(boardGameIdsString, metaData)

def getBoardGameMetaData(boardGameIds, metaData):
	url = 'http://www.boardgamegeek.com/xmlapi2/thing?id=' + boardGameIds + '&stats=1'
	r = requests.get(url)
	if r.status_code == 200:
		xml = r.content
		soup = BeautifulSoup(xml, 'xml')
		boardGames = soup.find_all('item')
		for boardGame in boardGames:
			print boardGame['id']
			metaData.insert_one({'id': boardGame['id'], 'xml': str(boardGame)})
	else:
		print r.status_code

if __name__ == '__main__':
	# getBoardGameIds()
	# getUsernames()
	getUsersData()
	# getBoardGamesMetaData()

