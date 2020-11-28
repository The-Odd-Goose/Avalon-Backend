from flask import Blueprint, request, jsonify

# firebase stuff
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
    u"fail": 0,
    u"rejected": 0,
    u"success": 0,
    u"turn": 0,
    u"voted": [],
    u"bad": [],
    u"merlin": None, # these are references to the special characters
    u"percival": None,
    u"morgana": None,
    u"mordred": None
}

# how we get the game's id
def getGameId(game_ref):
    return game_ref.id

# creating a game endpoint
@start.route("/createGame", methods=['POST'])
def createGame():

    # TODO: add in the type checking, our owner needs to have:
    # TODO: username, uid, photoURL
    if request.method ==  'POST':
        game_ref = db.collection(u'games').document()
        game_ref.set(newGame)

        data = request.json

        owner_ref = game_ref.collection(u'players').document()
        owner_ref.set({
            u'username': data.get('username')
        })

        game_ref.update({
            u'owner': owner_ref
        })


        # got the game id to work!!
        return jsonify({
            u"gameId": getGameId(game_ref)
        })

@start.route("/addToGame", methods=['POST'])
def addToGame():

    # TODO: same as above, type checking, etc.
    # TODO: extra field of gameId
    # TODO: make sure we can't add the same player multiple times, this will require a query
    # TODO: query to make sure game exists
    if request.method == 'POST':
        data = request.json

        # so now we grab the game reference, and we add our player to the collection of players
        game_id = data.get('gameId')
        new_player_ref = db.collection(u'games').document(game_id).collection(u'players').document()

        new_player_ref.set({
            u'username': data.get('username')
        })

        return "Success!"