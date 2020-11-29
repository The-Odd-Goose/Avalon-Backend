# firebase stuff, initialize once

import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("./service-account.json") # based on app, not here
default_app = firebase_admin.initialize_app(cred)
# TODO: switch to this for deployment
# default_app = firebase_admin.initialize_app()

db = firestore.client()

# given a game id, checking for a certain player's docId, and given userId,
# make sure that the player's docId.uid is the same as given userId
def checkPlayersUid(gameId, docId, userId):
    pass