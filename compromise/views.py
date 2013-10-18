from hashlib import md5
import json
import smtplib

from bson.objectid import ObjectId
from gdata.contacts.client import ContactsClient
from gdata.gauth import OAuth2Token
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from pymongo import Connection
from social_auth.models import UserSocialAuth

from compromise.settings import ANSWER_URL, EMAIL_SUBJECT_CREATE, EMAIL_TEXT_CREATE, EMAIL_HOST_USER

def sendMail(subj, text, reciver):
    msg = MIMEText(text)
    msg['Subject'] = subj
    msg['From'] = 'noreply@compromise.best',
    msg['To'] = reciver

    s = smtplib.SMTP('37.200.65.226')
    s.sendmail(msg['From'], [reciver], msg.as_string())


def hello(request):
    return HttpResponse("hello")


def index(request):
    if request.user.is_authenticated():
        return redirect('/newevent/')
    else:
        return render_to_response("index.html")


def newevent(request):
    if request.user.is_anonymous():
        return redirect('/')

    emails = []
    u = UserSocialAuth.get_social_auth_for_user(request.user).get()
    if u.provider == 'google-oauth2':
        access_token = u.tokens['access_token']
        credentials = OAuth2Token('342640484025.apps.googleusercontent.com', 'K_4sKJDOYZ0GNdKkiOaihPfk', 'user',
                                  'my-user-agent/1.0', access_token=access_token)
        gd_client = ContactsClient()
        credentials.authorize(gd_client)
        feed = gd_client.GetContacts()
        for entry in enumerate(feed.entry):
            for email in entry[1].email:
                emails.append(email.address)
    return render_to_response("newevent.html", {'emails': emails})


def saveCompromise(request):
    try:
        #user = "kniaz1234@gmail.com"
        #send_mail(EMAIL_SUBJECT_CREATE, (EMAIL_TEXT_CREATE % "http://ya.ru/"), EMAIL_HOST_USER, [user])
        currentCompromise = request.POST.get("json")

        currentCompromise = json.loads(currentCompromise)

        mongoConnection = Connection(host="127.0.0.1", port=27017)["compDB"]["compromiseCollection"]
        users = currentCompromise.get("users", [])
        if not users:
            users = ['kniaz1234@gmail.com', 'michaelpak@live.ru', "russtone@yandex.ru"]

        currentCompromise["type"] = "event"
        recordId = mongoConnection.insert(currentCompromise)

        for user in users:
            uniqDesc = md5(user + str(recordId)).hexdigest()
            uniqUrl = ANSWER_URL + uniqDesc

            mongoConnection.insert({"uniqDesc": uniqDesc, "idEvent": str(recordId), 'mail': user})
            send_mail(EMAIL_SUBJECT_CREATE, (EMAIL_TEXT_CREATE % uniqUrl), EMAIL_HOST_USER, [user])

        return HttpResponse('{"status": "ok", "url": %s}' % uniqUrl)

    except TypeError:
        return HttpResponse("bad json")


def renderAnswer(request):
    uniqDesc = request.GET.get("id")
    mongoConnection = Connection(host="127.0.0.1", port=27017)["compDB"]["compromiseCollection"]
    curAnswer = mongoConnection.find_one({"uniqDesc": uniqDesc})
    idEvent = curAnswer.get("idEvent")
    curEvent = mongoConnection.find_one({"_id": ObjectId(idEvent)})
    curEvent["_id"] = str(curEvent["_id"])
    return render_to_response("showevent.html", {"json": json.dumps(curEvent)})


def addAnswer(request):
    curAnswer = request.POST.get("json")
    curAnswer = json.loads(curAnswer)
    compromises = Connection(host="127.0.0.1", port=27017)["compDB"]["compromiseCollection"]
    curRecord = compromises.find_one({"_id": ObjectId(curAnswer["_id"])})

    del curAnswer["_id"]
    curAnswer["type"] = "answer"
    curAnswer["compromise_id"] = curRecord["_id"]

    answers = Connection(host="127.0.0.1", port=27017)["compDB"]["answers"]
    answers.insert(curAnswer)

    del curRecord["_id"]
    return HttpResponse(json.dumps(curRecord))


def ready(request):
    compromise_id = request.GET.get("id")

    compromises = Connection(host="127.0.0.1", port=27017)["compDB"]["compromiseCollection"]
    compromise = compromises.find_one({"_id": ObjectId(compromise_id)})

    for q in compromise["questions"]:
        for a in q["answers"]:
            a["current"] = 0.0
    answers = Connection(host="127.0.0.1", port=27017)['compDB']['answers']
    for answer in answers.find({'compromise_id': ObjectId(compromise_id)}):
        for i, q in enumerate(answer["questions"]):
            for j, a in enumerate(q["answers"]):
                compromise["questions"][i]["answers"][j]["current"] += float(a["current"])

    for q in compromise["questions"]:
        for a in q["answers"]:
            if a["current"] > q["answers"][0]["current"]:
                q["answers"][0] = a
        del q["answers"][1:]

    del compromise["_id"]
    return render_to_response("readyevent.html", {"json": json.dumps(compromise)})
