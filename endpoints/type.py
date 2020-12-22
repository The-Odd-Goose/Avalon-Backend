# this module here will define some type checking functions

from endpoints.firebase import doesUserExistInGame, getOwner

class UIDError(Exception):
    # the error that occurs with uids
    def __init__(self, message="A uid error has occured"):
        self.message = message

class GameIDError(Exception):
    def __init__(self, message="A game error has occured"):
        self.message = message

# this function checks if the user exists, if it does, returns the user object
def is_User(data):
    
    uid = data.get("uid")
    # checks the user ID directly if in object
    if uid == None or uid == "":
        raise UIDError("UID was not given in request")

    # then needs to check the firebase to see if user is in there
    # imports the firebase function that does this
    from endpoints.firebase import doesUserExist
    user = doesUserExist(uid)

    if type(user) == str:
        raise UIDError(user)

    return user

# ** this function returns the game_ref, or raises an error**
def game_Exist(data):

    game_id = data.get("gameId")

    if game_id == None:
        raise GameIDError("Game Id was not given in request")

    # returns a game from checking if the game exists -- a game ref actually
    from endpoints.firebase import doesGameExist
    game_ref = doesGameExist(game_id)

    # if it is a string however, an error has occured
    if type(game_ref) == str:
        raise GameIDError(game_ref)

    return game_ref

# ** this function returns a user_ref or raises an error**
def does_user_exist_in_game(players_ref, uid):

    user_ref = doesUserExistInGame(players_ref, uid)

    if type(user_ref) == list:
        raise UIDError("User is already in game!")

    return user_ref

# ** given a certain players_ref, search if the uid of the owner is the same as the given uid**
def is_owner_of_game(players_ref, uid):
    owner_ref = getOwner(players_ref)
    return owner_ref.to_dict().get("uid") == uid

def get_user(players_ref, uid):
    players = players_ref.where(u"uid", u"==", uid).limit(1)
    player_lst = [p for p in players.stream()]

    if len(player_lst) == 0:
        raise UIDError("user does not exist!")

    return player_lst[0].get().to_dict()