from flask import Blueprint, request, jsonify

# other required stuff
from typing import List
import random

from endpoints.firebase import db

# so here we'll define endpoints to start the game
start = Blueprint('start', __name__)

# the start of a new game
newGame = {
    u"fail": 0,
    u"rejected": 0,
    u"success": 0,
    u"turn": 0, # the turn of the game
    u"missionMaker": None, # the mission maker
    u"votedFor": [], # those who voted for the mission
    u"mission": [], # players on the mission
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

@start.route("/startGame", methods=['POST'])
def startGame():

    if request.method == 'POST':
        data = request.json

        # TODO: check if game exists, and if userId is the owner
        game_id = data.get('gameId')

        game_ref = db.collection(u'games').document(game_id)
        # input stream of all players
        players = game_ref.collection(u'players').stream()

        def selectRandomPlayer(lst_players: List):
            return random.randint(0, len(lst_players) - 1)

        # now we'll copy over the players from the stream
        lst_players = []

        for player in players:
            lst_players.append(player)

        if len(lst_players) < 5:
            return "Not enough players!"

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
