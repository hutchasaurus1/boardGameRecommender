##Board game recommender

###Pipeline

1. Scrape boardGameGeek.com for game data and user ratings
	-Grabbing basic html for pages for user data and board game data (Data already scraped)
	-There are over 300,000 users and 80,000 board games leading to 30gb of html data
2. Move all of the data up to an AWS server (this is the step I am currently on)
3. Format/clean the data (Not as simple as I first thought)
	-Use beautiful soup to parse html data
	-Store data in SQL database with the following tables
		•Board Games -Holds meta data for board games
			id, name, geek rating, min players, max players, min time, max time, etc...
		•Users -Holds meta data for users, only have username for now
			username
		•userGameRatings -relates users with games and stores rating
			username, gameId, rating, comment, userOwns
4. Build a first crappy recommender model using dato based on just the user ratings
5. Play with feature engineering
	-Board game categories
	-Board game mechanics
	-Play time
	-etc...
6. Build a simple web app where users can provide their boardGameGeek login and get recommendations
	-Can provide parameters for the recommendations to exclude certain types of games as well

###CRISPDM

1. Business Understanding
	-Sometimes it is hard to find good games that you will enjoy. Not every enjoys the highest rated game all the time. It would be convenient to have a board game recommender that would take personal preferences into account as well as specific preferences based on what the user is feeling at the time.

2. Data Understanding
	-Data will all come from boardGameGeek.com.
	-Available data includes
		•Board games
			-Meta Data such as id, name, geek rating, min players, max players, min time, max time, category, etc...
		•Users and user ratings of games as well as what games they own
	-This data can be used to create a matrix of user ratings per board game and user
		•This matrix can be used by dato to create a recommender

3. Data Preparation
	-Data needs to be scraped from boardGameGeek.com
		•The api is too poor to be used
	-There are 30gb of data, so moving it up to AWS seems like and unfortunate necessity
	-Move data to AWS
	-Build postgres SQL database that will be quick and easy to use

4. Modeling
	-I plan to use dato for most of the modeling
		•They have the best recommender that I know of out there
	-Feature engineering will be used attempted on all meta data as well as some clever things I can't think of right now

5. Evaluation
	-I will randomly split the data with 80% train and 20% test
	-I'm still not sure how to test recommender models, but I will learn that
	-Need to ensure that the same games aren't always getting recommended to all users
	-Does it recommend games for me that I like? How about for other people who like different types of games?

6. Deployment
	-Build web application that will enable users to provide a boardGameGeek username and get recommendations
	-Will also allow filtering if time permits (only recommend games that fall under the filtered parameters)
	-Will enable users to submit ratings to get better recommendations if there is enough time