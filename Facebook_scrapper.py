# mongo.py

from flask import Flask, render_template
from flask import jsonify
from flask import request, send_from_directory
from flask_pymongo import PyMongo
import urllib
from bson import json_util
from requests.exceptions import HTTPError
from bson.json_util import loads
from bson.json_util import dumps
import json
import datetime
import csv
import time
import re

try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib import urlopen, Request

app = Flask(__name__,static_url_path='/static')

app.config['MONGO_DBNAME'] = 'project4ds'
app.config['MONGO_URI'] = 'mongodb://log4coppertone:log4coppertone@ds155325.mlab.com:55325/project4ds'

# input date formatted as YYYY-MM-DD
since_date = ""
until_date = ""

app_id = "1817819741852164"
app_secret = "b0ec96124ba0807a6093455a86035cc3" # DO NOT SHARE WITH ANYONE!

access_token = app_id + "|" + app_secret
page_id = 'coppertone'

mongo = PyMongo(app)

@app.route('/', methods=['GET'])
def get_all_stats():
  Coppertone = mongo.db.Coppertone
  CopComments = mongo.db.CopComments
  pipeline = [{ '$group': { '_id': '$comment_author', 'total_comments': { '$sum': 1 } } },
                        { "$sort": { "total_comments": -1 } },
                          { "$limit": 10 }
             ]
  topCommenters = CopComments.aggregate(pipeline)
  pipeline1 = [{ '$group': { '_id': '$comment_author', 'total_comments': { '$sum': 1 } } },
                        { "$sort": { "total_comments": -1 } },
                          { "$limit": 1 }
             ]
  topComm = CopComments.aggregate(pipeline1)
  MaxShare = Coppertone.find({}).sort([('num_shares', -1)]).limit(1)
  MaxComment = Coppertone.find({}).sort([('num_comments', -1)]).limit(1)
  MaxReact = Coppertone.find({}).sort([('num_reactions', -1)]).limit(1)

  return render_template('index.html',topComment = topCommenters,MaxShare = MaxShare, MaxComment = MaxComment, MaxReact = MaxReact,TopComm = topComm)

@app.route('/posts/', methods=['GET'])
def get_all_posts():
  Coppertone = mongo.db.Coppertone
  allposts = Coppertone.find()
  CopComments = mongo.db.CopComments
  allcomments = CopComments.find()
  return render_template('tables.html',allposts=allposts,allcomments=allcomments)

@app.route('/comments/', methods=['GET'])
def get_all_comments():
  CopComments = mongo.db.CopComments
  allcomments = CopComments.find()
  return render_template('comments.html',allcomments=allcomments)




@app.route('/load', methods=['POST'])
def add_data():
  Coppertone = mongo.db.Coppertone
  CopComments = mongo.db.CopComments
  #statuses_dict = loads(scrapeFacebookPageFeedStatus(page_id, access_token, since_date, until_date))
  #status_id =[]
  #for status in statuses_dict:
  #status_id.append(Coppertone.insert(status))

  scrapeFacebookPageFeedComments(page_id, access_token)

 #new_status = Coppertone.find_one({'_id': status_id })
 # output =  statuses_dict
 #{'name' : new_star['name'], 'distance' : new_star['distance']}
  return loads(dumps(status_id, indent=4, sort_keys=True, default=str))

def request_until_succeed(url):
    req = Request(url)
    success = False
    count = 0
    while success is False:
        count+=1
        try:
            response = urlopen(req)
            if response.getcode() == 200:
                success = True
            if count==5:
                success = True
        except Exception as e:
            print(e)
            time.sleep(5)

            print("Error for URL {}: {}".format(url, datetime.datetime.now()))
            print("Retrying.")

    return response.read()

# Needed to write tricky unicode correctly to csv
def unicode_decode(text):
    try:
        return text.encode('utf-8').decode()
    except UnicodeDecodeError:
        return text.encode('utf-8')


def getFacebookPageFeedUrl(base_url):

    # Construct the URL string; see http://stackoverflow.com/a/37239851 for
    # Reactions parameters
    fields = "&fields=message,link,created_time,type,name,id," + \
        "comments.limit(0).summary(true),shares,reactions" + \
        ".limit(0).summary(true)"

    return base_url + fields



def processFacebookPageFeedStatus(status):

    # The status is now a Python dictionary, so for top-level items,
    # we can simply call the key.

    # Additionally, some items may not always exist,
    # so must check for existence first

    status_id = status['id']
    status_type = status['type']

    status_message = '' if 'message' not in status else \
        unicode_decode(status['message'])
    link_name = '' if 'name' not in status else \
        unicode_decode(status['name'])
    status_link = '' if 'link' not in status else \
        unicode_decode(status['link'])

    # Time needs special care since a) it's in UTC and
    # b) it's not easy to use in statistical programs.

    status_published = datetime.datetime.strptime(
        status['created_time'], '%Y-%m-%dT%H:%M:%S+0000')
    """status_published = status_published + \
        datetime.timedelta(hours=-5)  # EST
    status_published = status_published.strftime(
        '%Y-%m-%dT%H:%M:%S+0000')  # best time format for spreadsheet programs"""

    # Nested items require chaining dictionary keys.

    num_reactions = 0 if 'reactions' not in status else \
        status['reactions']['summary']['total_count']
    num_comments = 0 if 'comments' not in status else \
        status['comments']['summary']['total_count']
    num_shares = 0 if 'shares' not in status else status['shares']['count']
    result =  {'status_id': status_id, 'status_message': status_message, 'link_name': link_name, 'status_type' : status_type,
              'status_link': status_link, 'status_published': status_published, 'num_reactions': num_reactions, 'num_comments':num_comments,
               'num_shares': num_shares}

    return result
    #return (status_id, status_message, link_name, status_type, status_link,
    #        status_published, num_reactions, num_comments, num_shares)


def scrapeFacebookPageFeedStatus(page_id, access_token, since_date, until_date):
        has_next_page = True
        num_processed = 0
        scrape_starttime = datetime.datetime.now()
        after = ''
        base = "https://graph.facebook.com/v2.9"
        node = "/{}/posts".format(page_id)
        parameters = "/?limit={}&access_token={}".format(100, access_token)
        since = "&since={}".format(since_date) if since_date \
            is not '' else ''
        until = "&until={}".format(until_date) if until_date \
            is not '' else ''

        print("Scraping {} Facebook Page: {}\n".format(page_id, scrape_starttime))
        fbdata =[]
        while has_next_page:
            after = '' if after is '' else "&after={}".format(after)
            base_url = base + node + parameters + after + since + until

            url = getFacebookPageFeedUrl(base_url)
            statuses = json.loads(request_until_succeed(url))


            for status in statuses['data']:
                # Ensure it is a status with the expected metadata
                if 'reactions' in status:
                    status_data = processFacebookPageFeedStatus(status)
                    fbdata.append(status_data)

                num_processed += 1
                #print (json.dumps(fbdata))
                if num_processed % 100 == 0:
                    print("{} Statuses Processed: {}".format
                          (num_processed, datetime.datetime.now()))
            # if there is no next page, we're done.
            if 'paging' in statuses:
                after = statuses['paging']['cursors']['after']
            else:
                has_next_page = False

        print("\nDone!\n{} Statuses Processed in {}".format(
              num_processed, datetime.datetime.now() - scrape_starttime))
        res = dumps(fbdata)
        return res

def getFacebookCommentFeedUrl(base_url):

    # Construct the URL string
    fields = "&fields=id,message,reactions.limit(0).summary(true)" + \
        ",created_time,comments,from,attachment"
    url = base_url + fields

    return url

def processFacebookComment(comment, status_id, parent_id=''):

    # The status is now a Python dictionary, so for top-level items,
    # we can simply call the key.

    # Additionally, some items may not always exist,
    # so must check for existence first

    comment_id = comment['id']
    comment_message = '' if 'message' not in comment or comment['message'] \
        is '' else unicode_decode(comment['message'])
    comment_author = unicode_decode(comment['from']['name'])
    num_reactions = 0 if 'reactions' not in comment else \
        comment['reactions']['summary']['total_count']

    if 'attachment' in comment:
        attachment_type = comment['attachment']['type']
        attachment_type = 'gif' if attachment_type == 'animated_image_share' \
            else attachment_type
        attach_tag = "[[{}]]".format(attachment_type.upper())
        comment_message = attach_tag if comment_message is '' else \
            comment_message + " " + attach_tag

    # Time needs special care since a) it's in UTC and
    # b) it's not easy to use in statistical programs.

    comment_published = datetime.datetime.strptime(
        comment['created_time'], '%Y-%m-%dT%H:%M:%S+0000')
    """comment_published = comment_published + datetime.timedelta(hours=-5)  # EST
    comment_published = comment_published.strftime(
        '%Y-%m-%d %H:%M:%S')  # best time format for spreadsheet programs"""

    # Return a tuple of all processed data

    result = {'comment_id':comment_id, 'status_id':status_id, 'parent_id':parent_id, 'comment_message':comment_message,
             'comment_author':comment_author,'comment_published':comment_published, 'num_reactions':num_reactions}
    return result

def scrapeFacebookPageFeedComments(page_id, access_token):
            num_processed = 0
            scrape_starttime = datetime.datetime.now()
            after = ''
            base = "https://graph.facebook.com/v2.9"
            parameters = "/?limit={}&access_token={}".format(
                100, access_token)

            print("Scraping {} Comments From Posts: {}\n".format(
                page_id, scrape_starttime))

            Coppertone = mongo.db.Coppertone
            CopComments = mongo.db.CopComments
            cursor = Coppertone.find({},no_cursor_timeout=True)
            fbcomments = []
            # Uncomment below line to scrape comments for a specific status_id
            # reader = [dict(status_id='5550296508_10154352768246509')]

            for document in cursor:
                has_next_page = True

                while has_next_page:

                    node = "/{}/comments".format(document["status_id"])
                    after = '' if after is '' else "&after={}".format(after)
                    base_url = base + node + parameters + after

                    url = getFacebookCommentFeedUrl(base_url)
                    # print(url)
                    comments = json.loads(request_until_succeed(url))

                    for comment in comments['data']:
                        comment_data = processFacebookComment(
                            comment, document["status_id"])
                        CopComments.insert(loads(dumps(comment_data)))

                        if 'comments' in comment:
                            has_next_subpage = True
                            sub_after = ''

                            while has_next_subpage:
                                sub_node = "/{}/comments".format(comment['id'])
                                sub_after = '' if sub_after is '' else "&after={}".format(
                                    sub_after)
                                sub_base_url = base + sub_node + parameters + sub_after

                                sub_url = getFacebookCommentFeedUrl(
                                    sub_base_url)
                                sub_comments = json.loads(
                                    request_until_succeed(sub_url))

                                for sub_comment in sub_comments['data']:
                                    sub_comment_data = processFacebookComment(
                                        sub_comment, document['status_id'], comment['id'])
                                    CopComments.insert(loads(dumps(sub_comment_data)))


                                    num_processed += 1
                                    if num_processed % 100 == 0:
                                        print("{} Comments Processed: {}".format(
                                            num_processed,
                                            datetime.datetime.now()))

                                if 'paging' in sub_comments:
                                    if 'next' in sub_comments['paging']:
                                        sub_after = sub_comments[
                                            'paging']['cursors']['after']
                                    else:
                                        has_next_subpage = False
                                else:
                                    has_next_subpage = False

                        # output progress occasionally to make sure code is not
                        # stalling
                        num_processed += 1
                        if num_processed % 100 == 0:
                            print("{} Comments Processed: {}".format(
                                num_processed, datetime.datetime.now()))

                    if 'paging' in comments:
                        if 'next' in comments['paging']:
                            after = comments['paging']['cursors']['after']
                        else:
                            has_next_page = False
                    else:
                        has_next_page = False

            print("\nDone!\n{} Comments Processed in {}".format(
                num_processed, datetime.datetime.now() - scrape_starttime))

"""
                while has_next_page:

                    node = "/{}/comments".format(document["status_id"])
                    after = '' if after is '' else "&after={}".format(after)
                    base_url = base + node + parameters

                    url = getFacebookCommentFeedUrl(base_url)
                    # print(url)
                    comments = json.loads(request_until_succeed(url))


                    for comment in comments['data']:
                        comment_data = processFacebookComment(
                            comment, document["status_id"])
                        CopComments.insert(loads(dumps(comment_data)))

                        if 'comments' in comment:
                            has_next_subpage = True
                            sub_after = ''

                            while has_next_subpage:
                                sub_node = "/{}/comments".format(comment['id'])
                                sub_after = '' if sub_after is '' else "&after={}".format(
                                    sub_after)
                                sub_base_url = base + sub_node + parameters
                                sub_url = getFacebookCommentFeedUrl(
                                        sub_base_url)
                                sub_comments = json.loads(
                                        request_until_succeed(sub_url))

                                for sub_comment in sub_comments['data']:
                                    sub_comment_data = processFacebookComment(
                                        sub_comment, document["status_id"], comment['id'])
                                    CopComments.insert(loads(dumps(sub_comment_data)))

                                    num_processed += 1
                                    if num_processed % 100 == 0:
                                        print("{} Comments Processed: {}".format(
                                            num_processed,
                                            datetime.datetime.now()))

                                if 'paging' in sub_comments:
                                    if 'next' in sub_comments['paging']:
                                        sub_after = sub_comments[
                                            'paging']['cursors']['after']
                                    else:
                                        has_next_subpage = False
                                else:
                                    has_next_subpage = False

                        # output progress occasionally to make sure code is not
                        # stalling
                        num_processed += 1
                        if num_processed % 100 == 0:
                            print("{} Comments Processed: {}".format(
                                num_processed, datetime.datetime.now()))

                    if 'paging' in comments:
                        if 'next' in comments['paging']:
                            after = comments['paging']['cursors']['after']
                        else:
                            has_next_page = False
                    else:
                        has_next_page = False

            print("\nDone!\n{} Comments Processed in {}".format(
            num_processed, datetime.datetime.now() - scrape_starttime))
"""
if __name__ == '__main__':
    app.run(debug=True)
