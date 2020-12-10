from flask import Blueprint, request, jsonify, abort

# other required stuff
from typing import List
import random

from endpoints.firebase import db, getGameRef

# type checking + user auth:
from endpoints.type import does_user_exist_in_game, game_Exist, is_User, UIDError, GameIDError, is_owner_of_game

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
        u'morgana': False,
        u'owner': False
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

            # we'll update who the owner is by saving it directly into player
            owner_ref.update({
                u'owner': True
            })

            # got the game id to work!!
            return jsonify({
                u"gameId": getGameId(game_ref)
            })

        except UIDError as e:
            abort(403, e.message)
        except ValueError as e:
            abort(400, "UID request was incorrect")

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
            player_ref = game_ref.collection(u"players")
            new_player_ref = does_user_exist_in_game(player_ref, user.uid)

            # so now we grab the game reference, and we add our player to the collection of players
            init_player(new_player_ref, data.get("username"), user)

            return "Success!"

        # what happens with different types of errors
        except UIDError as e:
            abort(403, f"Failure occured due to user... {e.message}")
        except GameIDError as e:
            abort(400, f"Failure occured due to game id... {e.message}")

@start.route("/startGame", methods=['POST'])
def startGame():

    if request.method == 'POST':
        data = request.json

        # TODO: more authentication stuff, like when game has started, cannot do it again
        try: 
            game_ref = game_Exist(data)
            user = is_User(data)
            players_ref = game_ref.collection(u'players')

            # if they are not the owner of the game, return false
            if not is_owner_of_game(players_ref, user.uid):
                abort(403, "Not owner of game --- cannot start it!")

            game = game_ref.get().to_dict()
            turn = game.get("turn")

            if turn != 0:
                abort(403, "Game has already started, cannot start again!")

            # input stream of all players
            players = players_ref.stream()

            # now we'll copy over the players from the stream
            lst_players = [p for p in players]
            numPlayers = len(lst_players)

            if numPlayers < 5:
                abort(400, "Not enough players!")

            def selectRandomPlayer(lst_players: List):
                return random.randint(0, len(lst_players) - 1)

            missionMaker = lst_players[0].id # our mission maker is arbitrarily the first one

            # and now we'll assign their roles
            merlinIndex = selectRandomPlayer(lst_players)
            merlin = lst_players[merlinIndex] # grab merlin first
            players_ref.document(merlin.id).update({ # set merlin's role to true
                u'merlin': True
            })
            del lst_players[merlinIndex]

            percivalIndex = selectRandomPlayer(lst_players)
            percival = lst_players[percivalIndex] # grab percival's player_ref
            players_ref.document(percival.id).update({ # set percival's role to true
                u'percival': True
            })
            del lst_players[percivalIndex]

            morganaIndex = selectRandomPlayer(lst_players)
            morgana = lst_players[morganaIndex] # grab morgana's player_ref
            players_ref.document(morgana.id).update({ # set morgana's role to true
                u'morgana': True,
                u'bad': True
            })
            del lst_players[morganaIndex]

            mordredIndex = selectRandomPlayer(lst_players)
            mordred = lst_players[mordredIndex] # grab mordred's player_ref
            players_ref.document(mordred.id).update({ # set mordred's role to true
                u'mordred': True,
                u'bad': True
            })
            del lst_players[mordredIndex]

            # now if the number of players >= 7, add a third bad guy
            if numPlayers >= 7:
                badIndex = selectRandomPlayer(lst_players)
                bad = lst_players[badIndex]
                players_ref.document(bad.id).update({ # set bad's role to true
                    u'bad': True
                })

            # now we'll update the mission maker
            game_ref.update({
                u'missionMaker': missionMaker,
                u'turn': 1,
                u'numPlayers': numPlayers
            })

            return "Success!"

        except UIDError as e:
            abort(400, e.message)