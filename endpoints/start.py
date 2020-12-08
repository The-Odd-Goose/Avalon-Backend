from flask import Blueprint, request, jsonify

# other required stuff
from typing import List
import random

from endpoints.firebase import db, getGameRef

# type checking + user auth:
from endpoints.type import does_user_exist_in_game, game_Exist, is_User, UIDError, GameIDError

# so here we'll define endpoints to start the game
start = Blueprint('start', __name__)

# the start of a new game
newGame = {
    u"fail": 0,
    u"rejected": 0,
    u"success": 0,
    u"turn": 0, # the turn of the game
    u"missionMaker": None, # the mission maker
    u"votedFor": 0, # number of players voting for mission
    u"mission": [] # players on the mission
}

# how we get the game's id
def getGameId(game_ref):
    return game_ref.id

def init_player(player_ref, username, user):
    player_ref.set({
        u'username': username,
        u'uid': user.uid,
        u'photoURL': user.photo_url,
        u'merlin': False,
        u'mordred': False,
        u'bad': False,
        u'percival': False,
        u'morgana': False
    })

# creating a game endpoint
@start.route("/createGame", methods=['POST'])
def createGame():

    if request.method ==  'POST':
        try: 

            data = request.json
            user = is_User(data)

            game_ref = db.collection(u'games').document()
            game_ref.set(newGame)

            owner_ref = game_ref.collection(u'players').document()
            init_player(owner_ref, data.get("username"), user)

            game_ref.update({
                u'owner': owner_ref
            })

            # got the game id to work!!
            return jsonify({
                u"gameId": getGameId(game_ref)
            })

        except UIDError as e:
            return e.message
        except ValueError as e:
            return "UID request was incorrect"

@start.route("/addToGame", methods=['POST'])
def addToGame():

    # TODO: cap number of players
    if request.method == 'POST':
        # data needs to be of type:
        # {
        #   username, gameId, uid --- note we will get photoURL through uid
        # }
        data = request.json

        try:

            user = is_User(data)
            game_ref = game_Exist(data)
            new_player_ref = does_user_exist_in_game(game_ref, user.uid)

            # so now we grab the game reference, and we add our player to the collection of players
            init_player(new_player_ref, data.get("username"), user)

            return "Success!"

        # what happens with different types of errors
        except UIDError as e:
            return f"Failure occured due to user... {e.message}"
        except GameIDError as e:
            return f"Failure occured due to game id... {e.message}"

# TODO: rewrite the rules, so that way the bad, merlin, mordred, etc. are all in the players, not accessed to everyone
@start.route("/startGame", methods=['POST'])
def startGame():

    if request.method == 'POST':
        data = request.json

        # TODO: check if game exists, and if userId is the owner
        game_ref = game_Exist(data)

        # input stream of all players
        players = game_ref.collection(u'players').stream()

        # now we'll copy over the players from the stream
        lst_players = [p for p in players]

        if len(lst_players) < 5:
            return "Not enough players!"

        def selectRandomPlayer(lst_players: List):
            return random.randint(0, len(lst_players) - 1)

        missionMaker = lst_players[0].id # our mission maker is arbitrarily the first one

        # and now we'll assign their roles
        merlinIndex = selectRandomPlayer(lst_players)
        merlin = lst_players[merlinIndex].id # grab merlin first
        del lst_players[merlinIndex]

        percivalIndex = selectRandomPlayer(lst_players)
        percival = lst_players[percivalIndex].id # grab percival first
        del lst_players[percivalIndex]

        bad_players = []
        morganaIndex = selectRandomPlayer(lst_players)
        morgana = lst_players[morganaIndex].id # grab morgana first
        del lst_players[morganaIndex]

        mordredIndex = selectRandomPlayer(lst_players)
        mordred = lst_players[mordredIndex].id # grab mordred first
        del lst_players[mordredIndex]

        bad_players.append(morgana)
        bad_players.append(mordred)

        # now if the number of players >= 7, add a third bad guy
        if len(lst_players) >= 7:
            badIndex = selectRandomPlayer(lst_players)
            bad = lst_players[badIndex].id
            bad_players.append(bad)

        # now we'll update the roles
        game_ref.update({
            u'merlin': merlin,
            u'percival': percival,
            u'morgana': morgana,
            u'mordred': mordred,
            u'bad': bad_players,
            u'missionMaker': missionMaker
        })

        return "Success!"
