#!/usr/bin/python

import os
from time import time

from django.core.mail import send_mail
from pymongo import Connection

from settings import EMAIL_SUBJECT_RESULT, EMAIL_TEXT_RESULT, EMAIL_HOST_USER

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

compromises = Connection(host="127.0.0.1", port=27017)['compDB']['compromiseCollection']
for compromise in compromises.find({'type': 'event'}):
    compromise_id = compromise["_id"]
    timeEvent = compromise["timestamp"]
    deltaTime = time() * 1000 - (timeEvent + 300000)
    if deltaTime > 0:
        for user in compromises.find({'idEvent': str(compromise_id)}):
            send_mail(EMAIL_SUBJECT_RESULT, (EMAIL_TEXT_RESULT % compromise_id), EMAIL_HOST_USER, [user["mail"]])
        compromise["type"] = "protuxlo"
        compromises.save(compromise)
