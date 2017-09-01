import apiai
import json
import requests
from utils2 import fetch_repl

# from pymongo import MongoClient


# MONGODB_URI = "mongodb://test:test@ds111754.mlab.com:11754/chatbot"
# client = MongoClient(MONGODB_URI, connectTimeoutMS=30000, socketTimeoutMS=None, socketKeepAlive=True)
# db = client.get_default_database()
# news_records= db.news_records
# # users = db._users    for getting the users.

# def getRECORDS(user_id):
#     records = news_records.find({"sender_id":user_id})
#     return records

# def pushRECORD(record):
#     news_records.insert_one(record)

# record = {"sender_id":"1234",	
# 			"news_type":"sports",
# 			"language":"hindi",
# 			"geo-country":"india"
# 		}
# pushRECORD(record)


APIAI_ACCESS_TOKEN = "2542abe010a74c7fa9378e7886b66089"

ai = apiai.ApiAI(APIAI_ACCESS_TOKEN)


GNEWS_API_ENDPOINT = "https://gnewsapi.herokuapp.com"


def get_news(params):
	params['news'] = params['news_type']
	resp = requests.get(GNEWS_API_ENDPOINT, params = params)
	return resp.json()

def apiai_response(query, session_id):
	"""
	function to fetch api.ai response
	"""
	request = ai.text_request()
	request.lang='en'
	request.session_id=session_id
	request.query = query
	response = request.getresponse()
	return json.loads(response.read().decode('utf8'))


def parse_response(response):
	"""
	function to parse response and 
	return intent and its parameters
	"""
	result = response['result']
	params = result.get('parameters')
	intent = result['metadata'].get('intentName')
	return intent, params

	
def fetch_reply(query, session_id):
	"""
	main function to fetch reply for chatbot and 
	return a reply dict with reply 'type' and 'data'
	"""
	response = apiai_response(query, session_id)
	intent, params = parse_response(response)
	#print( "Intent = "+ intent+ "\n")
	reply = {}

	if intent == None:
		print ("\n\nIn None\n\n")
		reply = fetch_repl(query,session_id)

	elif intent == "news":
		print ("\n\nIn News\n\n")
		reply['type'] ='news'
		print(params)
		params['sender_id'] = session_id
		pushRECORD(params)
		articles = get_news(params)
		news_elements = []

		for article in articles:
			element = {}
			element['title'] = article['title']
			element['item_url'] = article['link']
			element['image_url'] = article['img']
			element['buttons'] = [{
				"type":"web_url",
				"title":"Read more",
				"url":article['link']}]
			news_elements.append(element)

		reply['data'] = news_elements

	elif intent.startswith('smalltalk'):
		print ("\n\nIn SmallTalk\n\n")

		reply['type'] = 'smalltalk'
		reply['data'] = response['result']['fulfillment']['speech']

	return reply