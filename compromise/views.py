from hashlib import md5
import json

from bson.objectid import ObjectId
from gdata.contacts.client import ContactsClient
from gdata.gauth import OAuth2Token
from django.core.mail import send_mail
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.shortcuts import render_to_response, redirect
from pymongo import Connection
from social_auth.models import UserSocialAuth

from compromise.settings import ANSWER_URL, EMAIL_SUBJECT_CREATE, EMAIL_TEXT_CREATE, EMAIL_HOST_USER


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
        currentCompromise = request.POST.get("json")
        currentCompromise = json.loads(currentCompromise)

        compromisesCollection = Connection(host="127.0.0.1", port=27017)["compDB"]["compromises"]
        invitesCollection = Connection(host="127.0.0.1", port=27017)["compDB"]["sentInvites"]

        users = currentCompromise.get("users", [])
        recordId = compromisesCollection.insert(currentCompromise)

        for user in users:
            uniqDesc = md5(user + str(recordId)).hexdigest()
            uniqUrl = ANSWER_URL + uniqDesc

            invitesCollection.insert({"uniqDesc": uniqDesc, "compromiseId": str(recordId)})
            send_mail(EMAIL_SUBJECT_CREATE, (EMAIL_TEXT_CREATE % uniqUrl), EMAIL_HOST_USER, [user])

        return HttpResponse('{"status": "ok", "url": %s}' % uniqUrl)

    except TypeError:
        return HttpResponse("bad json")


def renderAnswer(request):
    uniqDesc = request.GET.get("id")

    compromisesCollection = Connection(host="127.0.0.1", port=27017)["compDB"]["compromises"]

    answersCollection = Connection(host="127.0.0.1", port=27017)["compDB"]["answers"]
    curAnswer = answersCollection.find_one({"uniqDesc": uniqDesc})

    if curAnswer:
        return HttpResponseNotFound('<h1>You have already voted</h1>')   
    else:
        invitesCollection = Connection(host="127.0.0.1", port=27017)["compDB"]["sentInvites"]
        curAnswer = invitesCollection.find_one({"uniqDesc": uniqDesc})
        if curAnswer:
            idEvent = curAnswer.get("compromiseId")
            curEvent = compromisesCollection.find_one({"_id": ObjectId(idEvent)})
            curEvent["_id"] = str(curEvent["_id"])
            curEvent["uniqDesc"] = uniqDesc
            return render_to_response("showevent.html", {"json": json.dumps(curEvent)})
        else:
            return HttpResponseNotFound('<h1>Page not found</h1>')


def addAnswer(request):
    curAnswer = request.POST.get("json")
    curAnswer = json.loads(curAnswer)

    compromisesCollection = Connection(host="127.0.0.1", port=27017)["compDB"]["compromises"]
    curRecord = compromisesCollection.find_one({"_id": ObjectId(curAnswer["_id"])})

    del curAnswer["_id"]
    curAnswer["compromiseId"] = str(curRecord["_id"])
    curAnswer["uniqDesc"] = curAnswer["uniqDesc"]

    answersCollection = Connection(host="127.0.0.1", port=27017)["compDB"]["answers"]
    answersCollection.insert(curAnswer)

    del curRecord["_id"]
    return HttpResponse(json.dumps(curRecord))


def ready(request):
    compromise_id = request.GET.get("id")

    compromisesCollection = Connection(host="127.0.0.1", port=27017)["compDB"]["results"]
    compromise = compromisesCollection.find_one({"_id": ObjectId(compromise_id)})

    if compromise:
        del compromise["_id"]
        return render_to_response("readyevent.html", {"json": json.dumps(compromise)})
    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')