from flask import Flask, url_for, request, render_template, Markup
import json
from json2html import json2html
import requests
import socket
import graphlab
from src.modeling import getRecommendations
from pymongo import MongoClient
import pandas as pd

app = Flask(__name__)
PORT = 5353

@app.route('/')
@app.route('/index')
def api_root():
	recs = None
	if 'username' in request.args.keys():
		recs = getRecommendations(model, request.args['username'])
	return render_template('index.html', recs=recs)

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/contact')
def contact():
	return render_template('contact.html')

@app.route('/blog')
def blog():
	return render_template('blog.html')

if __name__ == '__main__':
	# Connect to the database
	client = MongoClient()
	db = client['boardGameGeek']

	# Get the model
	model = graphlab.load_model('../model1.pkl')

	# Start Flask app
	app.run(host='0.0.0.0', port=PORT, debug=True)
