from endpoints.type import GameIDError, game_Exist, get_user
from flask import Blueprint, request, jsonify, abort
from endpoints.firebase import db, doesGameExist, doesUserExistInGame, getGameDict, getGameRef

# TODO: add in the guessing of merlin
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

    return missions[ppl - 5][int((turn - 10)/10)]

# checks if the given uids are in the players list
def isUIDListInGame(uids, playersLst):
    players = {p: True for p in playersLst} # creates a dictionary of all the players, to query in O(1)

    for uid in uids:
        if players.get(uid) == None:
            abort(400, "Not all given uids is part of game!")

# endpoint to propose missions
@turns.route("/proposeMission", methods=['POST'])
def proposeMission():

    # data has to be of form:
    # {
    #   gameId: gameId,
    #   mission: array of player ids,
    #   uid: their user id
    # }

    # ** here we'll reset the votes **

    data = request.json
    try: 
        game_ref = game_Exist(data)
        game = getGameDict(game_ref)

        turn = game.get("turn")
        if turn < 10 or turn > 50 or turn % 10 != 0:
            abort(400, "error... something went wrong with the turn")

        uid = data.get("uid")
        if uid is None or uid == "":
            abort(400, "error... uid not found... login")

        lstPlayers = game.get("playersList")

        # have to check whether it is the right player
        if uid != lstPlayers[game.get("missionMaker")]:
            abort(403, "Not the mission maker cannot do that!")

        num_mission = pplOnMission(turn, game.get("numPlayers"))

        mission = data.get('mission')

        if not type(mission) == list:
            return "Not proper format!"

        if len(mission) != num_mission:
            return "Not the right number of people for the mission"

        mission = data.get("mission")
        # first check if everyone is in the game
        isUIDListInGame(mission, lstPlayers)
        
        game_ref.update({
            u'mission': mission, # we can only query the actual google id - possible vulnerability
            u'turn': turn + 1,
            u'vote': lstPlayers,
            u'voteFor': [],
            u'voteAgainst': [],
            u"successMission": 0,
            u"failMission": 0
        })

        return "Success! Added ppl to mission!"

    except GameIDError as e:
        return e.message

# the following function checks if uid is in list, and if it is, removes it
# only removes a single instance of the uid
def removeUID(uid, uidList):
    # we'll perform a single pass that checks for uid
    # then delete from the index of the uid
 
    uidIndex = None
    for i in range (len(uidList)):
        if uidList[i] == uid:
            uidIndex = i

    if uidIndex == None:
        abort(403, "Your uid was not in the provided list!")

    del uidList[uidIndex]

    return uidList

@turns.route("/voteMission", methods = ['POST'])
def vote():

    # data has to be of form:
    # {
    #   gameId: gameId,
    #   uid: their user id,
    #   voteFor: boolean, voting for the proposed mission or not 
    # }
    try:
        # TODO: check and make sure that the user's id is part of mission
        data = request.json

        uid = data.get("uid")
        voteFor = data.get("voteFor") # voting boolean

        game_ref = game_Exist(data)

        # now we'll query the game's data
        game = getGameDict(game_ref)

        # gets the turn of the game
        turn = game.get("turn")
        if turn % 10 != 1:
            abort(400, "Not time to vote for mission yet!")

        # checks if uid is able to vote
        votes = game.get("vote")

        # now gets the new votes by only adding the uids that aren't similar
        new_votes = removeUID(uid, votes)

        forArray = game.get('voteFor') # array of players voting for the mission
        againstArray = game.get("voteAgainst") # array of players voting against mission

        if voteFor:
            # now we'll add to the voteFor
            # first we'll have to query the score
            forArray.append(uid)
        else:
            againstArray.append(uid)

        
        update = {
            u'voteFor': forArray,
            u'voteAgainst': againstArray,
            u'vote': new_votes,
        }

        # if at the end
        if len(new_votes) == 0:

            votes_for = len(forArray)
            votes_against = len(againstArray)

            update.update({
                u'missionMaker': (game.get("missionMaker") + 1) % game.get("numPlayers"),
            })

            if votes_for >= votes_against:
                # what we do if the mission succeeds
                update.update({
                    u'turn': (turn + 4) # simply move onto next turn
                })
                game_ref.update(update)
                return "Mission passed, moving on"
            else:
                update.update(failTurn(game))
                game_ref.update(update)
                return "Mission rejected"

        # update the number of votes for, and the ones left to vote
        game_ref.update(update)
        return "Success, you have voted"

    except GameIDError as e:
        return e.message

# what we do if the mission is rejected
def failTurn(game):
    rejected = game.get('rejected') + 1
    if rejected >= 5:
        return {
            u'rejected': rejected,
            u'winner': "The bad guys won!",
            u'turn': 60
        }
    else:
        return {
            u'rejected': rejected,
            u'mission': [], # empty the mission, and choose next mission maker
            u'turn': game.get("turn") - 1, # choose next turn
        }

@turns.route("/choose", methods=['POST'])
def choosePassOrFail():

    if request.method == 'POST':
        try:

            # queries the game first
            data = request.json
            game_ref = game_Exist(data)
            game = getGameDict(game_ref)

            turn = game.get("turn")

            if turn % 10 != 5:
                return "Mission did not pass, cannot do this!"

            # gets the uid and checks the turn
            uid = data.get("uid")

            # gets the mission array, to check uids
            mission = game.get("mission")
            new_mission = removeUID(uid, mission)

            vote = data.get("vote") # we will pass in a vote boolean

            update = {}

            fail = game.get("failMission") # the number of fails for this mission
            success = game.get("successMission") # the number of successs for this mission

            if not vote:
                fail += 1 # the number of fails for this mission
                update.update({
                    u'failMission': fail
                })
            else:
                success += 1
                update.update({
                    u'successMission': success
                })

            if len(new_mission) == 0:
                # what we do when everyone has voted
                turn += 5
                update.update({
                    u'turn': turn, # increment to next proposal
                    u"mission": []
                })

                # TODO: add in some more restrictions for say 7-8 players on mission 4
                if fail > 0: # if there is a single fail, fail the mission
                    num_mission_fails = game.get("fail") + 1

                    if num_mission_fails >= 3:
                        update.update({
                            u"winner": "The bad guys won!"
                        })

                    update.update({
                        u"fail": num_mission_fails
                    })

                    game_ref.update(update)
                    return "Mission failed!"
                else:
                    num_mission_successes = game.get("success") + 1

                    if num_mission_successes >= 3:
                        update.update({
                            u"winner": "The good guys won!"
                        })
                    
                    update.update({
                        u"success": num_mission_successes
                    })

                    game_ref.update(update)
                    return "Mission successful!"

            # updates the mission
            update.update({
                u"mission": new_mission
            })

            game_ref.update(update)

            return "One person more has voted!"

        except GameIDError as e:
            return e.message