from pymongo import Connection
from time import time
import json

mongoConnection = Connection(host="127.0.0.1", port=27017)['compDB']['compromiseCollection']
for event in mongoConnection.find({'type': 'event'}):
	idEvent = event["_id"]
	timeEvent = event["timestamp"]
	deltaTime = time() - timeEvent
#	if deltaTime < 600:
#		continue
#	for event1 in mongoConnection.find({'idEvent': str(idEvent)})
	print event