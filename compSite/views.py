# Create your views here.
from django.http import HttpResponse
from pymongo import Connection

def hello(request):
	return HttpResponse("hello")

def saveCompromise(request):
 	a = Connection(host = "127.0.0.1", port=27017)
	return HttpResponse(request.POST.get("compromise", "asd"))
