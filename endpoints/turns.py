from flask import Blueprint, request, jsonify
from endpoints.firebase import db

turns = Blueprint('turns', __name__)

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

    game_id = data.get('gameId')
    game_ref = db.collection(u'games').document(game_id)

    game_ref.update({
        u'mission': data.get('mission')
    })

    return "Success! Added ppl to mission!"