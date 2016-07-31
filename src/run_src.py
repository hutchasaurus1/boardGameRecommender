'''
This file runs all relevant functions in src to gather the data, create the model, and start the web app
'''
from src.gatherData import getBoardGameIds, getUsernames, getUsersData, getBoardGamesMetaData
from src.dataCleaning import formatUserDataParallel, formatGameDataParallel
from src.dataHygiene import buildGameFeatureDF, generateExpansions, buildUserRatingsSFrame
from src.modeling import buildFactrizationModel, pickleModel

if __name__ == '__main__':
	# Gather and clean the data
	getBoardGameIds()
	getUsernames()
	getUsersData()
	getBoardGamesMetaData()
	formatGameDataParallel()

	# Prepare the data for the model
	columns = ['categories','minPlaytime','mechanics','families','maxPlayers','maxPlaytime','minAge','minPlayers','playtime','yearPublished']
	buildGameFeatureDF(columns)
	generateExpansions()
	sf_train = buildUserRatingsSFrame(remove_expansions=True, split_train_test=False)

	# Generate and pickle the model
	gameData = pd.read_csv('data/gameData.csv')
	gameData = graphlab.SFrame(gameData)
	model = buildFactrizationModel(sf_train, gameData, user_id='username', item_id='boardGameId', target='rating')
	pickleModel(model)