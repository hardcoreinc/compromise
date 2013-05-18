# -*- coding: utf-8 -*-
import json
import smtplib
#import requests
#from email.mime.text import MIMEText
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render_to_response
from pymongo import Connection
from hashlib import md5
from compromise.settings import *
from urllib import urlencode
from httplib import HTTPSConnection

def sendMail(subj, text, reciver):
	msg = MIMEText(text)
	msg['Subject'] = subj
	msg['From'] = 'noreply@compromise.best',
	msg['To'] = reciver

	s = smtplib.SMTP('37.200.65.226')
	s.sendmail(msg['From'] , [reciver], msg.as_string())


def hello(request):
	return HttpResponse("hello")


def index(request):
	return render_to_response("index.html")

def saveCompromise(request):
	try:
		#user = "kniaz1234@gmail.com"
		#send_mail(EMAIL_SUBJECT_CREATE, (EMAIL_TEXT_CREATE % "http://ya.ru/"), EMAIL_HOST_USER, [user])
		currentCompromise = request.POST.get("json")	

		currentCompromise = json.loads(currentCompromise)

	 	mongoConnection = Connection(host = "127.0.0.1", port=27017)["compDB"]["compromiseCollection"]
	 	users = currentCompromise.get("users", [])
	 	if not users:
	 		users = ['kniaz1234@gmail.com', 'michaelpak@live.ru']

		recordId = mongoConnection.insert(currentCompromise)
		
		for user in users:
			uniqDesc = md5(user + str(recordId)).hexdigest()
			uniqUrl = ANSWER_URL + uniqDesc

			mongoConnection.insert({"uniqDesc": uniqDesc, "idEvent": str(recordId)})
			send_mail(EMAIL_SUBJECT_CREATE, (EMAIL_TEXT_CREATE % uniqUrl), EMAIL_HOST_USER, [user])

		return HttpResponse({"status": "ok", "url": uniqUrl})

	except TypeError:
		return HttpResponse("bad json")

def renderAnswer(request):
	uniqDesc = request.GET.get("id")
	mongoConnection = Connection(host = "127.0.0.1", port=27017)["compDB"]["compromiseCollection"]
	curAnswer = mongoConnection.find({"uniqDesc": uniqDesc})
	idEvent = curAnswer.get("idEvent")
	curEvent = mongoConnection.find({"_id": idEvent})
	return HttpResponse(json.dumps(curEvent))

def addAnswer(request):
	try:
		currentCompromise = request.POST.get("compromise")
		uniqDesc = request.GET.get("id")
		currentCompromise = json.loads(currentCompromise)
	 	
	 	mongoConnection = Connection(host = "127.0.0.1", port=27017)
	 	users = currentCompromise.get("users")
	 	
		["compDB"]["compromiseCollection"].insert(currentCompromise)
		
		for user in users:
			send_mail(EMAIL_SUBJECT_CREATE, (EMAIL_TEXT_CREATE % "http://ya.ru/"), EMAIL_HOST_USER, [user])

		return HttpResponse("ok")
	#except ValueError:
	#	return HttpResponse("bad json")
	except TypeError:
		return HttpResponse("bad json")

def oauth2google(request):
	#return HttpResponse(request.GET.get("code"))
	postData = {
		"code": request.GET.get("code"),
		"client_id": "342640484025.apps.googleusercontent.com",
		"client_secret": "K_4sKJDOYZ0GNdKkiOaihPfk",
		"redirect_uri": "http//hardcoresoftware.ru:8000/",
		"grant_type": "authorization_code"
		}

	path = "http://accounts.google.com:443/o/oauth2/token"
	
	headerData = {'Content-type': 'application/x-www-form-urlencoded'}
	HTTPSConnection()
	r = requests.post(path, data=urlencode(postData), headers=headerData)
	r = requests.post("http://ya.ru/")
	return HttpResponse(r.content)
