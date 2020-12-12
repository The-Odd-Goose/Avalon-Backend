from endpoints.type import GameIDError
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

        uid = data.get("uid")
        if uid is None or uid == "":
            return "error... uid not found... login"


        players_ref = game_ref.collection(u'players')

        # have to check whether it is the right player
        mission_maker = players_ref.document(game.get("missionMaker")).get().to_dict()
        if uid != mission_maker.get("uid"):
            return "Not the mission maker cannot do that!"

        players_lst = [p for p in players_ref.stream()] # gets the list of players

        num_mission = pplOnMission(game.get("turn"), len(players_lst))

        mission = data.get('mission')

        if not type(mission) == list:
            return "Not proper format!"

        if len(mission) < num_mission:
            return "Not enought people on mission to set!"
        
        game_ref.update({
            u'mission': data.get('mission')
        })

        return "Success! Added ppl to mission!"

    except GameIDError as e:
        return e.message

# TODO: figure some more shit out dude
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