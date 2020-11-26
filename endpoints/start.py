from flask import Blueprint, request

# so here we'll define endpoints to start the game
start = Blueprint('start', __name__)

# creating a game endpoint
@start.route("/createGame", methods=['POST'])
def createGame():
    pass