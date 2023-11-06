# app.py
import os
from flask import Flask,render_template, request, redirect
import firebase_admin
import google.cloud
from flask import abort
import subprocess
from datetime import datetime,timezone,timedelta
from google.api_core import  datetime_helpers
import datetime as dt
from firebase_admin import credentials, firestore, storage, auth as fAuth
from google.cloud import firestore as fs
import pygeohash as pgh
import requests
import urllib.parse
import youtube_dl
import numpy as np
from werkzeug.utils import secure_filename
import uuid
import re
import copy
base_dir = os.path.dirname(os.path.abspath(__file__))
import base64
import string
import random
from PIL import Image
import io
from copy import deepcopy
from functools import wraps
from flask import session , url_for
from dateutil import parser
import dateparser
import pytz
from urllib.request import urlopen, Request, HTTPError, URLError
from urllib.parse import unquote, quote
import html

pdt_tz = pytz.timezone("America/Los_Angeles")
# cred = credentials.Certificate("/home/ubuntu/crime_central_test/crime-central-firebase-adminsdk-3hd1r-a45c86bf9c.json")
cred = credentials.Certificate("crime-central-firebase-adminsdk-3hd1r-a45c86bf9c.json")
firebase_app = firebase_admin.initialize_app(cred, {
    'storageBucket': 'crime-central.appspot.com'
})
store = firestore.client()
bucket = storage.bucket()

app = Flask(__name__)             # create an app instance
# GoogleMaps(app,key="AIzaSyDVu4ZjuyPf8s-uhRPP6RGLfczaLF8hJQY")
app.secret_key = os.urandom(24)
app.config["UPLOAD_PATH"] = base_dir + "/static/uploads"

"""
Default view. Yet to know what should happen
"""
def unique(list):
    x = np.array(list)
    return np.unique(x)

@app.route("/", methods = ['GET'])
def index():
    return render_template("404.html")

def checkProfileId(profile_id, context=''):
    ref = store.collection("profiles").document(profile_id).get()

    if ref.exists:
        data = get_profile(profile_id)
        data['videos'] = get_profile_video(profile_id)
        if context == 'video':
            pass
        elif context == 'article':
            data['article'] = get_profile_article(profile_id)
        elif context == 'podcast':
            data['podcast'] = get_profile_podcast(profile_id)
        elif context == 'trials':
            data['trials'] = get_profile_trial(profile_id)
        elif context == 's911s':
            data['s911s'] = get_profile_s911s(profile_id)
        elif context == 'police_reports':
            data['police_reports'] = get_profile_police_report(profile_id)
        elif context == 'photo':
            data['photos'] = get_profile_photo(profile_id)
        elif context == '3d':
            data['object'] = get_profile_3d(profile_id)
        else:
            data['photos'] = get_profile_photo(profile_id)
            data['portals'] = get_profile_portal(profile_id)
            data['article'] = get_profile_article(profile_id)
            data['podcast'] = get_profile_podcast(profile_id)
            data['object'] = get_profile_3d(profile_id)
        return {"status":True,"data":data}
    else:
        return {"status":False}

def get_profile_police_report(profile_id):
    police_report_data = list()
    try:
        police_report_ref = store.collection(u'police_reports')
        police_report_docs = police_report_ref.where(u'profile_id', u'==', str(profile_id)).order_by(u'index').stream()

        for police_report_doc in police_report_docs:
            dataDict = police_report_doc.to_dict()
            dataDict['doc_id'] = police_report_doc.id
            published_date = dataDict.get("published_date",None)
            if published_date and isinstance(published_date, datetime_helpers.DatetimeWithNanoseconds):
                published_date = dt.datetime.combine(date=published_date.date(), time=published_date.time(), tzinfo=published_date.tzinfo)
                dataDict['published_date'] = published_date.strftime("%Y-%m-%d %H:%M:%S")
            police_report_data.append(dataDict)
    except google.cloud.exceptions.NotFound:
        print(u'Missing data')
    return police_report_data

def get_profile_article(profile_id):
    article_data = list()
    try:
        article_ref = store.collection(u'articles')
        article_docs = article_ref.where(u'profile_id', u'==', str(profile_id)).order_by(u'index').stream()

        for article_doc in article_docs:
            dataDict = article_doc.to_dict()
            dataDict['doc_id'] = article_doc.id


            published_date = dataDict.get("published_date",None)
            if published_date and isinstance(published_date, datetime_helpers.DatetimeWithNanoseconds):
                published_date = dt.datetime.combine(date=published_date.date(), time=published_date.time(), tzinfo=published_date.tzinfo)
                dataDict['published_date'] = published_date.strftime("%Y-%m-%d %H:%M:%S")
            article_data.append(dataDict)
    except google.cloud.exceptions.NotFound:
        print(u'Missing data')
    return article_data

def get_profile_3d(profile_id):
    object_data = list()
    try:
        object_ref = store.collection(u'3d_object')
        object_docs = object_ref.where(u'profile_id', u'==', str(profile_id)).order_by(u'index').stream()

        for object_doc in object_docs:
            dataDict = object_doc.to_dict()
            dataDict['doc_id'] = object_doc.id
            object_data.append(dataDict)
    except google.cloud.exceptions.NotFound:
        print(u'Missing data')
    return object_data

def get_profile_podcast(profile_id):
    podcast_data = list()
    try:
        podcast_ref = store.collection(u'podcast')
        podcast_docs = podcast_ref.where(u'profile_id', u'==', str(profile_id)).order_by(u'index').stream()

        for podcast_doc in podcast_docs:
            dataDict = podcast_doc.to_dict()
            dataDict['doc_id'] = podcast_doc.id
            published_date = dataDict.get("published_date",None)
            description = unquote(dataDict['description'])
            dataDict['description'] = description
            if published_date and isinstance(published_date, datetime_helpers.DatetimeWithNanoseconds):
                published_date = dt.datetime.combine(date=published_date.date(), time=published_date.time(), tzinfo=published_date.tzinfo)
                dataDict['published_date'] = published_date.strftime("%Y-%m-%d %H:%M:%S")
            podcast_data.append(dataDict)
    except google.cloud.exceptions.NotFound:
        print(u'Missing data')
    return podcast_data

def get_profile_trial(profile_id):
    trial_data = list()
    try:
        trial_ref = store.collection(u'trials')
        trial_docs = trial_ref.where(u'profile_id', u'==', str(profile_id)).order_by(u'index').stream()

        for trial_doc in trial_docs:
            dataDict = trial_doc.to_dict()
            dataDict['doc_id'] = trial_doc.id
            published_date = dataDict.get("published_date",None)
            if published_date and isinstance(published_date, datetime_helpers.DatetimeWithNanoseconds):
                published_date = dt.datetime.combine(date=published_date.date(), time=published_date.time(), tzinfo=published_date.tzinfo)
                dataDict['published_date'] = published_date.strftime("%Y-%m-%d %H:%M:%S")
            trial_data.append(dataDict)
    except google.cloud.exceptions.NotFound:
        print(u'Missing data')
    return trial_data

def get_profile_s911s(profile_id):
    s911s_data = list()
    try:
        s911s_ref = store.collection(u's911s')
        s911s_docs = s911s_ref.where(u'profile_id', u'==', str(profile_id)).order_by(u'index').stream()

        for s911s_doc in s911s_docs:
            dataDict = s911s_doc.to_dict()
            dataDict['doc_id'] = s911s_doc.id
            published_date = dataDict.get("published_date",None)
            if published_date and isinstance(published_date, datetime_helpers.DatetimeWithNanoseconds):
                published_date = dt.datetime.combine(date=published_date.date(), time=published_date.time(), tzinfo=published_date.tzinfo)
                dataDict['published_date'] = published_date.strftime("%Y-%m-%d %H:%M:%S")
            s911s_data.append(dataDict)
    except google.cloud.exceptions.NotFound:
        print(u'Missing data')
    return s911s_data

def get_profile_video(profile_id):
    video_data = list()
    try:
        video_ref = store.collection(u'videos')
        video_docs = video_ref.where(u'profile_id', u'==', str(profile_id)).order_by(u'index').stream()

        for video_doc in video_docs:
            dataDict = video_doc.to_dict()
            dataDict['doc_id'] = video_doc.id
            published_date = dataDict.get("published_date",None)
            if published_date and isinstance(published_date, datetime_helpers.DatetimeWithNanoseconds):
                published_date = dt.datetime.combine(date=published_date.date(), time=published_date.time(), tzinfo=published_date.tzinfo)
                dataDict['published_date'] = published_date.strftime("%Y-%m-%d %H:%M:%S")
            video_data.append(dataDict)

    except google.cloud.exceptions.NotFound:
        print(u'Missing data')
    return video_data

def get_profile_photo(profile_id):
    photo_data = list()
    try:
        photo_ref = store.collection(u'photos')
        photo_docs = photo_ref.where(u'profile_id', u'==', str(profile_id)).order_by(u'index').stream()
        for photo_doc in photo_docs:
            dataDict = photo_doc.to_dict()
            dataDict['doc_id'] = photo_doc.id
            photo_data.append(dataDict)
    except google.cloud.exceptions.NotFound:
        print(u'Missing data')
    return photo_data

def get_profile_portal(profile_id):
    photo_data = list()
    try:
        photo_ref = store.collection(u'portalsV2')
        photo_docs = photo_ref.where(u'profile_id', u'==', str(profile_id)).order_by(u'index').stream()
        for photo_doc in photo_docs:
            dataDict = photo_doc.to_dict()
            dataDict['doc_id'] = photo_doc.id
            photo_data.append(dataDict)
    except google.cloud.exceptions.NotFound:
        print(u'Missing data')
    return photo_data

def get_profile(profile_id):
    profile_data = {}
    marketplace_video_data = list()
    marketplace_books_data = list()
    try:
        doc_ref = store.collection(u'profiles').document(profile_id)
        location = {
        'latitude' : '',
        'longitude' : '',
        }
        dbLoc = {}
        if doc_ref.get().to_dict():
            dbLoc = doc_ref.get().to_dict().get('location')

            if dbLoc and 'geopoint' in dbLoc:
                location['latitude'] = doc_ref.get().to_dict().get('location').get('geopoint').latitude
                location['longitude'] = doc_ref.get().to_dict().get('location').get('geopoint').longitude
            else:
                location['latitude'] = ""
                location['longitude'] = ""
            profile_data['img_name'] = doc_ref.get().to_dict().get('img_name')
            profile_data['tags'] = doc_ref.get().to_dict().get('tags')
            profile_data['causeofdeath'] = doc_ref.get().to_dict().get('causeofdeath')
            profile_data['dateofcrime'] = doc_ref.get().to_dict().get('dateofcrime')
            profile_data['img_url'] = doc_ref.get().to_dict().get('img_url')
            profile_data['profile_city'] = doc_ref.get().to_dict().get('profile_city')
            profile_data['profile_date_crime'] = doc_ref.get().to_dict().get('profile_date_crime')
            profile_data['dateofcrime'] = doc_ref.get().to_dict().get('dateofcrime')
            profile_data['profile_publish_date'] = doc_ref.get().to_dict().get('profile_publish_date')
            profile_data['profile_name'] = doc_ref.get().to_dict().get('profile_name')
            profile_data['profile_perpetrator'] = doc_ref.get().to_dict().get('profile_perpetrator')
            profile_data['profile_publish'] = doc_ref.get().to_dict().get('profile_publish')
            profile_data['crime_type'] = doc_ref.get().to_dict().get('crime_type')
            profile_data['monetization'] = doc_ref.get().to_dict().get('monetization','Free')
            profile_data['hasDoor'] = doc_ref.get().to_dict().get('hasDoor',False)
            profile_data['profile_state'] = doc_ref.get().to_dict().get('profile_state')
            profile_data['profile_country'] = doc_ref.get().to_dict().get('profile_country')
            profile_data['profile_crime_contact_info'] = doc_ref.get().to_dict().get('profile_crime_contact_info',None)
            profile_data['profile_story'] = doc_ref.get().to_dict().get('profile_story')
            profile_data['profile_notes'] = doc_ref.get().to_dict().get('profile_notes')
            profile_data['profile_street'] = doc_ref.get().to_dict().get('profile_street')
            profile_data['profile_teaser'] = doc_ref.get().to_dict().get('profile_teaser')
            profile_data['victim'] = doc_ref.get().to_dict().get('victim')
            profile_data['zip'] = doc_ref.get().to_dict().get('zip')
            profile_data['locationPref'] = doc_ref.get().to_dict().get('locationPref',"manual")
            profile_data['location'] = location
            sharing_link_prefix = store.collection("parameters").document("sharing_link_prefix").get().to_dict().get("sharing_link_prefix")
            print("sharing_link_prefix",sharing_link_prefix)
            profile_data['sharing_link_prefix'] = sharing_link_prefix


            marketplace_video_ref = store.collection(u'marketplace_video')
            marketplace_video_ref = marketplace_video_ref.where(u'profile_id', u'==', str(profile_id)).order_by(u'index').stream()
            for marketplace_doc in marketplace_video_ref:
                dataDict = marketplace_doc.to_dict()
                dataDict['doc_id'] = marketplace_doc.id
                marketplace_video_data.append(dataDict)
            profile_data["marketplace_video"] = marketplace_video_data

            marketplace_books_ref = store.collection(u'marketplace_books')
            marketplace_books_ref = marketplace_books_ref.where(u'profile_id', u'==', str(profile_id)).order_by(u'index').stream()
            for marketplace_doc in marketplace_books_ref:
                dataDict = marketplace_doc.to_dict()
                dataDict['doc_id'] = marketplace_doc.id
                marketplace_books_data.append(dataDict)
            profile_data["marketplace_books"] = marketplace_books_data
    except google.cloud.exceptions.NotFound:
        print(u'Missing data')
    return profile_data

def get_article(article_id):
    article_ref = store.collection(u'articles').document(article_id)
    article =  article_ref.get().to_dict()
    return article

def get_3d(object_id):
    object_ref = store.collection(u'3d_object').document(object_id)
    object =  object_ref.get().to_dict()
    return object

def get_poster(object_id):
    object_ref = store.collection(u'posters').document(object_id)
    object =  object_ref.get().to_dict()
    return object


def get_podcast(podcast_id):
    podcast_ref = store.collection(u'podcast').document(podcast_id)
    podcast =  podcast_ref.get().to_dict()
    description = unquote(podcast['description'])
    podcast['description'] = description
    return podcast


def get_portal(portal_id):
    portal_ref = store.collection(u'portalsV2').document(portal_id)
    portal =  portal_ref.get().to_dict()
    description = unquote(portal['teaser'])
    portal['teaser'] = description
    return portal
"""
Show profile content
"""
@app.route("/profile/<profile_id>", methods = ['GET'])
def showProfileContent(profile_id):
    response = checkProfileId(profile_id)
    if not response.get("status",None):
        return render_template("404.html")
    else:
        data = response.get("data")
    return render_template("profile.html",data=data)

@app.route("/truecrimecases", methods = ['GET'])
def showtruecrimecases():
    doc_ref = store.collection(u'profiles').where(u'profile_publish', u'==', "true").order_by('uid').stream()
    profiles=[]

    for doc in doc_ref:
        profile = {}
        profile['profile_id']=str(doc.id)
        profile['img_url']=doc.to_dict().get('img_url')
        profile['profile_name']=doc.to_dict().get('profile_name')
        profile['profile_teaser']=doc.to_dict().get('profile_teaser')
        profile['tags']=doc.to_dict().get('tags')
        profile['causeofdeath']=doc.to_dict().get('causeofdeath')
        profile['dateofcrime']=doc.to_dict().get('dateofcrime')
        if profile['tags'] is None:
            profile['count']=0
        else:
            profile['count']=len(doc.to_dict().get('tags'))
        profiles.append(profile)
    data = {}
    data['profiles'] = profiles
    return render_template("truecrimecases.html",data=data)


@app.route("/lookup/<content_id>", methods = ['GET'])
def lookupProfile(content_id):
    ref_video = store.collection("videos").document(content_id).get()
    ref_article = store.collection("articles").document(content_id).get()
    ref_photo = store.collection("photos").document(content_id).get()
    ref_podcast = store.collection("podcast").document(content_id).get()
    ref_trial = store.collection("trials").document(content_id).get()
    ref_911 = store.collection("s911s").document(content_id).get()
    ref_report = store.collection("police_reports").document(content_id).get()
    data = {}
    data['status'] = True
    if ref_video.exists :
        data['data'] = ref_video.to_dict()
        data['type'] = 'video';
    elif ref_article.exists :
        data['data'] = ref_article.to_dict()
        data['type'] = 'article';
    elif ref_photo.exists :
        data['data'] = ref_photo.to_dict()
        data['type'] = 'photo';
    elif ref_podcast.exists :
        data['data'] = ref_podcast.to_dict()
        data['type'] = 'podcast'
    elif ref_trial.exists :
        data['data'] = ref_trial.to_dict()
        data['type'] = 'trial'
    elif ref_911.exists :
        data['data'] = ref_911.to_dict()
        data['type'] = '911'
    elif ref_report.exists :
        data['data'] = ref_report.to_dict()
        data['type'] = 'report'
    else:
        data['status'] = False
        data['message'] = 'Empty Data'

    if data['status']:
        val = data['data']
        ref_profile = store.collection("profiles").document(val['profile_id']).get()
        data['profile'] = ref_profile.to_dict()
    return render_template("lookup.html",data=data)

@app.route("/article/<profile_id>", methods = ['GET'])
def showArticleContent(profile_id):
    print("profile_id",profile_id)
    response = checkProfileId(profile_id, context='article')
    if not response.get("status",None):
        return render_template("404.html")
    else:
        data = response.get("data")
    return render_template("article.html",data=data)

@app.route("/3ds/<profile_id>", methods = ['GET'])
def show3DContent(profile_id):
    print("profile_id",profile_id)
    response = checkProfileId(profile_id, context='3d')
    if not response.get("status",None):
        return render_template("404.html")
    else:
        data = response.get("data")
    return render_template("3d_templates.html",data=data)

# @app.route("/3d/<object_id>", methods = ['GET'])
# def Show3DDetail(object_id):
#     object = get_3d(object_id)
#     profile = store.collection("profiles").document(object['profile_id']).get().to_dict()
#     profile['id'] = object['profile_id']
#     file_url = object['file_url']
#     title = object['title']
#     url = f'https://urlparam-objectloader.glitch.me/?name={title}&url={file_url}'
#     return redirect(url)

@app.route("/3d/<object_id>", methods = ['GET'])
def Show3DAFrame(object_id):
    object = get_3d(object_id)

    profile = store.collection("profiles").document(object['profile_id']).get().to_dict()
    profile['id'] = object['profile_id']
    file_url = object['file_url']
    title = object['title']
    if 'cropped_image' in object and object['cropped_image']:
        object['thumbnail'] = object['cropped_image'].replace('&amp;', '&')
    else:
        object['thumbnail'] = ''


    if 'original_image' in object and object['original_image']:
        object['original_image'] = object['original_image'].replace('&amp;', '&')
    else:
        object['original_image'] = ''

    if 'social_image' in object and object['social_image']:
        object['social_image'] = object['social_image'].replace('&amp;', '&')
    else:
        object['social_image'] = object['original_image']

    if 'preview_image' in object and object['preview_image']:
        object['preview_image'] = object['preview_image'].replace('&amp;', '&')
    else:
        object['preview_image'] = object['original_image']

    object['social_image'] = object['preview_image']
    object['share_url'] = 'https://share.crimedoor.com/poster/' + object_id


    return render_template('3d_aframe.html', data=object, profile=profile)

@app.route('/3d/test', methods = ['GET'])
def Show3DTest():
    data = {
        'title': '3D Test Model',
        'file_url': url_for('static', filename='3d/model.glb')
    }
    return render_template('3d_test.html', data=data)



@app.route("/poster/<object_id>/removeLearnMore/1", methods = ['GET'])
def ShowPosterFromApp(object_id):
    return ShowPoster(object_id, True)

@app.route("/poster/<object_id>", methods = ['GET'])
def ShowPoster(object_id, remove_learn_more = False):
    object = get_poster(object_id)

    if object is None:
        return render_template("404.html")


    wall_url = 'https://crimedoor.8thwall.app/missing-persons?profile-url='
    dynamic_link = object['dynamic_link']
    embeded_url = wall_url + dynamic_link + '&object-url=' + object['file_url']
    object['embeded_url'] = embeded_url

    redirect_url = 'http://crimedoor.8thwall.app/missing-persons?'
    if remove_learn_more:
        profile_url = ''
    else:
        profile_link = dynamic_link
        profile_url = f'learnmore=&profile-url={profile_link}&'

    share_link = 'sharelink=http://share.crimedoor.com/poster/'+object_id+'&'

    object['redirect_url'] = 'http://crimedoor.8thwall.app/missing-persons?'+profile_url+share_link+'object-url='+object['file_url']

    if 'cropped_image' in object:
        object['thumbnail'] = object['cropped_image'].replace('&amp;', '&')
    else:
        object['thumbnail'] = ''

    if 'original_image' in object:
        object['original_image'] = object['original_image'].replace('&amp;', '&')
    else:
        object['original_image'] = ''

    if 'social_image' in object and object['social_image']:
        object['social_image'] = object['social_image'].replace('&amp;', '&')
    else:
        object['social_image'] = object['original_image']

    object['share_url'] = 'https://share.crimedoor.com/poster/' + object_id

    return render_template('poster.html', data = object)


@app.route("/question/<doc_id>", methods = ['GET'])
def question(doc_id):
    data = {}
    data['id'] = doc_id
    return render_template('3d_question.html', data=data);
@app.route("/articles/<article_id>", methods = ['GET'])
def ShowArticleDetail(article_id):
    article = get_article(article_id)
    profile = store.collection("profiles").document(article['profile_id']).get().to_dict()

    site_status = _http_request(article['url'])
    print(site_status)
    article['status'] = site_status
    return render_template("article_detail.html", data=article, profile=profile)

def _http_request(url):
   response = requests.get(url)
   headers = response.headers
   # Check Content-Security-Policy
   if headers.get('Content-Security-Policy',None) and headers.get('Content-Security-Policy',None) not in ["upgrade-insecure-requests","block-all-mixed-content"]:
       return False
   elif headers.get("X-Frame-Options",None) and headers.get("X-Frame-Options",None) in ("SAMEORIGIN","DENY"):
       return False
   elif headers.get('Set-Cookie',None) and headers.get('Set-Cookie').find("SameSite=None") > -1 :
       return False
   else:
       return True

@app.route("/podcasts", methods = ['GET'])
def podcasts():
    podcast_data = list()
    try:
        podcast_ref = store.collection(u'podcast')
        podcast_docs = podcast_ref.order_by(u'index').stream()

        for podcast_doc in podcast_docs:
            dataDict = podcast_doc.to_dict()
            dataDict['doc_id'] = podcast_doc.id
            published_date = dataDict.get("published_date",None)
            description = unquote(dataDict['description'])
            dataDict['description'] = description
            if published_date and isinstance(published_date, datetime_helpers.DatetimeWithNanoseconds):
                published_date = dt.datetime.combine(date=published_date.date(), time=published_date.time(), tzinfo=published_date.tzinfo)
                dataDict['published_date'] = published_date.strftime("%Y-%m-%d %H:%M:%S")
            podcast_data.append(dataDict)
    except google.cloud.exceptions.NotFound:
        print(u'Missing data')
    return render_template("podcast_list.html", data = podcast_data)

@app.route("/podcasts/<podcast_id>", methods = ['GET'])
def ShowPodcastDetail(podcast_id):
    podcast = get_podcast(podcast_id)
    print(podcast)
    return render_template("podcast_detail.html", data=podcast)


@app.route("/crimedoors/<portal_id>", methods = ['GET'])
def ShowPortalDetail(portal_id):
    portal = get_portal(portal_id)
    portal[id] = portal_id
    return render_template("portal_detail.html", data=portal)

@app.route("/podcast/<profile_id>", methods = ['GET'])
def showPodcastContent(profile_id):
    print("profile_id",profile_id)
    response = checkProfileId(profile_id, context='podcast')
    if not response.get("status",None):
        return render_template("404.html")
    else:
        data = response.get("data")
    return render_template("podcast.html",data=data)

@app.route("/trials/<profile_id>", methods = ['GET'])
def showTrialsContent(profile_id):
    print("profile_id",profile_id)
    response = checkProfileId(profile_id, context='trials')
    if not response.get("status",None):
        return render_template("404.html")
    else:
        data = response.get("data")
    return render_template("trials.html",data=data)

@app.route("/s911s/<profile_id>", methods = ['GET'])
def showS911sContent(profile_id):
    print("profile_id",profile_id)
    response = checkProfileId(profile_id, context='s911s')
    if not response.get("status",None):
        return render_template("404.html")
    else:
        data = response.get("data")
    return render_template("s911s.html",data=data)

@app.route("/police_reports/<profile_id>", methods = ['GET'])
def showPolice_reportsContent(profile_id):
    print("profile_id",profile_id)
    response = checkProfileId(profile_id, context='police_reports')
    if not response.get("status",None):
        return render_template("404.html")
    else:
        data = response.get("data")
    return render_template("police_reports.html",data=data)

@app.route("/video/<profile_id>", methods = ['GET'])
def showVideoContent(profile_id):
    print("profile_id",profile_id)
    response = checkProfileId(profile_id, context='video')
    if not response.get("status",None):
        return render_template("404.html")
    else:
        data = response.get("data")
    return render_template("video.html",data=data)

@app.route("/photo/<profile_id>", methods = ['GET'])
def showPhotoContent(profile_id):
    print("profile_id",profile_id)
    response = checkProfileId(profile_id, context='photo')
    if not response.get("status",None):
        return render_template("404.html")
    else:
        data = response.get("data")
    return render_template("photo.html",data=data)

@app.route("/contact", methods=['GET', 'POST'])
def contact ():
    if request.method == 'GET':
        return render_template("contact.html")
    else:
        pass

@app.route("/tags", methods=['GET'])
def tags():
    tags = list()
    list_val = list()

    list_val = [
        'murdered',
        'missing person',
        'mysterious death',
        'unsolved',
        'abducted',
        'arson',
        'assassinated',
        'bludgeoned',
        'bombed',
        'burned',
        'cannibalized',
        'crime of passion',
        'cult',
        'disappeared',
        'dismembered',
        'drowned',
        'exposure',
        'familicide',
        'filicide',
        'gang',
        'hanging',
        'hate crime',
        'hijacked',
        'honor killing',
        'infamous',
        'immolated',
        'mass murder',
        'mass suicide',
        'overdosed',
        'poisoned',
        'raped',
        'school shooting',
        'serial killer victim',
        'shot',
        'stabbed',
        'strangled',
        'suicide',
        'suspicious circumstances',
        'terrorism',
        'tortured',
        'reward offered'
    ]
    for tag in list_val:
        item = {}
        item['title'] = tag

        item['link'] = tag.replace('/', '=')
        tags.append(item)
    return render_template("tags.html", data=tags)

@app.route('/articles', methods = ['GET'])
def articles():
    articles = list()
    articles_ref = store.collection("articles").order_by("publishedAt",direction=firestore.Query.DESCENDING).stream()
    # orders_docs = [snapshot for snapshot in articles_ref]
    for item in orders_docs:
        article = {}
        article = item.to_dict()
        # published_date_time = ''
        # if 'publishedDate' in article:
        #     pass
        # else:
        #     if isinstance(article['publishedAt'], datetime_helpers.DatetimeWithNanoseconds):
        #         edit_data = dict()
        #         publishedAt = convertFirebaseTimeToPdt(article['publishedAt'],True)
        #         published_date_time = publishedAt.strftime("%m-%d-%Y")
        #         edit_data['publishedDate'] = published_date_time
        #         ref = store.collection('articles').document(item.id).update(edit_data)
        #     elif article['publishedAt']:
        #         edit_data = dict()
        #         publishedAt = convertFirebaseTimeToPdt(article['publishedAt'],True)
        #         published_date_time = publishedAt.strftime("%m-%d-%Y")
        #         edit_data['publishedDate'] = published_date_time
        #         ref = store.collection('articles').document(item.id).update(edit_data)
        article['id'] = item.id
        articles.append(article)
    return render_template('articles.html', data = articles)

@app.route("/photos/<doc_id>", methods = ["GET"])
def image(doc_id):
    image = store.collection("photos").document(doc_id).get().to_dict()
    return render_template("image.html", data = image)

@app.route("/videos/<doc_id>", methods = ["GET"])
def video(doc_id):
    video = store.collection("videos").document(doc_id).get().to_dict()
    profile = store.collection("profiles").document(video['profile_id']).get().to_dict()
    print(profile)
    return render_template("video_detail.html", data = video, profile= profile)

@app.route("/tags/<tag_name>", methods = ['GET'] )
def tag_filter(tag_name):
    tag_name = tag_name.replace('=', '/')
    profiles = list()
    data = {}
    profile_ref = store.collection(u'profiles')
    profiles_docs = profile_ref.where(u'profile_publish', u'==', "true").where("tags", "array_contains", str(tag_name)).stream()
    for profile_data in profiles_docs:
        profile = profile_data.to_dict()
        profile['doc_id'] = profile_data.id
        if profile['tags'] is None:
            profile['count']=0
        else:
            profile['count']=len(profile['tags'])
        profiles.append(profile)
        data['profiles'] = profiles
        data['tag'] = tag_name
    return render_template("tag_list.html", data=data)

def convertFirebaseTimeToPdt(dt,notFormatted=False):
  import pytz
  tz = pytz.timezone("America/Los_Angeles")
  try:
    if isinstance(dt,str):
      dt = parser.parse(dt)
    # dt = dt + timedelta(1)
    if notFormatted:
      return tz.normalize(dt.astimezone(tz))
    else:
      return tz.normalize(dt.astimezone(tz)).strftime("%Y-%m-%d")
  except Exception as e:
    print("Could not normalize=>",e)
    return dt

@app.route("/admin", methods = ['GET'])
def admin():
    return render_template("admin.html")

# @app.route('/get_page', methods = ['POST'])
# def get_page():
#     if request.method == 'POST':
#         data = {}
#         try:
#             post_data = request.form.to_dict()
#             collection_type = post_data['type']
#             print(post_data['page'])
#             start = int(post_data['page']) * 50
#             data['type'] = post_data['type']
#             data['data'] = list()

#             data_ref = store.collection(collection_type).order_by('index').start_at({u'index': 50}).limit(50).stream()
#             print(collection_type)
#             for item in data_ref:
#                 data['data'].append(item.to_dict())
#             print("HHHH")
#             data['status'] = True
#         except Exception as e:
#             print(e)
#             data['status'] = False

#     return data

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug = True)