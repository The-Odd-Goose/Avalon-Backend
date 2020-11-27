from flask import Blueprint, request
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('../service-account.json')
default_app = firebase_admin.initialize_app(cred)
# TODO: switch to this for deployment
# default_app = firebase_admin.initialize_app()

db = firestore.client()

# so here we'll define endpoints to start the game
start = Blueprint('start', __name__)

# creating a game endpoint
@start.route("/createGame", methods=['POST'])
def createGame():
    pass