# firebase stuff, initialize once

import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin.auth import UserNotFoundError

cred = credentials.Certificate("./service-account.json") # based on app, not here
default_app = firebase_admin.initialize_app(cred)
# TODO: switch to this for deployment
# default_app = firebase_admin.initialize_app()

db = firestore.client()

# given a game id, checking for a certain player's docId, and given userId,
# make sure that the player's docId.uid is the same as given userId
def checkPlayersUid(gameId, docId, userId):
    pass

def getGameRef(gameId):
    game_ref = db.collection(u'games').document(gameId)
    return game_ref

def getGameDict(game_ref):
    return game_ref.get().to_dict()

# checks if a user exists
# throws an error, and returns a string if user DNE, otherwise, returns the user itself
def doesUserExist(uid):
    from firebase_admin import auth
    UserNotFoundError = auth.UserNotFoundError

    try:
        user = auth.get_user(uid)
        return user
    except UserNotFoundError as e:
        return "User Not Found... Login"

def doesGameExist(game_id):
    game_ref = db.collection(u'games').document(game_id)
    game = game_ref.get()

    if game.exists:
        # if the game exists, return the game ref
        return game_ref
    
    # otherwise, return a string defining its error
    return "Error: game does not exist"

def doesUserExistInGame(game_ref, uid):
    players_ref = game_ref.collection(u'players')

    # now we query for a specific player with our uid
    players_ref.where(u"uid", u"==", uid).limit(1)

    player_lst = [p for p in players_ref.stream()]

    if len(player_lst) == 0:
        return players_ref.document()

    return "User already exists!"