#
import json
import pickle
import numpy as np
import pandas as pd
from flask import Flask, request
from sklearn.feature_extraction.text import HashingVectorizer
import warnings
warnings.filterwarnings('ignore')
from CustomCode import data_preprocessing
from tweet_scrapper import getoldtweets3

flask_app = Flask(__name__)

@flask_app.route('/', methods=['GET'])
def index_page():
    return_data = {
        "error" : "0",
        "message" : "Successful"
    }
    return flask_app.response_class(response=json.dumps(return_data), mimetype='application/json')


@flask_app.route('/get-tweets',methods=["GET"])
def fetch_tweets():
    try:
        data = request.json
        if not None in data and not "" in data:
            #pass command to function
            getoldtweets3.main(data['query'],data['since'],data['until'],data['maxtweeets'])
            #Import data
            tweets = pd.read_csv('Cleaned_data.csv')
            users_tweets = tweets[['date','username','tweets','permalink']]
            users_tweets['date'] = users_tweets['date'].apply(lambda x:x[0:10])
            result = users_tweets.to_dict(orient='records')
            status_code = 200
            return_data = {
                "error": "0",
                "message": "Successfull",
                "data": result
                }
        else:
            status_code = 400
            return_data = {
                "error": "1",
                "message": "Invalid Parameters"
                }
    except Exception as e:
        status_code = 500
        return_data = {
            'error':3,
            'message': str(e)
            }
    
    return flask_app.response_class(response=json.dumps(return_data), mimetype='application/json'),status_code
    


if __name__ == "__main__":
    flask_app.run(host="0.0.0.0",port=9090, debug=True)