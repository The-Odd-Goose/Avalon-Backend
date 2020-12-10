from flask import Blueprint, request, jsonify
from endpoints.firebase import db, doesGameExist, getGameDict, getGameRef

turns = Blueprint('turns', __name__)

# given a certain turn, and number of players, will return the 
def pplOnMission(turn: int, ppl: int) -> int:
    pass

# endpoint to propose missions
@turns.route("/proposeMission", methods=['POST'])
def proposeMission():

    # data has to be of form:
    # {
    #   gameId: gameId,
    #   mission: array of player ids,
    #   uid: their user id
    # }

    # TODO: check user id with players.missionmaker's uid -- import from firebase
    # TODO: add in the dictionaries for the different size of the groups,
    # TODO: its turns, and then corresponding mission sizes

    data = request.json
    game_ref = doesGameExist(data)

    game_ref.update({
        u'mission': data.get('mission')
    })

    return "Success! Added ppl to mission!"

@turns.route("/voteMission", methods = ['POST'])
def vote():

    # data has to be of form:
    # {
    #   gameId: gameId,
    #   userId: their user id,
    #   voteFor: boolean, voting for the proposed mission or not 
    # }

    # TODO: check and make sure that the user's id is part of mission
    data = request.json

    game_id = data.get('gameId')
    uid = data.get("userId")
    voteFor = data.get("voteFor")

    game_ref = getGameRef(game_id)

    # now we'll query the game's data
    game = getGameDict(game_ref)

    if voteFor:
        # now we'll add to the voteFor
        # first we'll have to query the score
        game_ref.update({
            u'votedFor': (game.get('votedFor') + 1)
        })

        return f"Number of votes for: {game.get('votedFor') + 1}"

    # TODO: after they vote, either for or against, remove them from the mission
    # TODO: so that way we can see if they already voted or not

    # TODO: after last person voted, determine if success or fail, and then do more checking
    
    return "You did not vote for the mission hehehe"