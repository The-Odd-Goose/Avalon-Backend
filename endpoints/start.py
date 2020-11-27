from flask import Blueprint, request
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("./service-account.json") # based on app, not here
default_app = firebase_admin.initialize_app(cred)
# TODO: switch to this for deployment
# default_app = firebase_admin.initialize_app()

db = firestore.client()

# so here we'll define endpoints to start the game
start = Blueprint('start', __name__)

# the start of a new game
newGame = {
    u'test': 0,
    u'bad': [],
    u'merlin': None
}

# how we get the game's id
def getGameId(game_ref):
    return game_ref.id

# creating a game endpoint
@start.route("/createGame", methods=['POST'])
def createGame():

    if request.method ==  'POST':
        game_ref = db.collection(u'games').document()
        game_ref.set(newGame)

        # got the game id to work!!
        return f"The Game id is {game_ref.id}"