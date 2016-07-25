from __future__ import division
import pandas as pd
import numpy as np
from pymongo import MongoClient
from bs4 import BeautifulSoup
import multiprocessing
from functools import partial

def formatUserDataParallel():
	'''
	Loops through all users in 'userData' table
	Parses content included in html column
	Data for each board game associated with the user will be stored in a dictionary
	{
		username: string,
		boardGames: {
			boardGameId: {
				name: string,
				rating: int,
				geekRating: float,
				owned: boolean,
				comment: string
			}
		}
	}
	'''
	client = MongoClient()
	db = client['boardGameGeek']
	userData = db['userData'].find()

	# pool = multiprocessing.Pool(processes=4)
	# outputs = pool.map(func=formatUserData, iterable=userData)
	for user in userData:
		formatUserData(user)

def formatUserData(userData):
	print userData['username']
	html = userData['html']
	soup = BeautifulSoup(html, 'html.parser')

	rows = soup.select('table.collection_table tr')
	boardGames = {}
	for row in rows:
		tds = row.find_all('td')
		if len(tds) > 0:
			boardGameLink = tds[0].find('a')['href'].split('/') if type(tds[0].find('a')) != type(None) else ''
			boardGameId = boardGameLink[2] if boardGameLink != '' else ''
			boardGameName = boardGameLink[3] if boardGameLink != '' else ''
			ratingText = row.find('div.ratingtext')
			rating = int(ratingText.get_text()) if type(ratingText) != type(None) else 0
			owned = 1 if type(row.find('div.owned')) != type(None) else 0
			commentText = row.find('td.collection_comment')
			comment = commentText.get_text() if type(commentText) != type(None) else ''
			boardGames[boardGameId] = {
				'name': boardGameName,
				'rating': rating,
				'owned': owned,
				'comment': comment
			}
	saveFormatedUserData(userData['username'], boardGames)

def saveFormatedUserData(username, boardGames):
	client = MongoClient()
	db = client['boardGameGeek']
	formattedUserData = db['formattedUserData']
	formattedUserData.insert({'username': username, 'boardGames': boardGames})



if __name__ == '__main__':
	formatUserDataParallel()