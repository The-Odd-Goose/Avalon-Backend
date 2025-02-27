# firebase stuff, initialize once

import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin.auth import UserNotFoundError

# cred = credentials.Certificate("./service-account.json") # based on app, not here
# default_app = firebase_admin.initialize_app(cred)
# TODO: switch to this for deployment
default_app = firebase_admin.initialize_app()

db = firestore.client()

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

# returns either the list with the player inside it, or a new reference to a new player
def doesUserExistInGame(players_ref, uid):

    # now we query for a specific player with our uid
    player_lst = getUser(players_ref, uid)

    if len(player_lst) == 0:
        return False
    return player_lst[0]

# only use getUser if we know 
def getUser(players_ref, uid):
    players = players_ref.where(u"uid", u"==", uid).limit(1)
    return [p for p in players.stream()]

# queries the owner of the game
def getOwner(players_ref):
    owner = players_ref.where(u"owner", u"==", True)
    owner_ref = [p for p in owner.stream()][0]
    return owner_ref

def getMerlinAndMorgana(players_ref, role):
    player = players_ref.where(role, u"==", True).limit(1)
    player_ref = [p for p in player.stream()][0]
    return player_ref