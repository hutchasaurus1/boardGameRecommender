'''
This file runs all relevant functions in src to gather the data, create the model, and start the web app
'''
from gatherData import getBoardGameIds, getUsernames, getUsersData, getBoardGamesMetaData
from dataCleaning import formatUserDataParallel, formatGameDataParallel

if __name__ == '__main__':
	getBoardGameIds()
	getUsernames()
	getUsersData()
	getBoardGamesMetaData()
	formatUserDataParallel()
	formatGameDataParallel()