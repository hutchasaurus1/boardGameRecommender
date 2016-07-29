from __future__ import division
import pandas as pd
import numpy as np
from pymongo import MongoClient
from bs4 import BeautifulSoup
import multiprocessing
from functools import partial

def formatGameDataParallel(limit=False):
	'''
	Loops through all games in 'boardGameData' table
	Parses content included in xml content.
	Information columns:
		id, name, description, yearPublished, minPlayers, maxPlayers, mecahnics,
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
	mechanics = getListIfNotNull(soup.find_all('link', type='boardgamemechanic'))
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
		'mechanics': mechanics,
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
	formatUserDataParallel()
	formatGameDataParallel()