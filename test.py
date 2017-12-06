from flask import Flask, render_template
from flask import jsonify
from flask import request, send_from_directory
from flask_pymongo import PyMongo
import urllib
from bson import json_util
from bson.json_util import loads
from bson.json_util import dumps
import json
import datetime
import csv
import time
import re

app = Flask(__name__,static_url_path='/static')



app.config['MONGO_DBNAME'] = 'project4ds'
app.config['MONGO_URI'] = 'mongodb://log4coppertone:log4coppertone@ds155325.mlab.com:55325/project4ds'
mongo = PyMongo(app)
@app.route('/', methods=['GET'])
def get_all_stars():
    from pymongo import MongoClient

    client = MongoClient("mongodb://log4coppertone:log4coppertone@ds155325.mlab.com:55325/project4ds")
    database = client["project4ds"]
    collection = database["Coppertone"]
    coppertone = mongo.db.Coppertone
    query = {}
    projection = {}
    projection["num_comments"] = -1.0

    sort = [ (u"num_comments", -1) ]

    cursor = coppertone.find({}).sort([('num_reactions', -1)]).limit(1)
    try:
        for doc in cursor:
          print (doc["num_reactions"])
    finally:
        cursor.close()
    return 'success'



if __name__ == '__main__':
    app.run(debug=True)
