from flask import Blueprint, request, jsonify, abort

# other required stuff
from typing import List
import random

from endpoints.firebase import db, doesUserExistInGame, getGameDict, getGameRef

# type checking + user auth:
from endpoints.type import does_user_exist_in_game, game_Exist, is_User, UIDError, GameIDError, is_owner_of_game

# so here we'll define endpoints to start the game
start = Blueprint('start', __name__)

# the start of a new game
newGame = {
    u"turn": 0, # the turn of the game -- x0 is proposal, x1 is voting, x5 is choice, 60 is finished
    u'numPlayers': 1,
}

freshGame = {
    u"failMission": 0, # for voting on the mission, num of  
    u"successMission": 0, # number of players voting for the mission to succeed
    u"rejected": 0, # number of rejected missions
    u"success": 0, # number of successful missions
    u"fail": 0, # number of failed missions -- not required, but easier for frontend
    u"missionMaker": 0, # the mission maker -- index based on all player's user id
    u"voteFor": [], # the players' uid voting for mission to run
    u"voteAgainst": [], # the players' uid voting against the mission to run
    u"mission": [], # ! players on the mission -- user ids
    u'vote': [], # this will have the different players who have not voted yet for the next mission -- user ids
    u"turn": 10,
    u'winner': None
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
        u'owner': False,
    })

# creating a game endpoint
# ! Deleting and creating works !
@start.route("/game", methods=['POST', 'DELETE'])
def createGame():

    # TODO: add a timestamp for when the game was created
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
    elif request.method == 'DELETE':
        try:
            data = request.json
            user = is_User(data)
            game_ref = game_Exist(data)
            
            user = doesUserExistInGame(game_ref.collection(u"players"), data.get("uid"))

            if user and user.to_dict().get("owner"):
                game_ref.delete()
                return {"message": "Delete"}

            # if not the owner, abort
            abort(403, "Not the owner, cannot delete this game")
        except UIDError as e:
            abort(403, e.message)
        except ValueError as e:
            abort(400, "UID request was incorrect")

# ! Adding a player works + removing a player works !
@start.route("/gameMember", methods=['POST', 'DELETE'])
def addToGame():

    if request.method == 'POST':
        # data needs to be of type:
        # {
        #   username, gameId, uid --- note we will get photoURL through uid
        # }
        data = request.json

        try:

            user = is_User(data)
            game_ref = game_Exist(data)
            game = getGameDict(game_ref)

            turn = game.get("turn")
            num_players = game.get("numPlayers")

            if turn != 0:
                abort(400, "Game has already started, cannot add players")
            
            if num_players >= 8:
                abort(400, "Max at 8 players!")

            player_ref = game_ref.collection(u"players")
            new_player_ref = does_user_exist_in_game(player_ref, user.uid)

            # if num_players < 8, then increment it
            game_ref.update({
                u"numPlayers": (num_players + 1)
            })

            # so now we grab the game reference, and we add our player to the collection of players
            init_player(new_player_ref, data.get("username"), user)
            return {"message": "Success!"}

        # what happens with different types of errors
        except UIDError as e:
            abort(403, f"Failure occured due to user... {e.message}")
        except GameIDError as e:
            abort(400, f"Failure occured due to game id... {e.message}")
    elif request.method == 'DELETE':
        data = request.json

        try:
            user = is_User(data)
            game_ref = game_Exist(data)
            game = getGameDict(game_ref)

            if game.get("turn") != 0:
                abort(400, "Game has already started, cannot leave")

            num_players = game.get("numPlayers") - 1
            if num_players == 0:
                game_ref.delete()
                return {"message": "Game deleted"}

            player_ref = game_ref.collection(u"players")
            user = doesUserExistInGame(players_ref=player_ref, uid=user.uid)

            # I realized too late that getGameDict gets any document dictionary for that matter

            if user:
                # if the user exists in the game, query its document id
                # then using this, we delete it from players_ref
                player_ref.document(user.id).delete()
                user_dict = user.to_dict()

                if user_dict.get("owner"):
                    # transfer ownership
                    nxt_player = [p for p in player_ref.limit(1).stream()][0]
                    player_ref.document(nxt_player.id).update({
                        u"owner": True
                    })

                game_ref.update({
                    u"numPlayers": num_players
                })

                return {"message": "Deleted"}
            
            abort(400, "User does not exist in game")

        except UIDError as e:
            abort(403, f"Failure occured due to user... {e.message}")
        except GameIDError as e:
            abort(400, f"Failure occured due to game id... {e.message}")

# ! the following two endpoints should work... !
@start.route("/startGame", methods=['POST'])
def startGame():

    if request.method == 'POST':
        data = request.json
        def turnCheck(turn):
            return turn != 0

        return cleanSlate(data, turnCheck)

@start.route("/restartGame", methods=['POST'])
def restartGame():
    if request.method == 'POST':
        data = request.json
        def turnCheck(turn):
            return False
        return cleanSlate(data, turnCheck)

# sets a clean slate to the game
def cleanSlate(data, turnCheck):
    try:
        game_ref = game_Exist(data)
        user = is_User(data)
        players_ref = game_ref.collection(u'players')

        # if they are not the owner of the game, return false
        if not is_owner_of_game(players_ref, user.uid):
            abort(403, "Not owner of game --- cannot start it!")

        game = game_ref.get().to_dict()
        turn = game.get("turn")

        if turnCheck(turn):
            abort(403, "Game has already started, cannot start again!")

        # input stream of all players
        players = players_ref.stream()

        # now we'll copy over the players from the stream
        lst_players = [p for p in players]
        players_id_lst = [p.to_dict().get("uid") for p in lst_players] # gets a list of all the player's access id
        numPlayers = game.get("numPlayers")

        if numPlayers < 5 or numPlayers > 8:
            abort(400, "Not the right number of players -- between 5 and 8!")

        restart = {
            u"vote": players_id_lst,
            u"playersList": players_id_lst,
            u"winner": None,
        }
        update = {**freshGame, **restart}

        # we need to update the players in the game
        game_ref.update(update)

        def selectRandomPlayer(lst_players: List):
            return random.randint(0, len(lst_players) - 1)

        # and now we'll assign their roles
        merlinIndex = selectRandomPlayer(lst_players)
        merlin = lst_players[merlinIndex] # grab merlin first
        players_ref.document(merlin.id).update({ # set merlin's role to true
            u'merlin': True,
            u"bad": False,
            u"morgana": False,
            u"mordred": False,
            u"percival": False
        })
        del lst_players[merlinIndex]

        percivalIndex = selectRandomPlayer(lst_players)
        percival = lst_players[percivalIndex] # grab percival's player_ref
        players_ref.document(percival.id).update({ # set percival's role to true
            u'percival': True,
            u"bad": False,
            u"morgana": False,
            u"mordred": False,
            u"merlin": False
        })
        del lst_players[percivalIndex]

        morganaIndex = selectRandomPlayer(lst_players)
        morgana = lst_players[morganaIndex] # grab morgana's player_ref
        players_ref.document(morgana.id).update({ # set morgana's role to true
            u'morgana': True,
            u'bad': True,
            u"percival": False,
            u"merlin": False,
            u"mordred": False,
        })
        del lst_players[morganaIndex]

        mordredIndex = selectRandomPlayer(lst_players)
        mordred = lst_players[mordredIndex] # grab mordred's player_ref
        players_ref.document(mordred.id).update({ # set mordred's role to true
            u'mordred': True,
            u'bad': True,
            u"percival": False,
            u"merlin": False,
            u'morgana': False,
        })
        del lst_players[mordredIndex]

        # now if the number of players >= 7, add a third bad guy
        if numPlayers >= 7:
            badIndex = selectRandomPlayer(lst_players)
            bad = lst_players[badIndex]
            players_ref.document(bad.id).update({ # set bad's role to true
                u'bad': True,
                u"percival": False,
                u"merlin": False,
                u"morgana": False,
                u"mordred": False,
            })

        return {"message": "Success!"}

    except GameIDError as e:
        abort(400, e.message)
    except UIDError as e:
        abort(400, e.message)