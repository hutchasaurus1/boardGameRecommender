from __future__ import division
import pandas as pd
import numpy as np
from pymongo import MongoClient
from bs4 import BeautifulSoup
import multiprocessing
from functools import partial

def formatUserDataParallel(limit=False):
	'''
	Loops through all users in 'userData' table
	Parses content included in html column
	An individual record will be created for each game, user combination
	{
		username: string,
		boardGameId: id,
		boardGameName: name,
		rating: int,
		owned: boolean,
		comment: string
	}
	'''
	client = MongoClient()
	db = client['boardGameGeek']
	if limit != False:
		userData = db['userData'].find().limit(limit)
	else:
		userData = db['userData'].find()

	pool = multiprocessing.Pool(processes=4)
	outputs = pool.map(func=formatUserData, iterable=userData)

def formatUserData(userData):
	print userData['username']
	html = userData['html']
	soup = BeautifulSoup(html, 'html.parser')
	client = MongoClient()
	db = client['boardGameGeek']
	table = db['formattedUserGameData']

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
					'username': userData['username'], 
					'boardGameId': boardGameId, 
					'boardGameName': boardGameName, 
					'rating': rating, 
					'owned': owned, 
					'comment': comment
				})

def formatGameDataParallel(limit=False):
	'''
	Loops through all games in 'boardGameData' table
	Parses content included in xml content.
	Information columns:
		id, name, description, yearPublished, minPlayers, maxPlayers,
		playtime, minPlaytime, maxPlaytime, minAge, categories, families, expansions,
		designers, artists, publishers, avgRating, bayesAverage, rank
	'''
	client = MongoClient()
	db = client['boardGameGeek']
	if limit != False:
		boardGameData = db['boardGameMetaData'].find().limit(limit)
	else:
		boardGameData = db['boardGameMetaData'].find()

	pool = multiprocessing.Pool(processes=4)
	outputs = pool.map(func=formatBoardGameData, iterable=boardGameData)

def formatBoardGameData(boardGameData):
	'''
	Parses html
	'''
	print boardGameData['id']
	xml = boardGameData['xml']
	soup = BeautifulSoup(xml, 'xml')

	gameId = boardGameData['id']
	name = getValueIfNotNull(soup.find('name', type='primary'))
	description = '' if soup.find('description') == None else soup.find('description').get_text().strip()
	yearPublished = getValueIfNotNull(soup.find('yearpublished'))
	minPlayers = getValueIfNotNull(soup.find('minplayers'))
	maxPlayers = getValueIfNotNull(soup.find('maxplayers'))
	playtime = getValueIfNotNull(soup.find('playingtime'))
	minPlaytime = getValueIfNotNull(soup.find('minplaytime'))
	maxPlaytime = getValueIfNotNull(soup.find('maxplaytime'))
	minAge = getValueIfNotNull(soup.find('minage'))
	categories = getListIfNotNull(soup.find_all('link', type='boardgamecategory'))
	families = getListIfNotNull(soup.find_all('link', type='boardgamefamily'))
	expansions = getListIfNotNull(soup.find_all('link', type='boardgameexpansion'))
	designers = getListIfNotNull(soup.find_all('link', type='boardgamedesigner'))
	artists = getListIfNotNull(soup.find_all('link', type='boardgameartist'))
	publishers = getListIfNotNull(soup.find_all('link', type='boardgamepublisher'))
	avgRating = getValueIfNotNull(soup.find('ratings average'))
	bayesAverage = getValueIfNotNull(soup.find('ratings bayesaverage'))
	rank = getValueIfNotNull(soup.find('ratings ranks rank', type='subtype'))

	client = MongoClient()
	db = client['boardGameGeek']
	table = db['formattedGameData']

	table.insert_one({
		'id': gameId,
		'name': name,
		'description': description,
		'yearPublished': yearPublished,
		'minPlayers': minPlayers,
		'maxPlayers': maxPlayers,
		'playtime': playtime,
		'minPlaytime': minPlaytime,
		'maxPlaytime': maxPlaytime,
		'minAge': minAge,
		'categories': categories,
		'families': families,
		'expansions': expansions,
		'designers': designers,
		'artists': artists,
		'publishers': publishers,
		'avgRating': avgRating,
		'bayesAverage': bayesAverage,
		'rank': rank
	})

def getValueIfNotNull(searchObject):
	return '' if searchObject == None else searchObject['value']

def getListIfNotNull(searchObject):
	return '' if searchObject == None else [x['value'] for x in searchObject]

if __name__ == '__main__':
	# formatUserDataParallel()
	formatGameDataParallel(limit=100)