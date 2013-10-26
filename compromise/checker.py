#!/usr/bin/python

import os
from time import time

from bson.objectid import ObjectId
from django.core.mail import send_mail
from pymongo import Connection

from settings import EMAIL_SUBJECT_RESULT, EMAIL_TEXT_RESULT, EMAIL_HOST_USER

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

compromises = Connection(host="127.0.0.1", port=27017)['compDB']['compromises']
for compromise in compromises.find():
    compromise_id = compromise["_id"]
    timeEvent = compromise["timestamp"]
    deltaTime = time() * 1000 - (timeEvent + 300000)
    if deltaTime > 0:
	    for q in compromise["questions"]:
	        for a in q["answers"]:
	            a["current"] = 0.0
	    answersCollection = Connection(host="127.0.0.1", port=27017)['compDB']['answers']
	    for answer in answersCollection.find({'compromiseId': str(compromise_id)}):
	        for i, q in enumerate(answer["questions"]):
	            for j, a in enumerate(q["answers"]):
	                compromise["questions"][i]["answers"][j]["current"] += float(a["current"])

	    for q in compromise["questions"]:
	        for a in q["answers"]:
	            if a["current"] > q["answers"][0]["current"]:
	                q["answers"][0] = a
	        del q["answers"][1:]

	    resultCollection = Connection(host="127.0.0.1", port=27017)['compDB']['results']
	    resultCollection.insert(compromise)

	    invitesCollection = Connection(host="127.0.0.1", port=27017)['compDB']['sentInvites']

	    compromises.remove({'_id': compromise_id})
	    answersCollection.remove({'compromiseId': str(compromise_id)})
	    invitesCollection.remove({'compromiseId': str(compromise_id)})

	    users = compromise.get("users", [])
	    for user in users:
	        send_mail(EMAIL_SUBJECT_RESULT, (EMAIL_TEXT_RESULT % compromise_id), EMAIL_HOST_USER, [user])