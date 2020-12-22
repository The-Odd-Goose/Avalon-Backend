from endpoints.type import GameIDError, game_Exist, get_user
from flask import Blueprint, request, jsonify
from endpoints.firebase import db, doesGameExist, doesUserExistInGame, getGameDict, getGameRef

turns = Blueprint('turns', __name__)

# given a certain turn, and number of players, will return the 
def pplOnMission(turn: int, ppl: int) -> int:
    # hold the array of mission and people here:
    missions = [
        [2, 3, 2, 3, 3], # 5 people
        [2, 3, 3, 3, 4], # 6 people
        [3, 4, 3, 4, 5], # 7 people
        [3, 4, 4, 4, 5] # 8 people
    ]

    return missions[ppl - 5][turn - 1]

# endpoint to propose missions
@turns.route("/proposeMission", methods=['POST'])
def proposeMission():

    # data has to be of form:
    # {
    #   gameId: gameId,
    #   mission: array of player ids,
    #   uid: their user id
    # }

    # TODO: test this!

    data = request.json
    try: 
        game_ref = doesGameExist(data)
        game = game_ref.get().to_dict()

        turn = game.get("turn")
        if turn < 1 or turn > 5 or turn % 1 != 0:
            return "error... something went wrong with the turn"

        uid = data.get("uid")
        if uid is None or uid == "":
            return "error... uid not found... login"

        players_ref = game_ref.collection(u'players')

        # have to check whether it is the right player
        if uid != game.get("playersList")[game.get("missionMaker")]:
            return "Not the mission maker cannot do that!"

        num_mission = pplOnMission(turn, game.get("numPlayers"))

        mission = data.get('mission')

        if not type(mission) == list:
            return "Not proper format!"

        if len(mission) != num_mission:
            return "Not the right number of people for the mission"
        
        game_ref.update({
            u'mission': data.get('mission'), # we can only query the actual google id - possible vulnerability
            u'turn': turn + 0.1,

        })

        return "Success! Added ppl to mission!"

    except GameIDError as e:
        return e.message

@turns.route("/voteMission", methods = ['POST'])
def vote():

    # data has to be of form:
    # {
    #   gameId: gameId,
    #   userId: their user id,
    #   voteFor: boolean, voting for the proposed mission or not 
    # }
    try:
        # TODO: check and make sure that the user's id is part of mission
        data = request.json

        uid = data.get("userId")
        voteFor = data.get("voteFor")

        game_ref = game_Exist(data)

        # now we'll query the game's data
        game = getGameDict(game_ref)

        # gets the turn of the game
        turn = game.get("turn")
        if turn % 1 != 0.1:
            return "Not time to vote for mission yet!"

        num_votes = game.get('votedFor')

        if voteFor:
            # now we'll add to the voteFor
            # first we'll have to query the score

            num_votes = num_votes + 1
            game_ref.update({
                u'votedFor': num_votes
            })
        
        player = get_user(game_ref.collection("players"), uid)

        votes = game.get("vote")
        new_votes = []
        for vote in votes:
            if vote != player.get("uid"):
                new_votes.append(vote)

        if len(new_votes) == 0:
            num_players = game.get("numPlayers")
            if num_votes >= (num_players / 2):
                runTurn(game_ref, game)
                return "Mission passed, moving on"
            else:
                failTurn(game_ref, game)
                return "Turn failed"
        return "Success, you have voted"

    except GameIDError as e:
        return e.message

# what we do if the mission proposal suceeds
def runTurn(game_ref, game):

    turn = game.get("turn")
    game_ref.update({
        u'turn': (turn + 0.4)
    })

# what we do if the mission is rejected
def failTurn(game_ref, game):
    rejected = game.get('rejected') + 1
    if rejected >= 5:
        game_ref.set({
            u'winner': "The bad guys won!"
        })
    else:
        game_ref.update({
            u'rejected': rejected,
            u'mission': [],
            u'missionMaker': (game.get("missionMaker") + 1) % game.get("numPlayers"),
            u'turn': game.get("turn") - 0.1
        })

@turns.route("/choose")
def choosePassOrFail():
    try:

        # queries the game first
        data = request.json
        game_ref = game_Exist(data)
        game = getGameDict(game_ref)
        
        # gets the uid
        uid = data.get("uid")
        turn = game.get("turn")

        if turn % 1 != 0.5:
            return "Mission did not pass, cannot do this!"

        mission = game.get("mission")
        
        voterIndex = None
        for i in range (len(mission)):
            player = mission[i]
            if uid == player:
                voterIndex = i
        
        if voterIndex == None:
            return "You are not deciding this mission!"

        vote = data.get("vote") # we will pass in a vote boolean
        fail = game.get("failMission") # the boolean that determines whether people have failed the mission


        if not vote:
            game_ref.update({
                u'fail': fail
            })
        
        del mission[voterIndex]

        if len(mission) == 0:
            # what we do when everyone has voted
            success = game.get("success") # the number of successful missions

        else:
            pass

        game.update({
            u"mission": mission
        })

        return "One person more has voted!"

    except GameIDError as e:
        return e.message